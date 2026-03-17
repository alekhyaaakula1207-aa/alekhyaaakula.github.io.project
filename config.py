# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Suppress gRPC verbose logging to avoid ALTS credentials warnings
os.environ.setdefault('GRPC_VERBOSITY', 'ERROR')
os.environ.setdefault('GRPC_TRACE', '')

class Config:
    # API Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Scraping Configuration
    SCRAPING_DELAY = float(os.getenv('SCRAPING_DELAY', 1.0))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 10))
    USER_AGENT = os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    # AI Processing Configuration
    MAX_TOKENS_SUMMARY = 200
    MAX_TOKENS_ENTITIES = 400
    MAX_TOKENS_QA = 300
    TEMPERATURE = 0.3
    
    # Content Processing
    MAX_CONTENT_LENGTH = 4000
    MIN_CONTENT_LENGTH = 100
    
    # Output Configuration
    DEFAULT_OUTPUT_FORMAT = 'json'
    MAX_URLS_BATCH = 50
