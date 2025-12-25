"""
Example programmatic usage of the AI Data Explorer.
"""
import asyncio
from data_loader import DataLoader
from schema_indexer import SchemaIndexer
from data_agent import init_agent


async def main():
    """Example usage of the data explorer."""
    
    # Initialize components
    print("Initializing data loader...")
    loader = DataLoader()
    
    # Load a CSV file (example - you would use your own file)
    # loader.load_csv("sales.csv")
    
    # Or connect to a database
    # loader.connect_database("sqlite:///data.db")
    # loader.load_database_table("mydb", "sales")
    
    print("Indexing schemas...")
    indexer = SchemaIndexer(loader)
    indexer.index_tables()
    
    print("Initializing agent...")
    agent = init_agent(loader, indexer)
    
    # Example questions
    questions = [
        "What tables are available?",
        "What's the average sales per month?",
        "Which product performs best?",
    ]
    
    for question in questions:
        print(f"\n🤔 Question: {question}")
        result = await agent.run(question)
        print(f"💬 Answer: {result.data}")
        print("-" * 50)


if __name__ == "__main__":
    asyncio.run(main())

