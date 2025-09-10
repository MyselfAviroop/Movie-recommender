import pickle
import streamlit as st
import requests
import os
import io
import time
import gdown  # Add this import

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

# =========================
# CUSTOM CSS STYLING
# =========================
st.markdown("""
<style>
/* ===== Body & Fonts ===== */
body, .block-container {
    background-color: #121212;
    color: #E0E0E0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* ===== Titles ===== */
h1, h2, h3 {
    color: #FF6F61;
    text-align: center;
    font-weight: 700;
    margin-bottom: 1rem;
}

/* ===== Streamlit Buttons ===== */
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

/* ===== Streamlit Text ===== */
.stText {
    font-size: 16px;
    font-weight: 600;
    text-align: center;
}

/* ===== Movie Posters ===== */
.stImage img {
    border-radius: 15px;
    box-shadow: 0px 5px 20px rgba(0,0,0,0.7);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.stImage img:hover {
    transform: scale(1.05);
    box-shadow: 0px 10px 30px rgba(255,111,97,0.6);
}

/* ===== Columns Layout ===== */
.css-1lcbmhc.e1fqkh3o3 { 
    justify-content: space-evenly;
}

/* ===== Scrollbar Styling ===== */
::-webkit-scrollbar {
    width: 10px;
}
::-webkit-scrollbar-thumb {
    background: #FF6F61;
    border-radius: 5px;
}
::-webkit-scrollbar-track {
    background: #1e1e2f;
}

/* ===== Selectbox Styling ===== */
.stSelectbox>div>div>div>div {
    background-color: #1e1e2f;
    color: #fff;
    border-radius: 8px;
    padding: 0.3rem 0.5rem;
}
.stSelectbox>div>div>div>div:hover {
    background-color: #2e2e3f;
}
</style>
""", unsafe_allow_html=True)

st.title("🎬 Movie Recommender System")

# =========================
# GOOGLE DRIVE PICKLE FILES
# =========================
MOVIES_ID = "1BjOlqZBEzu4OURzgGpdmySc3oF33DGxW"  # Extracted file ID
SIMILARITY_ID = "1rcTm8ewOzWXGEe5blo9yjxEA065MSx5A"  # Extracted file ID

def download_pickle(gdrive_id, filename):
    """Download a pickle file from Google Drive using gdown, validate it, and save locally."""
    if os.path.exists(filename):
        # Quick validation for existing file
        try:
            with open(filename, "rb") as f:
                if f.read(10).startswith(b'\x80'):
                    return filename
                else:
                    os.remove(filename)  # Invalid, remove it
        except:
            pass

    with st.spinner(f"Downloading {filename} from Google Drive..."):
        try:
            url = f"https://drive.google.com/uc?id={gdrive_id}"
            gdown.download(url, filename, quiet=False)
        except Exception as e:
            st.error(f"Failed to download {filename} using gdown: {e}. Ensure the file is publicly shared.")
            return None

        # Validate content: should start with b'\x80' for pickle
        try:
            with open(filename, "rb") as f:
                if not f.read(10).startswith(b'\x80'):
                    os.remove(filename)  # Remove invalid file
                    st.error(f"{filename} is not a valid pickle file. Check file integrity or sharing settings.")
                    return None
        except Exception as e:
            st.error(f"Validation failed for {filename}: {e}")
            if os.path.exists(filename):
                os.remove(filename)
            return None

    return filename

# Try downloading; fallback to manual upload if fails
movies_file = download_pickle(MOVIES_ID, "movies.pkl")
similarity_file = download_pickle(SIMILARITY_ID, "similarity.pkl")

if not movies_file or not similarity_file:
    st.warning("Downloads failed. Please upload the pickle files manually.")
    uploaded_movies = st.file_uploader("Upload movies.pkl", type="pkl")
    uploaded_similarity = st.file_uploader("Upload similarity.pkl", type="pkl")
    
    if uploaded_movies and uploaded_similarity:
        # Save uploaded files temporarily
        movies_file = "movies_uploaded.pkl"
        with open(movies_file, "wb") as f:
            f.write(uploaded_movies.getbuffer())
        
        similarity_file = "similarity_uploaded.pkl"
        with open(similarity_file, "wb") as f:
            f.write(uploaded_similarity.getbuffer())
        
        # Validate uploads
        with open(movies_file, "rb") as f:
            if not f.read(10).startswith(b'\x80'):
                st.error("Uploaded movies.pkl is invalid.")
                st.stop()
        with open(similarity_file, "rb") as f:
            if not f.read(10).startswith(b'\x80'):
                st.error("Uploaded similarity.pkl is invalid.")
                st.stop()
    else:
        st.stop()

# =========================
# LOAD DATA
# =========================
try:
    with open(movies_file, "rb") as f:
        movies = pickle.load(f)
  
except Exception as e:
    st.error(f"Failed to load movies.pkl: {e}")
    st.stop()

try:
    with open(similarity_file, "rb") as f:
        similarity = pickle.load(f)
   
except Exception as e:
    st.error(f"Failed to load similarity.pkl: {e}")
    st.stop()

# =========================
# OMDb CONFIG
# =========================
OMDB_API_KEY = "b95f82c7"  # Replace with your actual API key if needed
DEFAULT_POSTER = "https://via.placeholder.com/500x750?text=No+Poster"

def fetch_poster(title, retries=3):
    for attempt in range(retries):
        try:
            # URL-encode title to handle special characters
            encoded_title = requests.utils.quote(title)
            url = f"http://www.omdbapi.com/?t={encoded_title}&apikey={OMDB_API_KEY}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("Response") == "True":
                poster = data.get("Poster")
                if poster and poster != "N/A":
                    return poster
            return DEFAULT_POSTER
        except Exception:
            time.sleep(1)
    return DEFAULT_POSTER

# =========================
# SELECT MOVIE
# =========================
if 'title' not in movies.columns:
    st.error("Movies DataFrame missing 'title' column. Check data structure.")
    st.stop()

movie_list = movies['title'].values
selected_movie = st.selectbox("Select a movie", movie_list)

# =========================
# RECOMMENDATION FUNCTION
# =========================
def recommend(movie):
    try:
        idx = movies[movies['title'] == movie].index[0]
        distances = similarity[idx]
        top_indices = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

        recommended_movies = []
        recommended_posters = []
        for i, _ in top_indices:
            recommended_movies.append(movies.iloc[i].title)
            recommended_posters.append(fetch_poster(movies.iloc[i].title))
        return recommended_movies, recommended_posters
    except Exception as e:
        st.error(f"Recommendation error: {e}")
        return [], []

# =========================
# DISPLAY RECOMMENDATIONS
# =========================
if st.button("Recommend"):
    with st.spinner("Fetching recommendations and posters..."):
        names, posters = recommend(selected_movie)
        if names:
            cols = st.columns(5)
            for i, col in enumerate(cols):
                with col:
                    st.text(names[i])
                    st.image(posters[i], use_container_width=True)
        else:
            st.warning("No recommendations generated. Check data.")

