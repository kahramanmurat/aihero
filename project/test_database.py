"""
Test script for database connections.
This demonstrates how to connect to different database types.
"""
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from data_loader import DataLoader
from schema_indexer import SchemaIndexer


def test_sqlite_connection():
    """Test SQLite database connection."""
    print("=" * 60)
    print("Testing SQLite Connection")
    print("=" * 60)
    
    loader = DataLoader()
    
    # Create a simple SQLite database for testing
    import sqlite3
    test_db_path = "test_example.db"
    
    # Create test database with sample data
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    
    # Create a test table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY,
            product TEXT,
            amount REAL,
            date TEXT
        )
    """)
    
    # Insert sample data
    sample_data = [
        ("Widget A", 100.50, "2024-01-15"),
        ("Widget B", 200.75, "2024-01-16"),
        ("Widget C", 150.25, "2024-01-17"),
    ]
    
    cursor.executemany("INSERT INTO sales (product, amount, date) VALUES (?, ?, ?)", sample_data)
    conn.commit()
    conn.close()
    
    print(f"✅ Created test database: {test_db_path}")
    
    # Connect using DataLoader
    try:
        connection_string = f"sqlite:///{test_db_path}"
        db_name = loader.connect_database(connection_string)
        print(f"✅ Connected to database: {db_name}")
        
        # List tables
        tables = loader.list_database_tables(db_name)
        print(f"✅ Found tables: {tables}")
        
        # Load a table
        if tables:
            loaded_name = loader.load_database_table(db_name, tables[0])
            print(f"✅ Loaded table: {loaded_name}")
            
            # Get table info
            info = loader.get_table_info(loaded_name)
            print(f"✅ Table info:")
            print(f"   - Columns: {info['columns']}")
            print(f"   - Rows: {info['row_count']}")
            print(f"   - Sample row: {info['sample_rows'][0]}")
        
        # Test indexing
        indexer = SchemaIndexer(loader)
        indexer.index_tables()
        print("✅ Schema indexed successfully")
        
        # Clean up
        os.remove(test_db_path)
        print(f"✅ Cleaned up test database")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        # Clean up on error
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        return False


def test_postgresql_connection():
    """Test PostgreSQL connection (if available)."""
    print("\n" + "=" * 60)
    print("Testing PostgreSQL Connection")
    print("=" * 60)
    
    # Check if connection details are provided
    pg_host = os.getenv("PG_HOST", "localhost")
    pg_port = os.getenv("PG_PORT", "5432")
    pg_db = os.getenv("PG_DATABASE")
    pg_user = os.getenv("PG_USER")
    pg_password = os.getenv("PG_PASSWORD")
    
    if not all([pg_db, pg_user, pg_password]):
        print("⏭️  Skipping PostgreSQL test - environment variables not set")
        print("   Set: PG_HOST, PG_PORT, PG_DATABASE, PG_USER, PG_PASSWORD")
        return None
    
    loader = DataLoader()
    
    try:
        connection_string = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
        db_name = loader.connect_database(connection_string, db_name=pg_db)
        print(f"✅ Connected to PostgreSQL: {db_name}")
        
        tables = loader.list_database_tables(db_name)
        print(f"✅ Found {len(tables)} tables")
        
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False


def test_mysql_connection():
    """Test MySQL connection (if available)."""
    print("\n" + "=" * 60)
    print("Testing MySQL Connection")
    print("=" * 60)
    
    mysql_host = os.getenv("MYSQL_HOST", "localhost")
    mysql_port = os.getenv("MYSQL_PORT", "3306")
    mysql_db = os.getenv("MYSQL_DATABASE")
    mysql_user = os.getenv("MYSQL_USER")
    mysql_password = os.getenv("MYSQL_PASSWORD")
    
    if not all([mysql_db, mysql_user, mysql_password]):
        print("⏭️  Skipping MySQL test - environment variables not set")
        print("   Set: MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD")
        return None
    
    loader = DataLoader()
    
    try:
        # Try pymysql first
        try:
            connection_string = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}"
        except:
            connection_string = f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}"
        
        db_name = loader.connect_database(connection_string, db_name=mysql_db)
        print(f"✅ Connected to MySQL: {db_name}")
        
        tables = loader.list_database_tables(db_name)
        print(f"✅ Found {len(tables)} tables")
        
        return True
        
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        print("   Note: You may need to install: pip install pymysql")
        return False


def main():
    """Run all database connection tests."""
    print("\n🧪 Database Connection Tests\n")
    
    results = []
    
    # Test SQLite (always works)
    results.append(("SQLite", test_sqlite_connection()))
    
    # Test PostgreSQL (if configured)
    results.append(("PostgreSQL", test_postgresql_connection()))
    
    # Test MySQL (if configured)
    results.append(("MySQL", test_mysql_connection()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, result in results:
        if result is None:
            status = "⏭️  SKIPPED"
        elif result:
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"
        print(f"{name}: {status}")
    
    passed = [r for r in results if r[1] is True]
    if passed:
        print(f"\n✅ {len(passed)} connection test(s) passed!")
    else:
        print("\n⚠️  No connection tests passed")


if __name__ == "__main__":
    main()

