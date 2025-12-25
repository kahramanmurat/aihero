"""
Index schema and sample rows for natural language querying.
"""
from typing import Dict, List, Any
from minsearch import Index
from data_loader import DataLoader


class SchemaIndexer:
    """Indexes table schemas and sample data for semantic search."""
    
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader
        self.index = Index(text_fields=["table_name", "columns", "description", "sample_data"])
        self.table_docs: List[Dict] = []
    
    def index_tables(self, table_names: List[str] = None) -> None:
        """
        Index schema and sample data for specified tables.
        
        Args:
            table_names: List of table names to index. If None, indexes all loaded tables.
        """
        if table_names is None:
            table_names = self.data_loader.get_all_tables()
        
        self.table_docs = []
        
        for table_name in table_names:
            try:
                info = self.data_loader.get_table_info(table_name)
                
                # Create a searchable document
                doc = {
                    "table_name": table_name,
                    "columns": ", ".join(info["columns"]),
                    "column_types": ", ".join([f"{col}: {dtype}" for col, dtype in info["dtypes"].items()]),
                    "description": self._generate_description(info),
                    "sample_data": self._format_sample_data(info["sample_rows"]),
                    "row_count": info["row_count"],
                    "info": info,  # Store full info for reference
                }
                
                self.table_docs.append(doc)
            except Exception as e:
                print(f"Error indexing table {table_name}: {e}")
        
        # Build the index
        if self.table_docs:
            self.index.fit(self.table_docs)
    
    def _generate_description(self, info: Dict) -> str:
        """Generate a natural language description of the table."""
        cols = info["columns"]
        row_count = info["row_count"]
        
        numeric_cols = [col for col, dtype in info["dtypes"].items() 
                       if 'int' in dtype or 'float' in dtype]
        text_cols = [col for col, dtype in info["dtypes"].items() 
                    if 'object' in dtype or 'string' in dtype]
        
        desc_parts = [
            f"Table with {row_count} rows",
            f"Columns: {', '.join(cols)}",
        ]
        
        if numeric_cols:
            desc_parts.append(f"Numeric columns: {', '.join(numeric_cols)}")
        if text_cols:
            desc_parts.append(f"Text columns: {', '.join(text_cols)}")
        
        return ". ".join(desc_parts)
    
    def _format_sample_data(self, sample_rows: List[Dict]) -> str:
        """Format sample rows as a readable string."""
        if not sample_rows:
            return "No sample data"
        
        # Format first few rows
        formatted = []
        for i, row in enumerate(sample_rows[:3], 1):
            row_str = ", ".join([f"{k}: {v}" for k, v in list(row.items())[:5]])
            formatted.append(f"Row {i}: {row_str}")
        
        return " | ".join(formatted)
    
    def search_tables(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Search for relevant tables based on a natural language query.
        
        Args:
            query: Natural language query
            num_results: Maximum number of results to return
            
        Returns:
            List of relevant table documents
        """
        results = self.index.search(query, num_results=num_results)
        return results
    
    def get_table_info(self, table_name: str) -> Dict:
        """Get full information for a specific table."""
        for doc in self.table_docs:
            if doc["table_name"] == table_name:
                return doc["info"]
        raise ValueError(f"Table '{table_name}' not found in index")

