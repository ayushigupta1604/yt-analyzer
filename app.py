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
gemini_api_key = os.environ.get("GEMINI_API_KEY")

# --- USER INPUT ---
st.subheader("1. Enter Target Channel")
channel_id = st.text_input("Enter the YouTube Channel ID:")

if st.button("Run Market Analysis"):
    if not yt_api_key or not gemini_api_key:
        st.warning("API keys missing in Render settings.")
    elif not channel_id:
        st.warning("Please enter a Channel ID.")
    else:
        try:
            with st.spinner("Analyzing channel & querying AI..."):
                youtube = build('youtube', 'v3', developerKey=yt_api_key)
                
                # 1. Fetch channel stats
                ch_req = youtube.channels().list(part='statistics,contentDetails', id=channel_id).execute()
                stats = ch_req['items'][0]['statistics']
                uploads_id = ch_req['items'][0]['contentDetails']['relatedPlaylists']['uploads']
                
                # 2. Display Overview
                col1, col2, col3 = st.columns(3)
                col1.metric("Subscribers", stats.get('subscriberCount', '0'))
                col2.metric("Total Views", stats.get('viewCount', '0'))
                col3.metric("Video Count", stats.get('videoCount', '0'))

                # 3. Fetch Last 50 Videos
                res = youtube.playlistItems().list(playlistId=uploads_id, part='snippet,contentDetails', maxResults=50).execute()
                video_ids = [item['contentDetails']['videoId'] for item in res['items']]
                v_res = youtube.videos().list(id=','.join(video_ids), part='statistics,snippet').execute()
                
                video_data = []
                for v in v_res['items']:
                    video_data.append({
                        'ID': v['id'],
                        'Title': v['snippet']['title'],
                        'Description': v['snippet']['description'],
                        'Views': int(v['statistics'].get('viewCount', 0)),
                        'Link': f"https://www.youtube.com/watch?v={v['id']}"
                    })
                
                df = pd.DataFrame(video_data)
                
                # 4. Identify Viral Outlier
                avg_views = df['Views'].mean()
                viral_idx = df['Views'].idxmax()
                viral_video = df.loc[viral_idx]
                
                st.markdown("---")
                st.subheader("🔥 Viral Performance & AI Analysis")
                st.write(f"**Most Viral Video:** {viral_video['Title']}")
                st.write(f"🎯 **Views:** {viral_video['Views']:,} ({round(viral_video['Views']/avg_views, 1)}x higher than average)")
                
                # 5. --- GEMINI AI ANALYSIS ---
                genai.configure(api_key=gemini_api_key)
                # FIX: Using the current 2026 model version
                model = genai.GenerativeModel('gemini-2.5-flash') 
                
                ai_prompt = f"""
                You are an expert YouTube market analyst. Analyze this viral video metadata:
                Title: {viral_video['Title']}
                Description: {viral_video['Description'][:500]} 
                
                Why did this go viral? Provide 3 short, punchy bullet points explaining the potential psychological hooks, keyword strategies, or audience appeal.
                """
                
                ai_response = model.generate_content(ai_prompt)
                
                with st.expander("🤖 Read AI Breakdown on Why it Went Viral", expanded=True):
                    st.write(ai_response.text)

        except Exception as e:
            st.error(f"Something went wrong: {e}")

# --- GLOBAL & INDIA MARKET TRENDS ---
st.markdown("---")
st.subheader("📰 May 2026 Market Pulse: Creator Economy Trends")
colA, colB = st.columns(2)

with colA:
    st.info("**Trending in India 🇮🇳**\n"
            "* **The 'How-To' Boom:** Keeping videos short and simple to teach skills rapidly is a leading trend.\n"
            "* **Shorts-First Strategy:** Shorts are seeing massive adoption, with creators using them as a sneak peek to drive viewers to long-form content.\n"
            "* **AI Integration:** Tools for automatic video resizing and effortless editing are transforming Indian video production.")

with colB:
    st.info("**Global Trends 🌍**\n"
            "* **Strategic Storytelling:** Creators who build deep narrative architectures instead of just chasing virality are winning the audience's loyalty.\n"
            "* **Audience Ownership:** Because platform payouts are volatile, creators are prioritizing paid communities and digital products to gain stability.\n"
            "* **IRL Events Return:** There is a huge global push for in-person retreats, dinner series, and meetups to foster real-world connections.")
