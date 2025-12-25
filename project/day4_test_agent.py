"""
Test script: Create an agent for GitHub repository documentation.
This combines Day 1 (ingestion), Day 2 (chunking), and Day 4 (agents).
"""
import asyncio
from day1_ingest import read_repo_data
from day2_chunking import chunk_documents_sliding_window
from day4_agent import SimpleSearchIndex, create_agent_with_pydantic_ai
import os


async def test_agent_with_repo():
    """Test agent with real GitHub repository data."""
    print("=" * 60)
    print("Day 4: Testing Agent with GitHub Repository")
    print("=" * 60)
    print()
    
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  OPENAI_API_KEY not set!")
        print("   Set it with: export OPENAI_API_KEY='your-api-key'")
        return
    
    print("✅ OPENAI_API_KEY found")
    print()
    
    # Step 1: Download repository (Day 1)
    print("📥 Step 1: Downloading repository...")
    try:
        docs = read_repo_data('DataTalksClub', 'faq')
        print(f"✅ Downloaded {len(docs)} documents")
    except Exception as e:
        print(f"❌ Error downloading: {e}")
        return
    
    if not docs:
        print("❌ No documents to process")
        return
    
    # Step 2: Prepare documents for search
    print()
    print("📦 Step 2: Preparing documents for search...")
    search_docs = []
    for doc in docs:
        # Extract content and metadata
        content = doc.get('content', '')
        title = doc.get('title', doc.get('question', doc.get('filename', 'Untitled')))
        
        if content:
            search_docs.append({
                'title': title,
                'content': content,
                'metadata': {k: v for k, v in doc.items() if k not in ['content', 'title']}
            })
    
    print(f"✅ Prepared {len(search_docs)} documents for search")
    print()
    
    # Step 3: Create search index
    print("🔍 Step 3: Creating search index...")
    search_index = SimpleSearchIndex(search_docs)
    print("✅ Search index created")
    print()
    
    # Step 4: Create agent
    print("🤖 Step 4: Creating agent with search tool...")
    try:
        agent = create_agent_with_pydantic_ai(search_index)
        print("✅ Agent created")
        print()
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        return
    
    # Step 5: Test the agent
    print("💬 Step 5: Testing the agent...")
    print("-" * 60)
    
    test_questions = [
        "I just discovered the course, can I join now?",
        "How do I submit homework?",
        "Where can I get help?",
    ]
    
    for question in test_questions:
        print(f"\n❓ Question: {question}")
        try:
            result = await agent.run(user_prompt=question)
            print(f"💬 Answer: {result.data}")
        except Exception as e:
            print(f"❌ Error: {e}")
        print("-" * 60)
    
    print()
    print("=" * 60)
    print("✅ Agent testing complete!")
    print("=" * 60)
    print()
    print("💡 The agent can now:")
    print("   - Search through repository documentation")
    print("   - Answer questions based on actual content")
    print("   - Use tools to retrieve information")
    print("   - Provide context-aware responses")


if __name__ == '__main__':
    asyncio.run(test_agent_with_repo())

