from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from database.models import MenuCategory, MenuItem, DietaryRestriction, DietaryRestrictionType
from database.repository import MenuCategoryRepository, MenuItemRepository

def get_menu_categories(db: Session) -> List[Dict[str, Any]]:
    """
    Get all menu categories.
    
    Args:
        db: Database session
        
    Returns:
        List of menu categories
    """
    repo = MenuCategoryRepository(db)
    categories = repo.get_ordered_categories()
    
    return [
        {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "display_order": category.display_order
        }
        for category in categories
    ]

def get_menu_items_by_category(db: Session, category_id: int) -> List[Dict[str, Any]]:
    """
    Get menu items by category.
    
    Args:
        db: Database session
        category_id: Category ID
        
    Returns:
        List of menu items in the category
    """
    repo = MenuItemRepository(db)
    items = repo.get_by_category(category_id)
    
    return [
        {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "price": item.get_current_price(),
            "is_available": item.is_available,
            "special_item": item.special_item,
            "spiciness_level": item.spiciness_level,
            "preparation_time_minutes": item.preparation_time_minutes,
            "dietary_restrictions": [
                {
                    "id": dr.id,
                    "type": dr.restriction_type.value,
                    "description": dr.description
                }
                for dr in item.dietary_restrictions
            ]
        }
        for item in items
        if item.is_available
    ]

def search_menu_items(db: Session, query: str) -> List[Dict[str, Any]]:
    """
    Search for menu items.
    
    Args:
        db: Database session
        query: Search query
        
    Returns:
        List of matching menu items
    """
    repo = MenuItemRepository(db)
    items = repo.search_by_name(query)
    
    return [
        {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "price": item.get_current_price(),
            "category": item.category.name,
            "is_available": item.is_available
        }
        for item in items
        if item.is_available
    ]

def get_menu_items_by_dietary_restriction(
    db: Session, restriction_type: str
) -> List[Dict[str, Any]]:
    """
    Get menu items by dietary restriction.
    
    Args:
        db: Database session
        restriction_type: Dietary restriction type
        
    Returns:
        List of menu items with the given dietary restriction
    """
    try:
        enum_type = DietaryRestrictionType(restriction_type)
    except ValueError:
        allowed_values = [r.value for r in DietaryRestrictionType]
        raise ValueError(f"Invalid restriction type. Allowed values: {allowed_values}")
    
    repo = MenuItemRepository(db)
    items = repo.get_by_dietary_restriction(enum_type)
    
    return [
        {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "price": item.get_current_price(),
            "category": item.category.name,
            "is_available": item.is_available
        }
        for item in items
        if item.is_available
    ]

def get_menu_item_details(db: Session, item_id: int) -> Optional[Dict[str, Any]]:
    """
    Get details for a specific menu item.
    
    Args:
        db: Database session
        item_id: Menu item ID
        
    Returns:
        Menu item details or None if not found
    """
    repo = MenuItemRepository(db)
    item = repo.get_by_id(item_id)
    
    if not item:
        return None
    
    return {
        "id": item.id,
        "name": item.name,
        "description": item.description,
        "price": item.get_current_price(),
        "regular_price": item.price,
        "category": item.category.name,
        "is_available": item.is_available,
        "special_item": item.special_item,
        "spiciness_level": item.spiciness_level,
        "preparation_time_minutes": item.preparation_time_minutes,
        "dietary_restrictions": [
            {
                "id": dr.id,
                "type": dr.restriction_type.value,
                "description": dr.description
            }
            for dr in item.dietary_restrictions
        ],
        "ingredients": [
            {
                "id": ingredient.id,
                "name": ingredient.name,
                "description": ingredient.description,
                "allergen": ingredient.allergen
            }
            for ingredient in item.ingredients
        ],
        "special_pricing": [
            {
                "id": sp.id,
                "special_price": sp.special_price,
                "description": sp.description,
                "start_date": sp.start_date.isoformat(),
                "end_date": sp.end_date.isoformat(),
                "active": sp.is_active()
            }
            for sp in item.special_prices
            if sp.active
        ]
    }