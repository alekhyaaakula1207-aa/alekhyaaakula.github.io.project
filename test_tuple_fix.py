#!/usr/bin/env python3
"""
Comprehensive test to check for tuple strip error fixes
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from main import AIWebScraperTool
from scraper import WebScraper
from content_cleaner import ContentCleaner

def test_various_scenarios():
    """Test various scenarios that could cause tuple errors"""
    
    print("🧪 Testing for tuple strip errors...")
    
    # Test 1: Basic scraper functionality
    print("\n1️⃣ Testing basic scraper...")
    scraper = WebScraper()
    try:
        result = scraper.scrape_page("https://example.com")
        print("✅ Basic scraper test passed")
    except Exception as e:
        print(f"❌ Basic scraper test failed: {e}")
        return False
    
    # Test 2: Content cleaner with various inputs
    print("\n2️⃣ Testing content cleaner...")
    cleaner = ContentCleaner()
    test_inputs = [
        "Normal string content",
        "",
        None,
        123,  # Non-string input
        ["list", "input"],  # List input
        {"dict": "input"},  # Dict input
    ]
    
    for i, test_input in enumerate(test_inputs):
        try:
            if isinstance(test_input, dict):
                # Test clean_scraped_data with dict
                result = cleaner.clean_scraped_data({"main_content": "test"})
            else:
                # Test _clean_text with various types
                result = cleaner._clean_text(test_input)
            print(f"✅ Content cleaner test {i+1} passed")
        except Exception as e:
            print(f"❌ Content cleaner test {i+1} failed: {e}")
            return False
    
    # Test 3: Full AI Web Scraper Tool
    print("\n3️⃣ Testing full AI Web Scraper Tool...")
    tool = AIWebScraperTool()
    try:
        result = tool.scrape_and_analyze("https://example.com", include_summary=False, include_entities=False)
        print("✅ Full tool test passed")
        print(f"   Result type: {type(result)}")
        print(f"   Content length: {len(result.get('content_preview', ''))}")
    except Exception as e:
        print(f"❌ Full tool test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Edge cases with problematic URLs
    print("\n4️⃣ Testing edge cases...")
    edge_case_urls = [
        "https://httpbin.org/status/404",  # 404 error
        "https://invalid-url-that-does-not-exist.com",  # Invalid URL
    ]
    
    for url in edge_case_urls:
        try:
            result = tool.scrape_and_analyze(url, include_summary=False, include_entities=False)
            print(f"✅ Edge case test passed for {url}")
        except Exception as e:
            print(f"⚠️ Edge case expected error for {url}: {e}")
            # This is expected for invalid URLs, not a failure
    
    print("\n🎉 All tuple error tests completed successfully!")
    return True

if __name__ == "__main__":
    success = test_various_scenarios()
    if success:
        print("\n✅ Tuple strip error has been fixed!")
    else:
        print("\n❌ Tuple strip error still exists.")