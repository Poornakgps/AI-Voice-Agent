import sys
import os
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from database import init_db, db_session
from app.core.agent import RestaurantAgent

def print_header():
    """Print welcome header."""
    print("\n" + "=" * 70)
    print("                  Voice AI Restaurant Agent - Interactive Mode")
    print("=" * 70)
    print("\nWelcome to Taste of India! I'm Priya, your virtual assistant.")
    print("You can chat with me about our menu, make reservations, or ask general questions.")
    print("Type 'exit', 'quit', or press Ctrl+C to end the conversation.\n")

def print_help():
    """Print help information."""
    print("\nSample questions you can ask:")
    print("  - What's on your menu?")
    print("  - Do you have vegetarian options?")
    print("  - What are your specials today?")
    print("  - Can I make a reservation for 4 people tomorrow at 7pm?")
    print("  - What are your opening hours?")
    print("  - Do you have parking?")
    print("  - Where are you located?")

def interactive_session():
    """Run an interactive session with the agent."""
    print_header()
    print_help()
    
    print("\nInitializing the database and agent...")
    init_db()
    
    with db_session() as session:
        agent = RestaurantAgent(session)
        
        print("\nAgent is ready! You can start chatting now.\n")
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                    print("\nThank you for chatting with me! Goodbye!")
                    break
                
                if user_input.lower() in ["help", "?"]:
                    print_help()
                    continue
                
                if not user_input:
                    continue
                
                print("\nProcessing your request...")
                response = agent.process_message(user_input)
                
                print(f"\nPriya: {response}")
                
            except KeyboardInterrupt:
                print("\n\nSession terminated by user. Goodbye!")
                break
            except Exception as e:
                print(f"\nError: {str(e)}")
                print("Let's continue our conversation.")

if __name__ == "__main__":
    interactive_session()