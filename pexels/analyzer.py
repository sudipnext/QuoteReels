import logging
from typing import Dict, Optional, List, Any
from pexels.pexels import PexelsAPI
from api.gemini import GeminiAPI

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PexelsAnalyzer:
    def __init__(self):
        self.gemini = GeminiAPI()
        self.pexels = PexelsAPI()
        logger.info("PexelsAPI initialized successfully for PexelsAnalyzer.")
        
    def _extract_video_urls_from_pexels_hit(self, video_files: List[Dict[str, Any]]) -> Optional[Dict[str, Optional[str]]]:
        """
        Extracts high_quality, standard, and preview video URLs from Pexels video_files.
        """
        if not video_files:
            return None

        urls = {
            "high_quality": None,
            "standard": None,
            "preview": None
        }

        hd_videos = sorted([vf for vf in video_files if vf.get("quality") == "hd" and vf.get("link") and vf.get("width")], key=lambda x: x.get("width", 0), reverse=True)
        sd_videos = sorted([vf for vf in video_files if vf.get("quality") == "sd" and vf.get("link") and vf.get("width")], key=lambda x: x.get("width", 0), reverse=True)

        # High Quality: Largest HD video
        if hd_videos:
            urls["high_quality"] = hd_videos[0]["link"]

        # Standard Quality:
        # Try for HD around 1280-1920 width, or largest HD if only very large ones, else largest SD
        if hd_videos:
            # Prefer HD with width <= 1920 if available
            standard_hd = next((vf["link"] for vf in reversed(hd_videos) if vf.get("width", 0) <= 1920), None)
            if standard_hd:
                urls["standard"] = standard_hd
            else: # Fallback to the smallest HD if all are > 1920p or largest if only one
                urls["standard"] = hd_videos[-1]["link"] if len(hd_videos) > 1 else hd_videos[0]["link"]
        
        if not urls["standard"] and sd_videos: # Fallback to largest SD if no HD found for standard
             urls["standard"] = sd_videos[0]["link"]
        
        if not urls["high_quality"] and urls["standard"]: # If no specific HD, use standard as high
            urls["high_quality"] = urls["standard"]


        # Preview: Smallest SD video
        if sd_videos:
            urls["preview"] = sd_videos[-1]["link"] # Smallest width SD
        elif hd_videos: # Fallback to smallest HD if no SD
            urls["preview"] = hd_videos[-1]["link"]
            
        # If standard is still None, try to assign it from high_quality or preview
        if not urls["standard"]:
            urls["standard"] = urls["high_quality"] or urls["preview"]
        
        # If high_quality is still None, try to assign it from standard
        if not urls["high_quality"]:
            urls["high_quality"] = urls["standard"]

        if not any(urls.values()):
            logger.warning("Could not extract any valid video URLs from Pexels video_files.")
            return None
            
        return urls

    def get_video_url(self, quote: str, quote_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        1. Get quote (Input parameter)
        2. Use Gemini API to generate a search parameter for Pexels.
        3. Search videos on Pexels.
        4. Extract video URLs.
        5. Return a dictionary with quote, search query, video URLs, and Pexels info.
        """
        if not self.gemini:
            logger.error("GeminiAPI client not available in PexelsAnalyzer.")
            return None
        if not self.pexels:
            logger.error("PexelsAPI client not available in PexelsAnalyzer.")
            return None

        try:
            logger.info(f"PexelsAnalyzer: Analyzing quote to find video: '{quote}'")
            # Use quote_type as part of the context for Gemini if available
            search_context = f"{quote_type} quote: {quote}" if quote_type else quote
            search_query = self.gemini.give_nice_searchable_parameter_for_given_text(search_context, provider='pixels')
            
            if not search_query or not search_query.strip():
                logger.warning(f"PexelsAnalyzer: Gemini did not return a valid search query for quote: '{quote}'")
                return None
            
            logger.info(f"PexelsAnalyzer: Generated Pexels search query: '{search_query}' for quote: '{quote}'")

            # Adjust parameters as needed for your PexelsAPI client
            response = self.pexels.search_videos(
                query=search_query,
                orientation="landscape", 
                size="medium", 
                per_page=5
            )

            if response and response.get("videos"):
                pexels_videos_found = response["videos"]
                if not pexels_videos_found:
                    logger.warning(f"PexelsAnalyzer: No videos array found in Pexels response for query '{search_query}'.")
                    return None

                logger.info(f"PexelsAnalyzer: Found {len(pexels_videos_found)} videos on Pexels for query '{search_query}'.")
                
                # Iterate through videos to find one with good downloadable links
                for video_hit in pexels_videos_found:
                    video_id = video_hit.get("id")
                    video_files = video_hit.get("video_files")
                    user_info = video_hit.get("user", {})

                    if not video_files:
                        logger.debug(f"PexelsAnalyzer: Video hit ID {video_id} has no video_files. Skipping.")
                        continue
                    
                    video_urls = self._extract_video_urls_from_pexels_hit(video_files) # Renamed to match the defined method
                
                    return video_urls
                    
                
                logger.warning(f"PexelsAnalyzer: Could not find suitable video URLs in any of the {len(pexels_videos_found)} Pexels hits for query '{search_query}'.")
                return None
            else:
                logger.warning(f"PexelsAnalyzer: No videos found or empty response from Pexels for search query: '{search_query}'. Response: {response}")
                return None
        except Exception as e:
            logger.error(f"PexelsAnalyzer: An error occurred while getting video for quote '{quote}': {e}", exc_info=True)
            return None

