import streamlit as st
import os
import pandas as pd
from googleapiclient.discovery import build
import google.generativeai as genai

# --- PAGE CONFIG ---
st.set_page_config(page_title="YT Market Intelligence", page_icon="📊", layout="wide")

st.title("📈 YouTube Market Intelligence Dashboard")
st.markdown("---")

# --- SECURE API KEY LOADING ---
yt_api_key = os.environ.get("YOUTUBE_API_KEY")

# --- USER INPUT ---
st.subheader("1. Enter Target Channel")
channel_id = st.text_input("Enter the YouTube Channel ID:")

if st.button("Run Market Analysis"):
    if not yt_api_key:
        st.warning("API key missing in Render settings.")
    elif not channel_id:
        st.warning("Please enter a Channel ID.")
    else:
        try:
            with st.spinner("Analyzing channel performance..."):
                youtube = build('youtube', 'v3', developerKey=yt_api_key)
                
                # Fetch basic channel stats
                ch_req = youtube.channels().list(part='statistics,contentDetails', id=channel_id).execute()
                stats = ch_req['items'][0]['statistics']
                uploads_id = ch_req['items'][0]['contentDetails']['relatedPlaylists']['uploads']
                
                # --- DISPLAY OVERVIEW ---
                col1, col2, col3 = st.columns(3)
                col1.metric("Subscribers", stats.get('subscriberCount', '0'))
                col2.metric("Total Views", stats.get('viewCount', '0'))
                col3.metric("Video Count", stats.get('videoCount', '0'))

                # --- FETCH LAST 50 VIDEOS ---
                res = youtube.playlistItems().list(playlistId=uploads_id, part='snippet,contentDetails', maxResults=50).execute()
                video_ids = [item['contentDetails']['videoId'] for item in res['items']]
                
                # Get stats for these 50 videos
                v_res = youtube.videos().list(id=','.join(video_ids), part='statistics,snippet').execute()
                
                video_data = []
                for v in v_res['items']:
                    video_data.append({
                        'Title': v['snippet']['title'],
                        'Views': int(v['statistics'].get('viewCount', 0)),
                        'Link': f"https://www.youtube.com/watch?v={v['id']}"
                    })
                
                df = pd.DataFrame(video_data)
                
                # --- IDENTIFY VIRAL OUTLIER ---
                avg_views = df['Views'].mean()
                viral_video = df.loc[df['Views'].idxmax()]
                
                st.markdown("---")
                st.subheader("🔥 Viral Performance Analysis")
                st.write(f"The average views for the last 50 videos is **{int(avg_views):,}**.")
                
                st.info(f"**Most Viral Video Found:** {viral_video['Title']}")
                st.write(f"🎯 **Views:** {viral_video['Views']:,} (This is {round(viral_video['Views']/avg_views, 1)}x higher than average!)")
                st.write(f"🔗 [Watch Video]({viral_video['Link']})")

        except Exception as e:
            st.error(f"Something went wrong: {e}")
