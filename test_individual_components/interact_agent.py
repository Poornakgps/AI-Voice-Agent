import sys
import os
import logging
from pathlib import Path
from datetime import datetime

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
    
    # Create a log file with timestamp in filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"conversation_{timestamp}.txt"
    log_file = open(log_filename, "w", encoding="utf-8")
    
    # Write header to log file
    log_file.write("=== Voice AI Restaurant Agent Conversation Log ===\n")
    log_file.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    print(f"\nInitializing the database and agent...")
    print(f"Conversation will be logged to: {log_filename}")
    init_db()
    
    try:
        with db_session() as session:
            agent = RestaurantAgent(session)
            
            print("\nAgent is ready! You can start chatting now.\n")
            
            while True:
                try:
                    user_input = input("\nYou: ").strip()
                    
                    # Log user input
                    log_file.write(f"You: {user_input}\n")
                    
                    if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                        print("\nThank you for chatting with me! Goodbye!")
                        log_file.write("\nPriya: Thank you for chatting with me! Goodbye!\n")
                        break
                    
                    if user_input.lower() in ["help", "?"]:
                        print_help()
                        log_file.write("(Help information displayed)\n")
                        continue
                    
                    if not user_input:
                        continue
                    
                    print("\nProcessing your request...")
                    response = agent.process_message(user_input)
                    
                    print(f"\nPriya: {response}")
                    
                    # Log agent response
                    log_file.write(f"Priya: {response}\n\n")
                    
                except KeyboardInterrupt:
                    print("\n\nSession terminated by user. Goodbye!")
                    log_file.write("\n\nSession terminated by user. Goodbye!\n")
                    break
                except Exception as e:
                    error_message = f"\nError: {str(e)}"
                    print(error_message)
                    log_file.write(f"{error_message}\n")
                    print("Let's continue our conversation.")
                    log_file.write("Let's continue our conversation.\n")
    finally:
        # Write footer and close log file
        log_file.write(f"\nEnded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.close()
        print(f"\nConversation log saved to: {log_filename}")

if __name__ == "__main__":
    interactive_session()