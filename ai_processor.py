# ai_processor.py
import os
import json
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class AIProcessor:
    def __init__(self, api_key=None):
        """Initialize the AI processor with Gemini API"""
        self.api_key = api_key or os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        self.client = None
        
        if not self.api_key:
            print("Warning: No Gemini API key found. AI features will be disabled.")
            print("Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable to enable AI features.")
            return
        
        # Initialize the Gemini client with error handling
        try:
            self.client = genai.Client(api_key=self.api_key)
            
            # Default model configuration
            self.default_config = types.GenerateContentConfig(
                temperature=0.3,
                top_k=40,
                top_p=0.95,
                max_output_tokens=1024,
            )
        except Exception as e:
            print(f"Warning: Failed to initialize Gemini client: {str(e)}")
            print("AI features will be disabled.")
            self.client = None
    
    def __del__(self):
        """Properly close the client when object is destroyed"""
        self.close()
    
    def close(self):
        """Safely close the Gemini client"""
        if self.client and hasattr(self.client, 'close'):
            try:
                self.client.close()
            except (AttributeError, Exception):
                # Ignore errors during cleanup
                pass
            finally:
                self.client = None
    
    def _is_client_available(self):
        """Check if the client is properly initialized"""
        return self.client is not None
    
    def _safe_clean_response(self, response_text):
        """Safely clean response text and handle error cases"""
        if not response_text or not isinstance(response_text, str):
            return None
            
        if "not initialized" in response_text or "Error:" in response_text:
            return None
            
        clean_response = response_text.strip()
        if clean_response.startswith('```json'):
            clean_response = clean_response[7:]
        elif clean_response.startswith('```'):
            clean_response = clean_response[3:]
        if clean_response.endswith('```'):
            clean_response = clean_response[:-3]
        return clean_response.strip()
    
    def _make_request_with_retry(self, model, contents, config=None, max_retries=3):
        """Make API request with retry logic for error handling"""
        if not self._is_client_available():
            return "AI processor not initialized (missing API key or client error)"
        
        retry_count = 0
        delay = 1
        
        while retry_count < max_retries:
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config or self.default_config
                )
                
                # Check if response has text
                if hasattr(response, 'text') and response.text:
                    return response.text.strip()
                else:
                    # Handle case where response might be blocked or empty
                    return "Response was blocked or empty. Please try a different prompt."
                    
            except Exception as e:
                error_msg = str(e).lower()
                
                # Handle specific error types
                if '429' in error_msg or 'quota' in error_msg or 'rate limit' in error_msg:
                    print(f"Rate limit exceeded. Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                    retry_count += 1
                    
                elif '500' in error_msg or 'internal error' in error_msg:
                    print(f"Server error. Retrying in {delay} seconds...")
                    time.sleep(delay)
                    retry_count += 1
                    
                elif 'blocked' in error_msg or 'safety' in error_msg:
                    return "Content was blocked due to safety filters. Please modify your input."
                    
                else:
                    # For other errors, don't retry
                    return f"Error: {str(e)}"
        
        return "Maximum retries exceeded. Please try again later."
    
    def summarize_content(self, content, max_length=150):
        """Summarize webpage content using Gemini"""
        try:
            # Limit content to avoid token limits
            truncated_content = content[:4000] if len(content) > 4000 else content
            
            prompt = f"""
            Summarize the following webpage content in a clear and concise manner:
            
            Content: {truncated_content}
            
            Requirements:
            - Maximum {max_length} words
            - Focus on key points and main ideas
            - Use clear, professional language
            - Provide a comprehensive but brief overview
            """
            
            # Custom config for summarization
            summary_config = types.GenerateContentConfig(
                temperature=0.2,
                top_k=40,
                top_p=0.8,
                max_output_tokens=300,
            )
            
            return self._make_request_with_retry(
                model="gemini-2.0-flash-exp",
                contents=[prompt],
                config=summary_config
            )
            
        except Exception as e: # Catch any other unexpected errors
            return f"Error in summarization: {str(e)}"
    
    def extract_entities(self, content):
        """Extract named entities, prices, dates, etc. using Gemini"""
        try:
            # Limit content to avoid token limits
            truncated_content = content[:3000] if len(content) > 3000 else content
            
            prompt = f"""
            Extract key entities from the following content and return them in JSON format:
            
            Content: {truncated_content}
            
            Extract and categorize the following entities:
            - People: Names of individuals mentioned
            - Organizations: Companies, institutions, groups
            - Locations: Cities, countries, places, addresses
            - Dates: Specific dates, years, time periods
            - Prices: Money amounts, costs, financial figures
            - Products: Product names, services, technologies
            - Topics: Main themes, subjects, categories discussed
            
            Return ONLY valid JSON in this exact format:
            {{
                "people": ["name1", "name2"],
                "organizations": ["org1", "org2"],
                "locations": ["location1", "location2"],
                "dates": ["date1", "date2"],
                "prices": ["price1", "price2"],
                "products": ["product1", "product2"],
                "topics": ["topic1", "topic2"]
            }}
            
            If no entities are found for a category, use an empty array [].
            """
            
            # Custom config for entity extraction
            entity_config = types.GenerateContentConfig(
                temperature=0.1,
                top_k=20,
                top_p=0.9,
                max_output_tokens=500,
            )
            
            response_text = self._make_request_with_retry(
                model="gemini-2.0-flash-exp",
                contents=[prompt],
                config=entity_config
            )
            
            # Parse JSON response
            try:
                # Use safe cleaning helper
                clean_response = self._safe_clean_response(response_text)
                if clean_response is None:
                    return {
                        "people": [], "organizations": [], "locations": [], 
                        "dates": [], "prices": [], "products": [], "topics": [],
                        "error": "AI processor not available"
                    }
                
                entities = json.loads(clean_response)
                
                # Validate the structure
                expected_keys = ["people", "organizations", "locations", "dates", "prices", "products", "topics"]
                for key in expected_keys:
                    if key not in entities:
                        entities[key] = []
                
                return entities
                
            except json.JSONDecodeError as json_error:
                print(f"JSON parsing error: {json_error}")
                print(f"Raw response: {response_text}")
                return {
                    "people": [],
                    "organizations": [],
                    "locations": [],
                    "dates": [],
                    "prices": [],
                    "products": [],
                    "topics": [],
                    "error": "Could not parse entities into JSON format",
                    "raw_response": response_text
                }
            
        except Exception as e:
            return {"error": f"Error in entity extraction: {str(e)}"}
    
    def answer_question(self, content, question):
        """Answer questions about scraped content using Gemini"""
        try:
            # Limit content to avoid token limits
            truncated_content = content[:3500] if len(content) > 3500 else content
            
            prompt = f"""
            Based on the following webpage content, answer this question: {question}
            
            Content: {truncated_content}
            
            Instructions:
            - Provide a clear, accurate answer based only on the content provided
            - If the answer cannot be found in the content, explicitly state "The information is not available in the provided content."
            - Be specific and cite relevant details from the content when possible
            - Keep the answer concise but comprehensive
            """
            
            # Custom config for Q&A
            qa_config = types.GenerateContentConfig(
                temperature=0.2,
                top_k=40,
                top_p=0.9,
                max_output_tokens=400,
            )
            
            return self._make_request_with_retry(
                model="gemini-2.0-flash-exp",
                contents=[prompt],
                config=qa_config
            )
            
        except Exception as e:
            return f"Error answering question: {str(e)}"
    
    def analyze_sentiment(self, content):
        """Analyze sentiment of the content using Gemini"""
        try:
            # Limit content to avoid token limits
            truncated_content = content[:2000] if len(content) > 2000 else content
            
            prompt = f"""
            Analyze the sentiment of the following content and provide a detailed analysis:
            
            Content: {truncated_content}
            
            Provide your analysis in JSON format with these exact keys:
            - sentiment: Overall sentiment (Positive/Negative/Neutral)
            - confidence: Confidence score between 0.0 and 1.0
            - indicators: Array of key emotional indicators or phrases that influenced the sentiment
            - reasoning: Brief explanation of why this sentiment was determined
            
            Return ONLY valid JSON in this format:
            {{
                "sentiment": "Positive/Negative/Neutral",
                "confidence": 0.85,
                "indicators": ["phrase1", "phrase2", "phrase3"],
                "reasoning": "Brief explanation of the sentiment analysis"
            }}
            """
            
            # Custom config for sentiment analysis
            sentiment_config = types.GenerateContentConfig(
                temperature=0.1,
                top_k=20,
                top_p=0.8,
                max_output_tokens=300,
            )
            
            response_text = self._make_request_with_retry(
                model="gemini-2.0-flash-exp",
                contents=[prompt],
                config=sentiment_config
            )
            
            try:
                # Use safe cleaning helper
                clean_response = self._safe_clean_response(response_text)
                if clean_response is None:
                    return {
                        "sentiment": "Neutral",
                        "confidence": 0.5,
                        "indicators": [],
                        "reasoning": "AI processor not available",
                        "error": response_text or "Empty response"
                    }
                
                sentiment_data = json.loads(clean_response)
                
                # Validate and ensure required keys exist
                if "sentiment" not in sentiment_data:
                    sentiment_data["sentiment"] = "Neutral"
                if "confidence" not in sentiment_data:
                    sentiment_data["confidence"] = 0.5
                if "indicators" not in sentiment_data:
                    sentiment_data["indicators"] = []
                if "reasoning" not in sentiment_data:
                    sentiment_data["reasoning"] = "Unable to determine reasoning"
                
                # Ensure confidence is between 0 and 1
                try:
                    confidence = float(sentiment_data["confidence"])
                    sentiment_data["confidence"] = max(0.0, min(1.0, confidence))
                except (ValueError, TypeError):
                    sentiment_data["confidence"] = 0.5
                
                return sentiment_data
                
            except json.JSONDecodeError as json_error:
                print(f"JSON parsing error in sentiment analysis: {json_error}")
                print(f"Raw response: {response_text}")
                return {
                    "sentiment": "Neutral",
                    "confidence": 0.5,
                    "indicators": [],
                    "reasoning": "Could not parse sentiment analysis response",
                    "error": "JSON parsing failed",
                    "raw_response": response_text
                }
                
        except Exception as e:
            return {"error": f"Error in sentiment analysis: {str(e)}"}
    
    def generate_keywords(self, content, max_keywords=10):
        """Extract key keywords and phrases from content"""
        try:
            truncated_content = content[:2500] if len(content) > 2500 else content
            
            prompt = f"""
            Extract the most important keywords and phrases from the following content:
            
            Content: {truncated_content}
            
            Return up to {max_keywords} keywords/phrases that best represent the main topics and themes.
            Format as a JSON array of strings:
            ["keyword1", "keyword2", "phrase with multiple words", ...]
            
            Focus on:
            - Main topics and themes
            - Important proper nouns
            - Key technical terms
            - Significant concepts
            """
            
            keyword_config = types.GenerateContentConfig(
                temperature=0.2,
                top_k=30,
                top_p=0.9,
                max_output_tokens=200,
            )
            
            response_text = self._make_request_with_retry(
                model="gemini-2.0-flash-exp",
                contents=[prompt],
                config=keyword_config
            )
            
            try:
                # Clean and parse JSON response
                clean_response = response_text.strip()
                if clean_response.startswith('```'):
                    clean_response = clean_response[7:]
                if clean_response.endswith('```'):
                    clean_response = clean_response[:-3]
                clean_response = clean_response.strip()
                
                keywords = json.loads(clean_response)
                
                # Ensure it's a list
                if isinstance(keywords, list):
                    return keywords[:max_keywords]  # Limit to requested number
                else:
                    return []
                    
            except json.JSONDecodeError:
                # Fallback: try to extract keywords from plain text response
                lines = response_text.strip().split('\n')
                keywords = []
                for line in lines:
                    line = line.strip('- •*').strip()
                    if line and len(keywords) < max_keywords:
                        keywords.append(line)
                return keywords
                
        except Exception as e:
            return [f"Error extracting keywords: {str(e)}"]
    
    def classify_content(self, content):
        """Classify the type and category of content"""
        try:
            truncated_content = content[:2000] if len(content) > 2000 else content
            
            prompt = f"""
            Classify the following content and determine its category and characteristics:
            
            Content: {truncated_content}
            
            Analyze and return JSON with these classifications:
            {{
                "content_type": "news/blog/academic/product/tutorial/documentation/other",
                "subject_area": "technology/business/health/education/entertainment/other",
                "reading_level": "basic/intermediate/advanced",
                "purpose": "inform/persuade/entertain/instruct/sell",
                "target_audience": "general/professional/academic/technical/consumer"
            }}
            """
            
            classify_config = types.GenerateContentConfig(
                temperature=0.1,
                top_k=20,
                top_p=0.8,
                max_output_tokens=150,
            )
            
            response_text = self._make_request_with_retry(
                model="gemini-2.0-flash-exp",
                contents=[prompt],
                config=classify_config
            )
            
            try:
                clean_response = response_text.strip()
                if clean_response.startswith('```'):
                    clean_response = clean_response[7:]
                if clean_response.endswith('```'):
                    clean_response = clean_response[:-3]
                clean_response = clean_response.strip()
                
                classification = json.loads(clean_response)
                return classification
                
            except json.JSONDecodeError:
                return {
                    "content_type": "other",
                    "subject_area": "other",
                    "reading_level": "intermediate",
                    "purpose": "inform",
                    "target_audience": "general",
                    "error": "Could not parse classification response"
                }
                
        except Exception as e:
            return {"error": f"Error in content classification: {str(e)}"}

# Example usage and testing
if __name__ == "__main__":
    # Test the AI processor
    try:
        processor = AIProcessor()
        
        test_content = """
        Artificial Intelligence (AI) has revolutionized various industries in recent years. 
        Companies like Google, Microsoft, and OpenAI have invested billions in AI research. 
        The technology is being used in healthcare, finance, and autonomous vehicles. 
        AI models can now understand and generate human-like text, analyze images, and even create art.
        """
        
        print("Testing AI Processor with Gemini API...")
        print("-" * 50)
        
        # Test summarization
        print("1. Summary:")
        summary = processor.summarize_content(test_content, max_length=50)
        print(summary)
        print()
        
        # Test entity extraction
        print("2. Entities:")
        entities = processor.extract_entities(test_content)
        print(json.dumps(entities, indent=2))
        print()
        
        # Test Q&A
        print("3. Q&A:")
        answer = processor.answer_question(test_content, "What companies are mentioned?")
        print(answer)
        print()
        
        # Test sentiment analysis
        print("4. Sentiment:")
        sentiment = processor.analyze_sentiment(test_content)
        print(json.dumps(sentiment, indent=2))
        print()
        
    except Exception as e:
        print(f"Error testing AI processor: {e}")
        print("Make sure to set your GEMINI_API_KEY environment variable.")
