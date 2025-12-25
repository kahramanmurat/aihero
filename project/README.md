# AI Data Explorer

A conversational data analyst that lets you ask natural language questions about CSV files and databases.

## Features

- 📊 **Load CSV files** - Upload and analyze CSV files
- 🗄️ **Connect to databases** - Support for SQLite, PostgreSQL, MySQL, and more
- 🔍 **Schema indexing** - Automatically indexes table schemas and sample rows
- 💬 **Natural language queries** - Ask questions like:
  - "What's the average sales per month?"
  - "Which product performs best?"
  - "Show me the top 10 customers by revenue"
  - "What are the total sales by region?"

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

Or using uv:
```bash
uv pip install -r requirements.txt
```

## Usage

### Run the Streamlit app:

```bash
streamlit run app.py
```

### Using the app:

1. **Load Data:**
   - Upload a CSV file using the sidebar
   - Or connect to a database (SQLite, PostgreSQL, MySQL)
   - Load tables from connected databases

2. **Ask Questions:**
   - Type natural language questions in the chat
   - The AI will:
     - Find relevant tables
     - Understand the schema
     - Execute queries
     - Return answers

### Example Usage (Programmatic):

```python
from data_loader import DataLoader
from schema_indexer import SchemaIndexer
from data_agent import init_agent

# Load data
loader = DataLoader()
loader.load_csv("sales.csv")

# Index schemas
indexer = SchemaIndexer(loader)
indexer.index_tables()

# Create agent
agent = init_agent(loader, indexer)

# Ask questions
result = agent.run_sync("What's the average sales per month?")
print(result.data)
```

## Project Structure

- `data_loader.py` - Loads CSV files and connects to databases
- `schema_indexer.py` - Indexes table schemas and sample data
- `query_tools.py` - Tools for querying data
- `data_agent.py` - AI agent for natural language queries
- `app.py` - Streamlit web interface

## Supported Operations

The agent can handle:
- **Aggregations**: mean, sum, count, max, min
- **Filtering**: Filter by column values
- **Grouping**: Group by columns
- **Selection**: Select specific columns
- **Sorting**: Order results

## Database Support

- SQLite
- PostgreSQL
- MySQL
- Any database supported by SQLAlchemy

## Database Connections

The project supports connecting to various databases:

- **SQLite** - Local file-based database
- **PostgreSQL** - Popular open-source database
- **MySQL** - Widely-used relational database
- **Custom** - Any SQLAlchemy-supported database

See [DATABASE_CONNECTION.md](DATABASE_CONNECTION.md) for detailed connection instructions.

### Quick Example (SQLite)

```python
from data_loader import DataLoader

loader = DataLoader()
loader.connect_database("sqlite:///data.db")
tables = loader.list_database_tables("data")
loader.load_database_table("data", tables[0])
```

## Testing

### Quick Test

Run the automated test script:

```bash
python test.py
```

This tests all components:
- ✅ DataLoader (CSV loading)
- ✅ SchemaIndexer (schema indexing)
- ✅ Data Agent (requires `OPENAI_API_KEY`)

### Test with Sample Data

The project includes `test_data.csv` with sample sales data. You can use it to test:

1. **Automated tests:**
   ```bash
   python test.py
   ```

2. **Streamlit app:**
   ```bash
   streamlit run app.py
   # Then upload test_data.csv in the sidebar
   ```

3. **Try these questions:**
   - "What's the average sales?"
   - "Which product has the highest sales?"
   - "Show me sales by region"
   - "What's the total quantity sold?"

See [TESTING.md](TESTING.md) for detailed testing instructions.

## Requirements

- Python >= 3.12
- pydantic-ai
- streamlit
- pandas
- sqlalchemy
- openai
- minsearch

