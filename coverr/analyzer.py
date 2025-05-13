from typing import List, Dict, Optional
from api.gemini import GeminiAPI
from coverr.coverr import CoverrAPI
from api.gemini import GeminiAPIError
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


"""
This analyzer should be able to get the random quote USING THE GEMINI and then with that text along with it should call the coverr api to get the all video categories and then it should try to match the category description with the quote and then make sense of the category and then call the gemini api to compare and give me the proper video category and then it should finally call the coverr api video api to get the video download url and then return the video url.
"""

class CoverrAnalyzer:
    def __init__(self):
        self.gemini = GeminiAPI()
        self.coverr = CoverrAPI()

    def _extract_minimal_info(self, category: Dict) -> Dict:
        """Extract only name, tags, and id from a category"""
        return {
            "name": category.get("name", ""),
            "tags": category.get("tags", []),
            "id": category.get("id", "")
        }

    def _extract_category_info(self, categories: List[Dict]) -> List[Dict]:
        """
        Extract relevant category information including subcategories
        Returns list of dicts with name, tags, and id for both categories and subcategories
        """
        processed_categories = []
        for category in categories:
            # Process main category
            cat_info = self._extract_minimal_info(category)
            processed_categories.append(cat_info)
            
            # Process subcategories if they exist
            subcategories = category.get("subcategories", [])
            for subcat in subcategories:
                subcat_info = self._extract_minimal_info(subcat)
                processed_categories.append(subcat_info)
                
        return processed_categories

    def _extract_video_urls(self, video_data: Dict) -> Optional[Dict[str, str]]:
        """Extract and validate video URLs"""
        try:
            urls = video_data.get("urls", {})
            if not urls:
                return None
                
            extracted_urls = {
                "high_quality": urls.get("mp4_download"),
                "standard": urls.get("mp4"),
                "preview": urls.get("mp4_preview")
            }
            
            # Validate that at least one URL exists
            if not any(extracted_urls.values()):
                logger.error("No valid URLs found in video data")
                return None
                
            return extracted_urls
            
        except Exception as e:
            logger.error(f"Error extracting video URLs: {e}")
            return None

    def _get_category_videos(self, category_id: str) -> Optional[Dict]:
        """Helper method to get videos for a category with error handling"""
        try:
            videos = self.coverr.get_video(category_id)
            if not videos or "hits" not in videos or not videos["hits"]:
                logger.warning(f"No videos found for category ID: {category_id}")
                return None
            return videos
        except Exception as e:
            logger.error(f"Error fetching videos for category {category_id}: {e}")
            return None

    def _find_matching_category(self, matched_name: str, categories: List[Dict]) -> Optional[str]:
        """Helper method to find matching category with fuzzy matching"""
        matched_name = matched_name.lower().strip()
        
        # First try exact match
        for cat in categories:
            if cat['name'].lower() == matched_name:
                return cat['id']
        
        # Then try partial match
        for cat in categories:
            if matched_name in cat['name'].lower() or any(matched_name in tag.lower() for tag in cat['tags']):
                return cat['id']
        
        return None

    def get_video_url(self, quote: str) -> Dict[str, str]:
        """Get most relevant video URLs for the given quote"""
        try:
            # Get all categories and extract relevant info
            categories = self.coverr.get_video_all_categories()
            processed_categories = self._extract_category_info(categories.get("hits", []))

            # Simplified and more structured prompt for Gemini
            prompt = f"""
            Quote: "{quote}"
            Task: Match this quote with one of these categories:
            Categories:
            {[{cat['name']: cat['tags']} for cat in processed_categories]}
            
            Instructions: Analyze the quote's theme and emotion. Return only the category name that best matches, nothing else.
            """

            # Get category match from Gemini
            matched_category = self.gemini.analyze_content(prompt)
            if not matched_category:
                raise GeminiAPIError("No category match received from Gemini")
                
            logger.info(f"Gemini matched category: {matched_category}")
            
            # Find the category ID for the matched category
            category_id = self._find_matching_category(matched_category, processed_categories)

            if not category_id:
                logger.warning(f"No matching category found for quote: {quote}")
                return None

            # Get videos for the matched category
            category_videos = self._get_category_videos(category_id)
            
            if not category_videos:
                logger.error(f"No videos found for category: {matched_category}")
                return None
            # Randomly select a video from the category
            import random
            first_video = random.choice(category_videos["hits"])
            video_urls = self._extract_video_urls(first_video)
            
            logger.info(f"Found video URLs for category '{matched_category}': {video_urls}")
            return video_urls

        except Exception as e:
            logger.error(f"Error in get_video_url: {str(e)}")
            return None