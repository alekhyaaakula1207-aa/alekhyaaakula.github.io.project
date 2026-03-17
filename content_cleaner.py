# content_cleaner.py
import re
from bs4 import BeautifulSoup
import pandas as pd

class ContentCleaner:
    def __init__(self):
        self.noise_patterns = [
            r'\s+',  # Multiple whitespaces
            r'[\r\n\t]+',  # Line breaks and tabs
            r'[^\w\s\.\,\!\?\;\:\-\(\)]',  # Special characters except basic punctuation
        ]
    
    def clean_scraped_data(self, content_dict):
        """Clean and structure scraped content"""
        cleaned_content = {}
        
        for key, value in content_dict.items():
            if key == 'main_content':
                cleaned_content[key] = self._clean_text(value)
            elif key == 'title':
                cleaned_content[key] = self._clean_title(value)
            elif key == 'metadata':
                cleaned_content[key] = self._clean_metadata(value)
            elif key == 'links':
                cleaned_content[key] = self._clean_links(value)
            else:
                cleaned_content[key] = value
        
        return cleaned_content
    
    def _clean_text(self, text):
        """Clean main text content"""
        if not text:
            return ""
        
        # Ensure text is a string
        if not isinstance(text, str):
            try:
                text = str(text)
            except:
                return ""
        
        # Remove HTML entities
        try:
            text = BeautifulSoup(text, 'html.parser').get_text()
        except:
            # If BeautifulSoup fails, just use the original text
            pass
        
        # Ensure we still have a string after BeautifulSoup processing
        if not isinstance(text, str):
            return ""
        
        # More gentle cleaning - preserve structure
        # Replace multiple whitespaces with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Remove control characters but keep basic punctuation
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        # Clean up common web artifacts
        text = re.sub(r'(Cookie|Privacy Policy|Terms of Service|Subscribe|Sign up)[\w\s]*', '', text, flags=re.IGNORECASE)
        
        # Remove extra whitespaces
        text = ' '.join(text.split())
        
        # Less aggressive line filtering - keep sentences with at least 3 words
        sentences = re.split(r'[.!?]+', text)
        meaningful_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            # Keep sentences with at least 3 words and reasonable length
            if len(sentence.split()) >= 3 and 10 <= len(sentence) <= 1000:
                meaningful_sentences.append(sentence)
        
        # If we filtered too aggressively and have very little content, be more lenient
        if len(meaningful_sentences) < 3 and len(sentences) > 0:
            # Fallback: keep sentences with at least 2 words
            meaningful_sentences = [s.strip() for s in sentences 
                                  if len(s.strip().split()) >= 2 and len(s.strip()) >= 5]
        
        result = '. '.join(meaningful_sentences)
        
        # Final check: if result is too short, return original cleaned text
        if len(result.split()) < 10 and len(text.split()) >= 10:
            return text.strip()
        
        return result.strip() if result else text.strip()
    
    def _clean_title(self, title):
        """Clean page title"""
        # Remove site name patterns
        title = re.sub(r'\s*[\|\-\–]\s*.*$', '', title)
        return title.strip()
    
    def _clean_metadata(self, metadata):
        """Clean metadata fields"""
        cleaned_meta = {}
        for key, value in metadata.items():
            if value:
                cleaned_meta[key] = self._clean_text(value)
        return cleaned_meta
    
    def _clean_links(self, links):
        """Clean and filter links"""
        cleaned_links = []
        for link in links:
            if link['text'] and len(link['text'].strip()) > 3:
                cleaned_links.append({
                    'text': self._clean_text(link['text']),
                    'url': link['url']
                })
        return cleaned_links
