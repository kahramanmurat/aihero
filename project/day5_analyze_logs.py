"""
Analyze existing log files and generate evaluation report.
Useful for analyzing logs collected over time.
"""
import asyncio
from pathlib import Path
from day5_evaluation import (
    load_log_file,
    create_evaluation_agent,
    evaluate_log_record,
    calculate_metrics,
    print_evaluation_summary
)
from tqdm.auto import tqdm
import os


async def analyze_existing_logs(agent_name: str = None, source: str = None):
    """
    Analyze existing log files and generate evaluation report.
    
    Args:
        agent_name: Filter by agent name (e.g., 'faq_agent_v2')
        source: Filter by source ('user' or 'ai-generated')
    """
    print("=" * 60)
    print("Day 5: Analyzing Existing Logs")
    print("=" * 60)
    print()
    
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  OPENAI_API_KEY not set!")
        print("   Set it with: export OPENAI_API_KEY='your-api-key'")
        return
    
    # Find log files
    log_dir = Path('logs')
    if not log_dir.exists():
        print("❌ No logs directory found")
        return
    
    log_files = list(log_dir.glob('*.json'))
    
    if not log_files:
        print("❌ No log files found")
        return
    
    print(f"📁 Found {len(log_files)} log files")
    print()
    
    # Filter logs
    filtered_logs = []
    for log_file in log_files:
        try:
            log_record = load_log_file(log_file)
            
            if agent_name and agent_name not in log_record.get('agent_name', ''):
                continue
            
            if source and log_record.get('source') != source:
                continue
            
            filtered_logs.append(log_file)
        except Exception as e:
            print(f"⚠️  Error loading {log_file}: {e}")
            continue
    
    if not filtered_logs:
        print("❌ No logs match the filter criteria")
        return
    
    print(f"📊 Analyzing {len(filtered_logs)} log files")
    if agent_name:
        print(f"   Agent: {agent_name}")
    if source:
        print(f"   Source: {source}")
    print()
    
    # Evaluate logs
    print("🧪 Evaluating logs...")
    print("-" * 60)
    eval_agent = create_evaluation_agent()
    eval_results = []
    
    for log_file in tqdm(filtered_logs, desc="Evaluating"):
        try:
            log_record = load_log_file(log_file)
            eval_result = await evaluate_log_record(eval_agent, log_record)
            eval_results.append((log_record, eval_result))
        except Exception as e:
            print(f"❌ Error evaluating {log_file}: {e}")
            continue
    
    print(f"✅ Evaluated {len(eval_results)} logs")
    print()
    
    # Generate report
    if eval_results:
        print("📊 Generating evaluation report...")
        print("-" * 60)
        df_evals = calculate_metrics(eval_results)
        print_evaluation_summary(df_evals)
        
        # Save to CSV
        csv_file = log_dir / 'evaluation_report.csv'
        df_evals.to_csv(csv_file, index=False)
        print()
        print(f"💾 Saved detailed report to: {csv_file}")
    else:
        print("❌ No evaluation results to analyze")
    
    print()
    print("=" * 60)
    print("✅ Analysis complete!")
    print("=" * 60)


if __name__ == '__main__':
    import sys
    
    agent_name = None
    source = None
    
    if len(sys.argv) > 1:
        agent_name = sys.argv[1]
    if len(sys.argv) > 2:
        source = sys.argv[2]
    
    asyncio.run(analyze_existing_logs(agent_name=agent_name, source=source))

