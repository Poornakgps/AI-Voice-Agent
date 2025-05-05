from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from database.schema import DietaryRestrictionType, ReservationStatus

Base = declarative_base()

class MenuCategory(Base):
    """Menu category model."""
    __tablename__ = "menu_categories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    menu_items = relationship("MenuItem", back_populates="category")
    
    def __repr__(self):
        return f"<MenuCategory(id={self.id}, name='{self.name}')>"


class MenuItem(Base):
    """Menu item model."""
    __tablename__ = "menu_items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("menu_categories.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True)
    special_item = Column(Boolean, default=False)
    spiciness_level = Column(Integer, default=0)
    preparation_time_minutes = Column(Integer, default=15)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    category = relationship("MenuCategory", back_populates="menu_items")
    ingredients = relationship("Ingredient", secondary="menu_item_ingredients", back_populates="menu_items")
    dietary_restrictions = relationship("DietaryRestriction", secondary="menu_item_dietary_restrictions", back_populates="menu_items")
    special_prices = relationship("SpecialPricing", back_populates="menu_item")
    
    def __repr__(self):
        return f"<MenuItem(id={self.id}, name='{self.name}', price={self.price})>"
    
    def get_current_price(self):
        """Get the current price, taking into account any active special pricing."""
        now = datetime.now()
        for special in self.special_prices:
            if special.active and special.start_date <= now <= special.end_date:
                return special.special_price
        return self.price
    
    def is_vegetarian(self):
        """Check if the menu item is vegetarian."""
        return any(dr.restriction_type == DietaryRestrictionType.VEGETARIAN for dr in self.dietary_restrictions)
    
    def is_vegan(self):
        """Check if the menu item is vegan."""
        return any(dr.restriction_type == DietaryRestrictionType.VEGAN for dr in self.dietary_restrictions)
    
    def is_gluten_free(self):
        """Check if the menu item is gluten-free."""
        return any(dr.restriction_type == DietaryRestrictionType.GLUTEN_FREE for dr in self.dietary_restrictions)


class Ingredient(Base):
    """Ingredient model."""
    __tablename__ = "ingredients"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    allergen = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    menu_items = relationship("MenuItem", secondary="menu_item_ingredients", back_populates="ingredients")
    
    def __repr__(self):
        return f"<Ingredient(id={self.id}, name='{self.name}', allergen={self.allergen})>"


class MenuItemIngredient(Base):
    """Association table for menu items and ingredients."""
    __tablename__ = "menu_item_ingredients"
    
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), primary_key=True)
    optional = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())


class DietaryRestriction(Base):
    """Dietary restriction model."""
    __tablename__ = "dietary_restrictions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    restriction_type = Column(Enum(DietaryRestrictionType), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    menu_items = relationship("MenuItem", secondary="menu_item_dietary_restrictions", back_populates="dietary_restrictions")
    
    def __repr__(self):
        return f"<DietaryRestriction(id={self.id}, type='{self.restriction_type.value}')>"


class MenuItemDietaryRestriction(Base):
    """Association table for menu items and dietary restrictions."""
    __tablename__ = "menu_item_dietary_restrictions"
    
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), primary_key=True)
    dietary_restriction_id = Column(Integer, ForeignKey("dietary_restrictions.id"), primary_key=True)
    created_at = Column(DateTime, default=func.now())


class SpecialPricing(Base):
    """Special pricing model for menu items."""
    __tablename__ = "special_pricing"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    special_price = Column(Float, nullable=False)
    description = Column(String(255))
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    menu_item = relationship("MenuItem", back_populates="special_prices")
    
    def __repr__(self):
        return f"<SpecialPricing(id={self.id}, menu_item_id={self.menu_item_id}, price={self.special_price})>"
    
    def is_active(self):
        """Check if the special pricing is currently active."""
        now = datetime.now()
        return self.active and self.start_date <= now <= self.end_date


class Reservation(Base):
    """Reservation model."""
    __tablename__ = "reservations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_name = Column(String(100), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    customer_email = Column(String(100))
    party_size = Column(Integer, nullable=False)
    reservation_date = Column(DateTime, nullable=False)
    special_requests = Column(Text)
    status = Column(Enum(ReservationStatus), nullable=False, default=ReservationStatus.PENDING)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    tables = relationship("RestaurantTable", secondary="reservation_tables", back_populates="reservations")
    
    def __repr__(self):
        return f"<Reservation(id={self.id}, name='{self.customer_name}', date='{self.reservation_date}')>"
    
    def confirm(self):
        """Confirm the reservation."""
        self.status = ReservationStatus.CONFIRMED
        self.updated_at = datetime.now()
    
    def cancel(self):
        """Cancel the reservation."""
        self.status = ReservationStatus.CANCELED
        self.updated_at = datetime.now()
    
    def complete(self):
        """Mark the reservation as completed."""
        self.status = ReservationStatus.COMPLETED
        self.updated_at = datetime.now()
    
    def mark_no_show(self):
        """Mark the reservation as a no-show."""
        self.status = ReservationStatus.NO_SHOW
        self.updated_at = datetime.now()


class RestaurantTable(Base):
    """Restaurant table model."""
    __tablename__ = "restaurant_tables"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    table_number = Column(String(10), nullable=False, unique=True)
    capacity = Column(Integer, nullable=False)
    location = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    reservations = relationship("Reservation", secondary="reservation_tables", back_populates="tables")
    
    def __repr__(self):
        return f"<RestaurantTable(id={self.id}, number='{self.table_number}', capacity={self.capacity})>"


class ReservationTable(Base):
    """Association table for reservations and tables."""
    __tablename__ = "reservation_tables"
    
    reservation_id = Column(Integer, ForeignKey("reservations.id"), primary_key=True)
    table_id = Column(Integer, ForeignKey("restaurant_tables.id"), primary_key=True)
    created_at = Column(DateTime, default=func.now())