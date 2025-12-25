"""
Streamlit app for AI Data Explorer.
"""
import streamlit as st
import asyncio
import pandas as pd
from data_loader import DataLoader
from schema_indexer import SchemaIndexer
from data_agent import init_agent
import os


# --- Initialization ---
@st.cache_resource
def init_data_explorer():
    """Initialize the data explorer with empty loader and indexer."""
    data_loader = DataLoader()
    schema_indexer = SchemaIndexer(data_loader)
    return data_loader, schema_indexer


def get_agent(data_loader, schema_indexer):
    """Get or create the agent."""
    # Use session state to cache agent, but recreate when tables change
    tables_key = str(sorted(data_loader.get_all_tables()))
    
    if "agent" not in st.session_state or st.session_state.get("agent_tables_key") != tables_key:
        st.session_state.agent = init_agent(data_loader, schema_indexer)
        st.session_state.agent_tables_key = tables_key
    
    return st.session_state.agent


# Initialize
data_loader, schema_indexer = init_data_explorer()

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
        # Save uploaded file temporarily
        temp_path = f"/tmp/{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        try:
            table_name = data_loader.load_csv(temp_path)
            st.success(f"✅ Loaded: {table_name}")
            
            # Re-index tables
            schema_indexer.index_tables()
            st.rerun()
        except Exception as e:
            st.error(f"Error loading CSV: {e}")
    
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

# Main area
if not data_loader.get_all_tables():
    st.info("👈 Upload a CSV file or connect to a database to get started!")
    st.markdown("""
    ### Example Questions:
    - "What's the average sales per month?"
    - "Which product performs best?"
    - "Show me the top 10 customers by revenue"
    - "What are the total sales by region?"
    """)
else:
    # Initialize agent
    agent = get_agent(data_loader, schema_indexer)
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Streaming helper
    def stream_response(prompt: str):
        async def agen():
            async with agent.run_stream(user_prompt=prompt) as result:
                last_len = 0
                full_text = ""
                async for chunk in result.stream_output(debounce_by=0.01):
                    new_text = chunk[last_len:]
                    last_len = len(chunk)
                    full_text = chunk
                    if new_text:
                        yield new_text
                st.session_state._last_response = full_text
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        agen_obj = agen()
        
        try:
            while True:
                piece = loop.run_until_complete(agen_obj.__anext__())
                yield piece
        except StopAsyncIteration:
            return
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your data..."):
        # User message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Assistant message (streamed)
        with st.chat_message("assistant"):
            response_text = st.write_stream(stream_response(prompt))
        
        # Save full response to history
        final_text = getattr(st.session_state, "_last_response", response_text)
        st.session_state.messages.append({"role": "assistant", "content": final_text})

