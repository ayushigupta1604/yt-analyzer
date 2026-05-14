import streamlit as st
import os
import pandas as pd
import requests
from googleapiclient.discovery import build
import google.generativeai as genai
from streamlit_lottie import st_lottie

# --- UI ENHANCEMENTS (Industry Grade) ---
st.set_page_config(page_title="AnalystPro | YT Intelligence", page_icon="📈", layout="wide")

# Custom CSS for a professional look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    h1, h2, h3 { font-family: 'Inter', sans-serif; color: #1e293b; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #0f172a; color: white; }
    </style>
    """, unsafe_content_with_con_scope=True)

# Function for Motion Graphics
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200: return None
    return r.json()

lottie_loading = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_0m8bt9tf.json")

# --- APP HEADER ---
st.title("📊 AnalystPro: Market Intelligence")
st.caption("Advanced Video Performance & Trend Analysis Engine | May 2026 Edition")

# --- KEYS & INPUT ---
yt_api_key = os.environ.get("YOUTUBE_API_KEY")
gemini_api_key = os.environ.get("GEMINI_API_KEY")

channel_id = st.text_input("Target Channel ID", placeholder="Paste Channel ID here...")

if st.button("Generate Comprehensive Report"):
    if not yt_api_key or not gemini_api_key:
        st.error("API configuration missing.")
    else:
        try:
            # ADVANCED LOAD SEQUENCE
            with st.empty():
                st_lottie(lottie_loading, height=200, key="loader")
                st.write("🔍 Extracting metadata and calculating outliers...")
                
                # Fetch Data
                youtube = build('youtube', 'v3', developerKey=yt_api_key)
                ch_req = youtube.channels().list(part='statistics,contentDetails', id=channel_id).execute()
                stats = ch_req['items'][0]['statistics']
                uploads_id = ch_req['items'][0]['contentDetails']['relatedPlaylists']['uploads']
                
                res = youtube.playlistItems().list(playlistId=uploads_id, part='contentDetails', maxResults=50).execute()
                video_ids = [item['contentDetails']['videoId'] for item in res['items']]
                v_res = youtube.videos().list(id=','.join(video_ids), part='statistics,snippet').execute()
                
                video_data = []
                for v in v_res['items']:
                    video_data.append({
                        'Title': v['snippet']['title'],
                        'Desc': v['snippet']['description'],
                        'Views': int(v['statistics'].get('viewCount', 0)),
                        'Link': f"https://www.youtube.com/watch?v={v['id']}"
                    })
                df = pd.DataFrame(video_data)
                avg_v = df['Views'].mean()
            
            # --- DASHBOARD TABS ---
            tab1, tab2, tab3 = st.tabs(["📈 Performance Overview", "🧠 AI Insights", "🌍 Market Pulse"])

            with tab1:
                col1, col2, col3 = st.columns(3)
                col1.metric("Subscribers", f"{int(stats.get('subscriberCount', 0)):,}")
                col2.metric("Total Views", f"{int(stats.get('viewCount', 0)):,}")
                col3.metric("Recent Avg Views", f"{int(avg_v):,}")
                
                st.subheader("Video Performance Spread")
                st.bar_chart(df.set_index('Title')['Views'])

            with tab2:
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')

                # VIRAL ANALYSIS
                viral = df.loc[df['Views'].idxmax()]
                st.success(f"💎 **Top Performer:** {viral['Title']}")
                
                # LEAST VIEWED ANALYSIS (The "Underperformer" Section)
                least = df.loc[df['Views'].idxmin()]
                st.warning(f"📉 **Lowest Performer:** {least['Title']}")

                col_v, col_l = st.columns(2)
                
                with col_v:
                    st.write("**Why this went Viral:**")
                    prompt_v = f"In simple, professional English, why did this video go viral? Title: {viral['Title']}. Give 3 bullet points."
                    st.write(model.generate_content(prompt_v).text)
                
                with col_l:
                    st.write("**Why this underperformed:**")
                    prompt_l = f"In simple, professional English, why does this video have the least views on the channel? Title: {least['Title']}. Give 3 bullet points."
                    st.write(model.generate_content(prompt_l).text)

            with tab3:
                st.subheader("May 2026 Market Context")
                st.markdown("""
                *   **India Focus:** The "Regional Micro-Niche" trend is peaking. Small, specific topics in local languages are outperforming broad English content.
                *   **Global Focus:** "Hyper-Authentication"—audiences are rejecting over-edited videos for raw, behind-the-scenes expert analysis.
                """)

        except Exception as e:
            st.error(f"Analysis failed: {e}")
