"""
Main entry point for the Multi-Agent Tourism System.
"""
from agents.tourism_agent import TourismAgent


def main():
    """Main function to run the tourism system."""
    print("=" * 60)
    print("Multi-Agent Tourism System")
    print("=" * 60)
    print("\nEnter a place you want to visit. Type 'quit' or 'exit' to stop.\n")
    
    agent = TourismAgent()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nThank you for using the Tourism System. Goodbye!")
                break
            
            if not user_input:
                print("Please enter a valid query.")
                continue
            
            # Process the request
            response = agent.process_request(user_input)
            print(f"\nAgent: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\nThank you for using the Tourism System. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()

