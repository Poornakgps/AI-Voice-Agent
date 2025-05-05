from database import init_db, db_session
from database.models import MenuCategory

# Initialize the database with mock data
print('Initializing database...')
init_db()

# Verify the database was populated
with db_session() as session:
    categories = session.query(MenuCategory).all()
    print(f"Found {len(categories)} menu categories:")
    for category in categories:
        print(f"- {category.name}")

print("Database initialization complete!")
