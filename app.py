import pickle
import streamlit as st
import requests
import os
import time

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")
st.title("🎬 Movie Recommender System")

# =========================
# GOOGLE DRIVE FILES
# =========================
MOVIES_URL ="https://drive.google.com/file/d/1g3k7EtVxNeakNcJ4otAvSol219UYcLw-/view?usp=drive_link"
SIMILARITY_URL = "https://drive.google.com/file/d/1g3k7EtVxNeakNcJ4otAvSol219UYcLw-/view?usp=drive_link"
def download_file(url, filename):
    if not os.path.exists(filename):
        with st.spinner(f"Downloading {filename} ..."):
            r = requests.get(url)
            with open(filename, "wb") as f:
                f.write(r.content)

download_file(MOVIES_URL, "movies.pkl")
download_file(SIMILARITY_URL, "similarity.pkl")

# =========================
# LOAD DATA
# =========================
movies = pickle.load(open("movies.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# =========================
# OMDb CONFIG
# =========================
OMDB_API_KEY = "b95f82c7"
DEFAULT_POSTER = "https://via.placeholder.com/500x750?text=No+Poster"

def fetch_poster(title, retries=3):
    for attempt in range(retries):
        try:
            url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            poster = data.get("Poster")
            if poster and poster != "N/A":
                return poster
            return DEFAULT_POSTER
        except:
            time.sleep(1)
    return DEFAULT_POSTER

# =========================
# SELECT MOVIE
# =========================
movie_list = movies['title'].values
selected_movie = st.selectbox("Select a movie", movie_list)

# =========================
# RECOMMENDATION FUNCTION
# =========================
def recommend(movie):
    idx = movies[movies['title'] == movie].index[0]
    distances = similarity[idx]
    top_indices = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []
    for i, _ in top_indices:
        recommended_movies.append(movies.iloc[i].title)
        recommended_posters.append(fetch_poster(movies.iloc[i].title))
    return recommended_movies, recommended_posters

# =========================
# DISPLAY RECOMMENDATIONS
# =========================
if st.button("Recommend"):
    with st.spinner("Fetching recommendations and posters..."):
        names, posters = recommend(selected_movie)
        cols = st.columns(5)
        for i, col in enumerate(cols):
            with col:
                st.text(names[i])
                st.image(posters[i], use_container_width=True)
