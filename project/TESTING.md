# Testing Guide for AI Data Explorer

This guide explains how to test the AI Data Explorer project.

## Prerequisites

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set OpenAI API key** (for agent testing):
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

## Quick Test

Run the automated test script:

```bash
python test.py
```

This will test:
- ✅ DataLoader (CSV loading)
- ✅ SchemaIndexer (schema indexing and search)
- ✅ Data Agent (natural language queries - requires API key)

## Manual Testing

### 1. Test DataLoader

```python
from data_loader import DataLoader

loader = DataLoader()
table_name = loader.load_csv("test_data.csv")
info = loader.get_table_info(table_name)
print(info)
```

### 2. Test SchemaIndexer

```python
from data_loader import DataLoader
from schema_indexer import SchemaIndexer

loader = DataLoader()
loader.load_csv("test_data.csv")

indexer = SchemaIndexer(loader)
indexer.index_tables()

# Search for relevant tables
results = indexer.search_tables("sales data")
print(results)
```

### 3. Test Query Tools

```python
from data_loader import DataLoader
from schema_indexer import SchemaIndexer
from query_tools import QueryTool

loader = DataLoader()
loader.load_csv("test_data.csv")

indexer = SchemaIndexer(loader)
indexer.index_tables()

tool = QueryTool(loader, indexer)

# Query data
result = tool.query_data(
    table_name="test_data",
    aggregation="mean",
    columns=["sales"]
)
print(result)
```

### 4. Test Agent (Requires API Key)

```python
import asyncio
from data_loader import DataLoader
from schema_indexer import SchemaIndexer
from data_agent import init_agent

async def test():
    loader = DataLoader()
    loader.load_csv("test_data.csv")
    
    indexer = SchemaIndexer(loader)
    indexer.index_tables()
    
    agent = init_agent(loader, indexer)
    
    result = await agent.run("What's the average sales?")
    print(result.data)

asyncio.run(test())
```

## Test with Streamlit App

1. **Start the app:**
   ```bash
   streamlit run app.py
   ```

2. **Test CSV upload:**
   - Use the sidebar to upload `test_data.csv`
   - Verify it loads successfully

3. **Test questions:**
   - "What tables are available?"
   - "What's the average sales?"
   - "Which product has the highest sales?"
   - "Show me sales by region"

## Test Data

The project includes `test_data.csv` with sample sales data:
- 15 rows of sales data
- Columns: date, product, category, sales, quantity, region
- Perfect for testing queries

## Expected Test Results

### DataLoader Test
- ✅ Should load CSV successfully
- ✅ Should return table info with columns, row count, sample rows

### SchemaIndexer Test
- ✅ Should index tables
- ✅ Should find relevant tables when searching

### Agent Test (with API key)
- ✅ Should answer "What tables are available?" with table names
- ✅ Should answer questions about the data

## Troubleshooting

### Import Errors
- Make sure you're in the project directory
- Install all dependencies: `pip install -r requirements.txt`

### API Key Issues
- Set `OPENAI_API_KEY` environment variable
- Agent tests will be skipped if not set

### CSV Not Found
- Make sure `test_data.csv` is in the project directory
- Or provide your own CSV file path

## Example Test Output

```
🧪 Starting AI Data Explorer Tests

============================================================
Testing DataLoader...
============================================================
✅ Loaded CSV: test_data
✅ Table info retrieved:
   - Columns: ['date', 'product', 'category', 'sales', 'quantity', 'region']
   - Rows: 15
   - Sample row: {'date': '2024-01-15', 'product': 'Widget A', ...}

============================================================
Testing SchemaIndexer...
============================================================
✅ Tables indexed
✅ Search results: 1 tables found
   - Found table: test_data

============================================================
Testing Data Agent...
============================================================
✅ Agent initialized

🤔 Question: What tables are available?
💬 Answer: The available tables are: test_data
✅ Question answered successfully

============================================================
Test Summary
============================================================
DataLoader: ✅ PASSED
SchemaIndexer: ✅ PASSED
Agent: ✅ PASSED

🎉 All tests passed!
```

