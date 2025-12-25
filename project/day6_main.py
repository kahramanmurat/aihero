"""
Day 6: Command-line interface for the agent
Brings everything together for interactive CLI usage.
"""
import asyncio
from day6_ingest import index_data
from day6_search_agent import init_agent
from day6_logs import log_interaction_to_file


REPO_OWNER = "DataTalksClub"
REPO_NAME = "faq"


def initialize_index():
    """Initialize and return the search index."""
    print(f"Starting AI FAQ Assistant for {REPO_OWNER}/{REPO_NAME}")
    print("Initializing data ingestion...")
    
    def filter(doc):
        return 'data-engineering' in doc['filename']
    
    index = index_data(REPO_OWNER, REPO_NAME, filter=filter)
    print("Data indexing completed successfully!")
    return index


def initialize_agent(index):
    """Initialize and return the agent."""
    print("Initializing search agent...")
    agent = init_agent(index, REPO_OWNER, REPO_NAME)
    print("Agent initialized successfully!")
    return agent


def main():
    """Main CLI loop."""
    index = initialize_index()
    agent = initialize_agent(index)
    print("\nReady to answer your questions!")
    print("Type 'stop' to exit the program.\n")
    
    while True:
        question = input("Your question: ")
        if question.strip().lower() == 'stop':
            print("Goodbye!")
            break
        
        print("Processing your question...")
        response = asyncio.run(agent.run(user_prompt=question))
        log_interaction_to_file(agent, response.new_messages())
        
        print("\nResponse:\n", response.data)
        print("\n" + "="*50 + "\n")


if __name__ == "__main__":
    main()

