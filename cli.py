# cli.py
import argparse
import os
from main_app import AIWebScraperTool

def main():
    parser = argparse.ArgumentParser(description='AI Web Scraper Tool')
    
    # Required arguments
    parser.add_argument('url', nargs='?', help='URL to scrape (or use --urls-file)')
    
    # Optional arguments
    parser.add_argument('--urls-file', help='File containing URLs to scrape (one per line)')
    parser.add_argument('--output', '-o', help='Output filename')
    parser.add_argument('--format', choices=['json', 'csv'], default='json', help='Output format')
    parser.add_argument('--api-key', help='OpenAI API key (or set OPENAI_API_KEY env var)')
    
    # Feature flags
    parser.add_argument('--no-summary', action='store_true', help='Skip content summarization')
    parser.add_argument('--no-entities', action='store_true', help='Skip entity extraction')
    parser.add_argument('--question', help='Ask a question about the content')
    parser.add_argument('--use-langchain', action='store_true', help='Use LangChain for advanced processing')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.url and not args.urls_file:
        parser.error("Either provide a URL or use --urls-file")
    
    # Initialize the scraper
    api_key = args.api_key or os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Warning: No OpenAI API key found. AI features will not work.")
        return
    
    scraper_tool = AIWebScraperTool(openai_api_key=api_key)
    
    # Determine URLs to process
    urls = []
    if args.url:
        urls = [args.url]
    elif args.urls_file:
        try:
            with open(args.urls_file, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Error: File {args.urls_file} not found")
            return
    
    # Configure processing options
    options = {
        'include_summary': not args.no_summary,
        'include_entities': not args.no_entities,
        'include_qa': bool(args.question),
        'question': args.question,
        'use_langchain': args.use_langchain
    }
    
    print(f"Starting to process {len(urls)} URL(s)...")
    
    # Process URLs
    if len(urls) == 1:
        result = scraper_tool.scrape_and_analyze(urls[0], **options)
        print("\n" + "="*50)
        print("RESULTS")
        print("="*50)
        print(f"Title: {result.get('title', 'N/A')}")
        print(f"Word Count: {result.get('word_count', 0)}")
        
        if result.get('summary'):
            print(f"\nSummary:\n{result['summary']}")
        
        if result.get('entities'):
            print(f"\nEntities: {result['entities']}")
        
        if result.get('qa_response'):
            print(f"\nQ&A Response:\n{result['qa_response']}")
    else:
        results = scraper_tool.scrape_multiple_urls(urls, **options)
        
        # Display summary statistics
        stats = scraper_tool.get_summary_statistics()
        print("\n" + "="*50)
        print("SUMMARY STATISTICS")
        print("="*50)
        for key, value in stats.items():
            print(f"{key}: {value}")
    
    # Save results
    filename = scraper_tool.save_results(args.output, args.format)
    print(f"\nResults saved to: {filename}")

if __name__ == "__main__":
    main()
