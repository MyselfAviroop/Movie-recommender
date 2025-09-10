import pickle
import streamlit as st
import requests
import os
import io
import time

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

# =========================
# CUSTOM CSS STYLING
# =========================
st.markdown("""
<style>
body { background-color: #121212; color: #ffffff; font-family: 'Trebuchet MS', sans-serif; }
h1 { color: #ff6f61; text-align: center; }
.stButton>button { background-color: #ff6f61; color: white; font-weight: bold; border-radius: 10px; padding: 0.6rem 1rem; transition: all 0.3s ease; }
.stButton>button:hover { background-color: #ff4c3b; }
.stText { font-size: 16px; font-weight: bold; text-align: center; }
.stImage img { border-radius: 15px; box-shadow: 0px 5px 15px rgba(0,0,0,0.5); }
</style>
""", unsafe_allow_html=True)

st.title("🎬 Movie Recommender System")

# =========================
# GOOGLE DRIVE PICKLE FILES
# =========================
MOVIES_URL = "https://drive.google.com/uc?export=download&id=1BjOlqZBEzu4OURzgGpdmySc3oF33DGxW"
SIMILARITY_URL = "https://drive.google.com/uc?export=download&id=1rcTm8ewOzWXGEe5blo9yjxEA065MSx5A"

def download_pickle(url, filename):
    """Download a pickle file from Google Drive, validate it, and save locally."""
    if os.path.exists(filename):
        return filename  # already exists

    with st.spinner(f"Downloading {filename} ..."):
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
        except Exception as e:
            st.error(f"Failed to download {filename}: {e}")
            return None

        # Validate content: should start with b'\x80' for pickle
        if not r.content.startswith(b'\x80'):
            st.error(f"{filename} download is not a valid pickle file. Check your URL or file sharing settings.")
            return None

        with open(filename, "wb") as f:
            f.write(r.content)

    return filename

movies_file = download_pickle(MOVIES_URL, "movies.pkl")
similarity_file = download_pickle(SIMILARITY_URL, "similarity.pkl")

if not movies_file or not similarity_file:
    st.stop()

# =========================
# LOAD DATA
# =========================
with open(movies_file, "rb") as f:
    movies = pickle.load(f)

with open(similarity_file, "rb") as f:
    similarity = pickle.load(f)

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
