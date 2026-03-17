# langchain_processor.py
from langchain.chains import LLMChain, SequentialChain
from langchain.prompts import PromptTemplate
# Import the Gemini model from the correct library
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
import os

class ExtractedData(BaseModel):
    summary: str = Field(description="Summary of the content")
    key_points: List[str] = Field(description="List of key points")
    entities: dict = Field(description="Extracted entities")
    category: str = Field(description="Content category")

class LangChainProcessor:
    def __init__(self, api_key=None):
        """
        Initialize the processor with the Gemini model.
        It uses the provided api_key or falls back to the GOOGLE_API_KEY environment variable.
        """
        try:
            # Try to use Google's API key from environment or parameter
            google_api_key = api_key or os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
            
            if not google_api_key:
                print("Warning: No Google/Gemini API key found. LangChain features will be disabled.")
                self.llm = None
                self.output_parser = None
                return
            
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-pro", # Specify the Gemini model
                temperature=0.3,
                google_api_key=google_api_key # Use Google's API key
            )
            self.output_parser = PydanticOutputParser(pydantic_object=ExtractedData)
        except Exception as e:
            print(f"Warning: Failed to initialize LangChain processor: {str(e)}")
            print("LangChain features will be disabled.")
            self.llm = None
            self.output_parser = None
    
    def create_processing_chain(self):
        """Create a sequential chain for comprehensive content processing"""
        if not self.llm:
            raise Exception("LangChain processor not initialized")
        
        # First chain: Content Analysis
        # This chain remains the same as its logic is model-agnostic.
        analysis_template = """
        Analyze the following webpage content and extract key insights:
        
        Content: {content}
        
        Provide:
        1. Main topic/theme
        2. Content type (news, blog, product, academic, etc.)
        3. Target audience
        4. Key concepts mentioned
        
        Analysis:
        """
        
        analysis_prompt = PromptTemplate(
            template=analysis_template,
            input_variables=["content"]
        )
        
        analysis_chain = LLMChain(
            llm=self.llm,
            prompt=analysis_prompt,
            output_key="analysis"
        )
        
        # Second chain: Structured Extraction
        # This chain also remains the same.
        extraction_template = """
        Based on the content analysis below, create a structured summary:
        
        Original Content: {content}
        Analysis: {analysis}
        
        {format_instructions}
        
        Structured Output:
        """
        
        extraction_prompt = PromptTemplate(
            template=extraction_template,
            input_variables=["content", "analysis"],
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()}
        )
        
        extraction_chain = LLMChain(
            llm=self.llm,
            prompt=extraction_prompt,
            output_key="structured_data"
        )
        
        # Combine chains
        # The SequentialChain structure is unchanged.
        overall_chain = SequentialChain(
            chains=[analysis_chain, extraction_chain],
            input_variables=["content"],
            output_variables=["analysis", "structured_data"],
            verbose=True
        )
        
        return overall_chain
    
    def process_content(self, content):
        """Process content through the chain"""
        # Check if LangChain is properly initialized
        if not self.llm:
            return {
                "error": "LangChain processor not initialized (missing API key or initialization failed)",
                "success": False
            }
        
        # The processing and error handling logic is unchanged.
        try:
            chain = self.create_processing_chain()
            result = chain({"content": content[:3500]})  # Gemini can often handle slightly more context
            
            # Parse the structured output
            try:
                structured_data = self.output_parser.parse(result["structured_data"])
                return {
                    "analysis": result["analysis"],
                    "structured_data": structured_data.dict(),
                    "success": True
                }
            except Exception as e:
                # Fallback if parsing fails
                return {
                    "analysis": result["analysis"],
                    "structured_data": {"error": f"Parsing error: {str(e)}"},
                    "success": False
                }
                
        except Exception as e:
            return {
                "error": f"Chain processing error: {str(e)}",
                "success": False
            }