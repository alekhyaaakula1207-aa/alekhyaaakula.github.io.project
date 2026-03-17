# tests/test_scraper.py
import unittest
from unittest.mock import patch, Mock
from scraper import WebScraper
from content_cleaner import ContentCleaner

class TestWebScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = WebScraper()
        self.cleaner = ContentCleaner()
        
    @patch('requests.Session.get')
    def test_scrape_page_success(self, mock_get):
        # Mock successful response
        mock_response = Mock()
        mock_response.content = b'<html><title>Test Page</title><body><p>Test content</p></body></html>'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.scraper.scrape_page('https://example.com')
        
        self.assertIn('title', result)
        self.assertIn('main_content', result)
        self.assertEqual(result['title'], 'Test Page')
    
    @patch('requests.Session.get')
    def test_scrape_page_error(self, mock_get):
        # Mock failed response
        mock_get.side_effect = Exception("Connection error")
        
        result = self.scraper.scrape_page('https://example.com')
        
        self.assertIn('error', result)
    
    def test_content_cleaning(self):
        # Test content cleaner
        dirty_content = {
            'title': 'Test Title | Website Name',
            'main_content': '   Multiple    spaces   and\n\nline breaks   ',
            'metadata': {'description': 'Test description with <tag>'}
        }
        
        cleaned = self.cleaner.clean_scraped_data(dirty_content)
        
        self.assertEqual(cleaned['title'], 'Test Title')
        self.assertNotIn('\n\n', cleaned['main_content'])
        self.assertNotIn('<tag>', cleaned['metadata']['description'])

if __name__ == '__main__':
    unittest.main()
