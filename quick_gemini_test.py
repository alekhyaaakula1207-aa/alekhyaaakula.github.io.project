#!/usr/bin/env python3
"""
Quick GEMINI API test for the AI Web Scraper Tool
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from ai_processor import AIProcessor

def quick_gemini_test():
    """Quick test of GEMINI API functionality"""
    
    print("🚀 Quick GEMINI API Test")
    print("=" * 40)
    
    # Get API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ No GEMINI_API_KEY found in .env file")
        return False
    
    print(f"✅ API Key: {api_key[:15]}...")
    
    try:
        # Initialize processor
        processor = AIProcessor(api_key)
        print("✅ AIProcessor initialized")
        
        # Quick sentiment test
        result = processor.analyze_sentiment("I love this AI tool! It's amazing!")
        print(f"✅ Sentiment: {result['sentiment']} (confidence: {result['confidence']})")
        
        # Quick entity test
        entities = processor.extract_entities("Microsoft was founded by Bill Gates in Seattle.")
        print(f"✅ Entities found: {len(entities.get('people', []))} people, {len(entities.get('organizations', []))} orgs")
        
        # Quick summary test
        summary = processor.summarize_content("This is a test document about artificial intelligence and machine learning technologies.")
        print(f"✅ Summary generated: {len(summary)} characters")
        
        processor.close()
        print("✅ Cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = quick_gemini_test()
    if success:
        print("\n🎉 GEMINI API is working great!")
    else:
        print("\n❌ GEMINI API test failed.")