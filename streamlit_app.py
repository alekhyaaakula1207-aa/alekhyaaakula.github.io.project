# streamlit_app.py
import streamlit as st
import pandas as pd
import json
from main import AIWebScraperTool
import os
from datetime import datetime
import vercel_analytics

# Page configuration
st.set_page_config(
    page_title="AI Web Scraper Tool",
    page_icon="🕷️",
    layout="wide"
)

# Initialize Vercel Web Analytics
vercel_analytics.inject_vercel_analytics()

# Title and description
st.title("🕷️ AI Web Scraper Tool")
st.markdown("Extract, clean, and analyze web content using AI-powered insights")

# API Key input
api_key = os.getenv('GEMINI_API_KEY'),

# Processing options
st.sidebar.header("Processing Options")
include_summary = st.sidebar.checkbox("Generate Summary", value=True)
include_entities = st.sidebar.checkbox("Extract Entities", value=True)
use_langchain = st.sidebar.checkbox("Use LangChain (Advanced)", value=False)

# Main interface
tab1, tab2, tab3 = st.tabs(["Single URL", "Multiple URLs", "Results History"])

with tab1:
    st.header("Scrape Single URL")
    
    url = st.text_input("Enter Website URL", placeholder="https://example.com")
    question = st.text_input("Ask a Question (Optional)", placeholder="What is this article about?")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        scrape_button = st.button("🚀 Scrape & Analyze", type="primary")
    
    with col2:
        if st.button("📋 Load Example"):
            st.session_state.example_url = "https://en.wikipedia.org/wiki/Artificial_intelligence"
    
    # Use example URL if loaded
    if 'example_url' in st.session_state:
        url = st.session_state.example_url
        st.info(f"Example URL loaded: {url}")
    
    if scrape_button and url:
        if not api_key:
            st.error("Please provide an OpenAI API key in the sidebar")
        else:
            with st.spinner("Scraping and analyzing content..."):
                try:
                    scraper_tool = AIWebScraperTool(openai_api_key=api_key)
                    
                    options = {
                        'include_summary': include_summary,
                        'include_entities': include_entities,
                        'include_qa': bool(question),
                        'question': question,
                        'use_langchain': use_langchain
                    }
                    
                    result = scraper_tool.scrape_and_analyze(url, **options)
                    
                    if 'error' in result:
                        st.error(f"Error: {result['error']}")
                    else:
                        # Display results
                        st.success("✅ Scraping completed successfully!")
                        
                        # Basic info
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Word Count", result.get('word_count', 0))
                        with col2:
                            sentiment = result.get('sentiment', {})
                            st.metric("Sentiment", sentiment.get('sentiment', 'N/A'))
                        with col3:
                            confidence = sentiment.get('confidence', 0)
                            st.metric("Confidence", f"{confidence:.2f}" if confidence else "N/A")
                        
                        # Title and content preview
                        st.subheader("📄 Page Title")
                        st.write(result.get('title', 'No title found'))
                        
                        if result.get('content_preview'):
                            st.subheader("📖 Content Preview")
                            with st.expander("Show content preview", expanded=False):
                                st.write(result['content_preview'])
                        
                        # Summary
                        if result.get('summary'):
                            st.subheader("📝 AI Summary")
                            st.write(result['summary'])
                        
                        # Entities
                        if result.get('entities'):
                            st.subheader("🏷️ Extracted Entities")
                            entities = result['entities']
                            
                            # Create columns for different entity types
                            entity_cols = st.columns(3)
                            col_idx = 0
                            
                            for entity_type, entity_list in entities.items():
                                if entity_list and isinstance(entity_list, list) and len(entity_list) > 0:
                                    with entity_cols[col_idx % 3]:
                                        st.write(f"**{entity_type.title()}:**")
                                        for entity in entity_list[:5]:  # Show first 5
                                            st.write(f"• {entity}")
                                    col_idx += 1
                        
                        # Q&A Response
                        if result.get('qa_response'):
                            st.subheader("❓ Question & Answer")
                            st.write(f"**Q:** {question}")
                            st.write(f"**A:** {result['qa_response']}")
                        
                        # LangChain Results
                        if result.get('langchain_analysis'):
                            st.subheader("🔗 LangChain Analysis")
                            lc_result = result['langchain_analysis']
                            if lc_result.get('success'):
                                st.write("**Analysis:**")
                                st.write(lc_result.get('analysis', ''))
                                
                                structured_data = lc_result.get('structured_data', {})
                                if structured_data and 'error' not in structured_data:
                                    st.write("**Structured Data:**")
                                    st.json(structured_data)
                        
                        # Save to session state for history
                        if 'scraping_history' not in st.session_state:
                            st.session_state.scraping_history = []
                        st.session_state.scraping_history.append(result)
                        
                        # Download results
                        st.subheader("💾 Download Results")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            json_data = json.dumps(result, indent=2)
                            st.download_button(
                                "📄 Download JSON",
                                json_data,
                                file_name=f"scraping_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json"
                            )
                        
                        with col2:
                            # Create CSV data
                            csv_data = pd.DataFrame([{
                                'url': result.get('url', ''),
                                'title': result.get('title', ''),
                                'word_count': result.get('word_count', 0),
                                'summary': result.get('summary', ''),
                                'sentiment': sentiment.get('sentiment', ''),
                                'timestamp': result.get('timestamp', '')
                            }])
                            
                            st.download_button(
                                "📊 Download CSV",
                                csv_data.to_csv(index=False),
                                file_name=f"scraping_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

with tab2:
    st.header("Scrape Multiple URLs")
    
    # URL input methods
    input_method = st.radio(
        "Choose input method:",
        ["Text Area", "Upload File"]
    )
    
    urls = []
    
    if input_method == "Text Area":
        url_text = st.text_area(
            "Enter URLs (one per line):",
            placeholder="https://example1.com\nhttps://example2.com\nhttps://example3.com",
            height=150
        )
        if url_text:
            urls = [url.strip() for url in url_text.split('\n') if url.strip()]
    
    else:
        uploaded_file = st.file_uploader("Upload text file with URLs", type=['txt'])
        if uploaded_file:
            urls = [url.strip() for url in uploaded_file.getvalue().decode().split('\n') if url.strip()]
    
    if urls:
        st.write(f"Found {len(urls)} URLs to process")
        
        if st.button("🚀 Process All URLs", type="primary"):
            if not api_key:
                st.error("Please provide an OpenAI API key in the sidebar")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                scraper_tool = AIWebScraperTool(openai_api_key=api_key)
                results = []
                
                options = {
                    'include_summary': include_summary,
                    'include_entities': include_entities,
                    'use_langchain': use_langchain
                }
                
                for i, url in enumerate(urls):
                    status_text.text(f"Processing {i+1}/{len(urls)}: {url}")
                    
                    try:
                        result = scraper_tool.scrape_and_analyze(url, **options)
                        results.append(result)
                    except Exception as e:
                        results.append({"url": url, "error": str(e)})
                    
                    progress_bar.progress((i + 1) / len(urls))
                
                status_text.text("✅ Processing complete!")
                
                # Display results summary
                successful = len([r for r in results if 'error' not in r])
                failed = len(results) - successful
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total URLs", len(urls))
                with col2:
                    st.metric("Successful", successful)
                with col3:
                    st.metric("Failed", failed)
                
                # Show detailed results
                st.subheader("📊 Detailed Results")
                
                for i, result in enumerate(results, 1):
                    with st.expander(f"{i}. {result.get('title', result.get('url', 'Unknown'))[:100]}..."):
                        if 'error' in result:
                            st.error(f"Error: {result['error']}")
                        else:
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                st.write(f"**URL:** {result.get('url', '')}")
                                if result.get('summary'):
                                    st.write(f"**Summary:** {result['summary']}")
                            with col2:
                                st.write(f"**Words:** {result.get('word_count', 0)}")
                                sentiment = result.get('sentiment', {})
                                st.write(f"**Sentiment:** {sentiment.get('sentiment', 'N/A')}")
                
                # Save to session state
                if 'batch_results' not in st.session_state:
                    st.session_state.batch_results = []
                st.session_state.batch_results.extend(results)
                
                # Download batch results
                st.subheader("💾 Download Batch Results")
                
                # Prepare CSV data
                csv_rows = []
                for result in results:
                    if 'error' not in result:
                        sentiment = result.get('sentiment', {})
                        csv_rows.append({
                            'url': result.get('url', ''),
                            'title': result.get('title', ''),
                            'word_count': result.get('word_count', 0),
                            'summary': result.get('summary', ''),
                            'sentiment': sentiment.get('sentiment', ''),
                            'confidence': sentiment.get('confidence', ''),
                            'timestamp': result.get('timestamp', '')
                        })
                
                if csv_rows:
                    df = pd.DataFrame(csv_rows)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            "📊 Download Results CSV",
                            df.to_csv(index=False),
                            file_name=f"batch_scraping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    
                    with col2:
                        json_data = json.dumps(results, indent=2)
                        st.download_button(
                            "📄 Download Results JSON",
                            json_data,
                            file_name=f"batch_scraping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )

with tab3:
    st.header("📚 Results History")
    
    # Show scraping history
    if 'scraping_history' in st.session_state and st.session_state.scraping_history:
        st.write(f"You have {len(st.session_state.scraping_history)} results in history")
        
        # Summary statistics
        history = st.session_state.scraping_history
        total_words = sum([r.get('word_count', 0) for r in history])
        avg_words = total_words / len(history) if history else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Scraped", len(history))
        with col2:
            st.metric("Total Words", f"{total_words:,}")
        with col3:
            st.metric("Avg Words/Page", f"{avg_words:.0f}")
        
        # Display history
        for i, result in enumerate(reversed(history), 1):
            with st.expander(f"{i}. {result.get('title', 'Untitled')[:80]}..."):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**URL:** {result.get('url', '')}")
                    st.write(f"**Time:** {result.get('timestamp', '')}")
                    if result.get('summary'):
                        st.write(f"**Summary:** {result['summary'][:200]}...")
                
                with col2:
                    st.write(f"**Words:** {result.get('word_count', 0)}")
                    sentiment = result.get('sentiment', {})
                    st.write(f"**Sentiment:** {sentiment.get('sentiment', 'N/A')}")
        
        # Clear history button
        if st.button("🗑️ Clear History"):
            st.session_state.scraping_history = []
            st.success("History cleared!")
            st.rerun()
    
    else:
        st.info("No scraping history yet. Start by scraping some URLs!")

# Footer
st.markdown("---")
st.markdown(
    "**AI Web Scraper Tool** - Built with Streamlit, BeautifulSoup, and OpenAI API | "
    "Made for extracting and analyzing web content with AI-powered insights"
)
