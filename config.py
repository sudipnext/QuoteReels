import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

class Config:
    """Configuration class to manage all environment variables"""
    
    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    COVERR_API_KEY = os.getenv('COVERR_API_KEY')
    PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
    PIXABAY_API_KEY = os.getenv('PIXABAY_API_KEY')
    
    # API URLs
    COVERR_API_URL = os.getenv('COVERR_API_URL', 'https://coverr.co/api/videos')
    
    # Application Settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    @classmethod
    def validate_config(cls) -> bool:
        """
        Validate that all required environment variables are set
        Returns: bool indicating if config is valid
        """
        required_vars = [
            'GEMINI_API_KEY',
            'COVERR_API_KEY',
            'PEXELS_API_KEY',
            'PIXABAY_API_KEY',
        ]
        
        missing_vars = [var for var in required_vars if not getattr(cls, var, None)]
        
        if missing_vars:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing_vars)}\n"
                "Please check your .env file and ensure all required variables are set."
            )
        
        return True

# Validate configuration on import
Config.validate_config()