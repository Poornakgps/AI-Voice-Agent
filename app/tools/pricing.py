from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from database.models import MenuItem, SpecialPricing
from database.repository import MenuItemRepository, SpecialPricingRepository

def get_item_price(db: Session, item_id: int) -> Optional[Dict[str, Any]]:
    """
    Get price information for a menu item.
    
    Args:
        db: Database session
        item_id: Menu item ID
        
    Returns:
        Price information or None if item not found
    """
    repo = MenuItemRepository(db)
    item = repo.get_by_id(item_id)
    
    if not item:
        return None
    
    current_price = item.get_current_price()
    
    special_repo = SpecialPricingRepository(db)
    special_pricing = special_repo.get_active_for_menu_item(item_id)
    
    price_info = {
        "id": item.id,
        "name": item.name,
        "regular_price": item.price,
        "current_price": current_price,
        "has_special_pricing": special_pricing is not None
    }
    
    if special_pricing:
        price_info["special_pricing"] = {
            "price": special_pricing.special_price,
            "description": special_pricing.description,
            "start_date": special_pricing.start_date.isoformat(),
            "end_date": special_pricing.end_date.isoformat()
        }
        price_info["savings"] = item.price - special_pricing.special_price
    
    return price_info

def get_special_pricing(db: Session) -> List[Dict[str, Any]]:
    """
    Get all active special pricing.
    
    Args:
        db: Database session
        
    Returns:
        List of active special pricing
    """
    repo = SpecialPricingRepository(db)
    special_prices = repo.get_active_specials()
    
    result = []
    for sp in special_prices:
        item = sp.menu_item
        result.append({
            "item_id": item.id,
            "item_name": item.name,
            "category": item.category.name,
            "regular_price": item.price,
            "special_price": sp.special_price,
            "description": sp.description,
            "start_date": sp.start_date.isoformat(),
            "end_date": sp.end_date.isoformat(),
            "savings": item.price - sp.special_price,
            "savings_percentage": round(((item.price - sp.special_price) / item.price) * 100, 2)
        })
    
    return result

def calculate_order_total(db: Session, items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate the total for an order.
    
    Args:
        db: Database session
        items: List of items with keys 'id', 'quantity'
        
    Returns:
        Order total information
    """
    repo = MenuItemRepository(db)
    
    order_items = []
    subtotal = 0.0
    
    for item_data in items:
        item_id = item_data["id"]
        quantity = item_data.get("quantity", 1)
        
        item = repo.get_by_id(item_id)
        if not item:
            continue
        
        current_price = item.get_current_price()
        item_total = current_price * quantity
        
        order_items.append({
            "id": item.id,
            "name": item.name,
            "price": current_price,
            "quantity": quantity,
            "total": item_total
        })
        
        subtotal += item_total
    
    tax_rate = 0.085
    tax = subtotal * tax_rate
    
    total = subtotal + tax
    
    return {
        "items": order_items,
        "subtotal": subtotal,
        "tax_rate": tax_rate,
        "tax": tax,
        "total": total
    }