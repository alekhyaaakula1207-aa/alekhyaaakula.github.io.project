#!/usr/bin/env python3
"""
Test script for the improved web scraper
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from main import AIWebScraperTool

def test_scraper():
    """Test the scraper with various websites"""
    
    scraper = AIWebScraperTool()
    
    # Test URLs
    test_urls = [
        "https://example.com",
        "https://httpbin.org/html", 
        "https://quotes.toscrape.com/",
    ]
    
    print("🧪 Testing improved web scraper...")
    print("=" * 50)
    
    for url in test_urls:
        print(f"\n🔗 Testing: {url}")
        print("-" * 30)
        
        try:
            # Use debug method to see what happens
            debug_result = scraper.debug_scraping(url)
            
            # Also test normal scraping
            result = scraper.scrape_and_analyze(url, include_summary=False, include_entities=False)
            
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
                if 'debug_info' in result:
                    print(f"🔍 Debug info: {result['debug_info']}")
            else:
                print(f"✅ Success! Content extracted: {result['word_count']} words")
                print(f"📋 Preview: {result['content_preview'][:100]}...")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_scraper()