#!/usr/bin/env python3
"""
Debug script to identify why "No meaningful content extracted" error occurs
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from main import AIWebScraperTool
from scraper import WebScraper
from content_cleaner import ContentCleaner

def debug_content_extraction():
    """Debug the content extraction process step by step"""
    
    print("🔍 Debugging 'No meaningful content extracted' error...")
    print("=" * 60)
    
    # Test with various URLs
    test_urls = [
        "https://example.com",
        "https://httpbin.org/html",
        "https://quotes.toscrape.com/",
        "https://news.ycombinator.com",
        "https://www.wikipedia.org",
    ]
    
    scraper = WebScraper()
    cleaner = ContentCleaner()
    
    for url in test_urls:
        print(f"\n🌐 Testing URL: {url}")
        print("-" * 40)
        
        try:
            # Step 1: Raw scraping
            print("1️⃣ Raw scraping...")
            raw_content = scraper.scrape_page(url)
            
            if 'error' in raw_content:
                print(f"❌ Scraping failed: {raw_content['error']}")
                continue
            
            print(f"   ✅ Title: {raw_content.get('title', 'No title')}")
            print(f"   ✅ Raw content length: {len(raw_content.get('main_content', ''))}")
            print(f"   ✅ Links found: {len(raw_content.get('links', []))}")
            
            # Show raw content sample
            raw_text = raw_content.get('main_content', '')
            if raw_text:
                print(f"   📝 Raw sample: {raw_text[:150]}...")
            else:
                print("   ❌ No raw content found!")
                continue
            
            # Step 2: Content cleaning
            print("2️⃣ Content cleaning...")
            cleaned_content = cleaner.clean_scraped_data(raw_content)
            cleaned_text = cleaned_content.get('main_content', '')
            
            print(f"   ✅ Cleaned content length: {len(cleaned_text)}")
            if cleaned_text:
                print(f"   📝 Cleaned sample: {cleaned_text[:150]}...")
            else:
                print("   ❌ No content after cleaning!")
                
                # Debug cleaning process
                print("   🔍 Debugging cleaning process...")
                test_clean = cleaner._clean_text(raw_text)
                print(f"   🔍 Direct clean result length: {len(test_clean)}")
                if test_clean:
                    print(f"   🔍 Direct clean sample: {test_clean[:100]}...")
                continue
            
            # Step 3: Full pipeline test
            print("3️⃣ Full pipeline test...")
            tool = AIWebScraperTool()
            result = tool.scrape_and_analyze(url, include_summary=False, include_entities=False)
            
            if 'error' in result:
                print(f"   ❌ Pipeline error: {result['error']}")
                if 'debug_info' in result:
                    print(f"   🔍 Debug info: {result['debug_info']}")
            else:
                print(f"   ✅ Pipeline success: {result['word_count']} words")
                
        except Exception as e:
            print(f"❌ Exception occurred: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_content_extraction()