# scraper.py
import requests
from bs4 import BeautifulSoup, Comment
import time
import random
from urllib.parse import urljoin, urlparse
import re

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_page(self, url, delay=1):
        """Scrape content from a single webpage"""
        try:
            # Add random delay to avoid being blocked
            time.sleep(random.uniform(delay, delay + 1))
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract different content types
            content = {
                'url': url,
                'title': self._extract_title(soup),
                'main_content': self._extract_main_content(soup),
                'metadata': self._extract_metadata(soup),
                'links': self._extract_links(soup, url),
                'images': self._extract_images(soup, url)
            }
            
            return content
            
        except Exception as e:
            return {'error': str(e), 'url': url}
    
    def _extract_title(self, soup):
        """Extract page title"""
        title_tag = soup.find('title')
        if title_tag:
            try:
                title = title_tag.get_text()
                return title.strip() if isinstance(title, str) else "No title found"
            except (AttributeError, TypeError):
                return "No title found"
        return "No title found"
    
    def _extract_main_content(self, soup):
        """Extract main textual content, removing navigation and ads"""
        # Create a copy to preserve original
        soup_copy = BeautifulSoup(str(soup), 'html.parser')
        
        # Remove unwanted elements
        unwanted_tags = ['nav', 'header', 'footer', 'aside', 'script', 'style', 'noscript', 'iframe', 'embed']
        for tag in unwanted_tags:
            for element in soup_copy.find_all(tag):
                element.decompose()
        
        # Remove ads and promotional content (more comprehensive)
        ad_patterns = [
            re.compile(r'ad[s]?[-_]?', re.I),
            re.compile(r'advertisement', re.I),
            re.compile(r'promo', re.I),
            re.compile(r'sidebar', re.I),
            re.compile(r'popup', re.I),
            re.compile(r'banner', re.I),
            re.compile(r'sponsor', re.I),
            re.compile(r'widget', re.I)
        ]
        
        for pattern in ad_patterns:
            for element in soup_copy.find_all(class_=pattern):
                element.decompose()
            for element in soup_copy.find_all(id=pattern):
                element.decompose()
        
        # Remove comments
        for comment in soup_copy.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        
        # Extended content selectors (prioritized by likelihood of containing main content)
        content_selectors = [
            'article',
            '.content',
            '.post-content',
            '.entry-content',
            '.post',
            '.entry', 
            'main',
            '.article-body',
            '.story-body',
            '.post-body',
            '.content-body',
            '#content',
            '#main-content',
            '.main-content',
            '[role="main"]',
            '.article',
            '.story',
            '.text',
            '.body'
        ]
        
        main_content = ""
        
        # Try each selector
        for selector in content_selectors:
            content_element = soup_copy.select_one(selector)
            if content_element:
                try:
                    text = content_element.get_text(separator=' ', strip=True)
                    # Ensure text is a string and not empty
                    if isinstance(text, str) and len(text.split()) >= 10:  # At least 10 words
                        main_content = text
                        break
                except (AttributeError, TypeError) as e:
                    # Skip this element if get_text fails
                    continue
        
        # Enhanced fallback strategies
        if not main_content or len(main_content.split()) < 10:
            # Strategy 1: All paragraphs
            paragraphs = soup_copy.find_all('p')
            if paragraphs:
                p_texts = []
                for p in paragraphs:
                    try:
                        text = p.get_text()
                        if isinstance(text, str) and text.strip():
                            p_texts.append(text.strip())
                    except (AttributeError, TypeError):
                        continue
                p_text = ' '.join(p_texts)
                if len(p_text.split()) >= 10:
                    main_content = p_text
        
        if not main_content or len(main_content.split()) < 10:
            # Strategy 2: Divs with substantial text
            divs = soup_copy.find_all('div')
            div_texts = []
            for div in divs:
                try:
                    text = div.get_text(separator=' ', strip=True)
                    if isinstance(text, str) and 50 <= len(text) <= 5000:  # Reasonable content length
                        div_texts.append(text)
                except (AttributeError, TypeError):
                    continue
            if div_texts:
                main_content = max(div_texts, key=len)
        
        if not main_content or len(main_content.split()) < 5:
            # Strategy 3: Body text as last resort
            body = soup_copy.find('body')
            if body:
                try:
                    text = body.get_text(separator=' ', strip=True)
                    if isinstance(text, str):
                        main_content = text
                except (AttributeError, TypeError):
                    main_content = ""
        
        return main_content if main_content else ""
    
    def _extract_metadata(self, soup):
        """Extract metadata like description, keywords, author"""
        metadata = {}
        
        # Description
        desc_tag = soup.find('meta', attrs={'name': 'description'}) or \
                  soup.find('meta', attrs={'property': 'og:description'})
        if desc_tag:
            metadata['description'] = desc_tag.get('content', '')
        
        # Keywords
        keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_tag:
            metadata['keywords'] = keywords_tag.get('content', '')
        
        # Author
        author_tag = soup.find('meta', attrs={'name': 'author'})
        if author_tag:
            metadata['author'] = author_tag.get('content', '')
        
        return metadata
    
    def _extract_links(self, soup, base_url):
        """Extract all links from the page"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            try:
                text = link.get_text()
                link_text = text.strip() if isinstance(text, str) else ""
            except (AttributeError, TypeError):
                link_text = ""
            
            links.append({
                'text': link_text,
                'url': absolute_url
            })
        return links[:20]  # Limit to first 20 links
    
    def _extract_images(self, soup, base_url):
        """Extract image URLs"""
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            absolute_url = urljoin(base_url, src)
            images.append({
                'url': absolute_url,
                'alt': img.get('alt', ''),
                'title': img.get('title', '')
            })
        return images[:10]  # Limit to first 10 images
