import requests
import random
from typing import Dict, Optional, Tuple
import logging
from functools import wraps
from config import Config

class QuoteAPIError(Exception):
    """Custom exception for Quote API errors"""
    pass

class QuoteAPI:
    BASE_URL = Config.QUOTE_API_BASE_URL
    
    """List of available quote types"""
    QUOTE_TYPES  = [
        "happiness",
        "love",
        "selfconfidence",
        "success",
        "inspirational",
    ]

    def __init__(self):
        """Initialize Quote API client"""
            
        self.headers = Config.RAPIDAPI_HEADERS
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict] = None,
        **kwargs
    ) -> Dict:
        """
        Generic request handler for Quote API
        
        Args:
            endpoint: API endpoint to call
            method: HTTP method (GET, POST, etc.)
            params: Query parameters
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            JSON response from API
            
        Raises:
            QuoteAPIError: If API request fails
        """
        try:
            url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                **kwargs
            )
            print(f"Request URL: {url}")
            print(f"Request Params: {params}")
            print(f"Response Status Code: {response.status_code}")
            print(f"Response Headers: {response.headers}")

            print(response.json())
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logging.error(f"Quote API error: {str(e)}")
            raise QuoteAPIError(f"Failed to fetch data: {str(e)}")

    def get_random_quote(self, quote_type: Optional[str] = None) -> Dict[str, str]:
        """
        Fetch a random quote
        
        Args:
            quote_type: Optional specific quote type, if None random type is chosen
            
        Returns:
            Dictionary containing quote details with keys:
            - quote: The quote text
            - author: The quote author
            - type: The quote type/category
            
        Raises:
            QuoteAPIError: If quote fetch fails
        """
        try:
            quote_type = quote_type or random.choice(self.QUOTE_TYPES)
            
            response = self._make_request(
                "quotes/random",
                params={"type": quote_type}
            )
            print(response)
            
            # Extract quote from response structure
            return {
                "quote": response.get("quote", "An error occurred while fetching the quote"),
                "author": response.get("author", "Unknown"),
                "type": response.get("type", quote_type)
            }

        except QuoteAPIError as e:
            logging.error(f"Error fetching random quote: {e}")
            return {
                "quote": "An error occurred while fetching the quote",
                "author": "Unknown",
                "type": "error"
            }

    def get_quotes_by_type(self, quote_type: str, limit: int = 10) -> list:
        """
        Fetch multiple quotes of a specific type
        
        Args:
            quote_type: Type of quotes to fetch
            limit: Number of quotes to fetch
            
        Returns:
            List of quote dictionaries
        """
        try:
            response = self._make_request(
                "quotes",
                params={
                    "type": quote_type,
                }
            )
            return response.get("response", [])
            
        except QuoteAPIError as e:
            logging.error(f"Error fetching quotes by type: {e}")
            return []

