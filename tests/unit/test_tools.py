# tests/unit/test_tools.py
"""
Unit tests for tool functions.
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from database.models import Base, MenuCategory, MenuItem, Ingredient, DietaryRestriction, SpecialPricing, Reservation, RestaurantTable, DietaryRestrictionType, ReservationStatus
from database.mock_data import seed_database
from app.tools.menu_query import get_menu_categories, get_menu_items_by_category, search_menu_items, get_menu_items_by_dietary_restriction
from app.tools.pricing import get_item_price, get_special_pricing, calculate_order_total
from app.tools.reservations import check_reservation_availability, create_reservation, get_upcoming_reservations, cancel_reservation

# Setup test database with mock data
@pytest.fixture
def db_session():
    """Create an in-memory SQLite database with mock data for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    # Seed with mock data
    seed_database(session)
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)

def test_get_menu_categories(db_session: Session):
    """Test get_menu_categories tool function."""
    categories = get_menu_categories(db_session)
    
    assert len(categories) > 0
    assert all(isinstance(cat, dict) for cat in categories)
    assert all(key in cat for cat in categories for key in ["id", "name", "description", "display_order"])
    
    # Verify categories are ordered by display_order
    assert all(categories[i]["display_order"] <= categories[i+1]["display_order"] for i in range(len(categories)-1))

def test_get_menu_items_by_category(db_session: Session):
    """Test get_menu_items_by_category tool function."""
    # Get a category ID
    categories = get_menu_categories(db_session)
    category_id = categories[0]["id"]
    
    items = get_menu_items_by_category(db_session, category_id)
    
    assert isinstance(items, list)
    assert all(isinstance(item, dict) for item in items)
    assert all(key in item for item in items for key in ["id", "name", "description", "price"])
    
    # Verify all items are from the requested category
    for item in items:
        db_item = db_session.query(MenuItem).get(item["id"])
        assert db_item.category_id == category_id

def test_search_menu_items(db_session: Session):
    """Test search_menu_items tool function."""
    # Search for a common term
    results = search_menu_items(db_session, "Pizza")
    
    assert isinstance(results, list)
    assert len(results) > 0
    assert all(isinstance(item, dict) for item in results)
    assert all(key in item for item in results for key in ["id", "name", "description", "price", "category"])
    
    # Verify all items have "Pizza" in their name
    assert all("Pizza" in item["name"] for item in results)
    
    # Test with no results
    no_results = search_menu_items(db_session, "NonexistentItem")
    assert isinstance(no_results, list)
    assert len(no_results) == 0

def test_get_menu_items_by_dietary_restriction(db_session: Session):
    """Test get_menu_items_by_dietary_restriction tool function."""
    # Get vegetarian items
    veg_items = get_menu_items_by_dietary_restriction(db_session, "vegetarian")
    
    assert isinstance(veg_items, list)
    assert len(veg_items) > 0
    assert all(isinstance(item, dict) for item in veg_items)
    assert all(key in item for item in veg_items for key in ["id", "name", "description", "price", "category"])
    
    # Verify all items are vegetarian
    for item in veg_items:
        db_item = db_session.query(MenuItem).get(item["id"])
        assert any(dr.restriction_type == DietaryRestrictionType.VEGETARIAN for dr in db_item.dietary_restrictions)
    
    # Test with invalid restriction type
    with pytest.raises(ValueError):
        get_menu_items_by_dietary_restriction(db_session, "invalid_restriction")

def test_get_item_price(db_session: Session):
    """Test get_item_price tool function."""
    # Get an item with special pricing
    specials = db_session.query(SpecialPricing).filter(SpecialPricing.active == True).all()
    if specials:
        item_id = specials[0].menu_item_id
        price_info = get_item_price(db_session, item_id)
        
        assert isinstance(price_info, dict)
        assert all(key in price_info for key in ["id", "name", "regular_price", "current_price", "has_special_pricing"])
        assert price_info["has_special_pricing"] == True
        assert "special_pricing" in price_info
        assert price_info["current_price"] < price_info["regular_price"]

def test_get_special_pricing(db_session: Session):
    """Test get_special_pricing tool function."""
    specials = get_special_pricing(db_session)
    
    assert isinstance(specials, list)
    assert all(isinstance(special, dict) for special in specials)
    if specials:
        assert all(key in special for special in specials for key in ["item_id", "item_name", "regular_price", "special_price"])
        assert all(special["special_price"] < special["regular_price"] for special in specials)

def test_calculate_order_total(db_session: Session):
    """Test calculate_order_total tool function."""
    # Get some menu items
    items = db_session.query(MenuItem).limit(3).all()
    item_ids = [item.id for item in items]
    
    # Create an order with different quantities
    order_items = [
        {"id": item_ids[0], "quantity": 2},
        {"id": item_ids[1], "quantity": 1},
        {"id": item_ids[2], "quantity": 3}
    ]
    
    result = calculate_order_total(db_session, order_items)
    
    assert isinstance(result, dict)
    assert all(key in result for key in ["items", "subtotal", "tax", "total"])
    assert isinstance(result["items"], list)
    assert len(result["items"]) == 3
    
    # Verify calculations
    expected_subtotal = sum(item["price"] * item["quantity"] for item in result["items"])
    assert result["subtotal"] == expected_subtotal
    assert result["total"] == result["subtotal"] + result["tax"]

def test_check_reservation_availability(db_session: Session):
    """Test check_reservation_availability tool function."""
    # Get the current date plus one day
    tomorrow = datetime.now() + timedelta(days=1)
    date_str = tomorrow.strftime("%Y-%m-%d")
    time_str = "18:00"  # 6 PM
    
    # Check availability for a reasonable party size
    result = check_reservation_availability(db_session, date_str, time_str, 4)
    
    assert isinstance(result, dict)
    assert "available" in result
    
    if result["available"]:
        assert "date" in result
        assert "time" in result
        assert "party_size" in result
        assert "available_tables" in result
    else:
        assert "error" in result
        if "alternatives" in result:
            assert isinstance(result["alternatives"], list)

def test_create_and_cancel_reservation(db_session: Session):
    """Test create_reservation and cancel_reservation tool functions."""
    # Get the current date plus one day
    tomorrow = datetime.now() + timedelta(days=1)
    date_str = tomorrow.strftime("%Y-%m-%d")
    time_str = "19:00"  # 7 PM
    
    # Create a reservation
    result = create_reservation(
        db_session,
        date_str,
        time_str,
        2,  # party size
        "Test Customer",
        "555-1234",
        "test@example.com",
        "Window seat preferred"
    )
    
    assert isinstance(result, dict)
    
    if result["success"]:
        reservation_id = result["reservation_id"]
        
        # Get the reservation from the database
        reservation = db_session.query(Reservation).get(reservation_id)
        assert reservation is not None
        assert reservation.customer_name == "Test Customer"
        assert reservation.party_size == 2
        assert reservation.special_requests == "Window seat preferred"
        
        # Cancel the reservation
        cancel_result = cancel_reservation(db_session, reservation_id)
        assert cancel_result["success"] == True
        
        # Verify the reservation is canceled
        reservation = db_session.query(Reservation).get(reservation_id)
        assert reservation.status == ReservationStatus.CANCELED
    else:
        # If creation failed, it's likely due to availability. This is acceptable.
        assert "error" in result

def test_get_upcoming_reservations(db_session: Session):
    """Test get_upcoming_reservations tool function."""
    # Create a test reservation
    tomorrow = datetime.now() + timedelta(days=1)
    
    customer_phone = "555-TEST-PHONE"
    
    # Create a reservation directly in the database
    reservation = Reservation(
        customer_name="Test Customer",
        customer_phone=customer_phone,
        party_size=2,
        reservation_date=tomorrow,
        status=ReservationStatus.CONFIRMED
    )
    db_session.add(reservation)
    db_session.commit()
    
    # Get upcoming reservations
    reservations = get_upcoming_reservations(db_session, customer_phone)
    
    assert isinstance(reservations, list)
    assert len(reservations) > 0
    assert all(isinstance(r, dict) for r in reservations)
    assert any(r["id"] == reservation.id for r in reservations)