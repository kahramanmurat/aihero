"""
Day 4: Comparison - Agent with tools vs. LLM without tools
Demonstrates the difference between a simple LLM and an agentic system.
"""
import os
from openai import OpenAI
from day4_agent import SimpleSearchIndex, create_agent_with_pydantic_ai
import asyncio


async def compare_llm_vs_agent():
    """Compare LLM without tools vs. Agent with tools."""
    print("=" * 60)
    print("Day 4: LLM vs. Agent Comparison")
    print("=" * 60)
    print()
    
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  OPENAI_API_KEY not set!")
        print("   Set it with: export OPENAI_API_KEY='your-api-key'")
        return
    
    # Create sample documentation
    sample_docs = [
        {
            "title": "Course Enrollment",
            "content": "Yes, you can still join the course even after the start date. While you won't be able to officially register, you are eligible to submit your homework. Just keep in mind that there are deadlines for submitting assignments and final projects, so it's best not to leave everything to the last minute."
        },
        {
            "title": "Homework Submission",
            "content": "Homework should be submitted through the course platform. Each assignment has a specific deadline. Late submissions may be accepted with a penalty, depending on the instructor's policy."
        }
    ]
    
    search_index = SimpleSearchIndex(sample_docs)
    question = "I just discovered the course, can I join now?"
    
    print(f"❓ Question: {question}")
    print()
    
    # Method 1: LLM without tools (not agentic)
    print("1️⃣ LLM WITHOUT Tools (Not Agentic):")
    print("-" * 60)
    openai_client = OpenAI()
    
    try:
        response = openai_client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {"role": "user", "content": question}
            ]
        )
        answer_without_tools = response.choices[0].message.content
        print(f"Answer: {answer_without_tools}")
        print()
        print("⚠️  This is a generic answer - the LLM doesn't have access")
        print("   to the specific course documentation!")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Method 2: Agent WITH tools (agentic)
    print("2️⃣ Agent WITH Tools (Agentic):")
    print("-" * 60)
    
    try:
        agent = create_agent_with_pydantic_ai(search_index)
        result = await agent.run(user_prompt=question)
        answer_with_tools = result.data
        print(f"Answer: {answer_with_tools}")
        print()
        print("✅ This answer is based on actual documentation!")
        print("   The agent used the search tool to find relevant information.")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    print("=" * 60)
    print("📊 Key Difference:")
    print("=" * 60)
    print("   Without tools: Generic, training-data-based answers")
    print("   With tools: Specific, context-aware answers from your data")
    print()
    print("💡 Tools make the system 'agentic' - it can:")
    print("   - Search for information")
    print("   - Retrieve specific data")
    print("   - Take actions based on context")
    print("   - Provide accurate, domain-specific answers")


if __name__ == '__main__':
    asyncio.run(compare_llm_vs_agent())

