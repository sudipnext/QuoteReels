import google.generativeai as genai
from typing import Optional, Dict, Any
import logging
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiAPIError(Exception):
    """Custom exception for Gemini API errors"""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.original_error = original_error

class GeminiAPI:
    def __init__(self):
        """Initialize Gemini API client"""
        self.api_key = Config.GEMINI_API_KEY
        if not self.api_key:
            raise GeminiAPIError("GEMINI_API_KEY environment variable not set")
            
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
        except Exception as e:
            raise GeminiAPIError("Failed to initialize Gemini API", original_error=e)

    def analyze_content(self, prompt: str) -> str:
        """
        Analyze content using Gemini API
        
        Args:
            prompt: The text prompt to analyze
            
        Returns:
            str: The analyzed response from Gemini
            
        Raises:
            GeminiAPIError: If API call fails or returns invalid response
        """
        try:
            # Generate content using the model
            response = self.model.generate_content(prompt)
            
            # Check if response is valid
            if not response or not response.text:
                raise GeminiAPIError("Empty response from Gemini API")
                
            # Return the cleaned response text
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise GeminiAPIError(
                "Failed to analyze content with Gemini API", 
                original_error=e
            )

    def analyze_quote_category(self, quote: str, categories: list) -> str:
        """
        Analyze a quote and match it with the best category
        
        Args:
            quote: The quote to analyze
            categories: List of available categories
            
        Returns:
            str: The best matching category name
        """
        prompt = f"""
        Analyze this quote and match it with the most appropriate category.
        
        Quote: "{quote}"
        
        Available categories:
        {categories}
        
        Return only the category name that best matches the quote's theme and emotion.
        Do not include any additional text or explanation.
        """
        
        return self.analyze_content(prompt)