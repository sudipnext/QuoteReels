import random
from typing import Dict, Optional
import logging
from config import Config
from .gemini import GeminiAPI, GeminiAPIError

class QuoteAPIError(Exception):
    """Custom exception for Quote API errors"""
    pass

class QuoteAPI:
    """List of available quote types for Gemini generation"""
    QUOTE_TYPES  = [
        "happiness",
        "love",
        "selfconfidence",
        "success",
        "inspirational",
        "wisdom", 
        "courage",
        "life",
        "knowledge",
        "motivation"
    ]

    def __init__(self):
        """Initialize Quote API client with Gemini"""
        # Initialize Gemini Client
        try:
            self.gemini_client = GeminiAPI()
            logging.info("Gemini client initialized successfully.")
        except GeminiAPIError as e:
            logging.error(f"Failed to initialize Gemini client during QuoteAPI setup: {e}")
            self.gemini_client = None  # Set to None if initialization fails

    def get_random_quote(self, quote_type: Optional[str] = None) -> Dict[str, str]:
        """
        Fetch a random quote using Gemini API.
        
        Args:
            quote_type: Optional specific quote type, if None random type is chosen.
            
        Returns:
            Dictionary containing quote details with keys:
            - quote: The quote text
            - author: The quote author
            - type: The quote type/category
        """
        # Determine the topic for the quote
        topic = quote_type
        if not topic:
            topic = random.choice(self.QUOTE_TYPES)
        elif topic.lower() not in self.QUOTE_TYPES and topic.lower() != "error": # Allow "error" type if passed
            # If user provides a custom type not in QUOTE_TYPES, Gemini will try to generate for it.
            logging.info(f"Attempting to generate Gemini quote for user-specified type: {topic}")
        
        return self.generate_quote_with_gemini(topic)

    def generate_quote_with_gemini(self, quote_type: Optional[str] = None) -> Dict[str, str]:
        """
        Generate a quote using Gemini API.

        Args:
            quote_type: Optional specific quote type. If None, a random type from QUOTE_TYPES is chosen.

        Returns:
            Dictionary containing quote details with keys:
            - quote: The quote text
            - author: The quote author
            - type: The quote type/category
        """
        if not self.gemini_client:
            logging.warning("Gemini client not initialized. Cannot generate quote with Gemini.")
            return {
                "quote": "Failed to generate quote: Gemini client not available.",
                "author": "System",
                "type": quote_type or "error"
            }

        # Determine the topic for the quote
        topic = quote_type
        if not topic:
            topic = random.choice(self.QUOTE_TYPES)
        # If topic is provided but not in QUOTE_TYPES, we still proceed,
        # allowing users to request quotes on arbitrary topics.
        # Logging for this case is handled in get_random_quote or if called directly.
        
        prompt = f"""Generate a short, impactful quote about '{topic}'.
The quote should be original and insightful.
Also, provide the author of the quote. If the author is unknown, or if you are generating it, you can use "AI Generated" or "Anonymous".
Format your response strictly as:
Quote: [The quote text]
Author: [The author's name]"""

        try:
            response_text = self.gemini_client.analyze_content(prompt)
            
            # Default values if parsing fails
            final_quote = "Quote not found in Gemini response."
            final_author = "Author not found in Gemini response."
            
            lines = response_text.strip().split('\n')
            for line in lines:
                # Case-insensitive check for "Quote:" and "Author:"
                if line.lower().startswith("quote:"):
                    final_quote = line[len("quote:"):].strip()
                elif line.lower().startswith("author:"):
                    final_author = line[len("author:"):].strip()
            
            return {
                "quote": final_quote,
                "author": final_author,
                "type": topic # Return the requested/chosen topic
            }

        except GeminiAPIError as e:
            logging.error(f"Error generating quote with Gemini for topic '{topic}': {e}")
            return {
                "quote": f"An error occurred while generating an AI quote on '{topic}'.",
                "author": "System",
                "type": topic # Return the requested/chosen topic
            }
        except Exception as e:  # Catch any other unexpected errors
            logging.error(f"Unexpected error during Gemini quote generation for topic '{topic}': {e}")
            return {
                "quote": "An unexpected error occurred while generating an AI quote.",
                "author": "System",
                "type": topic # Return the requested/chosen topic
            }

