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

### Core Application Files
- `data_loader.py` - Loads CSV files and connects to databases
- `schema_indexer.py` - Indexes table schemas and sample data
- `query_tools.py` - Tools for querying data
- `data_agent.py` - AI agent for natural language queries
- `app.py` - Streamlit web interface

### AI Agents Course Implementation
- `day1_ingest.py` - Day 1: Download and parse GitHub repositories
- `day1_test_frontmatter.py` - Test frontmatter parsing
- `day2_chunking.py` - Day 2: Chunking and intelligent processing
- `day2_test_chunking.py` - Test different chunking methods
- `day1_day2_integration.py` - Complete pipeline: Download + Chunk
- `day4_agent.py` - Day 4: Agents and tools with Pydantic AI
- `day4_test_agent.py` - Test agent with GitHub repository data
- `day4_comparison.py` - Compare LLM vs. Agent (with/without tools)
- `day5_evaluation.py` - Day 5: Evaluation system with logging and LLM-as-judge
- `day5_test_evaluation.py` - Complete evaluation workflow
- `day5_analyze_logs.py` - Analyze existing log files
- `day6_ingest.py` - Day 6: Clean ingestion module (Days 1-3 combined)
- `day6_search_tools.py` - Day 6: Search tool class
- `day6_search_agent.py` - Day 6: Agent creation
- `day6_logs.py` - Day 6: Logging module
- `day6_main.py` - Day 6: Command-line interface
- `day6_app.py` - Day 6: Streamlit web interface

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

## AI Agents Course (Day 1 & Day 2)

This project also includes implementations from the AI Agents crash course:

### Day 1: GitHub Repository Ingestion

Download and parse markdown files from GitHub repositories:

```bash
python day1_ingest.py
```

Or test frontmatter parsing:
```bash
python day1_test_frontmatter.py
```

### Day 2: Document Chunking

Split large documents into smaller chunks for AI processing:

```bash
python day2_chunking.py
```

Or test chunking on real data:
```bash
python day2_test_chunking.py
```

Or run the complete pipeline (Day 1 + Day 2):
```bash
python day1_day2_integration.py
```

**Chunking Methods:**
- Sliding window chunking (with overlap)
- Section-based chunking (by markdown headers)
- Paragraph-based chunking
- Intelligent LLM-based chunking (requires OPENAI_API_KEY)

### Day 4: Agents and Tools

Create AI agents that can use tools (functions) to answer questions:

```bash
# Requires OPENAI_API_KEY
export OPENAI_API_KEY='your-api-key'
python day4_agent.py
```

Or test with real repository data:
```bash
python day4_test_agent.py
```

Or compare LLM vs. Agent:
```bash
python day4_comparison.py
```

**What You'll Learn:**
- What makes an AI system "agentic" (tools!)
- Function calling with OpenAI API
- Using Pydantic AI to simplify agent development
- Creating agents that can search and retrieve information
- The difference between LLMs and agents

### Day 5: Evaluation

Build logging system and automated evaluation using LLM as a judge:

```bash
# Requires OPENAI_API_KEY
export OPENAI_API_KEY='your-api-key'
python day5_evaluation.py
```

Or run complete evaluation workflow:
```bash
python day5_test_evaluation.py
```

Or analyze existing logs:
```bash
python day5_analyze_logs.py [agent_name] [source]
```

**What You'll Learn:**
- Logging agent interactions to JSON files
- Using LLM as a judge for automated evaluation
- Generating test questions with AI
- Calculating performance metrics
- Structured evaluation with Pydantic models
- Comparing different agent versions
- Making data-driven decisions about improvements

**Evaluation Features:**
- Interaction logging (all messages, tool calls, responses)
- LLM-as-judge evaluation with structured output
- Test question generation
- Performance metrics (pass rates, summary statistics)
- CSV export for detailed analysis

### Day 6: Publish Your Agent

Clean up code and deploy to the web:

```bash
# Command-line interface
python day6_main.py

# Streamlit web interface
streamlit run day6_app.py
```

**Modular Structure:**
- `day6_ingest.py` - Complete ingestion pipeline (download, chunk, index)
- `day6_search_tools.py` - Search tool class
- `day6_search_agent.py` - Agent creation with configurable prompts
- `day6_logs.py` - Logging system
- `day6_main.py` - CLI interface
- `day6_app.py` - Streamlit web UI with streaming responses

**What You'll Learn:**
- Organizing code into clean, modular files
- Creating Streamlit web interfaces
- Streaming agent responses for better UX
- Deploying to Streamlit Cloud
- Configuring environment variables and secrets

**Deployment:**
1. Export dependencies: `uv export --no-dev > requirements.txt`
2. Push code to GitHub
3. Deploy on Streamlit Cloud
4. Configure `OPENAI_API_KEY` in secrets

See `day6_deploy.md` for detailed deployment instructions.

## Requirements

- Python >= 3.12
- pydantic-ai
- streamlit
- pandas
- sqlalchemy
- openai
- minsearch
- python-frontmatter (for Day 1)
- requests (for Day 1)
- tqdm (for Day 2)

