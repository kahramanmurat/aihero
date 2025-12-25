"""
Day 5: Evaluation
Build logging system, automated evaluation using LLM as a judge, and performance metrics.
"""
import json
import secrets
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessagesTypeAdapter
import pandas as pd
from tqdm.auto import tqdm


# Create logs directory
LOG_DIR = Path('logs')
LOG_DIR.mkdir(exist_ok=True)


# Evaluation Models
class EvaluationCheck(BaseModel):
    """Individual evaluation check with justification."""
    check_name: str
    justification: str
    check_pass: bool


class EvaluationChecklist(BaseModel):
    """Complete evaluation checklist with summary."""
    checklist: List[EvaluationCheck]
    summary: str


class QuestionsList(BaseModel):
    """List of generated questions."""
    questions: List[str]


# Logging Functions
def serializer(obj):
    """JSON serializer for datetime objects."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def log_entry(agent: Agent, messages: Any, source: str = "user") -> Dict[str, Any]:
    """
    Extract key information from agent and messages for logging.
    
    Args:
        agent: Pydantic AI agent instance
        messages: Agent messages from result.new_messages()
        source: Source of the question ('user' or 'ai-generated')
    
    Returns:
        Dictionary with agent configuration and interaction log
    """
    tools = []
    for ts in agent.toolsets:
        tools.extend(ts.tools.keys())
    
    dict_messages = ModelMessagesTypeAdapter.dump_python(messages)
    
    return {
        "agent_name": agent.name,
        "system_prompt": agent._instructions,
        "provider": agent.model.system,
        "model": agent.model.model_name,
        "tools": tools,
        "messages": dict_messages,
        "source": source
    }


def log_interaction_to_file(
    agent: Agent, 
    messages: Any, 
    source: str = 'user'
) -> Path:
    """
    Log agent interaction to a JSON file.
    
    Args:
        agent: Pydantic AI agent instance
        messages: Agent messages from result.new_messages()
        source: Source of the question
    
    Returns:
        Path to the created log file
    """
    entry = log_entry(agent, messages, source)
    
    # Get timestamp from last message
    if entry['messages']:
        ts = entry['messages'][-1].get('timestamp', datetime.now())
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
    else:
        ts = datetime.now()
    
    ts_str = ts.strftime("%Y%m%d_%H%M%S")
    rand_hex = secrets.token_hex(3)
    
    filename = f"{agent.name}_{ts_str}_{rand_hex}.json"
    filepath = LOG_DIR / filename
    
    with filepath.open("w", encoding="utf-8") as f_out:
        json.dump(entry, f_out, indent=2, default=serializer)
    
    return filepath


def load_log_file(log_file: Path) -> Dict[str, Any]:
    """
    Load a log file and add filename to the record.
    
    Args:
        log_file: Path to log file
    
    Returns:
        Dictionary with log data
    """
    with open(log_file, 'r', encoding='utf-8') as f_in:
        log_data = json.load(f_in)
        log_data['log_file'] = str(log_file)
        return log_data


# Evaluation Functions
def simplify_log_messages(messages: List[Dict]) -> List[Dict]:
    """
    Simplify log messages by removing unnecessary fields.
    Reduces token usage for evaluation.
    
    Args:
        messages: List of message dictionaries
    
    Returns:
        Simplified message list
    """
    log_simplified = []
    
    for m in messages:
        parts = []
        
        for original_part in m.get('parts', []):
            part = original_part.copy()
            kind = part.get('part_kind', '')
            
            if kind == 'user-prompt':
                part.pop('timestamp', None)
            if kind == 'tool-call':
                part.pop('tool_call_id', None)
            if kind == 'tool-return':
                part.pop('tool_call_id', None)
                part.pop('metadata', None)
                part.pop('timestamp', None)
                # Replace actual search results with placeholder to save tokens
                part['content'] = 'RETURN_RESULTS_REDACTED'
            if kind == 'text':
                part.pop('id', None)
            
            parts.append(part)
        
        message = {
            'kind': m.get('kind', ''),
            'parts': parts
        }
        
        log_simplified.append(message)
    
    return log_simplified


def create_evaluation_agent() -> Agent:
    """
    Create an evaluation agent that uses LLM as a judge.
    
    Returns:
        Configured evaluation agent
    """
    evaluation_prompt = """
Use this checklist to evaluate the quality of an AI agent's answer (<ANSWER>) to a user question (<QUESTION>).
We also include the entire log (<LOG>) for analysis.

For each item, check if the condition is met. 

Checklist:

- instructions_follow: The agent followed the user's instructions (in <INSTRUCTIONS>)
- instructions_avoid: The agent avoided doing things it was told not to do  
- answer_relevant: The response directly addresses the user's question  
- answer_clear: The answer is clear and correct  
- answer_citations: The response includes proper citations or sources when required  
- completeness: The response is complete and covers all key aspects of the request
- tool_call_search: Is the search tool invoked? 

Output true/false for each check and provide a short explanation for your judgment.
""".strip()
    
    eval_agent = Agent(
        name='eval_agent',
        model='gpt-4o-mini',  # Using same model, but you can use different one
        instructions=evaluation_prompt,
        output_type=EvaluationChecklist
    )
    
    return eval_agent


async def evaluate_log_record(
    eval_agent: Agent, 
    log_record: Dict[str, Any]
) -> EvaluationChecklist:
    """
    Evaluate a single log record using the evaluation agent.
    
    Args:
        eval_agent: Evaluation agent instance
        log_record: Log record dictionary
    
    Returns:
        EvaluationChecklist with results
    """
    messages = log_record['messages']
    
    instructions = log_record['system_prompt']
    question = messages[0]['parts'][0]['content']
    answer = messages[-1]['parts'][0]['content']
    
    log_simplified = simplify_log_messages(messages)
    log = json.dumps(log_simplified)
    
    user_prompt_format = """
<INSTRUCTIONS>{instructions}</INSTRUCTIONS>
<QUESTION>{question}</QUESTION>
<ANSWER>{answer}</ANSWER>
<LOG>{log}</LOG>
""".strip()
    
    user_prompt = user_prompt_format.format(
        instructions=instructions,
        question=question,
        answer=answer,
        log=log
    )
    
    result = await eval_agent.run(user_prompt)
    return result.data


# Test Data Generation
def create_question_generator() -> Agent:
    """
    Create an agent for generating test questions.
    
    Returns:
        Configured question generator agent
    """
    question_generation_prompt = """
You are helping to create test questions for an AI agent that answers questions about documentation.

Based on the provided content, generate realistic questions that users might ask.

The questions should:

- Be natural and varied in style
- Range from simple to complex
- Include both specific technical questions and general questions

Generate one question for each record.
""".strip()
    
    question_generator = Agent(
        name="question_generator",
        instructions=question_generation_prompt,
        model='gpt-4o-mini',
        output_type=QuestionsList
    )
    
    return question_generator


async def generate_test_questions(
    question_generator: Agent,
    documents: List[Dict[str, Any]],
    num_questions: int = 10
) -> List[str]:
    """
    Generate test questions from documents.
    
    Args:
        question_generator: Question generator agent
        documents: List of documents to generate questions from
        num_questions: Number of questions to generate
    
    Returns:
        List of generated questions
    """
    import random
    
    # Sample documents
    sample = random.sample(documents, min(num_questions, len(documents)))
    prompt_docs = [d.get('content', '') for d in sample]
    prompt = json.dumps(prompt_docs)
    
    result = await question_generator.run(prompt)
    return result.data.questions


# Metrics and Analysis
def calculate_metrics(eval_results: List[tuple]) -> pd.DataFrame:
    """
    Calculate evaluation metrics from results.
    
    Args:
        eval_results: List of (log_record, eval_result) tuples
    
    Returns:
        DataFrame with metrics
    """
    rows = []
    
    for log_record, eval_result in eval_results:
        messages = log_record['messages']
        
        row = {
            'file': Path(log_record['log_file']).name,
            'question': messages[0]['parts'][0]['content'],
            'answer': messages[-1]['parts'][0]['content'],
        }
        
        checks = {c.check_name: c.check_pass for c in eval_result.checklist}
        row.update(checks)
        
        rows.append(row)
    
    df_evals = pd.DataFrame(rows)
    return df_evals


def print_evaluation_summary(df_evals: pd.DataFrame):
    """
    Print summary statistics from evaluation DataFrame.
    
    Args:
        df_evals: DataFrame with evaluation results
    """
    print("=" * 60)
    print("📊 Evaluation Summary")
    print("=" * 60)
    print()
    
    # Calculate mean pass rates for each check
    numeric_cols = df_evals.select_dtypes(include=['bool', 'int']).columns
    if len(numeric_cols) > 0:
        means = df_evals[numeric_cols].mean()
        
        print("Pass Rates (0.0 = 0%, 1.0 = 100%):")
        print("-" * 60)
        for check_name, pass_rate in means.items():
            percentage = pass_rate * 100
            status = "✅" if pass_rate >= 0.8 else "⚠️" if pass_rate >= 0.5 else "❌"
            print(f"   {status} {check_name}: {percentage:.1f}%")
        print()
    
    print(f"Total evaluations: {len(df_evals)}")
    print()
    
    # Show failed checks
    print("Failed Checks:")
    print("-" * 60)
    for idx, row in df_evals.iterrows():
        failed_checks = [col for col in numeric_cols if not row[col]]
        if failed_checks:
            print(f"   Question {idx + 1}: {', '.join(failed_checks)}")


async def main():
    """Example usage of evaluation system."""
    print("=" * 60)
    print("Day 5: Evaluation System")
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
    
    # Example: Create a simple agent for testing
    from day4_agent import SimpleSearchIndex, create_agent_with_pydantic_ai
    
    sample_docs = [
        {
            "title": "Course Enrollment",
            "content": "Yes, you can still join the course even after the start date. While you won't be able to officially register, you are eligible to submit your homework."
        },
        {
            "title": "Homework Submission",
            "content": "Homework should be submitted through the course platform. Each assignment has a specific deadline."
        }
    ]
    
    search_index = SimpleSearchIndex(sample_docs)
    agent = create_agent_with_pydantic_ai(search_index)
    
    print("🤖 Created test agent")
    print()
    
    # Test logging
    print("📝 Testing logging system...")
    print("-" * 60)
    question = "Can I join the course late?"
    result = await agent.run(user_prompt=question)
    log_file = log_interaction_to_file(agent, result.new_messages(), source='user')
    print(f"✅ Logged interaction to: {log_file}")
    print()
    
    # Test evaluation
    print("🧪 Testing evaluation system...")
    print("-" * 60)
    log_record = load_log_file(log_file)
    eval_agent = create_evaluation_agent()
    eval_result = await evaluate_log_record(eval_agent, log_record)
    
    print(f"Summary: {eval_result.summary}")
    print()
    print("Checklist:")
    for check in eval_result.checklist:
        status = "✅" if check.check_pass else "❌"
        print(f"   {status} {check.check_name}: {check.justification}")
    print()
    
    # Test question generation
    print("📝 Testing question generation...")
    print("-" * 60)
    question_generator = create_question_generator()
    questions = await generate_test_questions(question_generator, sample_docs, num_questions=2)
    print(f"✅ Generated {len(questions)} questions:")
    for i, q in enumerate(questions, 1):
        print(f"   {i}. {q}")
    print()
    
    print("=" * 60)
    print("✅ Day 5 evaluation system is ready!")
    print("=" * 60)
    print()
    print("💡 Next steps:")
    print("   - Collect more interaction logs")
    print("   - Run evaluations on all logs")
    print("   - Calculate metrics and compare different agent versions")
    print("   - Use metrics to improve your agent")


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

