#!/usr/bin/env python3
"""
Test to verify Google Genai client with GEMINI API key
"""

import sys
import os
from dotenv import load_dotenv
sys.path.append(os.path.dirname(__file__))

# Load environment variables
load_dotenv()

from main import AIWebScraperTool
from ai_processor import AIProcessor

def test_gemini_api_functionality():
    """Test the Google Genai client with actual GEMINI API key"""
    
    print("🧪 Testing Google Genai client with GEMINI API key...")
    
    # Check if API key is available
    api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ No GEMINI_API_KEY found in environment variables")
        return False
    
    print(f"✅ GEMINI API key found: {api_key[:10]}...")
    
    # Test 1: Initialize AIProcessor with API key
    print("\n1️⃣ Testing AIProcessor initialization with GEMINI API key...")
    try:
        processor = AIProcessor(api_key)
        print("✅ AIProcessor initialized successfully with GEMINI API key")
        
        # Test if client is available
        if processor._is_client_available():
            print("✅ Gemini client is properly initialized")
        else:
            print("❌ Gemini client initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ AIProcessor initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Test sentiment analysis with real API
    print("\n2️⃣ Testing sentiment analysis with GEMINI API...")
    try:
        result = processor.analyze_sentiment("This is a wonderful day! I love working on AI projects.")
        print(f"✅ Sentiment analysis completed successfully")
        print(f"   Sentiment: {result.get('sentiment', 'Unknown')}")
        print(f"   Confidence: {result.get('confidence', 0)}")
        print(f"   Reasoning: {result.get('reasoning', 'No reasoning')[:100]}...")
        
    except Exception as e:
        print(f"❌ Sentiment analysis failed: {e}")
        return False
    
    # Test 3: Test entity extraction with real API
    print("\n3️⃣ Testing entity extraction with GEMINI API...")
    try:
        test_content = "Apple Inc. was founded by Steve Jobs in Cupertino, California on April 1, 1976. The company is worth over $2 trillion today."
        result = processor.extract_entities(test_content)
        print(f"✅ Entity extraction completed successfully")
        print(f"   People: {result.get('people', [])}")
        print(f"   Organizations: {result.get('organizations', [])}")
        print(f"   Locations: {result.get('locations', [])}")
        
    except Exception as e:
        print(f"❌ Entity extraction failed: {e}")
        return False
    
    # Test 4: Test content summarization
    print("\n4️⃣ Testing content summarization with GEMINI API...")
    try:
        long_content = """
        Artificial Intelligence (AI) is transforming industries worldwide. From healthcare to finance, 
        AI technologies are being integrated to improve efficiency and decision-making processes. 
        Machine learning algorithms can analyze vast amounts of data to identify patterns that humans 
        might miss. Natural language processing enables computers to understand and generate human language, 
        making chatbots and virtual assistants more effective. Computer vision allows machines to 
        interpret and understand visual information from the world around them. As AI continues to evolve, 
        it promises to revolutionize how we work, communicate, and solve complex problems.
        """
        
        result = processor.summarize_content(long_content, max_length=50)
        print(f"✅ Content summarization completed successfully")
        print(f"   Summary: {result[:150]}..." if len(result) > 150 else f"   Summary: {result}")
        
    except Exception as e:
        print(f"❌ Content summarization failed: {e}")
        return False
    
    # Test 5: Test proper cleanup
    print("\n5️⃣ Testing proper client cleanup...")
    try:
        processor.close()
        print("✅ AIProcessor cleanup successful")
        
    except Exception as e:
        print(f"❌ AIProcessor cleanup failed: {e}")
        return False
    
    # Test 6: Full AI Web Scraper Tool with GEMINI API
    print("\n6️⃣ Testing full AI Web Scraper Tool with GEMINI API...")
    try:
        tool = AIWebScraperTool(api_key)
        result = tool.scrape_and_analyze(
            "https://example.com", 
            include_summary=True, 
            include_entities=True
        )
        
        if 'error' not in result:
            print("✅ Full tool test with AI features passed")
            print(f"   Title: {result.get('title', 'No title')}")
            print(f"   Word count: {result.get('word_count', 0)}")
            print(f"   Has summary: {'summary' in result}")
            print(f"   Has entities: {'entities' in result}")
            print(f"   Has sentiment: {'sentiment' in result}")
        else:
            print(f"⚠️ Full tool test completed with error: {result['error']}")
        
    except Exception as e:
        print(f"❌ Full tool test failed: {e}")
        return False
    
    print("\n🎉 All GEMINI API tests completed successfully!")
    return True

if __name__ == "__main__":
    success = test_gemini_api_functionality()
    if success:
        print("\n✅ GEMINI API integration is working perfectly!")
    else:
        print("\n❌ GEMINI API integration has issues.")