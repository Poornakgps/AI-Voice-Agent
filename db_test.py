import os
import sys
from datetime import datetime


sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from database import init_db, db_session
from database.models import MenuCategory, MenuItem, Ingredient, DietaryRestriction
from database.models import SpecialPricing, Reservation, RestaurantTable, DietaryRestrictionType
from database.repository import (
    MenuCategoryRepository, MenuItemRepository, SpecialPricingRepository,
    ReservationRepository, RestaurantTableRepository
)
from app.tools.menu_query import (
    get_menu_categories, get_menu_items_by_category,
    search_menu_items, get_menu_items_by_dietary_restriction
)
from app.tools.pricing import get_item_price, get_special_pricing, calculate_order_total
from app.tools.reservations import (
    check_reservation_availability, create_reservation,
    get_upcoming_reservations, cancel_reservation
)

def print_separator(title):
    """Print a separator with a title."""
    print("\n" + "=" * 80)
    print(" " * 35 + title)
    print("=" * 80 + "\n")

def test_database_init():
    """Initialize the database."""
    print_separator("Initializing Database")
    init_db()
    print("Database initialized successfully.")

def test_menu_categories():
    """Test fetching menu categories."""
    print_separator("Menu Categories")
    with db_session() as session:
        categories = get_menu_categories(session)
        print(f"Found {len(categories)} menu categories:")
        for category in categories:
            print(f"  - {category['name']}: {category['description']}")

def test_menu_items():
    """Test fetching menu items."""
    print_separator("Menu Items by Category")
    with db_session() as session:
        categories = get_menu_categories(session)
        category_id = categories[0]["id"]
        category_name = categories[0]["name"]
        
        items = get_menu_items_by_category(session, category_id)
        print(f"Found {len(items)} items in category '{category_name}':")
        for item in items:
            print(f"  - {item['name']}: ${item['price']:.2f}")
            if item.get('dietary_restrictions'):
                restrictions = [dr["type"] for dr in item["dietary_restrictions"]]
                print(f"    Dietary restrictions: {', '.join(restrictions)}")

def test_search_menu():
    """Test searching menu items."""
    print_separator("Search Menu Items")
    search_term = "Chicken"
    with db_session() as session:
        items = search_menu_items(session, search_term)
        print(f"Found {len(items)} items matching '{search_term}':")
        for item in items:
            print(f"  - {item['name']} (${item['price']:.2f}): {item['description']}")

def test_dietary_restrictions():
    """Test fetching items by dietary restriction."""
    print_separator("Items by Dietary Restriction")
    restriction = "vegetarian"
    with db_session() as session:
        items = get_menu_items_by_dietary_restriction(session, restriction)
        print(f"Found {len(items)} {restriction} items:")
        for item in items:
            print(f"  - {item['name']} (${item['price']:.2f})")

def test_special_pricing():
    """Test special pricing."""
    print_separator("Special Pricing")
    with db_session() as session:
        specials = get_special_pricing(session)
        print(f"Found {len(specials)} active special offers:")
        for special in specials:
            savings = special["regular_price"] - special["special_price"]
            print(f"  - {special['item_name']}: ${special['special_price']:.2f} (save ${savings:.2f}, {special['savings_percentage']}%)")
            print(f"    {special['description']} - Valid until {special['end_date']}")

def test_order_calculation():
    """Test order calculation."""
    print_separator("Order Calculation")
    with db_session() as session:
        items = session.query(MenuItem).limit(3).all()
        item_ids = [item.id for item in items]
        
        order_items = [
            {"id": item_ids[0], "quantity": 2},
            {"id": item_ids[1], "quantity": 1},
            {"id": item_ids[2], "quantity": 3}
        ]
        
        result = calculate_order_total(session, order_items)
        
        print("Order details:")
        for item in result["items"]:
            print(f"  - {item['name']} x{item['quantity']}: ${item['total']:.2f}")
        
        print(f"\nSubtotal: ${result['subtotal']:.2f}")
        print(f"Tax ({result['tax_rate']*100:.1f}%): ${result['tax']:.2f}")
        print(f"Total: ${result['total']:.2f}")

def test_reservation_availability():
    """Test reservation availability."""
    print_separator("Reservation Availability")
    tomorrow = datetime.now()
    date_str = f"{tomorrow.year}-{tomorrow.month:02d}-{tomorrow.day+1:02d}"
    time_str = "19:00"
    party_size = 4
    
    with db_session() as session:
        result = check_reservation_availability(session, date_str, time_str, party_size)
        
        if result["available"]:
            print(f"Reservation available for {party_size} people on {result['date']} at {result['time']}")
            print("Available tables:")
            for table in result["available_tables"]:
                print(f"  - Table {table['table_number']} (capacity: {table['capacity']}, location: {table['location']})")
        else:
            print(f"No availability for {party_size} people on {date_str} at {time_str}")
            if "alternatives" in result:
                print("Alternative times:")
                for alt in result["alternatives"]:
                    print(f"  - {alt}")

def test_make_reservation():
    """Test making a reservation."""
    print_separator("Make Reservation")
    tomorrow = datetime.now()
    date_str = f"{tomorrow.year}-{tomorrow.month:02d}-{tomorrow.day+1:02d}"
    time_str = "18:00"
    
    with db_session() as session:
        result = create_reservation(
            session,
            date_str,
            time_str,
            2,  # party size
            "Test Customer",
            "555-1234",
            "test@example.com",
            "Window seat preferred"
        )
        
        if result["success"]:
            print(f"Reservation created successfully (ID: {result['reservation_id']})")
            print(f"Customer: {result['customer_name']}")
            print(f"Date/time: {result['date']} at {result['time']}")
            print(f"Party size: {result['party_size']}")
            print("Assigned tables:")
            for table in result["tables"]:
                print(f"  - Table {table['table_number']} (capacity: {table['capacity']})")
        else:
            print(f"Failed to create reservation: {result.get('error', 'Unknown error')}")

def main():
    """Run all tests."""
    test_database_init()
    test_menu_categories()
    test_menu_items()
    test_search_menu()
    test_dietary_restrictions()
    test_special_pricing()
    test_order_calculation()
    test_reservation_availability()
    test_make_reservation()
    
    print_separator("Database Testing Complete")
    print("All database tests completed successfully.")

if __name__ == "__main__":
    main()