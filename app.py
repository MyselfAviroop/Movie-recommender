import pickle
import streamlit as st
import requests
import os
import gdown  
import base64  # ✅ Add this for base64 encoding

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="CineMatch", page_icon="🎬", layout="wide")

# =========================
# LOAD BACKGROUND IMAGE AS BASE64
# =========================
def get_base64_of_image(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# ✅ Change the filename to match your uploaded file
bg_base64 = get_base64_of_image("netflix-background-gs7hjuwvv2g0e9fj.jpg")

# =========================
# CUSTOM CSS (NETFLIX-STYLE)
# =========================
st.markdown(f"""
<style>
/* Fullscreen Hero Background */
.hero {{
    background-image: url("data:image/jpg;base64,{bg_base64}");
    background-size: cover;
    background-position: center;
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    color: white;
    backdrop-filter: brightness(0.5);
    margin: -3rem -3rem 0 -3rem;
    padding: 2rem;
}}

/* Title Styling */
.hero h1 {{
    font-size: 3rem;
    font-weight: 900;
    text-shadow: 2px 2px 10px rgba(0,0,0,0.7);
    margin-bottom: 1rem;
}}
.hero p {{
    font-size: 1.3rem;
    max-width: 700px;
    text-shadow: 1px 1px 6px rgba(0,0,0,0.8);
    margin-bottom: 1.5rem;
}}

/* Dropdown + Button Wrapper */
.recommend-box {{
    background: rgba(0,0,0,0.65);
    padding: 1.5rem;
    border-radius: 10px;
    display: inline-block;
    box-shadow: 0 4px 10px rgba(0,0,0,0.5);
}}

/* Button Styling */
.hero-btn {{
    margin-top: 1rem;
    background-color: #E50914;
    color: white;
    font-weight: 700;
    font-size: 18px;
    border-radius: 8px;
    padding: 0.6rem 1.8rem;
    text-decoration: none;
    display: inline-block;
    transition: all 0.3s ease;
}}
.hero-btn:hover {{
    background-color: #f40612;
    transform: scale(1.05);
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
    with st.spinner(f"Downloading {filename}..."):
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
# HERO SECTION WITH DROPDOWN
# =========================
st.markdown('<div class="hero">', unsafe_allow_html=True)
st.markdown("<h1>🎬 CineMatch</h1>", unsafe_allow_html=True)
st.markdown("<p>Find your next favorite movie instantly — just pick one you like.</p>", unsafe_allow_html=True)

movie_list = movies['title'].values
selected_movie = st.selectbox("Choose a movie you like:", movie_list, key="hero-dropdown", label_visibility="collapsed")

if st.button("🎥 Get Recommendations", key="hero-button"):
    names, posters = [], []
    idx = movies[movies['title'] == selected_movie].index[0]
    distances = similarity[idx]
    top_indices = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    for i, _ in top_indices:
        names.append(movies.iloc[i].title)
        posters.append(fetch_poster(movies.iloc[i].title))

    st.markdown("</div>", unsafe_allow_html=True)  # close hero div
    st.markdown("<h3 style='text-align:center; margin-top:2rem;'>Recommended for You</h3>", unsafe_allow_html=True)
    cols = st.columns(len(names))
    for i, col in enumerate(cols):
        with col:
            st.image(posters[i], use_container_width=True)
            st.markdown(f"<p style='text-align:center; font-weight:bold;'>{names[i]}</p>", unsafe_allow_html=True)
else:
    st.markdown("</div>", unsafe_allow_html=True)  # close hero div














