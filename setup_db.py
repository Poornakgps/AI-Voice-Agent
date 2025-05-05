from database import init_db, db_session
from database.models import MenuCategory

print('Initializing database...')
init_db()

with db_session() as session:
    categories = session.query(MenuCategory).all()
    print(f"Found {len(categories)} menu categories:")
    for category in categories:
        print(f"- {category.name}")

print("Database initialization complete!")
