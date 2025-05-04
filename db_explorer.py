#!/usr/bin/env python
"""
Interactive database explorer for the Voice AI Restaurant Agent.

This script provides a simple CLI for exploring the restaurant database.
"""
import os
import sys
from datetime import datetime
import cmd

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import database modules
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
        self.initialize_database()
    
    def initialize_database(self):
        """Initialize the database."""
        print("Initializing database...")
        init_db()
        print("Database initialized successfully.")
    
    def do_exit(self, arg):
        """Exit the explorer."""
        print("Exiting...")
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
            
            print("-" * 70)
            print(f"{'ID':<5} {'Name':<30} {'Price':<10} {'Special':<10} {'Available':<10}")
            print("-" * 70)
            
            for item in items:
                price = item.get_current_price()
                special = "Yes" if item.special_item else "No"
                available = "Yes" if item.is_available else "No"
                print(f"{item.id:<5} {item.name:<30} ${price:<9.2f} {special:<10} {available:<10}")
    
    def do_item(self, arg):
        """Show details for a specific menu item by ID."""
        if not arg:
            print("Please specify an item ID.")
            return
        
        try:
            item_id = int(arg)
        except ValueError:
            print(f"Invalid item ID: {arg}")
            return
        
        with db_session() as session:
            repo = MenuItemRepository(session)
            item = repo.get_by_id(item_id)
            
            if not item:
                print(f"Item with ID {item_id} not found.")
                return
            
            print("\nItem Details:")
            print("-" * 50)
            print(f"ID: {item.id}")
            print(f"Name: {item.name}")
            print(f"Description: {item.description}")
            print(f"Category: {item.category.name}")
            print(f"Regular Price: ${item.price:.2f}")
            print(f"Current Price: ${item.get_current_price():.2f}")
            print(f"Special Item: {item.special_item}")
            print(f"Available: {item.is_available}")
            print(f"Spiciness Level: {item.spiciness_level}/5")
            print(f"Preparation Time: {item.preparation_time_minutes} minutes")
            
            print("\nDietary Restrictions:")
            if item.dietary_restrictions:
                for dr in item.dietary_restrictions:
                    print(f"  - {dr.restriction_type.value}")
            else:
                print("  None")
            
            print("\nIngredients:")
            if item.ingredients:
                for ing in item.ingredients:
                    allergen = " (Allergen)" if ing.allergen else ""
                    print(f"  - {ing.name}{allergen}")
            else:
                print("  None")
            
            print("\nSpecial Pricing:")
            if item.special_prices:
                for sp in item.special_prices:
                    if sp.is_active():
                        active = " (Active)"
                    else:
                        active = ""
                    print(f"  - ${sp.special_price:.2f}: {sp.description}{active}")
                    print(f"    Valid: {sp.start_date} to {sp.end_date}")
            else:
                print("  None")
    
    def do_search(self, arg):
        """Search menu items by name."""
        if not arg:
            print("Please specify a search term.")
            return
        
        with db_session() as session:
            repo = MenuItemRepository(session)
            items = repo.search_by_name(arg)
            
            print(f"\nSearch Results for '{arg}':")
            print("-" * 70)
            
            if not items:
                print("No items found.")
                return
            
            print(f"{'ID':<5} {'Name':<30} {'Price':<10} {'Category':<20}")
            print("-" * 70)
            
            for item in items:
                price = item.get_current_price()
                print(f"{item.id:<5} {item.name:<30} ${price:<9.2f} {item.category.name:<20}")
    
    def do_dietary(self, arg):
        """List items by dietary restriction type."""
        restriction_types = [rt.value for rt in DietaryRestrictionType]
        
        if not arg:
            print("Please specify a dietary restriction type.")
            print(f"Available types: {', '.join(restriction_types)}")
            return
        
        if arg not in restriction_types:
            print(f"Invalid restriction type: {arg}")
            print(f"Available types: {', '.join(restriction_types)}")
            return
        
        with db_session() as session:
            repo = MenuItemRepository(session)
            restriction_type = DietaryRestrictionType(arg)
            items = repo.get_by_dietary_restriction(restriction_type)
            
            print(f"\n{arg.capitalize()} Menu Items:")
            print("-" * 70)
            
            if not items:
                print("No items found.")
                return
            
            print(f"{'ID':<5} {'Name':<30} {'Price':<10} {'Category':<20}")
            print("-" * 70)
            
            for item in items:
                price = item.get_current_price()
                print(f"{item.id:<5} {item.name:<30} ${price:<9.2f} {item.category.name:<20}")
    
    def do_specials(self, arg):
        """List active special pricing."""
        with db_session() as session:
            repo = SpecialPricingRepository(session)
            specials = repo.get_active_specials()
            
            print("\nActive Special Offers:")
            print("-" * 80)
            
            if not specials:
                print("No active specials found.")
                return
            
            for special in specials:
                item = special.menu_item
                savings = item.price - special.special_price
                savings_pct = (savings / item.price) * 100
                
                print(f"{item.name}")
                print(f"  Regular price: ${item.price:.2f}")
                print(f"  Special price: ${special.special_price:.2f} (save ${savings:.2f}, {savings_pct:.1f}%)")
                print(f"  {special.description}")
                print(f"  Valid until: {special.end_date}")
                print("-" * 80)
    
    def do_tables(self, arg):
        """List restaurant tables."""
        with db_session() as session:
            repo = RestaurantTableRepository(session)
            tables = repo.get_all()
            
            print("\nRestaurant Tables:")
            print("-" * 60)
            print(f"{'ID':<5} {'Number':<10} {'Capacity':<10} {'Location':<20} {'Active':<10}")
            print("-" * 60)
            
            for table in tables:
                active = "Yes" if table.is_active else "No"
                print(f"{table.id:<5} {table.table_number:<10} {table.capacity:<10} {table.location:<20} {active:<10}")
    
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
            
            print("-" * 100)
            
            if not reservations:
                print("No reservations found.")
                return
            
            print(f"{'ID':<5} {'Customer':<20} {'Date':<20} {'Status':<10} {'Party':<5} {'Tables':<20}")
            print("-" * 100)
            
            for reservation in reservations:
                date_str = reservation.reservation_date.strftime("%Y-%m-%d %H:%M")
                table_str = ", ".join([table.table_number for table in reservation.tables])
                print(f"{reservation.id:<5} {reservation.customer_name:<20} {date_str:<20} {reservation.status.value:<10} {reservation.party_size:<5} {table_str:<20}")
    
    def do_reservation(self, arg):
        """Show details for a specific reservation by ID."""
        if not arg:
            print("Please specify a reservation ID.")
            return
        
        try:
            reservation_id = int(arg)
        except ValueError:
            print(f"Invalid reservation ID: {arg}")
            return
        
        with db_session() as session:
            repo = ReservationRepository(session)
            reservation = repo.get_by_id(reservation_id)
            
            if not reservation:
                print(f"Reservation with ID {reservation_id} not found.")
                return
            
            print("\nReservation Details:")
            print("-" * 50)
            print(f"ID: {reservation.id}")
            print(f"Customer: {reservation.customer_name}")
            print(f"Phone: {reservation.customer_phone}")
            print(f"Email: {reservation.customer_email}")
            print(f"Date/Time: {reservation.reservation_date}")
            print(f"Party Size: {reservation.party_size}")
            print(f"Status: {reservation.status.value}")
            
            if reservation.special_requests:
                print(f"Special Requests: {reservation.special_requests}")
            
            print("\nAssigned Tables:")
            if reservation.tables:
                for table in reservation.tables:
                    print(f"  - Table {table.table_number} (capacity: {table.capacity}, location: {table.location})")
            else:
                print("  No tables assigned.")
    
    def do_help(self, arg):
        """List available commands with help text."""
        if arg:
            # Show help for specific command
            super().do_help(arg)
        else:
            # Show general help
            print("\nAvailable Commands:")
            print("-" * 50)
            print("categories       - List all menu categories")
            print("items [cat_id]   - List menu items, optionally by category ID")
            print("item <id>        - Show details for a specific menu item")
            print("search <term>    - Search menu items by name")
            print("dietary <type>   - List items by dietary restriction type")
            print("specials         - List active special pricing")
            print("tables           - List restaurant tables")
            print("reservations [phone] - List reservations, optionally by phone number")
            print("reservation <id> - Show details for a specific reservation")
            print("help [command]   - Show help, optionally for a specific command")
            print("exit/quit        - Exit the explorer")

if __name__ == "__main__":
    explorer = DatabaseExplorer()
    explorer.cmdloop()