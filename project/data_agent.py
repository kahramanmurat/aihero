"""
AI Agent for natural language data queries.
"""
from pydantic_ai import Agent
from data_loader import DataLoader
from schema_indexer import SchemaIndexer
from query_tools import QueryTool


SYSTEM_PROMPT = """
You are a helpful data analyst assistant that answers questions about datasets.

You have access to tools that let you:
1. Search for relevant tables based on questions
2. Get schema information about tables
3. Query data from tables

When a user asks a question:
1. First, use search_tables to find relevant tables
2. Use get_table_schema to understand the table structure
3. Use query_data to answer the question

For queries, translate natural language to appropriate operations:
- "average" or "mean" → aggregation='mean'
- "sum" or "total" → aggregation='sum'
- "count" → aggregation='count'
- "maximum" or "max" → aggregation='max'
- "minimum" or "min" → aggregation='min'
- "group by" or "per" → use group_by parameter
- Filter conditions → use filters parameter

Always provide clear, accurate answers based on the actual data.
If you need to see sample data, use query_data with a limit to preview rows.
Format numbers appropriately (e.g., round to 2 decimal places for averages).
"""


def init_agent(data_loader: DataLoader, schema_indexer: SchemaIndexer) -> Agent:
    """
    Initialize the data analysis agent.
    
    Args:
        data_loader: DataLoader instance with loaded data
        schema_indexer: SchemaIndexer instance with indexed schemas
        
    Returns:
        Configured Agent instance
    """
    query_tool = QueryTool(data_loader, schema_indexer)
    
    # Create tools for the agent
    def search_tables(query: str) -> list:
        """Search for tables relevant to a natural language query."""
        results = schema_indexer.search_tables(query, num_results=3)
        return [
            {
                "table_name": r["table_name"],
                "columns": r["columns"],
                "description": r["description"],
                "row_count": r["row_count"]
            }
            for r in results
        ]
    
    def get_table_schema(table_name: str) -> dict:
        """Get detailed schema information for a table."""
        return query_tool.get_table_schema(table_name)
    
    def query_data(
        table_name: str,
        operation: str = "select",
        columns: list[str] = None,
        filters: dict = None,
        aggregation: str = None,
        group_by: list[str] = None,
        limit: int = 100
    ) -> dict:
        """
        Query data from a table.
        
        Args:
            table_name: Name of the table
            operation: Type of operation (select, aggregate, filter)
            columns: List of column names to select
            filters: Dictionary of filters {column: value} or {column: {operator: value}}
            aggregation: Aggregation function (mean, sum, count, max, min)
            group_by: List of columns to group by
            limit: Maximum rows to return
        """
        return query_tool.query_data(
            table_name=table_name,
            operation=operation,
            columns=columns,
            filters=filters,
            aggregation=aggregation,
            group_by=group_by,
            limit=limit
        )
    
    def list_tables() -> list[str]:
        """List all available tables."""
        return query_tool.list_tables()
    
    agent = Agent(
        name="data_analyst",
        instructions=SYSTEM_PROMPT,
        tools=[search_tables, get_table_schema, query_data, list_tables],
        model='gpt-4o-mini'
    )
    
    return agent

