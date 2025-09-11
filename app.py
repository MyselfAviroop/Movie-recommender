import pickle
import streamlit as st
import requests
import os
import time
import gdown
import base64  # ✅ REQUIRED for base64 encoding

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="CineMatch", page_icon="🍿", layout="wide")

# =========================
# LOAD BACKGROUND IMAGE AS BASE64
# =========================
def get_base64_of_image(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

bg_base64 = get_base64_of_image("netflix-background-gs7hjuwvv2g0e9fj.jpg")

# =========================
# CUSTOM STYLING
# =========================
st.markdown(f"""
<style>
.main .block-container {{
    padding: 0;
    margin: 0;
}}
/* Remove Streamlit top padding completely */
.main .block-container {{
    padding-top: 0 !important;
    padding-bottom: 0 !important;
}}


.body{{
 background-image: url("data:image/jpg;base64,{bg_base64}");
}}

/* Dropdown Styling */
.stSelectbox > div > div {{
    background-color: #222;
    border-radius: 8px;
    color: white;
}}

/* Full width button */
.stButton>button {{
    background-color: #E50914;
    color: white;
    font-weight: bold;
    border-radius: 6px;
    font-size: 18px;
    padding: 0.7rem 1.5rem;
    width: 100%;
    transition: all 0.2s ease-in-out;
}}
.stButton>button:hover {{
    background-color: #f40612;
    transform: scale(1.03);
}}
</style>
""", unsafe_allow_html=True)

# =========================
# GOOGLE DRIVE PICKLE FILES
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
    st.warning("Downloads failed. Please upload pickle files manually.")
    uploaded_movies = st.file_uploader("Upload movies.pkl", type="pkl")
    uploaded_similarity = st.file_uploader("Upload similarity.pkl", type="pkl")
    if uploaded_movies and uploaded_similarity:
        with open("movies_uploaded.pkl", "wb") as f:
            f.write(uploaded_movies.getbuffer())
        with open("similarity_uploaded.pkl", "wb") as f:
            f.write(uploaded_similarity.getbuffer())
        movies_file = "movies_uploaded.pkl"
        similarity_file = "similarity_uploaded.pkl"
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

def fetch_poster(title, retries=3):
    for _ in range(retries):
        try:
            encoded_title = requests.utils.quote(title)
            url = f"http://www.omdbapi.com/?t={encoded_title}&apikey={OMDB_API_KEY}"
            r = requests.get(url, timeout=10).json()
            if r.get("Response") == "True":
                poster = r.get("Poster")
                return poster if poster and poster != "N/A" else DEFAULT_POSTER
        except:
            time.sleep(1)
    return DEFAULT_POSTER

def recommend(movie):
    try:
        idx = movies[movies['title'] == movie].index[0]
        distances = similarity[idx]
        top_indices = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
        return [movies.iloc[i].title for i, _ in top_indices], [fetch_poster(movies.iloc[i].title) for i, _ in top_indices]
    except:
        return [], []

# =========================
# HERO SECTION + UI
# =========================
st.markdown('<div class="hero">', unsafe_allow_html=True)
st.markdown("<h1>🍿 CineMatch</h1>", unsafe_allow_html=True)
st.markdown("<p>Find your next favorite movie instantly — just pick one you like.</p>", unsafe_allow_html=True)

# ✅ This box is now centered with flexbox and styled
st.markdown('<div class="recommend-box">', unsafe_allow_html=True)
movie_list = movies['title'].values
selected_movie = st.selectbox("Choose a movie", movie_list, key="hero-dropdown", label_visibility="collapsed")
get_reco = st.button("🎥 Get Recommendations")
st.markdown('</div>', unsafe_allow_html=True)  # close recommend-box
st.markdown('</div>', unsafe_allow_html=True)  # close hero

if get_reco:
    names, posters = recommend(selected_movie)
    st.markdown("<h3 style='text-align:center; margin-top:2rem;'>Recommended for You</h3>", unsafe_allow_html=True)
    if names:
        cols = st.columns(len(names))
        for i, col in enumerate(cols):
            with col:
                st.image(posters[i], use_container_width=True)
                st.markdown(f"<p style='text-align:center; font-weight:bold;'>{names[i]}</p>", unsafe_allow_html=True)
    else:
        st.warning("No recommendations available.")








