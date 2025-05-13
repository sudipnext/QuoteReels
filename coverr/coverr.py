import requests
from typing import Optional, Dict, Any, Union
from functools import wraps
import logging
from config import Config

class CoverrAPIError(Exception):
    """Custom exception for Coverr API errors"""
    pass

class CoverrAPI:
    BASE_URL = "https://api.coverr.co"
    
    def __init__(self):
        """Initialize the CoverrAPI client"""
        self.api_key = Config.COVERR_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _make_request(
        self, 
        endpoint: str, 
        method: str = "GET", 
        params: Optional[Dict] = None,
        **kwargs
    ) -> Union[Dict, Any]:
        """
        Generic request handler for Coverr API
        
        Args:
            endpoint: API endpoint to call
            method: HTTP method (GET, POST, etc.)
            params: Query parameters
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            JSON response from API
            
        Raises:
            CoverrAPIError: If API request fails
        """
        try:
            url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Coverr API error: {str(e)}")
            raise CoverrAPIError(f"Failed to fetch data: {str(e)}")

    def get_video_all_categories(self) -> Dict:
        """
        Fetch all available video categories
        
        Returns:
            Dict containing category information
        """
        return self._make_request("categories")

    def get_video(self, category: str) -> Dict:
        """
        Fetch videos for a specific category
        
        Args:
            category: Category ID or slug
            
        Returns:
            Dict containing video information
        """
        return self._make_request(f"categories/{category}/videos", params={"urls": "true"})
