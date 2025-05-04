# database/mock_data.py
"""
Mock data for the restaurant database with Indian cuisine.

This module provides functions to seed the database with realistic test data.
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
from database.models import (
    MenuCategory, MenuItem, Ingredient, DietaryRestriction,
    SpecialPricing, Reservation, RestaurantTable, ReservationTable,
    MenuItemIngredient, MenuItemDietaryRestriction, DietaryRestrictionType,
    ReservationStatus
)

def seed_database(session: Session):
    """
    Seed the database with mock data.
    
    Args:
        session: SQLAlchemy session
    """
    seed_categories(session)
    seed_ingredients(session)
    seed_dietary_restrictions(session)
    seed_menu_items(session)
    seed_menu_item_ingredients(session)
    seed_menu_item_dietary_restrictions(session)
    seed_special_pricing(session)
    seed_tables(session)
    seed_reservations(session)
    
    session.commit()

def seed_categories(session: Session):
    """
    Seed menu categories with Indian cuisine categories.
    
    Args:
        session: SQLAlchemy session
    """
    categories = [
        MenuCategory(name="Starters", description="Delicious appetizers to begin your meal", display_order=1),
        MenuCategory(name="Main Courses", description="Flavorful Indian curries and dishes", display_order=2),
        MenuCategory(name="Bread", description="Traditional Indian bread varieties", display_order=3),
        MenuCategory(name="Rice Dishes", description="Aromatic rice specialties", display_order=4),
        MenuCategory(name="Desserts", description="Sweet treats to complete your meal", display_order=5),
        MenuCategory(name="Beverages", description="Refreshing drinks and traditional Indian beverages", display_order=6),
    ]
    
    for category in categories:
        session.add(category)
    
    session.commit()

def seed_ingredients(session: Session):
    """
    Seed ingredients common in Indian cuisine.
    
    Args:
        session: SQLAlchemy session
    """
    ingredients = [
        Ingredient(name="Rice", description="Basmati rice", allergen=False),
        Ingredient(name="Wheat Flour", description="Atta flour for bread", allergen=True),
        Ingredient(name="Chickpea Flour", description="Besan flour", allergen=False),
        Ingredient(name="Paneer", description="Indian cottage cheese", allergen=True),
        Ingredient(name="Chicken", description="Fresh chicken", allergen=False),
        Ingredient(name="Lamb", description="Fresh lamb meat", allergen=False),
        Ingredient(name="Potatoes", description="Fresh potatoes", allergen=False),
        Ingredient(name="Onions", description="Red onions", allergen=False),
        Ingredient(name="Tomatoes", description="Ripe tomatoes", allergen=False),
        Ingredient(name="Garlic", description="Fresh garlic", allergen=False),
        Ingredient(name="Ginger", description="Fresh ginger", allergen=False),
        Ingredient(name="Cumin", description="Cumin seeds and powder", allergen=False),
        Ingredient(name="Coriander", description="Coriander seeds and powder", allergen=False),
        Ingredient(name="Turmeric", description="Turmeric powder", allergen=False),
        Ingredient(name="Garam Masala", description="Blend of spices", allergen=False),
        Ingredient(name="Chili", description="Green and red chilies", allergen=False),
        Ingredient(name="Cardamom", description="Green and black cardamom", allergen=False),
        Ingredient(name="Cinnamon", description="Cinnamon sticks", allergen=False),
        Ingredient(name="Milk", description="Whole milk", allergen=True),
        Ingredient(name="Yogurt", description="Plain yogurt", allergen=True),
        Ingredient(name="Ghee", description="Clarified butter", allergen=True),
        Ingredient(name="Sugar", description="Granulated sugar", allergen=False),
        Ingredient(name="Tea Leaves", description="Black tea leaves", allergen=False),
    ]
    
    for ingredient in ingredients:
        session.add(ingredient)
    
    session.commit()

def seed_dietary_restrictions(session: Session):
    """
    Seed dietary restrictions.
    
    Args:
        session: SQLAlchemy session
    """
    restrictions = [
        DietaryRestriction(
            restriction_type=DietaryRestrictionType.VEGETARIAN,
            description="No meat, poultry, or seafood"
        ),
        DietaryRestriction(
            restriction_type=DietaryRestrictionType.VEGAN,
            description="No animal products"
        ),
        DietaryRestriction(
            restriction_type=DietaryRestrictionType.GLUTEN_FREE,
            description="No wheat, barley, or rye"
        ),
        DietaryRestriction(
            restriction_type=DietaryRestrictionType.DAIRY_FREE,
            description="No milk, cheese, or dairy products"
        ),
        DietaryRestriction(
            restriction_type=DietaryRestrictionType.NUT_FREE,
            description="No nuts or nut products"
        ),
        DietaryRestriction(
            restriction_type=DietaryRestrictionType.HALAL,
            description="Prepared according to Islamic law"
        ),
    ]
    
    for restriction in restrictions:
        session.add(restriction)
    
    session.commit()

def seed_menu_items(session: Session):
    """
    Seed menu items with Indian dishes.
    
    Args:
        session: SQLAlchemy session
    """
    # Get categories
    categories = {category.name: category for category in session.query(MenuCategory).all()}
    
    menu_items = [
        # Starters
        MenuItem(
            category=categories["Starters"],
            name="Samosa",
            description="Crispy pastry filled with spiced potatoes and peas",
            price=5.99,
            is_available=True,
            special_item=False,
            spiciness_level=1,
            preparation_time_minutes=15
        ),
        MenuItem(
            category=categories["Starters"],
            name="Paneer Tikka",
            description="Marinated cottage cheese cubes grilled in tandoor",
            price=8.99,
            is_available=True,
            special_item=True,
            spiciness_level=2,
            preparation_time_minutes=20
        ),
        MenuItem(
            category=categories["Starters"],
            name="Pakora",
            description="Vegetable fritters with chickpea batter",
            price=6.99,
            is_available=True,
            special_item=False,
            spiciness_level=1,
            preparation_time_minutes=12
        ),
        
        # Main Courses
        MenuItem(
            category=categories["Main Courses"],
            name="Butter Chicken",
            description="Tandoori chicken in rich tomato and butter gravy",
            price=15.99,
            is_available=True,
            special_item=True,
            spiciness_level=2,
            preparation_time_minutes=25
        ),
        MenuItem(
            category=categories["Main Courses"],
            name="Palak Paneer",
            description="Cottage cheese cubes in spinach gravy",
            price=14.99,
            is_available=True,
            special_item=False,
            spiciness_level=1,
            preparation_time_minutes=20
        ),
        MenuItem(
            category=categories["Main Courses"],
            name="Chana Masala",
            description="Chickpeas cooked with onions, tomatoes and spices",
            price=12.99,
            is_available=True,
            special_item=False,
            spiciness_level=2,
            preparation_time_minutes=18
        ),
        MenuItem(
            category=categories["Main Courses"],
            name="Lamb Rogan Josh",
            description="Tender lamb in aromatic Kashmiri spices",
            price=16.99,
            is_available=True,
            special_item=False,
            spiciness_level=3,
            preparation_time_minutes=30
        ),
        
        # Bread
        MenuItem(
            category=categories["Bread"],
            name="Naan",
            description="Leavened flatbread baked in tandoor",
            price=2.99,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=8
        ),
        MenuItem(
            category=categories["Bread"],
            name="Garlic Naan",
            description="Naan bread with garlic and herbs",
            price=3.99,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=10
        ),
        MenuItem(
            category=categories["Bread"],
            name="Roti",
            description="Whole wheat flatbread",
            price=2.49,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=6
        ),
        
        # Rice Dishes
        MenuItem(
            category=categories["Rice Dishes"],
            name="Vegetable Biryani",
            description="Aromatic rice with mixed vegetables and spices",
            price=13.99,
            is_available=True,
            special_item=False,
            spiciness_level=2,
            preparation_time_minutes=25
        ),
        MenuItem(
            category=categories["Rice Dishes"],
            name="Chicken Biryani",
            description="Fragrant rice cooked with chicken and spices",
            price=15.99,
            is_available=True,
            special_item=True,
            spiciness_level=2,
            preparation_time_minutes=30
        ),
        MenuItem(
            category=categories["Rice Dishes"],
            name="Jeera Rice",
            description="Basmati rice with cumin seeds",
            price=5.99,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=15
        ),
        
        # Desserts
        MenuItem(
            category=categories["Desserts"],
            name="Gulab Jamun",
            description="Deep-fried milk solids soaked in sugar syrup",
            price=5.99,
            is_available=True,
            special_item=True,
            spiciness_level=0,
            preparation_time_minutes=10
        ),
        MenuItem(
            category=categories["Desserts"],
            name="Kheer",
            description="Rice pudding with cardamom and nuts",
            price=5.99,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=15
        ),
        
        # Beverages
        MenuItem(
            category=categories["Beverages"],
            name="Masala Chai",
            description="Spiced tea with milk",
            price=3.99,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=5
        ),
        MenuItem(
            category=categories["Beverages"],
            name="Mango Lassi",
            description="Yogurt drink with mango pulp",
            price=4.99,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=5
        ),
    ]
    
    for item in menu_items:
        session.add(item)
    
    session.commit()

def seed_menu_item_ingredients(session: Session):
    """
    Seed menu item ingredients relationships.
    
    Args:
        session: SQLAlchemy session
    """
    # Get ingredients
    ingredients = {ingredient.name: ingredient for ingredient in session.query(Ingredient).all()}
    
    # Get menu items
    menu_items = {item.name: item for item in session.query(MenuItem).all()}
    
    # Define relationships
    menu_item_ingredients = [
        # Samosa
        MenuItemIngredient(
            menu_item_id=menu_items["Samosa"].id,
            ingredient_id=ingredients["Wheat Flour"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Samosa"].id,
            ingredient_id=ingredients["Potatoes"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Samosa"].id,
            ingredient_id=ingredients["Cumin"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Samosa"].id,
            ingredient_id=ingredients["Coriander"].id,
            optional=False
        ),
        
        # Paneer Tikka
        MenuItemIngredient(
            menu_item_id=menu_items["Paneer Tikka"].id,
            ingredient_id=ingredients["Paneer"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Paneer Tikka"].id,
            ingredient_id=ingredients["Yogurt"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Paneer Tikka"].id,
            ingredient_id=ingredients["Garam Masala"].id,
            optional=False
        ),
        
        # Butter Chicken
        MenuItemIngredient(
            menu_item_id=menu_items["Butter Chicken"].id,
            ingredient_id=ingredients["Chicken"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Butter Chicken"].id,
            ingredient_id=ingredients["Tomatoes"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Butter Chicken"].id,
            ingredient_id=ingredients["Ghee"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Butter Chicken"].id,
            ingredient_id=ingredients["Garam Masala"].id,
            optional=False
        ),
        
        # Naan
        MenuItemIngredient(
            menu_item_id=menu_items["Naan"].id,
            ingredient_id=ingredients["Wheat Flour"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Naan"].id,
            ingredient_id=ingredients["Yogurt"].id,
            optional=False
        ),
        
        # Vegetable Biryani
        MenuItemIngredient(
            menu_item_id=menu_items["Vegetable Biryani"].id,
            ingredient_id=ingredients["Rice"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Vegetable Biryani"].id,
            ingredient_id=ingredients["Onions"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Vegetable Biryani"].id,
            ingredient_id=ingredients["Garam Masala"].id,
            optional=False
        ),
        
        # Gulab Jamun
        MenuItemIngredient(
            menu_item_id=menu_items["Gulab Jamun"].id,
            ingredient_id=ingredients["Milk"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Gulab Jamun"].id,
            ingredient_id=ingredients["Sugar"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Gulab Jamun"].id,
            ingredient_id=ingredients["Cardamom"].id,
            optional=False
        ),
        
        # Masala Chai
        MenuItemIngredient(
            menu_item_id=menu_items["Masala Chai"].id,
            ingredient_id=ingredients["Tea Leaves"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Masala Chai"].id,
            ingredient_id=ingredients["Milk"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Masala Chai"].id,
            ingredient_id=ingredients["Cardamom"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Masala Chai"].id,
            ingredient_id=ingredients["Cinnamon"].id,
            optional=False
        ),
    ]
    
    for item_ingredient in menu_item_ingredients:
        session.add(item_ingredient)
    
    session.commit()

def seed_menu_item_dietary_restrictions(session: Session):
    """
    Seed menu item dietary restrictions.
    
    Args:
        session: SQLAlchemy session
    """
    # Get dietary restrictions
    restrictions = {restriction.restriction_type.value: restriction for restriction in session.query(DietaryRestriction).all()}
    
    # Get menu items
    menu_items = {item.name: item for item in session.query(MenuItem).all()}
    
    # Define relationships
    menu_item_restrictions = [
        # Vegetarian options
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Samosa"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Paneer Tikka"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Pakora"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Palak Paneer"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Chana Masala"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Naan"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Garlic Naan"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Roti"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Vegetable Biryani"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Jeera Rice"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Gulab Jamun"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Kheer"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Masala Chai"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Mango Lassi"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        
        # Vegan options
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Chana Masala"].id,
            dietary_restriction_id=restrictions["vegan"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Roti"].id,
            dietary_restriction_id=restrictions["vegan"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Jeera Rice"].id,
            dietary_restriction_id=restrictions["vegan"].id
        ),
        
        # Gluten-free options
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Butter Chicken"].id,
            dietary_restriction_id=restrictions["gluten_free"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Palak Paneer"].id,
            dietary_restriction_id=restrictions["gluten_free"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Chana Masala"].id,
            dietary_restriction_id=restrictions["gluten_free"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Lamb Rogan Josh"].id,
            dietary_restriction_id=restrictions["gluten_free"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Vegetable Biryani"].id,
            dietary_restriction_id=restrictions["gluten_free"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Chicken Biryani"].id,
            dietary_restriction_id=restrictions["gluten_free"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Jeera Rice"].id,
            dietary_restriction_id=restrictions["gluten_free"].id
        ),
        
        # Halal options
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Butter Chicken"].id,
            dietary_restriction_id=restrictions["halal"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Lamb Rogan Josh"].id,
            dietary_restriction_id=restrictions["halal"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Chicken Biryani"].id,
            dietary_restriction_id=restrictions["halal"].id
        ),
    ]
    
    for item_restriction in menu_item_restrictions:
        session.add(item_restriction)
    
    session.commit()

def seed_special_pricing(session: Session):
    """
    Seed special pricing.
    
    Args:
        session: SQLAlchemy session
    """
    # Get menu items
    menu_items = {item.name: item for item in session.query(MenuItem).all()}
    
    # Define special pricing
    now = datetime.now()
    
    special_pricing = [
        # Current specials
        SpecialPricing(
            menu_item_id=menu_items["Butter Chicken"].id,
            special_price=13.99,
            description="Weekend Special",
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=2),
            active=True
        ),
        SpecialPricing(
            menu_item_id=menu_items["Paneer Tikka"].id,
            special_price=6.99,
            description="Starter Special",
            start_date=now - timedelta(days=3),
            end_date=now + timedelta(days=4),
            active=True
        ),
        SpecialPricing(
            menu_item_id=menu_items["Gulab Jamun"].id,
            special_price=4.99,
            description="Dessert of the Week",
            start_date=now - timedelta(days=2),
            end_date=now + timedelta(days=5),
            active=True
        ),
    ]
    
    for pricing in special_pricing:
        session.add(pricing)
    
    session.commit()

def seed_tables(session: Session):
    """
    Seed restaurant tables.
    
    Args:
        session: SQLAlchemy session
    """
    tables = [
        RestaurantTable(table_number="1", capacity=2, location="Window"),
        RestaurantTable(table_number="2", capacity=4, location="Center"),
        RestaurantTable(table_number="3", capacity=6, location="Corner"),
        RestaurantTable(table_number="4", capacity=8, location="Private Room"),
        RestaurantTable(table_number="5", capacity=2, location="Patio"),
        RestaurantTable(table_number="6", capacity=4, location="Patio"),
    ]
    
    for table in tables:
        session.add(table)
    
    session.commit()

def seed_reservations(session: Session):
    """
    Seed reservations with reduced data.
    
    Args:
        session: SQLAlchemy session
    """
    # Get tables
    tables = session.query(RestaurantTable).all()
    
    # Define reservations
    now = datetime.now()
    
    # Generate 5 reservations for the next few days
    customer_names = [
        "Raj Patel", "Priya Sharma", "Vikram Singh", 
        "Ananya Desai", "Arjun Mehta"
    ]
    
    reservation_times = [
        datetime(now.year, now.month, now.day, 18, 0) + timedelta(days=i)
        for i in range(1, 6)
    ]
    
    reservations = []
    for i, time in enumerate(reservation_times):
        party_size = random.randint(2, 6)
        
        reservation = Reservation(
            customer_name=customer_names[i],
            customer_phone=f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            customer_email=f"{customer_names[i].lower().replace(' ', '.')}@example.com",
            party_size=party_size,
            reservation_date=time,
            special_requests="Window seat if possible" if i % 2 == 0 else None,
            status=ReservationStatus.CONFIRMED
        )
        
        # Add tables to the reservation
        assigned_tables = []
        remaining_capacity = party_size
        
        # Find tables to accommodate the party size
        for table in sorted(tables, key=lambda t: t.capacity):
            if table not in assigned_tables and remaining_capacity > 0:
                assigned_tables.append(table)
                remaining_capacity -= table.capacity
                if remaining_capacity <= 0:
                    break
        
        reservation.tables = assigned_tables
        reservations.append(reservation)
    
    for reservation in reservations:
        session.add(reservation)
    
    session.commit()