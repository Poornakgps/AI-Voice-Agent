import logging
import sys

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

from database import init_db, db_session
from app.core.agent import RestaurantAgent

# Ensure database is initialized first
print('Making sure database is initialized...')
init_db()

print('Testing agent with detailed logging...')
with db_session() as session:
    # Create agent
    agent = RestaurantAgent(session)
    
    # Test a query that uses tools
    print('\nQuery: What vegetarian dishes do you have?')
    response = agent.process_message("What vegetarian dishes do you have?")
    print(f"\nFinal agent response: {response}")
