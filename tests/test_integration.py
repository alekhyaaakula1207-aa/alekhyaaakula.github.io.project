# tests/test_integration.py
import unittest
import os
from main_app import AIWebScraperTool

class TestIntegration(unittest.TestCase):
    def setUp(self):
        # Only run if API key is available
        if not os.getenv('GEMINI_KEY'):
            self.skipTest("GEMINI API key not available")
        
        self.scraper_tool = AIWebScraperTool()
    
    def test_full_scraping_pipeline(self):
        # Test with a reliable website
        url = "https://httpbin.org/html"
        
        result = self.scraper_tool.scrape_and_analyze(
            url, 
            include_summary=True,
            include_entities=False
        )
        
        self.assertNotIn('error', result)
        self.assertIn('title', result)
        self.assertIn('summary', result)
        self.assertGreater(result.get('word_count', 0), 0)

if __name__ == '__main__':
    unittest.main()
