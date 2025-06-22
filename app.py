import streamlit as st
import pandas as pd
import pickle
import requests  # To fetch data from TMDB API
import os       # To access environment variables securely

# Load your TMDB API key from environment variable (keep it secret!)
api_key = os.environ.get('TMDB_API_KEY')

# --------------- Function to fetch poster URL from TMDB API ---------------
def fetch_poster(movie_id):
    """
    Given a movie_id, call TMDB API to get the poster path.
    Returns the full URL of the poster image.
    """
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
    response = requests.get(url)
    data = response.json()
    
    # Poster URL format (w500 = width 500px)
    return "http://image.tmdb.org/t/p/w500/" + data['poster_path']

# --------------- Recommendation Function ---------------
def recommend(movie):
    """
    Given a movie title, find top 5 similar movies using the similarity matrix.
    Returns two lists: recommended movie titles and their corresponding poster URLs.
    """
    # Find the index of the selected movie in the DataFrame
    movie_index = movies_df[movies_df['title'] == movie].index[0]
    
    # Get similarity scores for this movie with all others
    distances = similarity[movie_index]
    
    # Sort by similarity score (descending), skip the first one (itself),
    # and pick top 5 recommended movies
    movies = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    recommended_movies = []
    recommended_posters = []
    
    for i in movies:
        idx = i[0]  # movie index
        recommended_movies.append(movies_df.iloc[idx].title)
        
        # Fetch poster URL from TMDB using movie_id
        movie_id = movies_df.iloc[idx].movie_id
        recommended_posters.append(fetch_poster(movie_id))
    
    return recommended_movies, recommended_posters

# --------------- Load Data ---------------
# Load movies DataFrame and similarity matrix from pickle files
movies_df = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Extract movie titles for dropdown selection
movie_titles = movies_df['title'].values

# --------------- Streamlit UI Layout ---------------
st.title('🎬 Movie Recommender System')

# Dropdown widget for movie selection
option = st.selectbox(
    "Select a movie to get recommendations:",
    movie_titles
)

# When the user clicks 'Recommend'
# When the user clicks 'Recommend'
if st.button("Recommend"):
    recommendations, posters = recommend(option)
    
    st.subheader("Recommended Movies:")
    
    # Display recommended movies and posters side by side in columns
    cols = st.columns(5)  # 5 columns for 5 recommendations
    
    for idx, col in enumerate(cols):
        with col:
            # ✅ Use updated parameter here
            st.image(posters[idx], use_container_width=True)
            st.caption(recommendations[idx])


# Optional Reset button (can be wired with session state if needed)
st.button("Reset", type="primary")
