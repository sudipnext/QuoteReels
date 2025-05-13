from coverr.analyzer import CoverrAnalyzer
from pexels.analyzer import PexelsAnalyzer
from pixabay.analyzer import PixabayAnalyzer
#initialize three analyzers
coverr_analyzer = CoverrAnalyzer()
pexels_analyzer = PexelsAnalyzer()
pixabay_analyzer = PixabayAnalyzer()

# Test data for all 3 analyzers to validate the response or functionality
test_quote = "A beautiful sunset over the mountains"


# Test the CoverrAnalyzer
coverr_response = coverr_analyzer.get_video_url(test_quote)
print(f"CoverrAnalyzer response: {coverr_response}")
# Test the PexelsAnalyzer
pexels_response = pexels_analyzer.get_video_url(test_quote)
print(f"PexelsAnalyzer response: {pexels_response}")
# Test the PixabayAnalyzer
pixabay_response = pixabay_analyzer.get_video_url(test_quote)
print(f"PixabayAnalyzer response: {pixabay_response}")
