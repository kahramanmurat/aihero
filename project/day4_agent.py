"""
Day 4: Agents and Tools
Create AI agents that can use tools (functions) to answer questions.
"""
import json
import os
from typing import List, Any, Dict
from openai import OpenAI
from pydantic_ai import Agent
import asyncio


# Example: Simple text search function for FAQ/documentation
class SimpleSearchIndex:
    """Simple in-memory search index for demonstration."""
    
    def __init__(self, documents: List[Dict[str, Any]]):
        """
        Initialize search index with documents.
        
        Args:
            documents: List of documents with 'content' and optionally 'title', 'metadata'
        """
        self.documents = documents
    
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Simple text search - finds documents containing query terms.
        
        Args:
            query: Search query
            num_results: Maximum number of results
        
        Returns:
            List of matching documents
        """
        query_lower = query.lower()
        results = []
        
        for doc in self.documents:
            content = doc.get('content', '').lower()
            title = doc.get('title', '').lower()
            
            # Simple keyword matching
            if query_lower in content or query_lower in title:
                results.append(doc)
                if len(results) >= num_results:
                    break
        
        return results


def text_search(query: str, search_index: SimpleSearchIndex) -> List[Dict[str, Any]]:
    """
    Perform a text-based search on the search index.

    Args:
        query (str): The search query string.

    Returns:
        List[Dict[str, Any]]: A list of up to 5 search results returned by the search index.
    """
    return search_index.search(query, num_results=5)


# Method 1: Using OpenAI Function Calling (without libraries)
def create_agent_with_openai(search_index: SimpleSearchIndex):
    """
    Create an agent using OpenAI function calling directly.
    This demonstrates the manual approach before using Pydantic AI.
    """
    openai_client = OpenAI()
    
    # Define the tool/function
    text_search_tool = {
        "type": "function",
        "name": "text_search",
        "description": "Search the FAQ/documentation database",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query text to look up in the documentation."
                }
            },
            "required": ["query"],
            "additionalProperties": False
        }
    }
    
    def ask_question(question: str) -> str:
        """Ask a question using OpenAI function calling."""
        system_prompt = """
You are a helpful assistant for a course/documentation. 

Use the search tool to find relevant information from the documentation before answering questions.

If you can find specific information through search, use it to provide accurate answers.
If the search doesn't return relevant results, let the user know and provide general guidance.
"""
        
        chat_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
        
        # First call - agent decides to use search
        response = openai_client.chat.completions.create(
            model='gpt-4o-mini',
            messages=chat_messages,
            tools=[text_search_tool]
        )
        
        message = response.choices[0].message
        
        # Check if agent wants to call a function
        if message.tool_calls:
            # Execute the function
            for tool_call in message.tool_calls:
                if tool_call.function.name == "text_search":
                    arguments = json.loads(tool_call.function.arguments)
                    search_results = search_index.search(**arguments)
                    
                    # Add function call and result to conversation
                    chat_messages.append(message)
                    chat_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(search_results)
                    })
            
            # Second call - agent uses search results to answer
            response = openai_client.chat.completions.create(
                model='gpt-4o-mini',
                messages=chat_messages,
                tools=[text_search_tool]
            )
            message = response.choices[0].message
        
        return message.content
    
    return ask_question


# Method 2: Using Pydantic AI (simpler approach)
def create_agent_with_pydantic_ai(search_index: SimpleSearchIndex) -> Agent:
    """
    Create an agent using Pydantic AI.
    This is the recommended approach - much simpler!
    """
    system_prompt = """
You are a helpful assistant for a course/documentation. 

Use the search tool to find relevant information from the documentation before answering questions.

If you can find specific information through search, use it to provide accurate answers.
If the search doesn't return relevant results, let the user know and provide general guidance.

Always search for relevant information before answering. 
If the first search doesn't give you enough information, try different search terms.
"""
    
    # Create a search function bound to this index
    def text_search_tool(query: str) -> List[Dict[str, Any]]:
        """
        Perform a text-based search on the documentation index.

        Args:
            query (str): The search query string.

        Returns:
            List[Dict[str, Any]]: A list of up to 5 search results returned by the index.
        """
        return search_index.search(query, num_results=5)
    
    # Create agent with the tool
    agent = Agent(
        name="documentation_agent",
        instructions=system_prompt,
        tools=[text_search_tool],
        model='gpt-4o-mini'
    )
    
    return agent


async def main():
    """Example usage of agents with tools."""
    print("=" * 60)
    print("Day 4: Agents and Tools")
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
    
    # Create sample documentation/FAQ
    sample_docs = [
        {
            "title": "Course Enrollment",
            "content": "Yes, you can still join the course even after the start date. While you won't be able to officially register, you are eligible to submit your homework. Just keep in mind that there are deadlines for submitting assignments and final projects, so it's best not to leave everything to the last minute."
        },
        {
            "title": "Homework Submission",
            "content": "Homework should be submitted through the course platform. Each assignment has a specific deadline. Late submissions may be accepted with a penalty, depending on the instructor's policy."
        },
        {
            "title": "Getting Help",
            "content": "If you need help, you can ask questions in the course Slack channel, contact the instructor, or check the FAQ section. The community is very helpful and responsive."
        }
    ]
    
    # Create search index
    search_index = SimpleSearchIndex(sample_docs)
    print(f"📚 Created search index with {len(sample_docs)} documents")
    print()
    
    # Test search
    print("🔍 Testing search function:")
    print("-" * 60)
    results = search_index.search("join course", num_results=2)
    print(f"   Query: 'join course'")
    print(f"   Found {len(results)} results")
    if results:
        print(f"   First result: {results[0].get('title', 'N/A')}")
    print()
    
    # Method 1: OpenAI Function Calling (manual)
    print("1️⃣ Method 1: OpenAI Function Calling (Manual)")
    print("-" * 60)
    try:
        ask_question = create_agent_with_openai(search_index)
        question = "I just discovered the course, can I join now?"
        print(f"   Question: {question}")
        answer = ask_question(question)
        print(f"   Answer: {answer}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()
    
    # Method 2: Pydantic AI (recommended)
    print("2️⃣ Method 2: Pydantic AI (Recommended)")
    print("-" * 60)
    try:
        agent = create_agent_with_pydantic_ai(search_index)
        question = "I just discovered the course, can I join now?"
        print(f"   Question: {question}")
        result = await agent.run(user_prompt=question)
        print(f"   Answer: {result.data}")
        
        # Show agent's reasoning
        print()
        print("   📋 Agent's reasoning:")
        messages = result.new_messages()
        for i, msg in enumerate(messages, 1):
            msg_type = type(msg).__name__
            print(f"   {i}. {msg_type}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    print()
    
    print("=" * 60)
    print("✅ Day 4 complete! Agents with tools are ready.")
    print("=" * 60)
    print()
    print("💡 Key takeaways:")
    print("   - Agents can use tools (functions) to get information")
    print("   - Pydantic AI simplifies agent development")
    print("   - System prompts control agent behavior")
    print("   - Tools make agents 'agentic' - they can take actions!")


if __name__ == '__main__':
    asyncio.run(main())

