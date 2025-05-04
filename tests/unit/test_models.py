# tests/unit/test_models.py
"""
Unit tests for database models.
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from database.models import Base, MenuCategory, MenuItem, Ingredient, DietaryRestriction, SpecialPricing, Reservation, RestaurantTable, DietaryRestrictionType, ReservationStatus

# Setup test database
@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)

def test_menu_category(db_session: Session):
    """Test MenuCategory model."""
    # Create a category
    category = MenuCategory(
        name="Test Category",
        description="Test Description",
        display_order=1
    )
    db_session.add(category)
    db_session.commit()
    
    # Retrieve and validate
    retrieved = db_session.query(MenuCategory).filter_by(name="Test Category").first()
    assert retrieved is not None
    assert retrieved.id is not None
    assert retrieved.name == "Test Category"
    assert retrieved.description == "Test Description"
    assert retrieved.display_order == 1

def test_menu_item_with_category(db_session: Session):
    """Test MenuItem model with category relationship."""
    # Create a category
    category = MenuCategory(name="Test Category")
    db_session.add(category)
    db_session.commit()
    
    # Create a menu item
    item = MenuItem(
        name="Test Item",
        description="Test Description",
        price=10.99,
        category_id=category.id
    )
    db_session.add(item)
    db_session.commit()
    
    # Retrieve and validate
    retrieved = db_session.query(MenuItem).filter_by(name="Test Item").first()
    assert retrieved is not None
    assert retrieved.id is not None
    assert retrieved.name == "Test Item"
    assert retrieved.price == 10.99
    assert retrieved.category.name == "Test Category"

def test_menu_item_with_ingredients(db_session: Session):
    """Test MenuItem model with ingredients relationship."""
    # Create a category
    category = MenuCategory(name="Test Category")
    db_session.add(category)
    db_session.commit()
    
    # Create ingredients
    ingredient1 = Ingredient(name="Ingredient 1", allergen=False)
    ingredient2 = Ingredient(name="Ingredient 2", allergen=True)
    db_session.add_all([ingredient1, ingredient2])
    db_session.commit()
    
    # Create a menu item with ingredients
    item = MenuItem(
        name="Test Item",
        description="Test Description",
        price=10.99,
        category_id=category.id,
        ingredients=[ingredient1, ingredient2]
    )
    db_session.add(item)
    db_session.commit()
    
    # Retrieve and validate
    retrieved = db_session.query(MenuItem).filter_by(name="Test Item").first()
    assert retrieved is not None
    assert len(retrieved.ingredients) == 2
    ingredient_names = {i.name for i in retrieved.ingredients}
    assert "Ingredient 1" in ingredient_names
    assert "Ingredient 2" in ingredient_names
    allergens = [i for i in retrieved.ingredients if i.allergen]
    assert len(allergens) == 1
    assert allergens[0].name == "Ingredient 2"

def test_menu_item_with_dietary_restrictions(db_session: Session):
    """Test MenuItem model with dietary restrictions relationship."""
    # Create a category
    category = MenuCategory(name="Test Category")
    db_session.add(category)
    db_session.commit()
    
    # Create dietary restrictions
    veg = DietaryRestriction(restriction_type=DietaryRestrictionType.VEGETARIAN)
    gf = DietaryRestriction(restriction_type=DietaryRestrictionType.GLUTEN_FREE)
    db_session.add_all([veg, gf])
    db_session.commit()
    
    # Create a menu item with dietary restrictions
    item = MenuItem(
        name="Test Item",
        description="Test Description",
        price=10.99,
        category_id=category.id,
        dietary_restrictions=[veg, gf]
    )
    db_session.add(item)
    db_session.commit()
    
    # Retrieve and validate
    retrieved = db_session.query(MenuItem).filter_by(name="Test Item").first()
    assert retrieved is not None
    assert len(retrieved.dietary_restrictions) == 2
    restriction_types = {dr.restriction_type for dr in retrieved.dietary_restrictions}
    assert DietaryRestrictionType.VEGETARIAN in restriction_types
    assert DietaryRestrictionType.GLUTEN_FREE in restriction_types
    assert retrieved.is_vegetarian()
    assert retrieved.is_gluten_free()
    assert not retrieved.is_vegan()

def test_special_pricing(db_session: Session):
    """Test SpecialPricing model."""
    # Create a category and menu item
    category = MenuCategory(name="Test Category")
    db_session.add(category)
    db_session.commit()
    
    item = MenuItem(
        name="Test Item",
        description="Test Description",
        price=10.99,
        category_id=category.id
    )
    db_session.add(item)
    db_session.commit()
    
    # Create special pricing
    now = datetime.now()
    special = SpecialPricing(
        menu_item_id=item.id,
        special_price=8.99,
        description="Weekend Special",
        start_date=now - timedelta(days=1),
        end_date=now + timedelta(days=1),
        active=True
    )
    db_session.add(special)
    db_session.commit()
    
    # Retrieve and validate
    retrieved_item = db_session.query(MenuItem).filter_by(name="Test Item").first()
    assert retrieved_item is not None
    assert len(retrieved_item.special_prices) == 1
    assert retrieved_item.special_prices[0].special_price == 8.99
    assert retrieved_item.special_prices[0].is_active()
    
    # Check current price
    assert retrieved_item.get_current_price() == 8.99

def test_reservation_with_tables(db_session: Session):
    """Test Reservation model with tables relationship."""
    # Create tables
    table1 = RestaurantTable(table_number="1", capacity=2, location="Window")
    table2 = RestaurantTable(table_number="2", capacity=4, location="Center")
    db_session.add_all([table1, table2])
    db_session.commit()
    
    # Create a reservation with tables
    now = datetime.now()
    reservation = Reservation(
        customer_name="John Doe",
        customer_phone="555-1234",
        customer_email="john@example.com",
        party_size=6,
        reservation_date=now + timedelta(days=1),
        status=ReservationStatus.CONFIRMED,
        tables=[table1, table2]
    )
    db_session.add(reservation)
    db_session.commit()
    
    # Retrieve and validate
    retrieved = db_session.query(Reservation).filter_by(customer_name="John Doe").first()
    assert retrieved is not None
    assert retrieved.customer_name == "John Doe"
    assert retrieved.party_size == 6
    assert retrieved.status == ReservationStatus.CONFIRMED
    assert len(retrieved.tables) == 2
    table_numbers = {t.table_number for t in retrieved.tables}
    assert "1" in table_numbers
    assert "2" in table_numbers
    
    # Test status change methods
    retrieved.cancel()
    db_session.commit()
    assert retrieved.status == ReservationStatus.CANCELED