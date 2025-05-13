import requests
from typing import Dict, Any, Optional
from config import Config

class PexelsAPIError(Exception):
    pass


class PexelsAPI:
    BASE_URL = "https://api.pexels.com"

    def __init__(self):
        self.api_key = Config.PEXELS_API_KEY
        self.headers = {
            "Authorization": self.api_key,
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
    ) -> Dict[str, Any]:
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
            raise PexelsAPIError(f"Failed to fetch data: {str(e)}")

    def search_videos(
        self,
        query: str,
        orientation: Optional[str] = None,
        size: Optional[str] = None,
        locale: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Search for videos on Pexels.

        Parameters:
            query (str): The search query.
            orientation (str, optional): Desired video orientation (landscape, portrait, or square).
            size (str, optional): Minimum video size (large, medium, or small).
            locale (str, optional): The locale of the search.
            page (int, optional): The page number to request.
            per_page (int, optional): The number of results per page.

        Returns:
            Dict[str, Any]: The JSON response from the API.
        """
        params = {"query": query}
        if orientation:
            params["orientation"] = orientation
        if size:
            params["size"] = size
        if locale:
            params["locale"] = locale
        if page:
            params["page"] = page
        if per_page:
            params["per_page"] = per_page
        
        return self._make_request(endpoint="videos/search", params=params)