"""
Vercel Web Analytics integration for Streamlit

This module provides a helper function to inject Vercel Web Analytics
into a Streamlit application using HTML components.
"""

import streamlit as st
import streamlit.components.v1 as components


def inject_vercel_analytics():
    """
    Inject Vercel Web Analytics script into the Streamlit app.
    
    This function uses Streamlit's HTML component to inject the Vercel Analytics
    tracking script. The analytics will only track page views when deployed on Vercel.
    
    Usage:
        Call this function once in your main Streamlit app, typically at the top
        of your script after st.set_page_config():
        
        import vercel_analytics
        vercel_analytics.inject_vercel_analytics()
    """
    
    # Vercel Analytics tracking script
    # This follows the HTML5 implementation from Vercel's documentation
    analytics_html = """
    <script>
      window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
    </script>
    <script defer src="/_vercel/insights/script.js"></script>
    """
    
    # Inject the analytics script into the page
    components.html(analytics_html, height=0, width=0)


def inject_vercel_speed_insights():
    """
    Inject Vercel Speed Insights script into the Streamlit app.
    
    This function adds Vercel Speed Insights to track Web Vitals metrics.
    Speed Insights is a separate feature from Web Analytics.
    
    Usage:
        Call this function in your main Streamlit app if you also want
        to track performance metrics:
        
        import vercel_analytics
        vercel_analytics.inject_vercel_speed_insights()
    """
    
    # Vercel Speed Insights tracking script
    speed_insights_html = """
    <script defer src="/_vercel/speed-insights/script.js"></script>
    """
    
    # Inject the speed insights script into the page
    components.html(speed_insights_html, height=0, width=0)
