import streamlit as st
import os
import pandas as pd
from googleapiclient.discovery import build
import google.generativeai as genai

# --- PAGE CONFIGURATION ---
# This sets up how your dashboard looks when opened
st.set_page_config(page_title="YT Market Intelligence", page_icon="📊", layout="wide")

st.title("📈 YouTube Market Intelligence Dashboard")
st.write("Identify channel trends, outliers, and use AI to decode viral success.")
st.markdown("---")

# --- SECURE API KEY LOADING ---
# We use os.environ so your keys stay completely hidden when we host it online!
yt_api_key = os.environ.get("YOUTUBE_API_KEY")
gemini_api_key = os.environ.get("GEMINI_API_KEY")

# --- USER INPUT ---
st.subheader("1. Enter Target Channel")
channel_id = st.text_input("Enter the YouTube Channel ID (e.g., UCc_1xVj1N1Q...):")

if st.button("Run Market Analysis"):
    # Safety Check: Did we put the keys in Render yet?
    if not yt_api_key or not gemini_api_key:
        st.warning("⚠️ API keys not detected! (Don't worry, we will set these up securely in Render in the next step).")
    
    elif not channel_id:
        st.warning("Please enter a valid Channel ID.")
        
    else:
        try:
            with st.spinner("Connecting to YouTube Database..."):
                # Talk to YouTube
                youtube = build('youtube', 'v3', developerKey=yt_api_key)
                
                # Fetch basic channel statistics
                ch_request = youtube.channels().list(part='statistics', id=channel_id)
                ch_response = ch_request.execute()
                
                stats = ch_response['items'][0]['statistics']
                
                # --- VISUAL DASHBOARD ---
                st.subheader("📺 Channel Overview")
                
                # Create 3 neat columns for our metrics
                col1, col2, col3 = st.columns(3)
                col1.metric("Subscribers", stats.get('subscriberCount', 'Hidden'))
                col2.metric("Total Views", stats.get('viewCount', '0'))
                col3.metric("Total Videos", stats.get('videoCount', '0'))

                st.success("✅ Secure connection established! Dashboard UI is active.")
                st.info("AI Viral Analysis module ready to deploy.")
                
        except Exception as e:
            st.error("❌ Could not fetch data. Please check if the Channel ID is correct.")
