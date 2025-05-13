from typing import List, Dict, Optional, Any
from api.gemini import GeminiAPI
from pixabay.pixibay import PixabayAPI
from api.gemini import GeminiAPIError
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


"""
This analyzer should be able to get the random quote USING THE GEMINI and then with that text it should generate a descriptive search parameter using gemini and then it should finally call the pixabay api to get the all video through the query before making a query and then it should finally call the pixabay api video api to get the video download url and then return the video url.
"""

class PixabayAnalyzer:
    def __init__(self):
        self.gemini = GeminiAPI()
        self.pixabay = PixabayAPI()
        logger.info("PixabayAPI initialized successfully for PixabayAnalyzer.") # Changed for consistency

    def _extract_video_urls(self, video_data_param: Dict) -> Optional[Dict[str, str]]:
        """Extract and validate video URLs"""
        try:
            urls_dict = video_data_param.get("urls", {}) 
            if not urls_dict: 
                logger.warning("'_extract_video_urls' received data without 'urls' key or empty 'urls' dict.")
                return None
                
            extracted_urls = {
                "high_quality": urls_dict.get("mp4_download"),
                "standard": urls_dict.get("mp4"),
                "preview": urls_dict.get("mp4_preview")
            }
            
            # Validate that at least one URL exists and is not None
            if not any(url for url in extracted_urls.values() if url is not None):
                logger.info("No valid URLs found after mapping in _extract_video_urls. All mapped URLs were None.")
                return None
                
            return extracted_urls
            
        except Exception as e:
            logger.error(f"Error extracting video URLs: {e}")
            return None

    

    def get_video_url(self, quote: str, quote_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        1. Get video Quote (Input parameter)
        2. Using the Gemini API to analyze the quote and get the most relevant search parameter for that quote to search for the video
        3. Do the video search from the pixabay API
        4. Get the video download url from the pixabay API using _extract_video_urls
        5. Return a dictionary containing the video download urls and other relevant info.
        6. If there is no video found for the quote or an error occurs, then return None.
        """
        if not self.gemini:
            logger.error("Analyzer: GeminiAPI client not available.")
            return None
        if not self.pixabay:
            logger.error("Analyzer: PixabayAPI client not available.")
            return None

        try:
            logger.info(f"Analyzer: Analyzing quote to find video: '{quote}'")
            search_context = f"{quote_type} quote: {quote}" if quote_type else quote
            search_query = self.gemini.give_nice_searchable_parameter_for_given_text(search_context, provider='pixabay')
            
            if not search_query or not search_query.strip():
                logger.warning(f"Analyzer: Gemini did not return a valid search query for quote: '{quote}'")
                return None
            
            logger.info(f"Analyzer: Generated Pixabay search query: '{search_query}' for quote: '{quote}'")

            response = self.pixabay.search_videos(
                query=search_query,
                language="en",
                video_type="film",
                per_page=5 # Changed from 3 to 5 for similarity with Pexels
            )

            if response and response.get("hits"):
                videos_found = response["hits"]
                if not videos_found:
                    logger.warning(f"Analyzer: No videos array ('hits') found in Pixabay response for query '{search_query}'.")
                    return None

                logger.info(f"Analyzer: Found {len(videos_found)} videos on Pixabay for query '{search_query}'.")
                
                # Iterate through videos to find one with processable video data
                for video_hit in videos_found:
                    video_id = video_hit.get("id")
                    pixabay_video_data = video_hit.get("videos", {}) # Main data payload for URLs

                    if not pixabay_video_data:
                        logger.debug(f"Analyzer: Video hit ID {video_id} has no 'videos' data. Skipping.")
                        continue
                    
                    # Construct the input for _extract_video_urls
                    preview_url_small = pixabay_video_data.get("small", {}).get("url")
                    preview_url_tiny = pixabay_video_data.get("tiny", {}).get("url")
                    actual_preview_url = preview_url_small if preview_url_small else preview_url_tiny

                    input_for_extraction = {
                        "urls": {
                            "mp4_download": pixabay_video_data.get("large", {}).get("url"),
                            "mp4": pixabay_video_data.get("medium", {}).get("url"),
                            "mp4_preview": actual_preview_url
                        }
                    }
                    
                    video_urls = self._extract_video_urls(input_for_extraction)
                
                    logger.info(f"Analyzer: Extracted video URLs for category '{quote_type}' from hit ID {video_id}: {video_urls}")
                    return video_urls # Return after processing the first hit with 'videos' data
                    
                # This part is reached if all video_hits lacked 'videos' data
                logger.warning(f"Analyzer: None of the {len(videos_found)} Pixabay hits had 'videos' data for query '{search_query}'.")
                return None
            else:
                logger.warning(f"Analyzer: No videos found or empty response from Pixabay for search query: '{search_query}'. Response: {response}")
                return None

        except GeminiAPIError as e:
            logger.error(f"Analyzer: Gemini API error during search query generation for quote '{quote}': {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Analyzer: Unexpected error in get_video_url for quote '{quote}': {str(e)}", exc_info=True)
            return None