"""
Test script to verify the system works with the provided examples.
"""
from agents.tourism_agent import TourismAgent


def test_examples():
    """Test the three provided examples."""
    agent = TourismAgent()
    
    examples = [
        "I'm going to go to Bangalore, let's plan my trip.",
        "I'm going to go to Bangalore, what is the temperature there",
        "I'm going to go to Bangalore, what is the temperature there? And what are the places I can visit?"
    ]
    
    print("=" * 60)
    print("Testing Multi-Agent Tourism System")
    print("=" * 60)
    print()
    
    for i, example in enumerate(examples, 1):
        print(f"Example {i}:")
        print(f"Input: {example}")
        print("\nProcessing...")
        response = agent.process_request(example)
        print(f"Output:\n{response}")
        print("\n" + "-" * 60 + "\n")


if __name__ == "__main__":
    test_examples()

