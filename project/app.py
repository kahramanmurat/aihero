"""
Streamlit app for AI Data Explorer.
"""
import streamlit as st
import streamlit.components.v1 as components
import asyncio
import pandas as pd
from data_loader import DataLoader
from schema_indexer import SchemaIndexer
from data_agent import init_agent
import os
import re


# --- Initialization ---
# Use session state instead of cache_resource to ensure data persists across reruns
if "data_loader" not in st.session_state:
    st.session_state.data_loader = DataLoader()
    st.session_state.schema_indexer = SchemaIndexer(st.session_state.data_loader)

# Always get fresh references
data_loader = st.session_state.data_loader
schema_indexer = st.session_state.schema_indexer

# Ensure schema is indexed if we have tables
if data_loader.get_all_tables() and len(schema_indexer.table_docs) == 0:
    schema_indexer.index_tables()


def get_agent(data_loader, schema_indexer):
    """Get or create the agent."""
    # Use session state to cache agent, but recreate when tables change
    tables_key = str(sorted(data_loader.get_all_tables()))
    
    if "agent" not in st.session_state or st.session_state.get("agent_tables_key") != tables_key:
        st.session_state.agent = init_agent(data_loader, schema_indexer)
        st.session_state.agent_tables_key = tables_key
    
    return st.session_state.agent


def _create_chart_from_question(user_question: str, data_loader: DataLoader, table_name: str, schema_indexer: SchemaIndexer) -> dict:
    """Directly create a chart from user question using QueryTool."""
    try:
        from query_tools import QueryTool
        query_tool = QueryTool(data_loader, schema_indexer)
        
        # Get table info
        df = data_loader.dataframes[table_name]
        columns = df.columns.tolist()
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Determine chart type - default to bar for aggregations
        chart_type = "bar"
        if "line" in user_question:
            chart_type = "line"
        elif "pie" in user_question:
            chart_type = "pie"
        elif "scatter" in user_question:
            chart_type = "scatter"
        elif "histogram" in user_question:
            chart_type = "histogram"
        
        # Find columns
        x_column = None
        y_column = None
        group_by = None
        aggregation = None
        
        # Pattern 1: "total X per Y" or "total X by Y"
        if "total" in user_question:
            aggregation = "sum"
            # Find the grouping column (usually after "per" or "by")
            if "per" in user_question or "by" in user_question:
                # Split on "per" or "by"
                separator = "per" if "per" in user_question else "by"
                parts = user_question.split(separator)
                if len(parts) >= 2:
                    # Look for region/category column in second part
                    for col in categorical_cols:
                        if col.lower() in parts[1].lower():
                            x_column = col
                            group_by = col
                            break
                    
                    # Look for sales/amount column in first part
                    for col in numeric_cols:
                        if col.lower() in parts[0].lower():
                            y_column = col
                            break
        
        # Pattern 2: "X by Y" (without "total")
        if not x_column and "by" in user_question:
            parts = user_question.split("by")
            if len(parts) == 2:
                # Find columns mentioned
                for col in numeric_cols:
                    if col.lower() in parts[0].lower():
                        y_column = col
                        break
                for col in categorical_cols:
                    if col.lower() in parts[1].lower():
                        x_column = col
                        group_by = col
                        break
        
        # Pattern 3: "What are the total sales by region?" - extract "sales" and "region"
        if not x_column or not y_column:
            # Look for common column names in the question
            for col in categorical_cols:
                if col.lower() in user_question.lower():
                    if not x_column:  # Use first match
                        x_column = col
                        group_by = col
                        break
            
            for col in numeric_cols:
                if col.lower() in user_question.lower():
                    if not y_column:  # Use first match
                        y_column = col
                        break
        
        # Fallback: use first categorical and first numeric if we have aggregation keywords
        if ("total" in user_question or "sum" in user_question or "average" in user_question) and not x_column:
            if categorical_cols:
                x_column = categorical_cols[0]
                group_by = categorical_cols[0]
            if not y_column and numeric_cols:
                y_column = numeric_cols[0]
            if not aggregation and "total" in user_question:
                aggregation = "sum"
            elif not aggregation and ("average" in user_question or "mean" in user_question):
                aggregation = "mean"
        
        # If we have both columns, create the chart
        if x_column and y_column:
            return query_tool.create_chart(
                table_name=table_name,
                chart_type=chart_type,
                x_column=x_column,
                y_column=y_column,
                group_by=group_by,
                aggregation=aggregation,
                title=f"{y_column} by {x_column}" if aggregation else f"{y_column} by {x_column}"
            )
    except Exception as e:
        import traceback
        # Silently fail - don't break the app
        pass
    
    return None


def _force_create_chart(user_question: str, data_loader: DataLoader, table_name: str) -> dict:
    """Force create a chart when detection fails - last resort fallback."""
    try:
        from query_tools import QueryTool
        from schema_indexer import SchemaIndexer
        
        # Create a minimal schema indexer (we don't need it for chart creation)
        schema_indexer = SchemaIndexer(data_loader)
        query_tool = QueryTool(data_loader, schema_indexer)
        
        df = data_loader.dataframes[table_name]
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Default: use first categorical for x, first numeric for y
        x_column = categorical_cols[0] if categorical_cols else None
        y_column = numeric_cols[0] if numeric_cols else None
        group_by = x_column
        aggregation = "sum" if "total" in user_question.lower() else None
        
        # Try to find better matches
        for col in categorical_cols:
            if col.lower() in user_question.lower():
                x_column = col
                group_by = col
                break
        
        for col in numeric_cols:
            if col.lower() in user_question.lower():
                y_column = col
                break
        
        if x_column and y_column:
            return query_tool.create_chart(
                table_name=table_name,
                chart_type="bar",
                x_column=x_column,
                y_column=y_column,
                group_by=group_by,
                aggregation=aggregation,
                title=f"{y_column} by {x_column}"
            )
    except Exception as e:
        pass
    
    return None


def _try_extract_chart_params(user_question: str, data_loader: DataLoader, loaded_tables: list) -> dict:
    """Try to extract chart parameters from user question as fallback."""
    try:
        # Get the first available table
        if not loaded_tables:
            return None
        
        table_name = loaded_tables[0]
        df = data_loader.dataframes[table_name]
        
        # Determine chart type
        chart_type = "bar"
        if "line" in user_question:
            chart_type = "line"
        elif "pie" in user_question:
            chart_type = "pie"
        elif "scatter" in user_question:
            chart_type = "scatter"
        elif "histogram" in user_question:
            chart_type = "histogram"
        
        # Try to find columns
        columns = df.columns.tolist()
        
        # Look for "total X per Y" or "X by Y" pattern
        x_column = None
        y_column = None
        group_by = None
        aggregation = "sum" if "total" in user_question or "sum" in user_question else None
        
        # Common patterns
        if "per" in user_question or "by" in user_question:
            # Try to find region, category, or similar grouping column
            for col in columns:
                if col.lower() in user_question.lower():
                    if df[col].dtype == 'object' or df[col].dtype.name == 'category':
                        x_column = col
                        group_by = col
                        break
            
            # Try to find numeric column for y-axis
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            for col in numeric_cols:
                if col.lower() in user_question.lower():
                    y_column = col
                    break
            
            # If no match, use first numeric column
            if not y_column and numeric_cols:
                y_column = numeric_cols[0]
        
        if x_column and y_column:
            return {
                "success": True,
                "chart_type": chart_type,
                "x_column": x_column,
                "y_column": y_column,
                "group_by": group_by,
                "aggregation": aggregation,
                "table_name": table_name,
                "title": f"{y_column} by {x_column}"
            }
    except Exception as e:
        pass
    
    return None


def _recreate_and_display_chart(chart_params: dict, data_loader: DataLoader):
    """Recreate and display a chart from chart parameters."""
    try:
        import plotly.express as px
        import pandas as pd
        
        # Debug: Log chart parameters
        if st.session_state.get('debug_charts', False):
            st.json(chart_params)
        
        chart_type = chart_params.get('chart_type', 'bar')
        x_column = chart_params.get('x_column')
        y_column = chart_params.get('y_column')
        group_by = chart_params.get('group_by')
        aggregation = chart_params.get('aggregation')
        filters = chart_params.get('filters')
        title = chart_params.get('title', 'Chart')
        table_name = chart_params.get('table_name')
        
        # Get the dataframe
        if not table_name or table_name not in data_loader.dataframes:
            st.error(f"Could not recreate chart: table '{table_name}' not found")
            return
        
        df = data_loader.dataframes[table_name].copy()
        
        # Apply filters if any
        if filters:
            for col, value in filters.items():
                if col in df.columns:
                    if isinstance(value, dict):
                        for op, val in value.items():
                            if op == '>':
                                df = df[df[col] > val]
                            elif op == '<':
                                df = df[df[col] < val]
                            elif op == '>=':
                                df = df[df[col] >= val]
                            elif op == '<=':
                                df = df[df[col] <= val]
                            elif op == '==':
                                df = df[df[col] == val]
                            elif op == '!=':
                                df = df[df[col] != val]
                    else:
                        df = df[df[col] == value]
        
        # Apply grouping and aggregation if needed
        if group_by and aggregation:
            if group_by in df.columns:
                if aggregation == 'sum':
                    if y_column and y_column in df.columns:
                        df = df.groupby(group_by)[y_column].sum().reset_index()
                        # After grouping, x_column should be the group_by column
                        x_column = group_by
                    else:
                        df = df.groupby(group_by).sum().reset_index()
                        x_column = group_by
                elif aggregation == 'mean':
                    if y_column and y_column in df.columns:
                        df = df.groupby(group_by)[y_column].mean().reset_index()
                        x_column = group_by
                    else:
                        df = df.groupby(group_by).mean().reset_index()
                        x_column = group_by
                elif aggregation == 'count':
                    df = df.groupby(group_by).size().reset_index(name='count')
                    x_column = group_by
                    y_column = 'count'
                elif aggregation == 'max':
                    if y_column and y_column in df.columns:
                        df = df.groupby(group_by)[y_column].max().reset_index()
                        x_column = group_by
                    else:
                        df = df.groupby(group_by).max().reset_index()
                        x_column = group_by
                elif aggregation == 'min':
                    if y_column and y_column in df.columns:
                        df = df.groupby(group_by)[y_column].min().reset_index()
                        x_column = group_by
                    else:
                        df = df.groupby(group_by).min().reset_index()
                        x_column = group_by
        
        # Ensure we have valid columns after processing
        if not x_column or x_column not in df.columns:
            st.error(f"Invalid x_column '{x_column}'. Available columns: {list(df.columns)}")
            return
        
        if not y_column or y_column not in df.columns:
            st.error(f"Invalid y_column '{y_column}'. Available columns: {list(df.columns)}")
            return
        
        # Recreate the chart
        fig = None
        if chart_type == "bar" and x_column and y_column:
            fig = px.bar(df, x=x_column, y=y_column, title=title)
        elif chart_type == "line" and x_column and y_column:
            fig = px.line(df, x=x_column, y=y_column, title=title)
        elif chart_type == "scatter" and x_column and y_column:
            fig = px.scatter(df, x=x_column, y=y_column, title=title)
        elif chart_type == "pie" and x_column and y_column:
            fig = px.pie(df, names=x_column, values=y_column, title=title)
        elif chart_type == "histogram" and y_column:
            fig = px.histogram(df, x=y_column, title=title)
        
        if fig:
            # Display the interactive Plotly chart
            st.plotly_chart(fig, width='stretch')
        else:
            st.error(f"Could not recreate {chart_type} chart. Missing columns: x={x_column}, y={y_column}")
            st.info(f"Available columns: {list(df.columns)}")
            st.info(f"DataFrame shape: {df.shape}")
            st.dataframe(df.head())
    except Exception as e:
        st.error(f"Error displaying chart: {e}")
        import traceback
        with st.expander("Chart Error Details", expanded=True):
            st.code(traceback.format_exc())

# --- Streamlit UI ---
st.set_page_config(
    page_title="AI Data Explorer", 
    page_icon="📊", 
    layout="wide"
)

st.title("📊 AI Data Explorer")
st.caption("Ask natural language questions about your CSV files and databases")

# Sidebar for data loading
with st.sidebar:
    st.header("📁 Load Data")
    
    # CSV Upload
    st.subheader("Upload CSV")
    uploaded_file = st.file_uploader(
        "Choose a CSV file", 
        type=['csv'],
        help="Upload a CSV file to analyze"
    )
    
    if uploaded_file is not None:
        # Check if this file was already processed (to avoid reloading on rerun)
        file_key = f"uploaded_{uploaded_file.name}_{uploaded_file.size}"
        
        if file_key not in st.session_state:
            # Save uploaded file temporarily
            import tempfile
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, uploaded_file.name)
            
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                table_name = data_loader.load_csv(temp_path)
                st.success(f"✅ Loaded: {table_name}")
                
                # Re-index tables
                schema_indexer.index_tables()
                
                # Mark as processed
                st.session_state[file_key] = True
                st.session_state.last_uploaded_table = table_name
                
                st.rerun()
            except Exception as e:
                st.error(f"Error loading CSV: {e}")
                import traceback
                with st.expander("Error Details"):
                    st.code(traceback.format_exc())
        else:
            # File already loaded
            if hasattr(st.session_state, 'last_uploaded_table'):
                st.success(f"✅ File already loaded: {st.session_state.last_uploaded_table}")
    
    # Database Connection
    st.subheader("Connect Database")
    db_type = st.selectbox(
        "Database Type",
        ["SQLite", "PostgreSQL", "MySQL", "Custom"]
    )
    
    if db_type == "SQLite":
        db_path = st.text_input("Database Path", placeholder="data.db")
        if st.button("Connect SQLite") and db_path:
            try:
                connection_string = f"sqlite:///{db_path}"
                db_name = data_loader.connect_database(connection_string)
                st.success(f"✅ Connected: {db_name}")
                
                # List tables
                tables = data_loader.list_database_tables(db_name)
                if tables:
                    st.write("**Available tables:**")
                    for table in tables:
                        if st.button(f"Load {table}", key=f"load_{table}"):
                            try:
                                loaded_name = data_loader.load_database_table(db_name, table)
                                st.success(f"✅ Loaded: {loaded_name}")
                                schema_indexer.index_tables()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
            except Exception as e:
                st.error(f"Error connecting: {e}")
    
    elif db_type == "PostgreSQL":
        host = st.text_input("Host", value="localhost")
        port = st.text_input("Port", value="5432")
        database = st.text_input("Database")
        user = st.text_input("User")
        password = st.text_input("Password", type="password")
        
        if st.button("Connect PostgreSQL") and all([host, database, user, password]):
            try:
                connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
                db_name = data_loader.connect_database(connection_string, db_name=database)
                st.success(f"✅ Connected: {database}")
                
                tables = data_loader.list_database_tables(db_name)
                if tables:
                    st.write("**Available tables:**")
                    for table in tables:
                        if st.button(f"Load {table}", key=f"load_{table}"):
                            try:
                                loaded_name = data_loader.load_database_table(db_name, table)
                                st.success(f"✅ Loaded: {loaded_name}")
                                schema_indexer.index_tables()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
            except Exception as e:
                st.error(f"Error connecting: {e}")
    
    elif db_type == "MySQL":
        host = st.text_input("Host", value="localhost", key="mysql_host")
        port = st.text_input("Port", value="3306", key="mysql_port")
        database = st.text_input("Database", key="mysql_database")
        user = st.text_input("User", key="mysql_user")
        password = st.text_input("Password", type="password", key="mysql_password")
        
        if st.button("Connect MySQL") and all([host, database, user, password]):
            try:
                connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
                db_name = data_loader.connect_database(connection_string, db_name=database)
                st.success(f"✅ Connected: {database}")
                
                tables = data_loader.list_database_tables(db_name)
                if tables:
                    st.write("**Available tables:**")
                    for table in tables:
                        if st.button(f"Load {table}", key=f"load_mysql_{table}"):
                            try:
                                loaded_name = data_loader.load_database_table(db_name, table)
                                st.success(f"✅ Loaded: {loaded_name}")
                                schema_indexer.index_tables()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
            except Exception as e:
                st.error(f"Error connecting: {e}")
                st.info("💡 Tip: Install MySQL driver with: pip install pymysql")
    
    elif db_type == "Custom":
        connection_string = st.text_input(
            "Connection String", 
            placeholder="postgresql://user:pass@host:port/db",
            help="Enter a SQLAlchemy connection string"
        )
        
        if st.button("Connect Custom") and connection_string:
            try:
                db_name = data_loader.connect_database(connection_string)
                st.success(f"✅ Connected: {db_name}")
                
                tables = data_loader.list_database_tables(db_name)
                if tables:
                    st.write("**Available tables:**")
                    for table in tables:
                        if st.button(f"Load {table}", key=f"load_custom_{table}"):
                            try:
                                loaded_name = data_loader.load_database_table(db_name, table)
                                st.success(f"✅ Loaded: {loaded_name}")
                                schema_indexer.index_tables()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
            except Exception as e:
                st.error(f"Error connecting: {e}")
    
    # Show loaded tables
    st.divider()
    loaded_tables = data_loader.get_all_tables()
    if loaded_tables:
        st.subheader("📋 Loaded Tables")
        for table in loaded_tables:
            st.write(f"• {table}")
            info = data_loader.get_table_info(table)
            st.caption(f"  {info['row_count']} rows, {len(info['columns'])} columns")

# Main area - Chat Interface
# Always get fresh list of tables
loaded_tables = data_loader.get_all_tables()

# Debug info
if len(loaded_tables) == 0:
    # Check if there's a pending upload
    if hasattr(st.session_state, 'last_uploaded_table'):
        # Try to reload
        try:
            # Force re-index
            schema_indexer.index_tables()
            loaded_tables = data_loader.get_all_tables()
        except:
            pass

# Debug: Show loaded tables status
if st.sidebar.checkbox("Show Debug Info", value=False):
    st.sidebar.write(f"Loaded tables: {loaded_tables}")
    st.sidebar.write(f"DataLoader tables: {data_loader.get_all_tables()}")

# Example questions
example_questions = [
    "What's the average sales per month?",
    "Which product performs best?",
    "Show me the top 10 customers by revenue",
    "What are the total sales by region?",
    "What columns are in the data?",
    "How many rows are in the dataset?",
    "What's the maximum sales value?",
    "Show me sales by category",
]

if not loaded_tables:
    st.warning("⚠️ No data loaded yet!")
    st.info("👈 **Please upload a CSV file in the sidebar** (left side) to get started!")
    st.markdown("")
    st.markdown("### 📋 Steps to use:")
    st.markdown("1. Look at the **sidebar on the left**")
    st.markdown("2. Under '📁 Load Data' → 'Upload CSV'")
    st.markdown("3. Click 'Browse files' and select your CSV file")
    st.markdown("4. Wait for the success message: '✅ Loaded: [filename]'")
    st.markdown("5. Then you can ask questions below!")
    st.markdown("")
    st.markdown("### 💡 Example Questions You Can Ask:")
    st.markdown("")
    # Display example questions in a more visible format
    for i, question in enumerate(example_questions, 1):
        st.markdown(f"{i}. **{question}**")
    st.markdown("")
    st.markdown("---")
    
    # Don't show chat input when no data - it's confusing
    st.info("💡 Upload a CSV file first, then the chat input will appear!")
else:
    # Show loaded tables info
    st.success(f"✅ **{len(loaded_tables)} table(s) loaded and ready for questions!**")
    st.markdown("")
    st.markdown(f"**Loaded tables:** {', '.join(loaded_tables)}")
    st.markdown("")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Show example questions - always visible, not in expander
    st.markdown("### 💡 Example Questions You Can Ask:")
    st.markdown("")
    for i, question in enumerate(example_questions, 1):
        st.markdown(f"{i}. **{question}**")
    st.markdown("")
    st.markdown("---")
    st.markdown("")
    
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Initialize agent and handle questions
    agent = None
    agent_error = None
    
    # Check for API key first
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.warning("⚠️ OPENAI_API_KEY not set! Agent will not work.")
        with st.expander("How to set OPENAI_API_KEY"):
            st.code("""
# In terminal (before running streamlit):
export OPENAI_API_KEY='your-api-key-here'
streamlit run app.py

# Or set it in the terminal where you run streamlit:
export OPENAI_API_KEY='your-api-key-here'
            """)
    else:
        try:
            agent = get_agent(data_loader, schema_indexer)
            st.success("✅ Agent initialized successfully!")
        except Exception as e:
            agent_error = str(e)
            st.error(f"❌ Error initializing agent: {e}")
            import traceback
            with st.expander("Error Details"):
                st.code(traceback.format_exc())
    
    # Streaming helper (only if agent is available)
    def stream_response(prompt: str, conversation_history: list = None):
        if agent is None:
            yield "Agent not initialized. Please set OPENAI_API_KEY environment variable."
            return
        
        async def agen():
            try:
                # Build conversation context from history
                # Include previous messages to maintain context
                context_prompt = prompt
                if conversation_history and len(conversation_history) > 0:
                    # Build context from previous messages (last 5 exchanges to avoid token limits)
                    recent_history = conversation_history[-10:]  # Last 10 messages (5 exchanges)
                    context_parts = []
                    for msg in recent_history:
                        role = msg.get("role", "")
                        content = msg.get("content", "")
                        if role == "user":
                            context_parts.append(f"User: {content}")
                        elif role == "assistant":
                            context_parts.append(f"Assistant: {content}")
                    
                    if context_parts:
                        context = "\n\nPrevious conversation:\n" + "\n".join(context_parts) + "\n\nCurrent question: " + prompt
                        context_prompt = context
                
                async with agent.run_stream(user_prompt=context_prompt) as result:
                    last_len = 0
                    full_text = ""
                    async for chunk in result.stream_output(debounce_by=0.01):
                        new_text = chunk[last_len:]
                        last_len = len(chunk)
                        full_text = chunk
                        if new_text:
                            yield new_text
                    st.session_state._last_response = full_text
                    
                    # Check for chart data in tool calls - try multiple methods
                    chart_found = False
                    try:
                        # Method 1: Check result's new_messages for tool calls
                        if hasattr(result, 'new_messages'):
                            for msg in result.new_messages():
                                # Check for tool calls in the message
                                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                                    for tool_call in msg.tool_calls:
                                        # Check if this is a create_chart call
                                        tool_name = getattr(tool_call, 'name', None) or getattr(tool_call, 'function_name', None) or str(tool_call)
                                        if 'create_chart' in str(tool_name).lower():
                                            # Get the result
                                            if hasattr(tool_call, 'result'):
                                                result_dict = tool_call.result
                                                if isinstance(result_dict, dict) and 'chart_type' in result_dict:
                                                    st.session_state._last_chart_params = result_dict
                                                    chart_found = True
                                        
                                        # Also check result directly for chart indicators
                                        if hasattr(tool_call, 'result') and isinstance(tool_call.result, dict):
                                            result_dict = tool_call.result
                                            if 'chart_type' in result_dict and 'table_name' in result_dict and result_dict.get('success'):
                                                st.session_state._last_chart_params = result_dict
                                                chart_found = True
                        
                        # Method 2: Check all_messages if available
                        if not chart_found and hasattr(result, 'all_messages'):
                            for msg in result.all_messages():
                                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                                    for tool_call in msg.tool_calls:
                                        tool_name = getattr(tool_call, 'name', None) or getattr(tool_call, 'function_name', None) or str(tool_call)
                                        if 'create_chart' in str(tool_name).lower():
                                            if hasattr(tool_call, 'result') and isinstance(tool_call.result, dict):
                                                result_dict = tool_call.result
                                                if 'chart_type' in result_dict:
                                                    st.session_state._last_chart_params = result_dict
                                                    chart_found = True
                        
                        # Method 3: Check result object directly for tool results
                        if not chart_found and hasattr(result, 'tool_results'):
                            for tool_result in result.tool_results:
                                if isinstance(tool_result, dict) and 'chart_type' in tool_result:
                                    st.session_state._last_chart_params = tool_result
                                    chart_found = True
                        
                        # Method 4: Check result.data if available (pydantic-ai stores tool results here)
                        if not chart_found and hasattr(result, 'data'):
                            result_data = result.data
                            if isinstance(result_data, dict) and 'chart_type' in result_data:
                                st.session_state._last_chart_params = result_data
                                chart_found = True
                    except Exception as e:
                        # Silently fail chart detection - don't break the response
                        pass
                    
                    # Store flag that we checked for charts
                    st.session_state._checked_for_chart = True
            except Exception as e:
                error_msg = f"Error in agent execution: {str(e)}"
                yield error_msg
                st.session_state._last_response = error_msg
                # Don't raise - let it return gracefully so user sees the error
                return
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        agen_obj = agen()
        
        try:
            while True:
                piece = loop.run_until_complete(agen_obj.__anext__())
                yield piece
        except StopAsyncIteration:
            return
        except Exception as e:
            error_msg = f"\n\n❌ Error: {str(e)}"
            yield error_msg
            # Ensure error is stored
            if not hasattr(st.session_state, '_last_response') or not st.session_state._last_response:
                st.session_state._last_response = error_msg
            return
    
    # IMPORTANT: Chat input MUST be at the end, outside all conditionals
    # This ensures it's always rendered when tables are loaded
    st.markdown("---")
    st.markdown("### 💬 Ask a Question")
    st.markdown("")
    
    # Chat input - This should always be visible at the bottom
    prompt = st.chat_input("💬 Ask a question about your data...")
    
    # Process the prompt if received
    if prompt:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()  # Rerun to process the message
    
    # Process any pending messages that need responses (from previous reruns)
    if st.session_state.messages:
        # Check if last message is user and hasn't been answered yet
        last_msg = st.session_state.messages[-1]
        if last_msg["role"] == "user":
            # Check if we need to generate a response (no assistant message after this user message)
            needs_response = True
            if len(st.session_state.messages) > 1:
                # Check if last message is already an assistant response
                if st.session_state.messages[-2]["role"] == "assistant":
                    needs_response = False
            
            # Also check if we're currently processing (to avoid duplicate responses)
            if "processing" in st.session_state and st.session_state.processing:
                needs_response = False
            
            if needs_response:
                # Mark as processing to prevent duplicate responses
                st.session_state.processing = True
                last_user_msg = last_msg["content"]
                
                # Generate response
                with st.chat_message("assistant"):
                    if agent is None:
                        st.error("❌ Agent not initialized!")
                        if not api_key:
                            st.error("OPENAI_API_KEY is not set!")
                        elif agent_error:
                            st.error(f"Error: {agent_error}")
                        st.info("💡 Please set your OPENAI_API_KEY environment variable and restart the app.")
                        response_text = "Agent not available. Please set OPENAI_API_KEY."
                    else:
                        try:
                            # Show spinner while thinking
                            with st.spinner("🤔 Thinking and analyzing your data..."):
                                # Pass conversation history for context
                                conversation_history = st.session_state.messages[:-1]  # All messages except the current one
                                # Stream the response with conversation history
                                response_text = st.write_stream(stream_response(last_user_msg, conversation_history))
                                
                                # Check if a chart was created and display it
                                chart_params = None
                                if hasattr(st.session_state, '_last_chart_params') and st.session_state._last_chart_params:
                                    chart_params = st.session_state._last_chart_params
                                
                                # Prepare variables for fallback detection
                                user_question = last_user_msg.lower()
                                response_lower = response_text.lower() if response_text else ""
                                
                                # Check if user asked for a chart OR if agent said it created one
                                chart_keywords = ['chart', 'graph', 'visualize', 'plot', 'bar chart', 'line chart', 'pie chart']
                                agent_created_chart = any(phrase in response_lower for phrase in [
                                    'chart has been created', 'chart displaying', 'created a chart', 
                                    'created successfully', 'has been created', 'chart for', 'chart of',
                                    'showing', 'displaying', 'you can see', 'you can now see', 'you can review',
                                    'i will create', 'now i will create', 'will create', 'creating a chart',
                                    'create a bar chart', 'create a chart', 'visualize'
                                ])
                                
                                # Also check for aggregation questions that would benefit from a chart
                                # But only create chart if user explicitly asked for one OR agent said it created one
                                aggregation_patterns = [
                                    'total', 'sum', 'average', 'mean', 'per', 'by', 'group by',
                                    'what are the', 'show me the', 'list the'
                                ]
                                is_aggregation_question = any(pattern in user_question for pattern in aggregation_patterns)
                                
                                # Only auto-create chart if user explicitly asked OR agent claimed to create one
                                # Also create if agent says "I will create" or "to visualize"
                                should_auto_create_chart = (
                                    any(keyword in user_question for keyword in chart_keywords) or 
                                    agent_created_chart or
                                    ('visualize' in response_lower and 'chart' in response_lower) or
                                    ('will create' in response_lower and 'chart' in response_lower)
                                )
                                
                                # Fallback: If user asked for a chart but tool wasn't called, try to create it automatically
                                if not chart_params:
                                    if should_auto_create_chart:
                                        # Try to extract chart parameters from the question and create chart directly
                                        chart_params = _try_extract_chart_params(user_question, data_loader, loaded_tables)
                                        
                                        # If we extracted params, also try calling the tool directly
                                        if not chart_params and loaded_tables:
                                            chart_params = _create_chart_from_question(user_question, data_loader, loaded_tables[0], schema_indexer)
                                        
                                        # If still no chart_params, force create one for common patterns
                                        if not chart_params and loaded_tables and ("total" in user_question or "by" in user_question):
                                            chart_params = _force_create_chart(user_question, data_loader, loaded_tables[0])
                                
                                if chart_params:
                                    st.markdown("### 📊 Chart:")
                                    try:
                                        # Verify chart_params has required fields
                                        if not chart_params.get('table_name'):
                                            st.error("Chart parameters missing table_name")
                                        elif not chart_params.get('x_column') or not chart_params.get('y_column'):
                                            st.error(f"Chart parameters missing columns. x_column: {chart_params.get('x_column')}, y_column: {chart_params.get('y_column')}")
                                        else:
                                            _recreate_and_display_chart(chart_params, data_loader)
                                    except Exception as e:
                                        st.error(f"Failed to display chart: {e}")
                                        import traceback
                                        with st.expander("Chart Display Error", expanded=True):
                                            st.code(traceback.format_exc())
                                        # Show chart params for debugging
                                        with st.expander("Chart Parameters (Debug)", expanded=False):
                                            st.json(chart_params)
                                    finally:
                                        if hasattr(st.session_state, '_last_chart_params'):
                                            del st.session_state._last_chart_params
                                elif agent_created_chart or ('chart' in user_question and 'bar' in user_question):
                                    # Agent claimed it created a chart but we don't have params - show error
                                    st.warning("⚠️ The agent mentioned creating a chart, but it wasn't detected. Trying to create it now...")
                                    # Last attempt to create chart
                                    if loaded_tables:
                                        final_chart = _force_create_chart(last_user_msg.lower(), data_loader, loaded_tables[0])
                                        if final_chart:
                                            st.markdown("### 📊 Chart:")
                                            _recreate_and_display_chart(final_chart, data_loader)
                                        else:
                                            st.error("Could not automatically create the chart. Please try rephrasing your request.")
                        except Exception as e:
                            st.error(f"❌ Error generating response: {e}")
                            import traceback
                            with st.expander("Error Details", expanded=True):
                                st.code(traceback.format_exc())
                            response_text = f"Sorry, I encountered an error: {str(e)}"
                        
                        # Always ensure we have a response
                        if not response_text or response_text.strip() == "":
                            response_text = "I'm sorry, I couldn't generate a response. Please try rephrasing your question."
                
                # Save full response to history - always save something
                final_text = getattr(st.session_state, "_last_response", None)
                if final_text and final_text.strip():
                    response_to_save = final_text
                elif response_text and response_text.strip():
                    response_to_save = response_text
                else:
                    # Fallback if no response was generated
                    response_to_save = "I'm sorry, I couldn't generate a response. Please try rephrasing your question."
                
                # Only append if we don't already have this response (avoid duplicates)
                if len(st.session_state.messages) == 0 or st.session_state.messages[-1]["role"] != "assistant":
                    st.session_state.messages.append({"role": "assistant", "content": response_to_save})
                elif st.session_state.messages[-1]["role"] == "assistant" and st.session_state.messages[-1]["content"] != response_to_save:
                    # Update the last assistant message if it's different
                    st.session_state.messages[-1]["content"] = response_to_save
                
                # Clear the last response from session state to avoid stale data
                if hasattr(st.session_state, '_last_response'):
                    del st.session_state._last_response
                
                # Clear processing flag
                if "processing" in st.session_state:
                    del st.session_state.processing
                
                st.rerun()

