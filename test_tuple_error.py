#!/usr/bin/env python3
"""
Test script to reproduce the tuple strip error
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from main import AIWebScraperTool

def test_tuple_error():
    """Test to reproduce the tuple error"""
    
    scraper = AIWebScraperTool()
    
    try:
        # Test with a simple URL
        result = scraper.scrape_and_analyze("https://example.com", include_summary=False, include_entities=False)
        print("✅ No error occurred")
        print(f"Result: {result}")
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tuple_error()