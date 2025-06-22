import os
from pathlib import Path
import gdown
import streamlit as st
import pandas as pd
import pickle
import requests

# ----------- Load environment variables safely -----------
SIMILARITY_FILE_ID = os.getenv("SIMILARITY_FILE_ID")
api_key = os.getenv("TMDB_API_KEY")

if not SIMILARITY_FILE_ID:
    st.error("❌ SIMILARITY_FILE_ID is not set in the environment.")
    st.stop()
if not api_key:
    st.error("❌ TMDB_API_KEY is not set in the environment.")
    st.stop()

# ----------- Google Drive download for large file -----------
SIMILARITY_FILE = "similarity.pkl"
if not Path(SIMILARITY_FILE).exists():
    url = f"https://drive.google.com/uc?id={SIMILARITY_FILE_ID}"
    gdown.download(url, SIMILARITY_FILE, quiet=False)

# ----------- TMDB Poster & Trailer fetch function -----------
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&append_to_response=videos"
    response = requests.get(url)
    if response.status_code != 200:
        return None, None, None
    data = response.json()

    poster_url = f"https://image.tmdb.org/t/p/w500{data.get('poster_path', '')}"
    overview = data.get('overview', 'No description available.')

    trailer_url = None
    videos = data.get("videos", {}).get("results", [])
    for video in videos:
        if video["type"] == "Trailer" and video["site"] == "YouTube":
            trailer_url = f"https://www.youtube.com/watch?v={video['key']}"
            break

    return poster_url, overview, trailer_url

# ----------- Recommendation Function -----------
def recommend(movie_title):
    index = movies_df[movies_df['title'] == movie_title].index[0]
    distances = similarity[index]
    movie_indices = sorted(list(enumerate(distances)), key=lambda x: x[1], reverse=True)[1:6]

    recommended_data = []
    for i in movie_indices:
        idx = i[0]
        title = movies_df.iloc[idx].title
        movie_id = movies_df.iloc[idx].movie_id
        poster, overview, trailer = fetch_movie_details(movie_id)
        recommended_data.append({
            "title": title,
            "poster": poster,
            "overview": overview,
            "trailer": trailer
        })
    return recommended_data

# ----------- Load Data -----------
with open('movies.pkl', 'rb') as f:
    movies_df = pickle.load(f)

with open('similarity.pkl', 'rb') as f:
    similarity = pickle.load(f)

movie_titles = movies_df['title'].tolist()

# ----------- Streamlit App UI -----------
st.set_page_config(page_title="🎥 Movie Recommender", layout="wide")
st.markdown("<h1 style='text-align: center;'>🎬 Personalized Movie Recommender</h1>", unsafe_allow_html=True)

st.markdown("## 🔍 Choose a movie you liked:")
selected_movie = st.selectbox("Pick a movie", movie_titles)

if st.button("🔮 Recommend Similar Movies"):
    with st.spinner("Fetching recommendations..."):
        recommendations = recommend(selected_movie)

    st.markdown("---")
    st.markdown("## 🎯 Top 5 Recommendations for You:")
    cols = st.columns(5)

    for idx, col in enumerate(cols):
        with col:
            movie = recommendations[idx]
            st.image(movie["poster"], use_container_width=True)
            st.markdown(f"**{movie['title']}**", unsafe_allow_html=True)
            st.markdown(f"<small>{movie['overview'][:150]}...</small>", unsafe_allow_html=True)
            if movie["trailer"]:
                st.markdown(f"[▶ Watch Trailer]({movie['trailer']})", unsafe_allow_html=True)

if st.button("🔄 Reset"):
    st.rerun()
