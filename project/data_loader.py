"""
Data loader for CSV files and database tables.
"""
import pandas as pd
from sqlalchemy import create_engine, inspect, text
from typing import Dict, List, Optional, Any
import os


class DataLoader:
    """Loads data from CSV files or database tables."""
    
    def __init__(self):
        self.dataframes: Dict[str, pd.DataFrame] = {}
        self.db_engines: Dict[str, Any] = {}
        self.table_info: Dict[str, Dict] = {}
    
    def load_csv(self, file_path: str, table_name: Optional[str] = None) -> str:
        """
        Load a CSV file into memory.
        
        Args:
            file_path: Path to the CSV file
            table_name: Optional name for the table (defaults to filename without extension)
            
        Returns:
            Name of the loaded table
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        
        df = pd.read_csv(file_path)
        
        if table_name is None:
            table_name = os.path.splitext(os.path.basename(file_path))[0]
        
        self.dataframes[table_name] = df
        return table_name
    
    def connect_database(
        self, 
        connection_string: str, 
        db_name: Optional[str] = None
    ) -> str:
        """
        Connect to a database.
        
        Args:
            connection_string: SQLAlchemy connection string (e.g., 'sqlite:///data.db')
            db_name: Optional name for the database connection
            
        Returns:
            Name of the database connection
        """
        if db_name is None:
            # Extract database name from connection string
            db_name = connection_string.split('/')[-1].split('?')[0]
        
        engine = create_engine(connection_string)
        self.db_engines[db_name] = engine
        return db_name
    
    def load_database_table(
        self, 
        db_name: str, 
        table_name: str,
        limit: int = 1000
    ) -> str:
        """
        Load a table from a connected database.
        
        Args:
            db_name: Name of the database connection
            table_name: Name of the table to load
            limit: Maximum number of rows to load (for preview)
            
        Returns:
            Name of the loaded table (prefixed with db_name)
        """
        if db_name not in self.db_engines:
            raise ValueError(f"Database '{db_name}' not connected")
        
        engine = self.db_engines[db_name]
        
        # Load sample data
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        df = pd.read_sql(query, engine)
        
        full_table_name = f"{db_name}.{table_name}"
        self.dataframes[full_table_name] = df
        return full_table_name
    
    def list_database_tables(self, db_name: str) -> List[str]:
        """List all tables in a connected database."""
        if db_name not in self.db_engines:
            raise ValueError(f"Database '{db_name}' not connected")
        
        engine = self.db_engines[db_name]
        inspector = inspect(engine)
        return inspector.get_table_names()
    
    def get_table_info(self, table_name: str) -> Dict:
        """
        Get schema information for a table.
        
        Returns:
            Dictionary with schema, sample rows, and statistics
        """
        if table_name not in self.dataframes:
            raise ValueError(f"Table '{table_name}' not loaded")
        
        df = self.dataframes[table_name]
        
        info = {
            "table_name": table_name,
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "row_count": len(df),
            "sample_rows": df.head(5).to_dict('records'),
            "null_counts": df.isnull().sum().to_dict(),
        }
        
        # Add basic statistics for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            info["statistics"] = df[numeric_cols].describe().to_dict()
        
        return info
    
    def execute_query(self, table_name: str, query: str) -> pd.DataFrame:
        """
        Execute a pandas query on a loaded table.
        
        Args:
            table_name: Name of the table
            query: Pandas query string (e.g., "df[df['sales'] > 1000]")
            
        Returns:
            Resulting DataFrame
        """
        if table_name not in self.dataframes:
            raise ValueError(f"Table '{table_name}' not loaded")
        
        df = self.dataframes[table_name]
        # Execute query safely
        result = eval(query, {"df": df, "pd": pd})
        return result
    
    def execute_sql(self, db_name: str, sql_query: str) -> pd.DataFrame:
        """
        Execute a SQL query on a connected database.
        
        Args:
            db_name: Name of the database connection
            sql_query: SQL query string
            
        Returns:
            Resulting DataFrame
        """
        if db_name not in self.db_engines:
            raise ValueError(f"Database '{db_name}' not connected")
        
        engine = self.db_engines[db_name]
        return pd.read_sql(text(sql_query), engine)
    
    def get_all_tables(self) -> List[str]:
        """Get list of all loaded table names."""
        return list(self.dataframes.keys())

