"""
Day 2: Intelligent Chunking with LLM
This script demonstrates LLM-based intelligent chunking.
Requires OPENAI_API_KEY environment variable.
"""
import os
from openai import OpenAI
from day1_ingest import read_repo_data
from day2_chunking import chunk_documents_intelligent, intelligent_chunking


def llm(prompt: str, model: str = 'gpt-4o-mini') -> str:
    """
    Invoke an LLM with the provided prompt.
    
    Args:
        prompt: The prompt to send to the LLM
        model: The model to use (default: gpt-4o-mini)
    
    Returns:
        The LLM response text
    """
    openai_client = OpenAI()
    
    messages = [
        {"role": "user", "content": prompt}
    ]

    response = openai_client.chat.completions.create(
        model=model,
        messages=messages
    )

    return response.choices[0].message.content


def main():
    """Example of intelligent chunking with LLM."""
    print("=" * 60)
    print("Day 2: Intelligent Chunking with LLM")
    print("=" * 60)
    print()
    
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  OPENAI_API_KEY not set!")
        print("   Set it with: export OPENAI_API_KEY='your-api-key'")
        print("   Or use direnv for automatic loading")
        return
    
    print("✅ OPENAI_API_KEY found")
    print()
    
    # Example text for demonstration
    sample_text = """
# Machine Learning Basics

Machine learning is a subset of artificial intelligence that focuses on 
enabling computers to learn from data without being explicitly programmed.

## Supervised Learning

Supervised learning uses labeled data to train models. The algorithm learns 
from input-output pairs and can then make predictions on new data.

### Classification

Classification is a type of supervised learning where the output is a category. 
Examples include spam detection and image recognition.

### Regression

Regression predicts continuous values. Examples include house price prediction 
and stock market forecasting.

## Unsupervised Learning

Unsupervised learning finds patterns in data without labels. Common techniques 
include clustering and dimensionality reduction.

## Reinforcement Learning

Reinforcement learning trains agents through rewards and penalties. It's used 
in game playing and robotics.
""".strip()
    
    print("📄 Sample Document:")
    print(f"   Length: {len(sample_text)} characters")
    print()
    
    print("🤖 Using LLM to intelligently chunk the document...")
    print("-" * 60)
    
    try:
        sections = intelligent_chunking(sample_text, llm_func=llm)
        print(f"✅ Created {len(sections)} logical sections")
        print()
        
        for i, section in enumerate(sections, 1):
            print(f"Section {i}:")
            print(section[:150] + "..." if len(section) > 150 else section)
            print("-" * 60)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("   Make sure your OPENAI_API_KEY is valid and you have credits")
        return
    
    print()
    print("=" * 60)
    print("💡 Note: Intelligent chunking costs money.")
    print("   Use it only when simpler methods don't work well.")
    print("=" * 60)


if __name__ == '__main__':
    main()

