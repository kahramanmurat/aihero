"""
Test script: Complete evaluation workflow
1. Generate test questions
2. Run agent on questions
3. Log interactions
4. Evaluate results
5. Calculate metrics
"""
import asyncio
from day1_ingest import read_repo_data
from day4_agent import SimpleSearchIndex, create_agent_with_pydantic_ai
from day5_evaluation import (
    log_interaction_to_file,
    load_log_file,
    create_evaluation_agent,
    evaluate_log_record,
    create_question_generator,
    generate_test_questions,
    calculate_metrics,
    print_evaluation_summary
)
from pathlib import Path
import os
from tqdm.auto import tqdm


async def run_complete_evaluation():
    """Run complete evaluation workflow."""
    print("=" * 60)
    print("Day 5: Complete Evaluation Workflow")
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
    
    # Step 1: Download repository data
    print("📥 Step 1: Downloading repository data...")
    try:
        docs = read_repo_data('DataTalksClub', 'faq')
        print(f"✅ Downloaded {len(docs)} documents")
    except Exception as e:
        print(f"❌ Error downloading: {e}")
        return
    
    if not docs:
        print("❌ No documents to process")
        return
    
    # Step 2: Prepare search index
    print()
    print("🔍 Step 2: Creating search index...")
    search_docs = []
    for doc in docs:
        content = doc.get('content', '')
        title = doc.get('title', doc.get('question', doc.get('filename', 'Untitled')))
        
        if content:
            search_docs.append({
                'title': title,
                'content': content,
                'metadata': {k: v for k, v in doc.items() if k not in ['content', 'title']}
            })
    
    search_index = SimpleSearchIndex(search_docs)
    print(f"✅ Index created with {len(search_docs)} documents")
    print()
    
    # Step 3: Create agent
    print("🤖 Step 3: Creating agent...")
    agent = create_agent_with_pydantic_ai(search_index)
    print("✅ Agent created")
    print()
    
    # Step 4: Generate test questions
    print("📝 Step 4: Generating test questions...")
    question_generator = create_question_generator()
    num_questions = 5  # Start with 5 for testing
    questions = await generate_test_questions(
        question_generator, 
        search_docs, 
        num_questions=num_questions
    )
    print(f"✅ Generated {len(questions)} test questions")
    print()
    
    # Step 5: Run agent and log interactions
    print("💬 Step 5: Running agent on questions and logging...")
    print("-" * 60)
    log_files = []
    
    for q in tqdm(questions, desc="Processing questions"):
        try:
            result = await agent.run(user_prompt=q)
            log_file = log_interaction_to_file(
                agent,
                result.new_messages(),
                source='ai-generated'
            )
            log_files.append(log_file)
        except Exception as e:
            print(f"❌ Error processing question '{q}': {e}")
            continue
    
    print(f"✅ Logged {len(log_files)} interactions")
    print()
    
    # Step 6: Evaluate logs
    print("🧪 Step 6: Evaluating interactions...")
    print("-" * 60)
    eval_agent = create_evaluation_agent()
    eval_results = []
    
    for log_file in tqdm(log_files, desc="Evaluating"):
        try:
            log_record = load_log_file(log_file)
            eval_result = await evaluate_log_record(eval_agent, log_record)
            eval_results.append((log_record, eval_result))
        except Exception as e:
            print(f"❌ Error evaluating {log_file}: {e}")
            continue
    
    print(f"✅ Evaluated {len(eval_results)} interactions")
    print()
    
    # Step 7: Calculate metrics
    print("📊 Step 7: Calculating metrics...")
    print("-" * 60)
    if eval_results:
        df_evals = calculate_metrics(eval_results)
        print_evaluation_summary(df_evals)
    else:
        print("❌ No evaluation results to analyze")
    
    print()
    print("=" * 60)
    print("✅ Complete evaluation workflow finished!")
    print("=" * 60)
    print()
    print("💡 You can now:")
    print("   - Review individual evaluations in the logs/ directory")
    print("   - Compare different agent versions")
    print("   - Use metrics to improve your agent")


if __name__ == '__main__':
    asyncio.run(run_complete_evaluation())

