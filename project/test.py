"""
Test script for the AI Data Explorer project.
Run this to verify all components work correctly.
"""
import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from data_loader import DataLoader
from schema_indexer import SchemaIndexer
from data_agent import init_agent


async def test_data_loader():
    """Test the DataLoader component."""
    print("=" * 60)
    print("Testing DataLoader...")
    print("=" * 60)
    
    loader = DataLoader()
    
    # Test CSV loading
    csv_path = Path(__file__).parent / "test_data.csv"
    if csv_path.exists():
        table_name = loader.load_csv(str(csv_path))
        print(f"✅ Loaded CSV: {table_name}")
        
        # Test getting table info
        info = loader.get_table_info(table_name)
        print(f"✅ Table info retrieved:")
        print(f"   - Columns: {info['columns']}")
        print(f"   - Rows: {info['row_count']}")
        print(f"   - Sample row: {info['sample_rows'][0]}")
    else:
        print(f"❌ Test CSV not found: {csv_path}")
        return False
    
    return True


def test_schema_indexer():
    """Test the SchemaIndexer component."""
    print("\n" + "=" * 60)
    print("Testing SchemaIndexer...")
    print("=" * 60)
    
    loader = DataLoader()
    csv_path = Path(__file__).parent / "test_data.csv"
    
    if not csv_path.exists():
        print("❌ Test CSV not found")
        return False
    
    loader.load_csv(str(csv_path))
    indexer = SchemaIndexer(loader)
    
    # Index tables
    indexer.index_tables()
    print("✅ Tables indexed")
    
    # Test search
    results = indexer.search_tables("sales data", num_results=3)
    print(f"✅ Search results: {len(results)} tables found")
    if results:
        print(f"   - Found table: {results[0]['table_name']}")
    
    return True


async def test_agent():
    """Test the AI Agent."""
    print("\n" + "=" * 60)
    print("Testing Data Agent...")
    print("=" * 60)
    
    loader = DataLoader()
    csv_path = Path(__file__).parent / "test_data.csv"
    
    if not csv_path.exists():
        print("❌ Test CSV not found")
        return False
    
    # Load data
    loader.load_csv(str(csv_path))
    
    # Index schemas
    indexer = SchemaIndexer(loader)
    indexer.index_tables()
    
    # Create agent
    agent = init_agent(loader, indexer)
    print("✅ Agent initialized")
    
    # Test questions
    test_questions = [
        "What tables are available?",
        "What columns are in the test_data table?",
    ]
    
    for question in test_questions:
        print(f"\n🤔 Question: {question}")
        try:
            result = await agent.run(question)
            print(f"💬 Answer: {result.data}")
            print("✅ Question answered successfully")
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    return True


async def run_all_tests():
    """Run all tests."""
    print("\n🧪 Starting AI Data Explorer Tests\n")
    
    results = []
    
    # Test 1: DataLoader
    try:
        results.append(("DataLoader", await test_data_loader()))
    except Exception as e:
        print(f"❌ DataLoader test failed: {e}")
        results.append(("DataLoader", False))
    
    # Test 2: SchemaIndexer
    try:
        results.append(("SchemaIndexer", test_schema_indexer()))
    except Exception as e:
        print(f"❌ SchemaIndexer test failed: {e}")
        results.append(("SchemaIndexer", False))
    
    # Test 3: Agent (requires OpenAI API key)
    try:
        import os
        if not os.getenv("OPENAI_API_KEY"):
            print("\n⚠️  Skipping Agent test - OPENAI_API_KEY not set")
            print("   Set it with: export OPENAI_API_KEY='your-key'")
            results.append(("Agent", None))
        else:
            results.append(("Agent", await test_agent()))
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        results.append(("Agent", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, result in results:
        if result is None:
            status = "⏭️  SKIPPED"
        elif result:
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"
        print(f"{name}: {status}")
    
    all_passed = all(r for r in results if r is not None)
    if all_passed:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed or were skipped")


if __name__ == "__main__":
    asyncio.run(run_all_tests())

