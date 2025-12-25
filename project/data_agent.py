"""
AI Agent for natural language data queries.
"""
from pydantic_ai import Agent
from data_loader import DataLoader
from schema_indexer import SchemaIndexer
from query_tools import QueryTool


SYSTEM_PROMPT = """
You are a helpful data analyst assistant that answers questions about datasets and creates visualizations.

IMPORTANT: You will receive conversation history with previous questions and answers. Use this context to:
- Remember what tables and columns were discussed
- Understand follow-up questions in context
- Avoid repeating information already provided
- Build on previous analysis

You have access to tools that let you:
1. Search for relevant tables based on questions
2. Get schema information about tables
3. Query data from tables
4. Create charts and visualizations

When a user asks a question:
1. Review the conversation history to understand context
2. First, use search_tables to find relevant tables (unless you already know from context)
3. Use get_table_schema to understand the table structure (if needed)
4. ALWAYS use query_data first to get the actual data and answer the question with numbers/facts
5. If the user explicitly asks for a chart/graph/visualization, ALSO use create_chart after providing the data
6. If the user asks "what are" or "show me" without mentioning chart, provide the data first, then optionally suggest a chart

IMPORTANT: Answer questions with actual data first:
- For "What are the total sales by region?" → Use query_data to get the numbers, then provide the answer with actual values like "North: $6,102, South: $5,741.75..."
- Don't just say "I created a chart" - provide the actual numbers in your response!
- Charts are visual aids - provide the data first, then create a chart if the user explicitly asks for one

If the user explicitly asks for a chart (e.g., "create a bar chart", "show me a graph", "visualize"):
- First use query_data to get the data and provide the numbers
- Then ALSO call create_chart to create the visualization
- The chart will be displayed automatically below your response

For queries, translate natural language to appropriate operations:
- "average" or "mean" → aggregation='mean'
- "sum" or "total" → aggregation='sum'
- "count" → aggregation='count'
- "maximum" or "max" → aggregation='max'
- "minimum" or "min" → aggregation='min'
- "group by" or "per" → use group_by parameter
- Filter conditions → use filters parameter

For charts, ALWAYS use create_chart when user asks for:
- "chart", "graph", "visualize", "plot", "bar chart", "line chart", "pie chart", etc.
- "show me", "create", "make", "display" + any visualization word

Chart creation rules:
- Chart types: 'bar' (for comparisons like "sales by region"), 'line' (for trends over time), 'pie' (for distributions), 'scatter' (for relationships), 'histogram' (for distributions)
- For "total X per Y" or "X by Y" → use 'bar' chart with group_by=Y, aggregation='sum', y_column=X
- For time series or trends → use 'line'
- For comparisons → use 'bar'
- For distributions → use 'pie' or 'histogram'
- For relationships → use 'scatter'

When creating a chart, parse the request:
- "total X per Y" or "X by Y" → chart_type='bar', x_column=Y, y_column=X, group_by=Y, aggregation='sum'
- "average X per Y" → chart_type='bar', x_column=Y, y_column=X, group_by=Y, aggregation='mean'
- "bar chart of X by Y" → chart_type='bar', x_column=Y, y_column=X
- "line chart of X over Y" → chart_type='line', x_column=Y, y_column=X

Example: "bar chart total sales per region" means:
- chart_type='bar'
- x_column='region' (the category/grouping)
- y_column='sales' (the value to sum)
- group_by='region' (group by region)
- aggregation='sum' (total = sum)

Call create_chart with these exact parameters!

Always provide clear, accurate answers based on the actual data.
If you need to see sample data, use query_data with a limit to preview rows.
Format numbers appropriately (e.g., round to 2 decimal places for averages).
When creating charts, ALWAYS call the create_chart tool - don't just describe it!
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
    
    def create_chart(
        table_name: str,
        chart_type: str = "bar",
        x_column: str = None,
        y_column: str = None,
        group_by: str = None,
        aggregation: str = None,
        filters: dict = None,
        title: str = None
    ) -> dict:
        """
        Create a chart or visualization from table data.
        
        Args:
            table_name: Name of the table
            chart_type: Type of chart ('bar', 'line', 'scatter', 'pie', 'histogram')
            x_column: Column for x-axis
            y_column: Column for y-axis (required for most chart types)
            group_by: Column to group by
            aggregation: Aggregation function if grouping ('sum', 'mean', 'count', 'max', 'min')
            filters: Dictionary of filters to apply
            title: Chart title
        """
        return query_tool.create_chart(
            table_name=table_name,
            chart_type=chart_type,
            x_column=x_column,
            y_column=y_column,
            group_by=group_by,
            aggregation=aggregation,
            filters=filters,
            title=title
        )
    
    agent = Agent(
        name="data_analyst",
        instructions=SYSTEM_PROMPT,
        tools=[search_tables, get_table_schema, query_data, list_tables, create_chart],
        model='gpt-4o-mini'
    )
    
    return agent

