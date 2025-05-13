import requests
from typing import Dict, Any, Optional
import logging
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PixabayAPIError(Exception):
    """Custom exception for Pixabay API errors"""
    pass

class PixabayAPI:
    """Client for the Pixabay Video API"""
    
    BASE_URL = "https://pixabay.com/api/videos/"
    
    def __init__(self):
        """Initialize the Pixabay API client with the API key
        
        Args:
            api_key: Your Pixabay API key
        """
        self.api_key = Config.PIXABAY_API_KEY
        self.session = requests.Session()
        
    def _make_request(
        self, 
        params: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Make a request to the Pixabay API
        
        Args:
            params: Query parameters for the request
            **kwargs: Additional arguments to pass to requests.request
            
        Returns:
            Dict containing the API response
            
        Raises:
            PixabayAPIError: If the request fails
        """
        try:
            if params is None:
                params = {}
                
            # Always include the API key in the parameters
            params["key"] = self.api_key
            
            response = self.session.get(
                url=self.BASE_URL,
                params=params,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Pixabay API request failed: {str(e)}")
            raise PixabayAPIError(f"Failed to fetch data: {str(e)}")
    
    def search_videos(
        self, 
        query: Optional[str] = None,
        language: str = "en",
        video_type: str = "all",
        category: Optional[str] = None,
        min_width: int = 0,
        min_height: int = 0,
        editors_choice: bool = False,
        safesearch: bool = False,
        order: str = "popular",
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """Search for videos on Pixabay
        
        Args:
            query: Search term (URL encoded)
            language: Language code (default: "en")
            video_type: Type of video ("all", "film", "animation")
            category: Filter by category
            min_width: Minimum video width
            min_height: Minimum video height
            editors_choice: Only return Editor's Choice videos
            safesearch: Only return videos suitable for all ages
            order: Order of results ("popular", "latest")
            page: Page number for pagination
            per_page: Number of results per page (3-200)
            
        Returns:
            Dict containing search results
        """
        params = {
            "lang": language,
            "video_type": video_type,
            "min_width": min_width,
            "min_height": min_height,
            "editors_choice": "true" if editors_choice else "false",
            "safesearch": "true" if safesearch else "false",
            "order": order,
            "page": page,
            "per_page": per_page
        }
        
        # Only add optional parameters if they are provided
        if query:
            params["q"] = query
            
        if category:
            params["category"] = category
            
        return self._make_request(params=params)
    
    def get_video_by_id(self, video_id: str) -> Dict[str, Any]:
        """Get a specific video by its ID
        
        Args:
            video_id: The ID of the video to retrieve
            
        Returns:
            Dict containing the video data
        """
        params = {"id": video_id}
        return self._make_request(params=params)