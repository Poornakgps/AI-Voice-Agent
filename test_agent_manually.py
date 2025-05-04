# test_agent_manually.py
import asyncio
from database import init_db, db_session
from app.core.agent import RestaurantAgent

async def test_agent():
    # Initialize database
    init_db()
    
    with db_session() as session:
        # Create agent
        agent = RestaurantAgent(session)
        
        # Test queries
        queries = [
            "What's on your menu?",
            "Do you have any vegetarian options?",
            "What are your hours?",
            "Can I make a reservation for 4 people tomorrow at 7pm?",
        ]
        
        for query in queries:
            print(f"\n\n--- Query: {query} ---")
            response = agent.process_message(query)
            print(f"Response: {response}")

if __name__ == "__main__":
    asyncio.run(test_agent())