from sqlalchemy import (
    MetaData, Table, Column, Integer, String, Float, 
    DateTime, Boolean, ForeignKey, Text, Enum, CheckConstraint
)
from sqlalchemy.sql import func
import enum
from datetime import datetime, timedelta

metadata = MetaData()

class DietaryRestrictionType(enum.Enum):
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"
    NUT_FREE = "nut_free"
    HALAL = "halal"
    KOSHER = "kosher"

class ReservationStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELED = "canceled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


menu_categories = Table(
    "menu_categories",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(50), nullable=False, unique=True),
    Column("description", Text),
    Column("display_order", Integer, default=0),
    Column("created_at", DateTime, default=func.now()),
    Column("updated_at", DateTime, default=func.now(), onupdate=func.now()),
)

menu_items = Table(
    "menu_items",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("category_id", Integer, ForeignKey("menu_categories.id"), nullable=False),
    Column("name", String(100), nullable=False),
    Column("description", Text),
    Column("price", Float, nullable=False),
    Column("is_available", Boolean, default=True),
    Column("special_item", Boolean, default=False),
    Column("spiciness_level", Integer, default=0),
    Column("preparation_time_minutes", Integer, default=15),
    Column("created_at", DateTime, default=func.now()),
    Column("updated_at", DateTime, default=func.now(), onupdate=func.now()),
    CheckConstraint("price >= 0", name="ck_menu_items_price_positive"),
    CheckConstraint("spiciness_level BETWEEN 0 AND 5", name="ck_spiciness_level_range"),
)

ingredients = Table(
    "ingredients",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(100), nullable=False, unique=True),
    Column("description", Text),
    Column("allergen", Boolean, default=False),
    Column("created_at", DateTime, default=func.now()),
    Column("updated_at", DateTime, default=func.now(), onupdate=func.now()),
)

menu_item_ingredients = Table(
    "menu_item_ingredients",
    metadata,
    Column("menu_item_id", Integer, ForeignKey("menu_items.id"), primary_key=True),
    Column("ingredient_id", Integer, ForeignKey("ingredients.id"), primary_key=True),
    Column("optional", Boolean, default=False),
    Column("created_at", DateTime, default=func.now()),
)

dietary_restrictions = Table(
    "dietary_restrictions",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "restriction_type", 
        Enum(DietaryRestrictionType), 
        nullable=False, 
        unique=True
    ),
    Column("description", Text),
    Column("created_at", DateTime, default=func.now()),
    Column("updated_at", DateTime, default=func.now(), onupdate=func.now()),
)

menu_item_dietary_restrictions = Table(
    "menu_item_dietary_restrictions",
    metadata,
    Column("menu_item_id", Integer, ForeignKey("menu_items.id"), primary_key=True),
    Column("dietary_restriction_id", Integer, ForeignKey("dietary_restrictions.id"), primary_key=True),
    Column("created_at", DateTime, default=func.now()),
)

special_pricing = Table(
    "special_pricing",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("menu_item_id", Integer, ForeignKey("menu_items.id"), nullable=False),
    Column("special_price", Float, nullable=False),
    Column("description", String(255)),
    Column("start_date", DateTime, nullable=False),
    Column("end_date", DateTime, nullable=False),
    Column("active", Boolean, default=True),
    Column("created_at", DateTime, default=func.now()),
    Column("updated_at", DateTime, default=func.now(), onupdate=func.now()),
    CheckConstraint("special_price >= 0", name="ck_special_pricing_price_positive"),
    CheckConstraint("end_date > start_date", name="ck_special_pricing_date_range"),
)

reservations = Table(
    "reservations",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("customer_name", String(100), nullable=False),
    Column("customer_phone", String(20), nullable=False),
    Column("customer_email", String(100)),
    Column("party_size", Integer, nullable=False),
    Column("reservation_date", DateTime, nullable=False),
    Column("special_requests", Text),
    Column("status", Enum(ReservationStatus), nullable=False, default=ReservationStatus.PENDING),
    Column("created_at", DateTime, default=func.now()),
    Column("updated_at", DateTime, default=func.now(), onupdate=func.now()),
    CheckConstraint("party_size > 0", name="ck_reservation_party_size_positive"),
    CheckConstraint("reservation_date > created_at", name="ck_reservation_future_date"),
)

restaurant_tables = Table(
    "restaurant_tables",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("table_number", String(10), nullable=False, unique=True),
    Column("capacity", Integer, nullable=False),
    Column("location", String(50)),  # e.g., "Window", "Bar", "Patio"
    Column("is_active", Boolean, default=True),
    Column("created_at", DateTime, default=func.now()),
    Column("updated_at", DateTime, default=func.now(), onupdate=func.now()),
    CheckConstraint("capacity > 0", name="ck_table_capacity_positive"),
)

reservation_tables = Table(
    "reservation_tables",
    metadata,
    Column("reservation_id", Integer, ForeignKey("reservations.id"), primary_key=True),
    Column("table_id", Integer, ForeignKey("restaurant_tables.id"), primary_key=True),
    Column("created_at", DateTime, default=func.now()),
)

def create_tables(engine):
    """Create all tables in the database."""
    metadata.create_all(engine)

def drop_tables(engine):
    """Drop all tables from the database."""
    metadata.drop_all(engine)