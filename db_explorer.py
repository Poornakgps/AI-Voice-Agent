import os
import sys
import cmd
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from database import init_db, db_session
from database.models import (
    MenuCategory, MenuItem, Ingredient, DietaryRestriction,
    SpecialPricing, Reservation, RestaurantTable, DietaryRestrictionType,
    ReservationStatus
)
from database.repository import (
    MenuCategoryRepository, MenuItemRepository, SpecialPricingRepository,
    ReservationRepository, RestaurantTableRepository
)

class DatabaseExplorer(cmd.Cmd):
    """Interactive database explorer."""
    
    intro = """
============================================================================
                        Restaurant Database Explorer
============================================================================

Type 'help' or '?' to list commands.
Type 'exit' or 'quit' to exit.
    """
    prompt = "db> "
    
    def __init__(self):
        """Initialize the database explorer."""
        super().__init__()
        init_db()
        print("Database initialized successfully.")
    
    def do_exit(self, arg):
        """Exit the explorer."""
        return True
    
    def do_quit(self, arg):
        """Exit the explorer."""
        return self.do_exit(arg)
    
    def do_categories(self, arg):
        """List all menu categories."""
        with db_session() as session:
            repo = MenuCategoryRepository(session)
            categories = repo.get_ordered_categories()
            
            print("\nMenu Categories:")
            print("-" * 50)
            for category in categories:
                print(f"{category.id}: {category.name} - {category.description}")
    
    def do_items(self, arg):
        """List menu items, optionally by category ID."""
        with db_session() as session:
            repo = MenuItemRepository(session)
            
            if arg:
                try:
                    category_id = int(arg)
                    items = repo.get_by_category(category_id)
                    cat_repo = MenuCategoryRepository(session)
                    category = cat_repo.get_by_id(category_id)
                    print(f"\nMenu Items in Category '{category.name}':")
                except ValueError:
                    print(f"Invalid category ID: {arg}")
                    return
            else:
                items = repo.get_all()
                print("\nAll Menu Items:")
            
            print("-" * 50)
            print(f"{'ID':<5} {'Name':<30} {'Price':<10}")
            print("-" * 50)
            
            for item in items:
                price = item.get_current_price()
                print(f"{item.id:<5} {item.name:<30} ${price:<9.2f}")
    
    def do_search(self, arg):
        """Search menu items by name."""
        if not arg:
            print("Please specify a search term.")
            return
        
        with db_session() as session:
            repo = MenuItemRepository(session)
            items = repo.search_by_name(arg)
            
            print(f"\nSearch Results for '{arg}':")
            print("-" * 50)
            
            if not items:
                print("No items found.")
                return
            
            for item in items:
                price = item.get_current_price()
                print(f"{item.id}: {item.name} (${price:.2f}), Category: {item.category.name}")
    
    def do_dietary(self, arg):
        """List items by dietary restriction type."""
        restriction_types = [rt.value for rt in DietaryRestrictionType]
        
        if not arg:
            print(f"Please specify a dietary restriction type: {', '.join(restriction_types)}")
            return
        
        if arg not in restriction_types:
            print(f"Invalid restriction type. Available types: {', '.join(restriction_types)}")
            return
        
        with db_session() as session:
            repo = MenuItemRepository(session)
            restriction_type = DietaryRestrictionType(arg)
            items = repo.get_by_dietary_restriction(restriction_type)
            
            print(f"\n{arg.capitalize()} Menu Items:")
            print("-" * 50)
            
            if not items:
                print("No items found.")
                return
            
            for item in items:
                price = item.get_current_price()
                print(f"{item.name} (${price:.2f}) - {item.description[:40]}...")
    
    def do_specials(self, arg):
        """List active special pricing."""
        with db_session() as session:
            repo = SpecialPricingRepository(session)
            specials = repo.get_active_specials()
            
            print("\nActive Special Offers:")
            print("-" * 50)
            
            if not specials:
                print("No active specials found.")
                return
            
            for special in specials:
                item = special.menu_item
                print(f"{item.name}: ${special.special_price:.2f} (regular: ${item.price:.2f})")
                print(f"  {special.description}, valid until {special.end_date.strftime('%Y-%m-%d')}")
    
    def do_reservations(self, arg):
        """List reservations, optionally by phone number."""
        with db_session() as session:
            repo = ReservationRepository(session)
            
            if arg:
                reservations = repo.get_by_phone(arg)
                print(f"\nReservations for phone number {arg}:")
            else:
                reservations = repo.get_all()
                print("\nAll Reservations:")
            
            print("-" * 50)
            
            if not reservations:
                print("No reservations found.")
                return
            
            for r in reservations:
                date_str = r.reservation_date.strftime("%Y-%m-%d %H:%M")
                tables = ", ".join([t.table_number for t in r.tables])
                print(f"ID: {r.id}, {r.customer_name}, {date_str}, {r.status.value}, Tables: {tables}")
    
    def do_help(self, arg):
        """List available commands with help text."""
        if arg:
            super().do_help(arg)
        else:
            print("\nCommands:")
            print("  categories       - List all menu categories")
            print("  items [cat_id]   - List menu items, optionally by category ID")
            print("  search <term>    - Search menu items by name")
            print("  dietary <type>   - List items by dietary restriction type")
            print("  specials         - List active special pricing")
            print("  reservations [phone] - List reservations, optionally by phone number")
            print("  exit/quit        - Exit the explorer")

if __name__ == "__main__":
    explorer = DatabaseExplorer()
    explorer.cmdloop()