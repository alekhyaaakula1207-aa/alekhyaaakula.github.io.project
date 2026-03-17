# AI-web-scraper
An intelligent web scraping tool that combines traditional data extraction with AI-powered content analysis and summarization.

---

## Problem Statement:
Traditional web scrapers only extract raw text/HTML, requiring manual cleaning and structuring. Non-technical users struggle with writing scrapers. There’s a need for an AI-powered tool that can:

- Scrape data from websites,
- Clean & structure it,
- Use LLMs to summarize, analyze, or generate insights.

---

# Project Goal:
Build a Python-based AI Web Scraper Tool that allows users to input a URL and get structured, summarized, or analyzed content using LLMs.

---

## Features

- **Smart Web Scraping**: Extract content from any webpage with automatic cleaning
- **AI-Powered Analysis**: Generate summaries, extract entities, and answer questions
- **Multiple Interfaces**: Both CLI and web-based GUI
- **Flexible Output**: Export results in JSON or CSV formats
- **Batch Processing**: Handle multiple URLs simultaneously
- **Content Cleaning**: Automatically remove ads, navigation, and irrelevant content

---

## Output: 

- JSON
- CSV
- Plain text.

---

## Vercel Web Analytics

This project is configured with Vercel Web Analytics to track page views and user interactions when deployed on Vercel.

### How it works:
- Analytics tracking is automatically enabled when the app is deployed on Vercel
- The `vercel_analytics.py` module injects the Vercel Analytics script into the Streamlit app
- Analytics data can be viewed in your Vercel project dashboard under the Analytics tab

### To enable analytics:
1. Deploy this project to Vercel
2. Navigate to your project settings in the Vercel dashboard
3. Go to the Analytics tab and click "Enable"
4. Analytics will start tracking page views automatically

No additional configuration is needed in the code - the analytics script is already integrated!