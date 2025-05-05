from typing import List, Optional, Dict, Any, Type, TypeVar, Generic, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, select
from database.models import (
    Base, MenuCategory, MenuItem, Ingredient, DietaryRestriction,
    SpecialPricing, Reservation, RestaurantTable, DietaryRestrictionType,
    ReservationStatus
)

T = TypeVar('T', bound=Base) # type: ignore

class Repository(Generic[T]):
    """Base repository class for database operations."""
    
    def __init__(self, session: Session, model: Type[T]):
        """
        Initialize the repository.
        
        Args:
            session: SQLAlchemy session
            model: SQLAlchemy model class
        """
        self.session = session
        self.model = model
    
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """
        Get entity by ID.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Entity object or None if not found
        """
        return self.session.query(self.model).filter(self.model.id == entity_id).first()
    
    def get_all(self) -> List[T]:
        """
        Get all entities.
        
        Returns:
            List of all entities
        """
        return self.session.query(self.model).all()
    
    def create(self, **kwargs) -> T:
        """
        Create a new entity.
        
        Args:
            **kwargs: Entity attributes
            
        Returns:
            Created entity
        """
        entity = self.model(**kwargs)
        self.session.add(entity)
        self.session.commit()
        return entity
    
    def update(self, entity_id: int, **kwargs) -> Optional[T]:
        """
        Update an entity.
        
        Args:
            entity_id: Entity ID
            **kwargs: Entity attributes to update
            
        Returns:
            Updated entity or None if not found
        """
        entity = self.get_by_id(entity_id)
        if entity:
            for key, value in kwargs.items():
                setattr(entity, key, value)
            self.session.commit()
        return entity
    
    def delete(self, entity_id: int) -> bool:
        """
        Delete an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            True if entity was deleted, False otherwise
        """
        entity = self.get_by_id(entity_id)
        if entity:
            self.session.delete(entity)
            self.session.commit()
            return True
        return False


class MenuCategoryRepository(Repository[MenuCategory]):
    """Repository for menu categories."""
    
    def __init__(self, session: Session):
        super().__init__(session, MenuCategory)
    
    def get_by_name(self, name: str) -> Optional[MenuCategory]:
        """
        Get category by name.
        
        Args:
            name: Category name
            
        Returns:
            Category object or None if not found
        """
        return self.session.query(self.model).filter(self.model.name == name).first()
    
    def get_ordered_categories(self) -> List[MenuCategory]:
        """
        Get categories ordered by display_order.
        
        Returns:
            Ordered list of categories
        """
        return self.session.query(self.model).order_by(self.model.display_order).all()


class MenuItemRepository(Repository[MenuItem]):
    """Repository for menu items."""
    
    def __init__(self, session: Session):
        super().__init__(session, MenuItem)
    
    def get_by_category(self, category_id: int) -> List[MenuItem]:
        """
        Get menu items by category.
        
        Args:
            category_id: Category ID
            
        Returns:
            List of menu items in the category
        """
        return self.session.query(self.model).filter(self.model.category_id == category_id).all()
    
    def get_available_items(self) -> List[MenuItem]:
        """
        Get available menu items.
        
        Returns:
            List of available menu items
        """
        return self.session.query(self.model).filter(self.model.is_available == True).all()
    
    def get_special_items(self) -> List[MenuItem]:
        """
        Get special menu items.
        
        Returns:
            List of special menu items
        """
        return self.session.query(self.model).filter(self.model.special_item == True).all()
    
    def search_by_name(self, search_term: str) -> List[MenuItem]:
        """
        Search menu items by name.
        
        Args:
            search_term: Search term
            
        Returns:
            List of matching menu items
        """
        search_pattern = f"%{search_term}%"
        return self.session.query(self.model).filter(self.model.name.ilike(search_pattern)).all()
    
    def get_by_dietary_restriction(self, restriction_type: DietaryRestrictionType) -> List[MenuItem]:
        """
        Get menu items by dietary restriction.
        
        Args:
            restriction_type: Dietary restriction type
            
        Returns:
            List of menu items with the given dietary restriction
        """
        return (
            self.session.query(self.model)
            .join(MenuItem.dietary_restrictions)
            .filter(DietaryRestriction.restriction_type == restriction_type)
            .all()
        )
    
    def get_by_ingredient(self, ingredient_id: int) -> List[MenuItem]:
        """
        Get menu items containing a specific ingredient.
        
        Args:
            ingredient_id: Ingredient ID
            
        Returns:
            List of menu items containing the ingredient
        """
        return (
            self.session.query(self.model)
            .join(MenuItem.ingredients)
            .filter(Ingredient.id == ingredient_id)
            .all()
        )
    
    def get_without_allergens(self) -> List[MenuItem]:
        """
        Get menu items without any allergenic ingredients.
        
        Returns:
            List of menu items without allergens
        """
        items_with_allergens = (
            self.session.query(MenuItem.id)
            .join(MenuItem.ingredients)
            .filter(Ingredient.allergen == True)
            .subquery()
        )
        
        return (
            self.session.query(self.model)
            .filter(~self.model.id.in_(items_with_allergens))
            .all()
        )


class SpecialPricingRepository(Repository[SpecialPricing]):
    """Repository for special pricing."""
    
    def __init__(self, session: Session):
        super().__init__(session, SpecialPricing)
    
    def get_active_specials(self) -> List[SpecialPricing]:
        """
        Get currently active special pricing.
        
        Returns:
            List of active special pricing
        """
        now = datetime.now()
        return (
            self.session.query(self.model)
            .filter(
                self.model.active == True,
                self.model.start_date <= now,
                self.model.end_date >= now
            )
            .all()
        )
    
    def get_for_menu_item(self, menu_item_id: int) -> List[SpecialPricing]:
        """
        Get special pricing for a specific menu item.
        
        Args:
            menu_item_id: Menu item ID
            
        Returns:
            List of special pricing for the menu item
        """
        return (
            self.session.query(self.model)
            .filter(self.model.menu_item_id == menu_item_id)
            .all()
        )
    
    def get_active_for_menu_item(self, menu_item_id: int) -> Optional[SpecialPricing]:
        """
        Get active special pricing for a specific menu item.
        
        Args:
            menu_item_id: Menu item ID
            
        Returns:
            Active special pricing for the menu item or None
        """
        now = datetime.now()
        return (
            self.session.query(self.model)
            .filter(
                self.model.menu_item_id == menu_item_id,
                self.model.active == True,
                self.model.start_date <= now,
                self.model.end_date >= now
            )
            .first()
        )


class ReservationRepository(Repository[Reservation]):
    """Repository for reservations."""
    
    def __init__(self, session: Session):
        super().__init__(session, Reservation)
    
    def get_by_phone(self, phone: str) -> List[Reservation]:
        """
        Get reservations by phone number.
        
        Args:
            phone: Phone number
            
        Returns:
            List of reservations with the given phone number
        """
        return (
            self.session.query(self.model)
            .filter(self.model.customer_phone == phone)
            .all()
        )
    
    def get_by_email(self, email: str) -> List[Reservation]:
        """
        Get reservations by email.
        
        Args:
            email: Email address
            
        Returns:
            List of reservations with the given email
        """
        return (
            self.session.query(self.model)
            .filter(self.model.customer_email == email)
            .all()
        )
    
    def get_by_date(self, date: datetime) -> List[Reservation]:
        """
        Get reservations for a specific date.
        
        Args:
            date: Reservation date
            
        Returns:
            List of reservations for the date
        """
        start_date = datetime(date.year, date.month, date.day, 0, 0, 0)
        end_date = datetime(date.year, date.month, date.day, 23, 59, 59)
        
        return (
            self.session.query(self.model)
            .filter(
                self.model.reservation_date >= start_date,
                self.model.reservation_date <= end_date
            )
            .all()
        )
    
    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Reservation]:
        """
        Get reservations within a date range.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List of reservations within the date range
        """
        return (
            self.session.query(self.model)
            .filter(
                self.model.reservation_date >= start_date,
                self.model.reservation_date <= end_date
            )
            .all()
        )
    
    def get_by_status(self, status: ReservationStatus) -> List[Reservation]:
        """
        Get reservations by status.
        
        Args:
            status: Reservation status
            
        Returns:
            List of reservations with the given status
        """
        return (
            self.session.query(self.model)
            .filter(self.model.status == status)
            .all()
        )
    
    def get_upcoming(self) -> List[Reservation]:
        """
        Get upcoming reservations.
        
        Returns:
            List of upcoming reservations
        """
        now = datetime.now()
        return (
            self.session.query(self.model)
            .filter(
                self.model.reservation_date >= now,
                self.model.status == ReservationStatus.CONFIRMED
            )
            .order_by(self.model.reservation_date)
            .all()
        )
    
    def check_availability(self, date: datetime, party_size: int) -> bool:
        """
        Check if there is availability for a reservation.
        
        Args:
            date: Reservation date
            party_size: Party size
            
        Returns:
            True if there is availability, False otherwise
        """
        window_start = date - timedelta(hours=1)
        window_end = date + timedelta(hours=1)
        
        reservations_in_window = (
            self.session.query(func.count(self.model.id))
            .filter(
                self.model.reservation_date >= window_start,
                self.model.reservation_date <= window_end,
                self.model.status.in_([ReservationStatus.CONFIRMED, ReservationStatus.PENDING])
            )
            .scalar()
        )
        
        return reservations_in_window < 10


class RestaurantTableRepository(Repository[RestaurantTable]):
    """Repository for restaurant tables."""
    
    def __init__(self, session: Session):
        super().__init__(session, RestaurantTable)
    
    def get_available_tables(self, date: datetime, party_size: int) -> List[RestaurantTable]:
        """
        Get available tables for a specific date and party size.
        
        Args:
            date: Reservation date
            party_size: Party size
            
        Returns:
            List of available tables
        """
        suitable_tables = (
            self.session.query(self.model)
            .filter(
                self.model.is_active == True,
                self.model.capacity >= party_size
            )
            .all()
        )

        window_start = date - timedelta(hours=1)
        window_end = date + timedelta(hours=1)

        reserved_table_ids_query = (
            self.session.query(RestaurantTable.id)
            .join(RestaurantTable.reservations)
            .filter(
                Reservation.reservation_date >= window_start,
                Reservation.reservation_date <= window_end,
                Reservation.status.in_([ReservationStatus.CONFIRMED, ReservationStatus.PENDING])
            )
        )
        
        reserved_table_ids = [row[0] for row in reserved_table_ids_query.all()]
        
        available_tables = [
            table for table in suitable_tables
            if table.id not in reserved_table_ids
        ]
        
        return available_tables
    
    def get_by_location(self, location: str) -> List[RestaurantTable]:
        """
        Get tables by location.
        
        Args:
            location: Table location
            
        Returns:
            List of tables in the given location
        """
        return (
            self.session.query(self.model)
            .filter(self.model.location == location)
            .all()
        )