# database/mock_data.py
"""
Mock data for the restaurant database.

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
    Seed menu categories.
    
    Args:
        session: SQLAlchemy session
    """
    categories = [
        MenuCategory(name="Appetizers", description="Small dishes to start your meal", display_order=1),
        MenuCategory(name="Soups & Salads", description="Fresh and healthy options", display_order=2),
        MenuCategory(name="Main Courses", description="Our signature dishes", display_order=3),
        MenuCategory(name="Pasta", description="Homemade pasta dishes", display_order=4),
        MenuCategory(name="Pizza", description="Wood-fired pizzas", display_order=5),
        MenuCategory(name="Sides", description="Perfect accompaniments", display_order=6),
        MenuCategory(name="Desserts", description="Sweet treats to end your meal", display_order=7),
        MenuCategory(name="Beverages", description="Refreshing drinks", display_order=8),
    ]
    
    for category in categories:
        session.add(category)
    
    session.commit()

def seed_ingredients(session: Session):
    """
    Seed ingredients.
    
    Args:
        session: SQLAlchemy session
    """
    ingredients = [
        Ingredient(name="Tomato", description="Fresh ripe tomatoes", allergen=False),
        Ingredient(name="Onion", description="Sweet yellow onions", allergen=False),
        Ingredient(name="Garlic", description="Fresh garlic cloves", allergen=False),
        Ingredient(name="Basil", description="Fresh basil leaves", allergen=False),
        Ingredient(name="Mozzarella", description="Fresh mozzarella cheese", allergen=True),
        Ingredient(name="Parmesan", description="Aged Parmesan cheese", allergen=True),
        Ingredient(name="Olive Oil", description="Extra virgin olive oil", allergen=False),
        Ingredient(name="Salt", description="Sea salt", allergen=False),
        Ingredient(name="Black Pepper", description="Freshly ground black pepper", allergen=False),
        Ingredient(name="Flour", description="All-purpose flour", allergen=True),
        Ingredient(name="Chicken", description="Free-range chicken", allergen=False),
        Ingredient(name="Beef", description="Grass-fed beef", allergen=False),
        Ingredient(name="Salmon", description="Wild-caught salmon", allergen=False),
        Ingredient(name="Shrimp", description="Wild-caught shrimp", allergen=True),
        Ingredient(name="Pasta", description="Homemade pasta", allergen=True),
        Ingredient(name="Rice", description="Arborio rice", allergen=False),
        Ingredient(name="Lettuce", description="Fresh lettuce", allergen=False),
        Ingredient(name="Cucumber", description="Fresh cucumber", allergen=False),
        Ingredient(name="Carrot", description="Fresh carrots", allergen=False),
        Ingredient(name="Mushroom", description="Fresh mushrooms", allergen=False),
        Ingredient(name="Egg", description="Free-range eggs", allergen=True),
        Ingredient(name="Milk", description="Whole milk", allergen=True),
        Ingredient(name="Cream", description="Heavy cream", allergen=True),
        Ingredient(name="Butter", description="Unsalted butter", allergen=True),
        Ingredient(name="Sugar", description="Granulated sugar", allergen=False),
        Ingredient(name="Chocolate", description="Dark chocolate", allergen=True),
        Ingredient(name="Vanilla", description="Pure vanilla extract", allergen=False),
        Ingredient(name="Lemon", description="Fresh lemons", allergen=False),
        Ingredient(name="Lime", description="Fresh limes", allergen=False),
        Ingredient(name="Wine", description="White wine", allergen=False),
        Ingredient(name="Bread", description="Artisan bread", allergen=True),
        Ingredient(name="Nuts", description="Mixed nuts", allergen=True),
        Ingredient(name="Wheat", description="Wheat products", allergen=True),
        Ingredient(name="Soy", description="Soy products", allergen=True),
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
        DietaryRestriction(
            restriction_type=DietaryRestrictionType.KOSHER,
            description="Prepared according to Jewish dietary laws"
        ),
    ]
    
    for restriction in restrictions:
        session.add(restriction)
    
    session.commit()

def seed_menu_items(session: Session):
    """
    Seed menu items.
    
    Args:
        session: SQLAlchemy session
    """
    # Get categories
    categories = {category.name: category for category in session.query(MenuCategory).all()}
    
    menu_items = [
        # Appetizers
        MenuItem(
            category=categories["Appetizers"],
            name="Bruschetta",
            description="Grilled bread rubbed with garlic and topped with diced tomatoes, fresh basil, and olive oil",
            price=8.99,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=10
        ),
        MenuItem(
            category=categories["Appetizers"],
            name="Garlic Bread",
            description="Freshly baked bread with garlic butter and herbs",
            price=5.99,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=8
        ),
        MenuItem(
            category=categories["Appetizers"],
            name="Calamari",
            description="Lightly fried squid served with marinara sauce",
            price=12.99,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=15
        ),
        MenuItem(
            category=categories["Appetizers"],
            name="Mozzarella Sticks",
            description="Breaded and fried mozzarella cheese served with marinara sauce",
            price=9.99,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=12
        ),
        
        # Soups & Salads
        MenuItem(
            category=categories["Soups & Salads"],
            name="Caesar Salad",
            description="Romaine lettuce with Caesar dressing, croutons, and Parmesan cheese",
            price=10.99,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=10
        ),
        MenuItem(
            category=categories["Soups & Salads"],
            name="Minestrone Soup",
            description="Traditional Italian vegetable soup with pasta and beans",
            price=7.99,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=5
        ),
        MenuItem(
            category=categories["Soups & Salads"],
            name="Caprese Salad",
            description="Fresh mozzarella, tomatoes, and basil with balsamic glaze",
            price=11.99,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=8
        ),
        MenuItem(
            category=categories["Soups & Salads"],
            name="Italian Chopped Salad",
            description="Mixed greens, salami, provolone, chickpeas, and Italian dressing",
            price=12.99,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=10
        ),
        
        # Main Courses
        MenuItem(
            category=categories["Main Courses"],
            name="Chicken Parmesan",
            description="Breaded chicken breast topped with marinara sauce and mozzarella, served with pasta",
            price=18.99,
            is_available=True,
            special_item=True,
            spiciness_level=0,
            preparation_time_minutes=25
        ),
        MenuItem(
            category=categories["Main Courses"],
            name="Grilled Salmon",
            description="Atlantic salmon with lemon butter sauce, served with seasonal vegetables",
            price=22.99,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=20
        ),
        MenuItem(
            category=categories["Main Courses"],
            name="Veal Marsala",
            description="Pan-seared veal with mushrooms in Marsala wine sauce, served with pasta",
            price=24.99,
            is_available=True,
            special_item=True,
            spiciness_level=0,
            preparation_time_minutes=30
        ),
        MenuItem(
            category=categories["Main Courses"],
            name="Eggplant Parmesan",
            description="Breaded eggplant topped with marinara sauce and mozzarella, served with pasta",
            price=16.99,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=25
        ),
        
        # Pasta
        MenuItem(
            category=categories["Pasta"],
            name="Spaghetti Bolognese",
            description="Spaghetti with slow-cooked meat sauce",
            price=15.99,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=20
        ),
        MenuItem(
            category=categories["Pasta"],
            name="Fettuccine Alfredo",
            description="Fettuccine pasta in a rich, creamy Parmesan sauce",
            price=14.99,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=18
        ),
        MenuItem(
            category=categories["Pasta"],
            name="Lasagna",
            description="Layers of pasta, ricotta cheese, and meat sauce",
            price=16.99,
            is_available=True,
            special_item=True,
            spiciness_level=0,
            preparation_time_minutes=15
        ),
        MenuItem(
            category=categories["Pasta"],
            name="Linguine with Clams",
            description="Linguine pasta with fresh clams in white wine sauce",
            price=19.99,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=22
        ),
        
        # Pizza
        MenuItem(
            category=categories["Pizza"],
            name="Margherita Pizza",
            description="Tomato sauce, fresh mozzarella, and basil",
            price=14.99,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=15
        ),
        MenuItem(
            category=categories["Pizza"],
            name="Pepperoni Pizza",
            description="Tomato sauce, mozzarella, and pepperoni",
            price=15.99,
            is_available=True,
            special_item=False,
            spiciness_level=1,
            preparation_time_minutes=15
        ),
        MenuItem(
            category=categories["Pizza"],
            name="Vegetarian Pizza",
            description="Tomato sauce, mozzarella, and assorted vegetables",
            price=16.99,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=18
        ),
        MenuItem(
            category=categories["Pizza"],
            name="Quattro Formaggi",
            description="Four cheese pizza with mozzarella, gorgonzola, Parmesan, and fontina",
            price=17.99,
            is_available=True,
            special_item=True,
            spiciness_level=0,
            preparation_time_minutes=15
        ),
        
        # Sides
        MenuItem(
            category=categories["Sides"],
            name="Roasted Potatoes",
            description="Potatoes roasted with rosemary and garlic",
            price=5.99,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=8
        ),
        MenuItem(
            category=categories["Sides"],
            name="Grilled Vegetables",
            description="Seasonal vegetables grilled with olive oil and herbs",
            price=6.99,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=10
        ),
        MenuItem(
            category=categories["Sides"],
            name="Sauteed Spinach",
            description="Spinach sautéed with garlic and olive oil",
            price=5.99,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=8
        ),
        MenuItem(
            category=categories["Sides"],
            name="Truffle Fries",
            description="French fries with truffle oil and Parmesan cheese",
            price=7.99,
            is_available=True,
            special_item=True,
            spiciness_level=0,
            preparation_time_minutes=10
        ),
        
        # Desserts
        MenuItem(
            category=categories["Desserts"],
            name="Tiramisu",
            description="Classic Italian dessert with layers of coffee-soaked ladyfingers and mascarpone cream",
            price=8.99,
            is_available=True,
            special_item=True,
            spiciness_level=0,
            preparation_time_minutes=5
        ),
        MenuItem(
            category=categories["Desserts"],
            name="Cannoli",
            description="Crispy pastry shells filled with sweet ricotta cream",
            price=7.99,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=5
        ),
        MenuItem(
            category=categories["Desserts"],
            name="Panna Cotta",
            description="Italian custard with vanilla and berries",
            price=8.99,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=5
        ),
        MenuItem(
            category=categories["Desserts"],
            name="Chocolate Lava Cake",
            description="Warm chocolate cake with a molten center, served with vanilla ice cream",
            price=9.99,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=12
        ),
        
        # Beverages
        MenuItem(
            category=categories["Beverages"],
            name="Sparkling Water",
            description="San Pellegrino sparkling water",
            price=3.99,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=1
        ),
        MenuItem(
            category=categories["Beverages"],
            name="Soda",
            description="Assorted sodas",
            price=2.99,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=1
        ),
        MenuItem(
            category=categories["Beverages"],
            name="Iced Tea",
            description="Fresh brewed iced tea",
            price=3.99,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=2
        ),
        MenuItem(
            category=categories["Beverages"],
            name="Espresso",
            description="Traditional Italian espresso",
            price=3.99,
            is_available=True,
            special_item=False,
            spiciness_level=0,
            preparation_time_minutes=3
        ),
    ]
    
    for item in menu_items:
        session.add(item)
    
    session.commit()

def seed_menu_item_ingredients(session: Session):
    """
    Seed menu item ingredients.
    
    Args:
        session: SQLAlchemy session
    """
    # Get ingredients
    ingredients = {ingredient.name: ingredient for ingredient in session.query(Ingredient).all()}
    
    # Get menu items
    menu_items = {item.name: item for item in session.query(MenuItem).all()}
    
    # Define relationships
    menu_item_ingredients = [
        # Bruschetta
        MenuItemIngredient(
            menu_item_id=menu_items["Bruschetta"].id,
            ingredient_id=ingredients["Tomato"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Bruschetta"].id,
            ingredient_id=ingredients["Garlic"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Bruschetta"].id,
            ingredient_id=ingredients["Basil"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Bruschetta"].id,
            ingredient_id=ingredients["Olive Oil"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Bruschetta"].id,
            ingredient_id=ingredients["Bread"].id,
            optional=False
        ),
        
        # Garlic Bread
        MenuItemIngredient(
            menu_item_id=menu_items["Garlic Bread"].id,
            ingredient_id=ingredients["Garlic"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Garlic Bread"].id,
            ingredient_id=ingredients["Butter"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Garlic Bread"].id,
            ingredient_id=ingredients["Bread"].id,
            optional=False
        ),
        
        # Chicken Parmesan
        MenuItemIngredient(
            menu_item_id=menu_items["Chicken Parmesan"].id,
            ingredient_id=ingredients["Chicken"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Chicken Parmesan"].id,
            ingredient_id=ingredients["Tomato"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Chicken Parmesan"].id,
            ingredient_id=ingredients["Mozzarella"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Chicken Parmesan"].id,
            ingredient_id=ingredients["Parmesan"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Chicken Parmesan"].id,
            ingredient_id=ingredients["Pasta"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Chicken Parmesan"].id,
            ingredient_id=ingredients["Egg"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Chicken Parmesan"].id,
            ingredient_id=ingredients["Flour"].id,
            optional=False
        ),
        
        # Margherita Pizza
        MenuItemIngredient(
            menu_item_id=menu_items["Margherita Pizza"].id,
            ingredient_id=ingredients["Tomato"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Margherita Pizza"].id,
            ingredient_id=ingredients["Mozzarella"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Margherita Pizza"].id,
            ingredient_id=ingredients["Basil"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Margherita Pizza"].id,
            ingredient_id=ingredients["Olive Oil"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Margherita Pizza"].id,
            ingredient_id=ingredients["Flour"].id,
            optional=False
        ),
        
        # Vegetarian Pizza
        MenuItemIngredient(
            menu_item_id=menu_items["Vegetarian Pizza"].id,
            ingredient_id=ingredients["Tomato"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Vegetarian Pizza"].id,
            ingredient_id=ingredients["Mozzarella"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Vegetarian Pizza"].id,
            ingredient_id=ingredients["Mushroom"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Vegetarian Pizza"].id,
            ingredient_id=ingredients["Onion"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Vegetarian Pizza"].id,
            ingredient_id=ingredients["Olive Oil"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Vegetarian Pizza"].id,
            ingredient_id=ingredients["Flour"].id,
            optional=False
        ),
        
        # Tiramisu
        MenuItemIngredient(
            menu_item_id=menu_items["Tiramisu"].id,
            ingredient_id=ingredients["Egg"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Tiramisu"].id,
            ingredient_id=ingredients["Sugar"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Tiramisu"].id,
            ingredient_id=ingredients["Milk"].id,
            optional=False
        ),
        MenuItemIngredient(
            menu_item_id=menu_items["Tiramisu"].id,
            ingredient_id=ingredients["Cream"].id,
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
            menu_item_id=menu_items["Bruschetta"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Garlic Bread"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Mozzarella Sticks"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Caesar Salad"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Minestrone Soup"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Caprese Salad"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Eggplant Parmesan"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Fettuccine Alfredo"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Margherita Pizza"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Vegetarian Pizza"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Quattro Formaggi"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Roasted Potatoes"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Grilled Vegetables"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Sauteed Spinach"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Truffle Fries"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Tiramisu"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Cannoli"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Panna Cotta"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Chocolate Lava Cake"].id,
            dietary_restriction_id=restrictions["vegetarian"].id
        ),
        
        # Vegan options
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Bruschetta"].id,
            dietary_restriction_id=restrictions["vegan"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Minestrone Soup"].id,
            dietary_restriction_id=restrictions["vegan"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Grilled Vegetables"].id,
            dietary_restriction_id=restrictions["vegan"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Sauteed Spinach"].id,
            dietary_restriction_id=restrictions["vegan"].id
        ),
        
        # Gluten-free options
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Grilled Salmon"].id,
            dietary_restriction_id=restrictions["gluten_free"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Caprese Salad"].id,
            dietary_restriction_id=restrictions["gluten_free"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Grilled Vegetables"].id,
            dietary_restriction_id=restrictions["gluten_free"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Sauteed Spinach"].id,
            dietary_restriction_id=restrictions["gluten_free"].id
        ),
        MenuItemDietaryRestriction(
            menu_item_id=menu_items["Panna Cotta"].id,
            dietary_restriction_id=restrictions["gluten_free"].id
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
            menu_item_id=menu_items["Chicken Parmesan"].id,
            special_price=16.99,
            description="Weekend Special",
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=2),
            active=True
        ),
        SpecialPricing(
            menu_item_id=menu_items["Lasagna"].id,
            special_price=14.99,
            description="Chef's Special",
            start_date=now - timedelta(days=3),
            end_date=now + timedelta(days=4),
            active=True
        ),
        SpecialPricing(
            menu_item_id=menu_items["Tiramisu"].id,
            special_price=7.49,
            description="Dessert of the Week",
            start_date=now - timedelta(days=2),
            end_date=now + timedelta(days=5),
            active=True
        ),
        
        # Future specials
        SpecialPricing(
            menu_item_id=menu_items["Margherita Pizza"].id,
            special_price=12.99,
            description="Pizza Night Special",
            start_date=now + timedelta(days=7),
            end_date=now + timedelta(days=14),
            active=True
        ),
        SpecialPricing(
            menu_item_id=menu_items["Fettuccine Alfredo"].id,
            special_price=12.99,
            description="Pasta Week",
            start_date=now + timedelta(days=10),
            end_date=now + timedelta(days=17),
            active=True
        ),
        
        # Past specials
        SpecialPricing(
            menu_item_id=menu_items["Calamari"].id,
            special_price=10.99,
            description="Appetizer Special",
            start_date=now - timedelta(days=30),
            end_date=now - timedelta(days=23),
            active=False
        ),
        SpecialPricing(
            menu_item_id=menu_items["Grilled Salmon"].id,
            special_price=19.99,
            description="Fish Friday",
            start_date=now - timedelta(days=14),
            end_date=now - timedelta(days=7),
            active=False
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
        RestaurantTable(table_number="2", capacity=2, location="Window"),
        RestaurantTable(table_number="3", capacity=4, location="Window"),
        RestaurantTable(table_number="4", capacity=4, location="Center"),
        RestaurantTable(table_number="5", capacity=4, location="Center"),
        RestaurantTable(table_number="6", capacity=6, location="Center"),
        RestaurantTable(table_number="7", capacity=6, location="Corner"),
        RestaurantTable(table_number="8", capacity=8, location="Corner"),
        RestaurantTable(table_number="9", capacity=2, location="Bar"),
        RestaurantTable(table_number="10", capacity=2, location="Bar"),
        RestaurantTable(table_number="11", capacity=4, location="Patio"),
        RestaurantTable(table_number="12", capacity=4, location="Patio"),
        RestaurantTable(table_number="13", capacity=6, location="Patio"),
        RestaurantTable(table_number="14", capacity=8, location="Private Room"),
        RestaurantTable(table_number="15", capacity=10, location="Private Room"),
    ]
    
    for table in tables:
        session.add(table)
    
    session.commit()

def seed_reservations(session: Session):
    """
    Seed reservations.
    
    Args:
        session: SQLAlchemy session
    """
    # Get tables
    tables = session.query(RestaurantTable).all()
    
    # Define reservations
    now = datetime.now()
    
    # Generate reservation times for the next week
    reservation_times = []
    for day in range(7):
        for hour in [18, 19, 20]:  # 6pm, 7pm, 8pm
            reservation_times.append(
                datetime(now.year, now.month, now.day, hour, 0) + timedelta(days=day)
            )
    
    # Create mock customer data
    customer_names = [
        "John Smith", "Jane Doe", "Michael Johnson", "Emily Williams",
        "David Brown", "Sarah Miller", "Robert Wilson", "Jennifer Moore",
        "William Taylor", "Linda Anderson", "James Thomas", "Patricia Jackson",
        "Christopher White", "Barbara Harris", "Matthew Martin", "Elizabeth Thompson"
    ]
    
    # Generate some reservations
    reservations = []
    for i, time in enumerate(reservation_times[:15]):  # Create 15 reservations
        customer_index = i % len(customer_names)
        party_size = random.randint(2, 8)
        
        reservation = Reservation(
            customer_name=customer_names[customer_index],
            customer_phone=f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            customer_email=f"{customer_names[customer_index].lower().replace(' ', '.')}@example.com",
            party_size=party_size,
            reservation_date=time,
            special_requests="Window seat if possible" if i % 5 == 0 else None,
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
    
    # Add some past reservations
    for i in range(5):
        past_date = now - timedelta(days=i+1, hours=random.randint(1, 5))
        customer_index = (i + 10) % len(customer_names)
        party_size = random.randint(2, 6)
        
        reservation = Reservation(
            customer_name=customer_names[customer_index],
            customer_phone=f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            customer_email=f"{customer_names[customer_index].lower().replace(' ', '.')}@example.com",
            party_size=party_size,
            reservation_date=past_date,
            status=ReservationStatus.COMPLETED
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
    
    # Add some canceled reservations
    for i in range(3):
        future_date = now + timedelta(days=i+10, hours=random.randint(1, 5))
        customer_index = (i + 5) % len(customer_names)
        party_size = random.randint(2, 4)
        
        reservation = Reservation(
            customer_name=customer_names[customer_index],
            customer_phone=f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            customer_email=f"{customer_names[customer_index].lower().replace(' ', '.')}@example.com",
            party_size=party_size,
            reservation_date=future_date,
            status=ReservationStatus.CANCELED
        )
        
        reservations.append(reservation)
    
    for reservation in reservations:
        session.add(reservation)
    
    session.commit()