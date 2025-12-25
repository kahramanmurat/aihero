# Database Connection Guide

This guide shows you how to connect to various databases in the AI Data Explorer.

## Connection Methods

### 1. Via Streamlit UI (Easiest)

1. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. In the sidebar, go to **"Connect Database"**
3. Select your database type and enter connection details
4. Click "Connect" and then load tables

### 2. Programmatically (Python)

```python
from data_loader import DataLoader
from schema_indexer import SchemaIndexer
from data_agent import init_agent

# Initialize
loader = DataLoader()
indexer = SchemaIndexer(loader)

# Connect to database
# ... (see examples below)

# Index schemas
indexer.index_tables()

# Create agent
agent = init_agent(loader, indexer)
```

## Database Types

### SQLite

**Streamlit UI:**
- Select "SQLite" from dropdown
- Enter database path (e.g., `data.db` or `/path/to/database.db`)
- Click "Connect SQLite"

**Programmatic:**
```python
# Connect to SQLite database
connection_string = "sqlite:///data.db"  # Relative path
# or
connection_string = "sqlite:////absolute/path/to/data.db"  # Absolute path

db_name = loader.connect_database(connection_string)

# List available tables
tables = loader.list_database_tables(db_name)
print(f"Available tables: {tables}")

# Load a table
loaded_name = loader.load_database_table(db_name, "table_name")
```

### PostgreSQL

**Streamlit UI:**
- Select "PostgreSQL" from dropdown
- Enter:
  - Host: `localhost` (or your server)
  - Port: `5432` (default)
  - Database: database name
  - User: your username
  - Password: your password
- Click "Connect PostgreSQL"

**Programmatic:**
```python
# Connect to PostgreSQL
connection_string = "postgresql://username:password@localhost:5432/database_name"

db_name = loader.connect_database(connection_string, db_name="mydb")

# List and load tables
tables = loader.list_database_tables(db_name)
for table in tables:
    loader.load_database_table(db_name, table)
```

**With SSL:**
```python
connection_string = "postgresql://user:pass@host:5432/db?sslmode=require"
```

### MySQL

**Streamlit UI:**
- Currently not in UI, but you can use "Custom" option
- Enter connection string manually

**Programmatic:**
```python
# Connect to MySQL
connection_string = "mysql+pymysql://username:password@localhost:3306/database_name"

db_name = loader.connect_database(connection_string, db_name="mydb")
tables = loader.list_database_tables(db_name)
```

**Note:** You may need to install MySQL driver:
```bash
pip install pymysql
# or
pip install mysqlclient
```

### Custom Database (Any SQLAlchemy-supported)

**Streamlit UI:**
- Select "Custom" from dropdown
- Enter full SQLAlchemy connection string

**Programmatic:**
```python
# Any SQLAlchemy connection string works
connection_string = "mssql+pyodbc://user:pass@server/db?driver=ODBC+Driver+17+for+SQL+Server"

db_name = loader.connect_database(connection_string, db_name="custom_db")
```

## Complete Example

```python
import asyncio
from data_loader import DataLoader
from schema_indexer import SchemaIndexer
from data_agent import init_agent

async def main():
    # Initialize
    loader = DataLoader()
    
    # Connect to database (SQLite example)
    connection_string = "sqlite:///example.db"
    db_name = loader.connect_database(connection_string)
    
    # List available tables
    tables = loader.list_database_tables(db_name)
    print(f"Available tables: {tables}")
    
    # Load a table (loads first 1000 rows by default)
    if tables:
        loaded_name = loader.load_database_table(db_name, tables[0])
        print(f"Loaded table: {loaded_name}")
    
    # Index schemas
    indexer = SchemaIndexer(loader)
    indexer.index_tables()
    
    # Create agent and ask questions
    agent = init_agent(loader, indexer)
    
    result = await agent.run("What tables are available?")
    print(result.data)

if __name__ == "__main__":
    asyncio.run(main())
```

## Connection String Formats

### SQLite
- `sqlite:///relative/path.db`
- `sqlite:////absolute/path.db`

### PostgreSQL
- `postgresql://user:password@host:port/database`
- `postgresql+psycopg2://user:password@host:port/database`

### MySQL
- `mysql+pymysql://user:password@host:port/database`
- `mysql+mysqlconnector://user:password@host:port/database`

### SQL Server
- `mssql+pyodbc://user:password@server/database?driver=ODBC+Driver+17+for+SQL+Server`

### Oracle
- `oracle+cx_oracle://user:password@host:port/database`

## Loading Tables

After connecting, you can load tables:

```python
# Load with default limit (1000 rows)
loaded_name = loader.load_database_table(db_name, "table_name")

# The loaded table will be named: "db_name.table_name"
# You can query it like any other table
```

**Note:** Only the first 1000 rows are loaded by default for preview. The agent can still query the full database when needed.

## Troubleshooting

### Connection Errors

1. **SQLite file not found:**
   - Use absolute path: `sqlite:////Users/name/data.db`
   - Check file exists and has read permissions

2. **PostgreSQL connection refused:**
   - Check if PostgreSQL is running
   - Verify host, port, and firewall settings
   - Check username/password

3. **MySQL driver missing:**
   ```bash
   pip install pymysql
   ```

4. **SSL/Connection issues:**
   - Add SSL parameters to connection string
   - Check network connectivity
   - Verify credentials

### Testing Connection

```python
from data_loader import DataLoader

loader = DataLoader()
try:
    db_name = loader.connect_database("your_connection_string")
    tables = loader.list_database_tables(db_name)
    print(f"✅ Connected! Found {len(tables)} tables")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

## Security Notes

- **Never commit connection strings with passwords to version control**
- Use environment variables for sensitive credentials:
  ```python
  import os
  connection_string = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@host/db"
  ```
- Consider using connection pooling for production
- Use SSL/TLS for remote database connections

