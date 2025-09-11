import pickle
import streamlit as st
import requests
import os
import time
import gdown  

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
<style>
body, .block-container {
    background-color: #121212;
    color: #E0E0E0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
h1, h2, h3 {
    color: #FF6F61;
    text-align: center;
    font-weight: 700;
    margin-bottom: 1rem;
}
.stButton>button {
    background-color: #FF6F61;
    color: white;
    font-weight: 700;
    border-radius: 12px;
    padding: 0.7rem 1.2rem;
    font-size: 16px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(255, 111, 97, 0.4);
}
.stButton>button:hover {
    background-color: #FF4C3B;
    transform: translateY(-2px);
}
.stImage img {
    border-radius: 15px;
    box-shadow: 0px 5px 20px rgba(0,0,0,0.7);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.stImage img:hover {
    transform: scale(1.05);
    box-shadow: 0px 10px 30px rgba(255,111,97,0.6);
}
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER SECTION (HOME PAGE)
# =========================
st.markdown(
    """
    <div style='text-align:center; padding: 2rem;'>
        <h1>🎬 Movie Recommender System</h1>
        <p style='font-size:18px; max-width:700px; margin:auto;'>
        Your personalized movie discovery engine — explore new favorites based on what you love.
        Powered by ML similarity scores and live poster fetching from OMDb API.
        </p>
    </div>
    """, unsafe_allow_html=True
)

# =========================
# LOAD PICKLE FILES
# =========================
MOVIES_ID = "1BjOlqZBEzu4OURzgGpdmySc3oF33DGxW"
SIMILARITY_ID = "1rcTm8ewOzWXGEe5blo9yjxEA065MSx5A"

def download_pickle(gdrive_id, filename):
    if os.path.exists(filename):
        try:
            with open(filename, "rb") as f:
                if f.read(10).startswith(b'\x80'):
                    return filename
                else:
                    os.remove(filename)
        except:
            pass
    with st.spinner(f"Downloading {filename} from Google Drive..."):
        try:
            url = f"https://drive.google.com/uc?id={gdrive_id}"
            gdown.download(url, filename, quiet=False)
        except Exception as e:
            st.error(f"Failed to download {filename}: {e}")
            return None
        try:
            with open(filename, "rb") as f:
                if not f.read(10).startswith(b'\x80'):
                    os.remove(filename)
                    st.error(f"{filename} is not a valid pickle file.")
                    return None
        except:
            return None
    return filename

movies_file = download_pickle(MOVIES_ID, "movies.pkl")
similarity_file = download_pickle(SIMILARITY_ID, "similarity.pkl")

if not movies_file or not similarity_file:
    st.warning("Could not download data automatically. Please upload the files manually.")
    uploaded_movies = st.file_uploader("Upload movies.pkl", type="pkl")
    uploaded_similarity = st.file_uploader("Upload similarity.pkl", type="pkl")
    if uploaded_movies and uploaded_similarity:
        movies_file = "movies_uploaded.pkl"
        with open(movies_file, "wb") as f:
            f.write(uploaded_movies.getbuffer())
        similarity_file = "similarity_uploaded.pkl"
        with open(similarity_file, "wb") as f:
            f.write(uploaded_similarity.getbuffer())
    else:
        st.stop()

try:
    with open(movies_file, "rb") as f:
        movies = pickle.load(f)
    with open(similarity_file, "rb") as f:
        similarity = pickle.load(f)
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

# =========================
# OMDb CONFIG
# =========================
OMDB_API_KEY = "b95f82c7"
DEFAULT_POSTER = "https://via.placeholder.com/500x750?text=No+Poster"

def fetch_poster(title):
    try:
        encoded_title = requests.utils.quote(title)
        url = f"http://www.omdbapi.com/?t={encoded_title}&apikey={OMDB_API_KEY}"
        data = requests.get(url, timeout=10).json()
        if data.get("Response") == "True":
            poster = data.get("Poster")
            return poster if poster and poster != "N/A" else DEFAULT_POSTER
    except:
        pass
    return DEFAULT_POSTER

# =========================
# MAIN RECOMMENDER SECTION
# =========================
st.subheader("🔍 Find Your Next Movie")
movie_list = movies['title'].values
selected_movie = st.selectbox("Choose a movie you like:", movie_list)

def recommend(movie):
    idx = movies[movies['title'] == movie].index[0]
    distances = similarity[idx]
    top_indices = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    recommended_movies, recommended_posters = [], []
    for i, _ in top_indices:
        recommended_movies.append(movies.iloc[i].title)
        recommended_posters.append(fetch_poster(movies.iloc[i].title))
    return recommended_movies, recommended_posters

if st.button("🎥 Get Recommendations"):
    names, posters = recommend(selected_movie)
    st.markdown("<h3 style='text-align:center;'>Recommended for You</h3>", unsafe_allow_html=True)
    cols = st.columns(len(names))
    for i, col in enumerate(cols):
        with col:
            st.image(posters[i], use_container_width=True)
            st.markdown(f"<p style='text-align:center; font-weight:bold;'>{names[i]}</p>", unsafe_allow_html=True)
