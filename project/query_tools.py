"""
Tools for querying data using pandas operations.
"""
from typing import Any, Dict, List
import pandas as pd
from data_loader import DataLoader
from schema_indexer import SchemaIndexer


class QueryTool:
    """Tool for executing queries on loaded data."""
    
    def __init__(self, data_loader: DataLoader, schema_indexer: SchemaIndexer):
        self.data_loader = data_loader
        self.schema_indexer = schema_indexer
    
    def query_data(
        self, 
        table_name: str, 
        operation: str,
        columns: List[str] = None,
        filters: Dict[str, Any] = None,
        aggregation: str = None,
        group_by: List[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Execute a query on a table.
        
        Args:
            table_name: Name of the table to query
            operation: Operation to perform ('select', 'aggregate', 'filter', etc.)
            columns: List of columns to select
            filters: Dictionary of column: value filters
            aggregation: Aggregation function ('mean', 'sum', 'count', 'max', 'min')
            group_by: Columns to group by
            limit: Maximum number of rows to return
            
        Returns:
            Dictionary with results and metadata
        """
        if table_name not in self.data_loader.dataframes:
            return {
                "error": f"Table '{table_name}' not found",
                "available_tables": self.data_loader.get_all_tables()
            }
        
        df = self.data_loader.dataframes[table_name]
        original_count = len(df)
        
        try:
            # Apply filters
            if filters:
                for col, value in filters.items():
                    if col in df.columns:
                        if isinstance(value, dict):
                            # Support operators like {'>': 100}
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
            
            # Select columns
            if columns:
                available_cols = [col for col in columns if col in df.columns]
                if available_cols:
                    df = df[available_cols]
            
            # Apply aggregation
            if aggregation:
                if group_by:
                    group_cols = [col for col in group_by if col in df.columns]
                    if group_cols:
                        if aggregation == 'mean':
                            result = df.groupby(group_cols).mean()
                        elif aggregation == 'sum':
                            result = df.groupby(group_cols).sum()
                        elif aggregation == 'count':
                            result = df.groupby(group_cols).size().reset_index(name='count')
                        elif aggregation == 'max':
                            result = df.groupby(group_cols).max()
                        elif aggregation == 'min':
                            result = df.groupby(group_cols).min()
                        else:
                            result = df
                    else:
                        result = df
                else:
                    # Aggregate entire dataframe
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    if len(numeric_cols) > 0:
                        if aggregation == 'mean':
                            result = df[numeric_cols].mean()
                        elif aggregation == 'sum':
                            result = df[numeric_cols].sum()
                        elif aggregation == 'count':
                            result = pd.Series({'count': len(df)})
                        elif aggregation == 'max':
                            result = df[numeric_cols].max()
                        elif aggregation == 'min':
                            result = df[numeric_cols].min()
                        else:
                            result = df
                    else:
                        result = df
            else:
                result = df
            
            # Convert to records for JSON serialization
            if isinstance(result, pd.Series):
                result_dict = result.to_dict()
            elif isinstance(result, pd.DataFrame):
                result_dict = result.head(limit).to_dict('records')
            else:
                result_dict = {"result": str(result)}
            
            return {
                "success": True,
                "table_name": table_name,
                "result": result_dict,
                "row_count": len(result) if isinstance(result, pd.DataFrame) else 1,
                "original_row_count": original_count,
                "columns": list(result.columns) if isinstance(result, pd.DataFrame) else list(result.index) if isinstance(result, pd.Series) else []
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "table_name": table_name
            }
    
    def get_table_schema(self, table_name: str) -> Dict:
        """Get schema information for a table."""
        try:
            return self.schema_indexer.get_table_info(table_name)
        except Exception as e:
            return {"error": str(e)}
    
    def list_tables(self) -> List[str]:
        """List all available tables."""
        return self.data_loader.get_all_tables()

