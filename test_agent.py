from database import init_db, db_session
from app.core.agent import RestaurantAgent

# Ensure database is initialized first
print('Making sure database is initialized...')
init_db()

print('Testing agent with simple queries...')
with db_session() as session:
    # Create agent
    agent = RestaurantAgent(session)
    
    # Test a simple query
    print('\nQuery: Hello, what\'s on your menu?')
    response = agent.process_message("Hello, what's on your menu?")
    print(f"Agent response: {response}")
    
    # Test another query
    print('\nQuery: Do you have vegetarian options?')
    response = agent.process_message("Do you have vegetarian options?")
    print(f"Agent response: {response}")

print('\nAgent testing complete!')
