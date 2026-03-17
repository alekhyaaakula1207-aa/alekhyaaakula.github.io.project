#!/bin/bash
# setup.sh

echo "Setting up AI Web Scraper Tool..."

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p data
mkdir -p logs
mkdir -p tests

# Copy example environment file
cp .env.example .env

echo "Setup complete! Please edit .env file with your API keys."
echo "Run 'streamlit run streamlit_app.py' to start the web interface."
