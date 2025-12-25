"""
Day 6: Logging module
Handles logging of agent interactions to JSON files.
"""
import os
import json
import secrets
from pathlib import Path
from datetime import datetime
from typing import Any, Dict
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessagesTypeAdapter


LOG_DIR = Path(os.getenv('LOGS_DIRECTORY', 'logs'))
LOG_DIR.mkdir(exist_ok=True)


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


def serializer(obj):
    """JSON serializer for datetime objects."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


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

