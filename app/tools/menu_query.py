from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from database.models import MenuCategory, MenuItem, DietaryRestriction, DietaryRestrictionType
from database.repository import MenuCategoryRepository, MenuItemRepository

def get_menu_categories(db: Session) -> List[Dict[str, Any]]:
    """Get all menu categories."""
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
    """Get menu items by category."""
    repo = MenuItemRepository(db)
    items = repo.get_by_category(category_id)
    
    return [
        {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "price": item.get_current_price(),
            "dietary_restrictions": [dr.restriction_type.value for dr in item.dietary_restrictions]
        }
        for item in items
        if item.is_available
    ]

def search_menu_items(db: Session, query: str) -> List[Dict[str, Any]]:
    """Search for menu items."""
    repo = MenuItemRepository(db)
    items = repo.search_by_name(query)
    
    return [
        {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "price": item.get_current_price(),
            "category": item.category.name
        }
        for item in items
        if item.is_available
    ]

def get_menu_items_by_dietary_restriction(
    db: Session, restriction_type: str
) -> List[Dict[str, Any]]:
    """Get menu items by dietary restriction."""
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
            "category": item.category.name
        }
        for item in items
        if item.is_available
    ]

def get_menu_item_details(db: Session, item_id: int) -> Optional[Dict[str, Any]]:
    """Get details for a specific menu item."""
    repo = MenuItemRepository(db)
    item = repo.get_by_id(item_id)
    
    if not item:
        return None
    
    return {
        "id": item.id,
        "name": item.name,
        "description": item.description,
        "price": item.get_current_price(),
        "category": item.category.name,
        "dietary_restrictions": [dr.restriction_type.value for dr in item.dietary_restrictions],
        "ingredients": [ingredient.name for ingredient in item.ingredients],
        "special_pricing": [
            {
                "special_price": sp.special_price,
                "description": sp.description,
                "end_date": sp.end_date.isoformat()
            }
            for sp in item.special_prices
            if sp.is_active()
        ]
    }