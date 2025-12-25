"""
Day 6: Search tools for the agent
Encapsulates search functionality in a class.
"""
from typing import List, Any
from minsearch import Index


class SearchTool:
    """Search tool that wraps the Minsearch index."""
    
    def __init__(self, index: Index):
        """
        Initialize search tool with an index.
        
        Args:
            index: Minsearch Index instance
        """
        self.index = index
    
    def search(self, query: str) -> List[Any]:
        """
        Perform a text-based search on the index.

        Args:
            query (str): The search query string.

        Returns:
            List[Any]: A list of up to 5 search results returned by the index.
        """
        return self.index.search(query, num_results=5)

