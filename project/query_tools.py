"""
Tools for querying data using pandas operations.
"""
from typing import Any, Dict, List, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import base64
from io import StringIO
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
    
    def create_chart(
        self,
        table_name: str,
        chart_type: str = "bar",
        x_column: Optional[str] = None,
        y_column: Optional[str] = None,
        group_by: Optional[str] = None,
        aggregation: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a chart from table data.
        
        Args:
            table_name: Name of the table
            chart_type: Type of chart ('bar', 'line', 'scatter', 'pie', 'histogram')
            x_column: Column for x-axis
            y_column: Column for y-axis (required for bar, line, scatter)
            group_by: Column to group by
            aggregation: Aggregation function if grouping ('sum', 'mean', 'count', 'max', 'min')
            filters: Dictionary of filters to apply
            title: Chart title
            
        Returns:
            Dictionary with chart HTML and metadata
        """
        if table_name not in self.data_loader.dataframes:
            return {
                "error": f"Table '{table_name}' not found",
                "available_tables": self.data_loader.get_all_tables()
            }
        
        df = self.data_loader.dataframes[table_name].copy()
        
        try:
            # Apply filters
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
                        df_grouped = df.groupby(group_by)[y_column].sum().reset_index() if y_column else df.groupby(group_by).sum().reset_index()
                    elif aggregation == 'mean':
                        df_grouped = df.groupby(group_by)[y_column].mean().reset_index() if y_column else df.groupby(group_by).mean().reset_index()
                    elif aggregation == 'count':
                        df_grouped = df.groupby(group_by).size().reset_index(name='count')
                    elif aggregation == 'max':
                        df_grouped = df.groupby(group_by)[y_column].max().reset_index() if y_column else df.groupby(group_by).max().reset_index()
                    elif aggregation == 'min':
                        df_grouped = df.groupby(group_by)[y_column].min().reset_index() if y_column else df.groupby(group_by).min().reset_index()
                    else:
                        df_grouped = df
                    df = df_grouped
            
            # Create chart based on type
            fig = None
            
            if chart_type == "bar":
                if not x_column or not y_column:
                    return {"error": "Bar chart requires both x_column and y_column"}
                fig = px.bar(df, x=x_column, y=y_column, title=title or f"{y_column} by {x_column}")
            
            elif chart_type == "line":
                if not x_column or not y_column:
                    return {"error": "Line chart requires both x_column and y_column"}
                fig = px.line(df, x=x_column, y=y_column, title=title or f"{y_column} over {x_column}")
            
            elif chart_type == "scatter":
                if not x_column or not y_column:
                    return {"error": "Scatter chart requires both x_column and y_column"}
                fig = px.scatter(df, x=x_column, y=y_column, title=title or f"{y_column} vs {x_column}")
            
            elif chart_type == "pie":
                if not x_column or not y_column:
                    return {"error": "Pie chart requires both x_column (labels) and y_column (values)"}
                fig = px.pie(df, names=x_column, values=y_column, title=title or f"Distribution of {y_column}")
            
            elif chart_type == "histogram":
                if not y_column:
                    return {"error": "Histogram requires y_column"}
                fig = px.histogram(df, x=y_column, title=title or f"Distribution of {y_column}")
            
            else:
                return {"error": f"Unknown chart type: {chart_type}. Supported: bar, line, scatter, pie, histogram"}
            
            if fig:
                # Store chart parameters for the app to recreate
                # We can't serialize Plotly figures through the agent, so return parameters
                return {
                    "success": True,
                    "chart_type": chart_type,
                    "x_column": x_column,
                    "y_column": y_column,
                    "group_by": group_by,
                    "aggregation": aggregation,
                    "filters": filters,
                    "title": title or (f"{y_column} by {x_column}" if x_column and y_column else f"Chart of {y_column}"),
                    "table_name": table_name,
                    "data_points": len(df),
                    "columns_used": [x_column, y_column] if x_column and y_column else [y_column] if y_column else []
                }
            
        except Exception as e:
            return {
                "error": str(e),
                "table_name": table_name
            }
        
        return {"error": "Failed to create chart"}

