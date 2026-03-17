# main_app.py
import os
# Suppress gRPC verbose logging to avoid ALTS credentials warnings
os.environ.setdefault('GRPC_VERBOSITY', 'ERROR')
os.environ.setdefault('GRPC_TRACE', '')

import pandas as pd
import json
from datetime import datetime
from scraper import WebScraper
from content_cleaner import ContentCleaner
from ai_processor import AIProcessor
from langchain_processor import LangChainProcessor

class AIWebScraperTool:
    def __init__(self, openai_api_key=None):
        self.scraper = WebScraper()
        self.cleaner = ContentCleaner()
        self.ai_processor = AIProcessor(openai_api_key)
        self.langchain_processor = LangChainProcessor(openai_api_key)
        self.results = []
    
    def scrape_and_analyze(self, url, include_summary=True, include_entities=True, 
                          include_qa=False, question=None, use_langchain=False):
        """Main method to scrape and analyze content"""
        
        print(f"Scraping URL: {url}")
        
        # Step 1: Scrape content
        raw_content = self.scraper.scrape_page(url)
        
        if 'error' in raw_content:
            return {"error": raw_content['error'], "url": url}
        
        # Step 2: Clean content
        cleaned_content = self.cleaner.clean_scraped_data(raw_content)
        
        # Step 3: Prepare result structure
        result = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "title": cleaned_content.get('title', ''),
            "content_preview": cleaned_content.get('main_content', '')[:500] + "...",
            "metadata": cleaned_content.get('metadata', {}),
            "word_count": len(cleaned_content.get('main_content', '').split())
        }
        
        main_content = cleaned_content.get('main_content', '')
        
        # Ensure main_content is a string
        if not isinstance(main_content, str):
            main_content = str(main_content) if main_content else ""
        
        # Enhanced debugging information
        if not main_content or len(main_content.strip()) == 0:
            debug_info = {
                "raw_content_length": len(raw_content.get('main_content', '')),
                "title_found": bool(cleaned_content.get('title', '')),
                "metadata_found": bool(cleaned_content.get('metadata', {})),
                "url": url
            }
            result["error"] = "No meaningful content extracted"
            result["debug_info"] = debug_info
            print(f"Debug: Raw content length: {debug_info['raw_content_length']}")
            print(f"Debug: Title found: {debug_info['title_found']}")
            return result
        
        # Check if content is too short
        if len(main_content.split()) < 5:
            result["warning"] = f"Very short content extracted: only {len(main_content.split())} words"
            print(f"Warning: Content is very short ({len(main_content.split())} words): {main_content[:100]}...")
        
        # Step 4: AI Processing
        if use_langchain:
            print("Processing with LangChain...")
            langchain_result = self.langchain_processor.process_content(main_content)
            result["langchain_analysis"] = langchain_result
        
        if include_summary:
            print("Generating summary...")
            result["summary"] = self.ai_processor.summarize_content(main_content)
        
        if include_entities:
            print("Extracting entities...")
            result["entities"] = self.ai_processor.extract_entities(main_content)
        
        if include_qa and question:
            print(f"Answering question: {question}")
            result["qa_response"] = self.ai_processor.answer_question(main_content, question)
        
        # Add sentiment analysis
        print("Analyzing sentiment...")
        result["sentiment"] = self.ai_processor.analyze_sentiment(main_content)
        
        self.results.append(result)
        return result
    
    def debug_scraping(self, url):
        """Debug method to understand why scraping fails"""
        print(f"\n🔍 Debugging scraping for: {url}")
        
        # Step 1: Raw scraping
        raw_content = self.scraper.scrape_page(url)
        if 'error' in raw_content:
            print(f"❌ Scraping failed: {raw_content['error']}")
            return raw_content
        
        print(f"✅ Successfully scraped page")
        print(f"📄 Title: {raw_content.get('title', 'No title')}")
        print(f"📝 Raw content length: {len(raw_content.get('main_content', ''))}")
        print(f"🔗 Links found: {len(raw_content.get('links', []))}")
        print(f"🖼️ Images found: {len(raw_content.get('images', []))}")
        
        if raw_content.get('main_content'):
            print(f"📋 Raw content preview: {raw_content['main_content'][:200]}...")
        
        # Step 2: Content cleaning
        cleaned_content = self.cleaner.clean_scraped_data(raw_content)
        print(f"🧹 Cleaned content length: {len(cleaned_content.get('main_content', ''))}")
        
        if cleaned_content.get('main_content'):
            print(f"📋 Cleaned content preview: {cleaned_content['main_content'][:200]}...")
        else:
            print("❌ No content after cleaning!")
        
        return {
            'raw': raw_content,
            'cleaned': cleaned_content
        }
    
    def scrape_multiple_urls(self, urls, **kwargs):
        """Scrape and analyze multiple URLs"""
        results = []
        for i, url in enumerate(urls, 1):
            print(f"\nProcessing {i}/{len(urls)}: {url}")
            result = self.scrape_and_analyze(url, **kwargs)
            results.append(result)
        return results
    
    def save_results(self, filename=None, format='json'):
        """Save results to file"""
        if not self.results:
            print("No results to save")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == 'json':
            filename = filename or f"scraping_results_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        elif format == 'csv':
            filename = filename or f"scraping_results_{timestamp}.csv"
            
            # Flatten results for CSV
            flattened_results = []
            for result in self.results:
                flat_result = {
                    'url': result.get('url', ''),
                    'title': result.get('title', ''),
                    'word_count': result.get('word_count', 0),
                    'summary': result.get('summary', ''),
                    'sentiment': result.get('sentiment', {}).get('sentiment', ''),
                    'timestamp': result.get('timestamp', '')
                }
                
                # Add entities as separate columns
                entities = result.get('entities', {})
                for entity_type, entity_list in entities.items():
                    if isinstance(entity_list, list):
                        flat_result[f'entities_{entity_type}'] = '; '.join(entity_list)
                
                flattened_results.append(flat_result)
            
            df = pd.DataFrame(flattened_results)
            df.to_csv(filename, index=False, encoding='utf-8')
        
        print(f"Results saved to {filename}")
        return filename
    
    def get_summary_statistics(self):
        """Get summary statistics of scraping results"""
        if not self.results:
            return {}
        
        stats = {
            "total_pages_scraped": len(self.results),
            "successful_scrapes": len([r for r in self.results if 'error' not in r]),
            "failed_scrapes": len([r for r in self.results if 'error' in r]),
            "average_word_count": sum([r.get('word_count', 0) for r in self.results]) / len(self.results),
            "sentiment_distribution": {}
        }
        
        # Sentiment distribution
        sentiments = [r.get('sentiment', {}).get('sentiment', 'Unknown') for r in self.results]
        for sentiment in set(sentiments):
            stats["sentiment_distribution"][sentiment] = sentiments.count(sentiment)
        
        return stats
