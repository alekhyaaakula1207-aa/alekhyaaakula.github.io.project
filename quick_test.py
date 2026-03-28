#!/usr/bin/env python3
"""
Quick test to verify the scraper works with common websites
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from main import AIWebScraperTool

def quick_test():
    """Quick test of the scraper"""
    scraper = AIWebScraperTool()
    
    # Test a reliable website
    url = "https://example.com"
    print(f"🧪 Testing scraper with: {url}")
    
    result = scraper.scrape_and_analyze(url, include_summary=False, include_entities=False, use_langchain=False)
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        return False
    else:
        print(f"✅ Success!")
        print(f"📄 Title: {result['title']}")
        print(f"📝 Word count: {result['word_count']}")
        print(f"📋 Content preview: {result['content_preview']}")
        return True

if __name__ == "__main__":
    success = quick_test()
    if success:
        print("\n🎉 The 'No meaningful content extracted' error has been fixed!")
    else:
        print("\n❌ The error still exists.")