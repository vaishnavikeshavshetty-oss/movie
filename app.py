import streamlit as st
import pandas as pd
import requests
import pickle
import os
import gdown

# ---------------- DOWNLOAD FILE FROM GOOGLE DRIVE IF NOT EXISTS ----------------
file_id = "1B52-pG2gQggEZgI3l2LkkbX1R52EAmiw"
url = f"https://drive.google.com/uc?id={file_id}"
output = "movie_data.pkl"

if not os.path.exists(output):
    with st.spinner("📥 Downloading movie dataset..."):
        gdown.download(url, output, quiet=False)

# ---------------- SESSION SETUP ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# ---------------- LOGIN FUNCTION ----------------
def login():
    st.markdown("<h1 style='text-align: center;'>🔐 LOGIN </h1>", unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username.strip() != "" and password.strip() != "":
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"✅ Welcome, {username}!")
            st.rerun()
        else:
            st.error("❌ Please enter both username and password")

# ---------------- LOGOUT FUNCTION ----------------
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.success("✅ Logged out successfully!")
    st.rerun()

# ---------------- MAIN APP ----------------
def main_app():
    # Load the data
    with open('movie_data.pkl', 'rb') as file:
        movies, cosine_sim = pickle.load(file)

    def fetch_poster(movie_id):
        api_key = "7a793d14632a0c96f773222088510b5d"
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            poster_path = data.get('poster_path')
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
        except:
            return None
        return None

    def fetch_rating(movie_id):
        api_key = "7a793d14632a0c96f773222088510b5d"
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            return data.get('vote_average', 'N/A')
        except:
            return "N/A"

    def get_recommendations(title, cosine_sim=cosine_sim):
        try:
            idx = movies[movies['title'] == title].index[0]
        except IndexError:
            st.error("Selected movie not found in the dataset.")
            return pd.DataFrame()
        
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:11]
        movie_indices = [i[0] for i in sim_scores]
        return movies.iloc[movie_indices]

    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"<h3>🎬 Welcome, {st.session_state.username}!</h3>", unsafe_allow_html=True)
    with col2:
        if st.button("🚪 Logout"):
            logout()

    st.markdown("<h1 style='text-align: center; color: #E50914;'>Movie Recommendation System</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Find similar movies with posters and ratings</p><br>", unsafe_allow_html=True)

    selected_movie = st.selectbox("🎞️ Select a Movie:", movies['title'].values)

    if st.button("Recommend"):
        recommendations = get_recommendations(selected_movie)

        if recommendations.empty:
            st.warning("No recommendations found.")
        else:
            st.markdown("### ⭐ Top 10 Recommended Movies")
            st.markdown("<hr style='border: 1px solid #444;'>", unsafe_allow_html=True)
            
            for i in range(0, 10, 5):
                cols = st.columns(5)
                for col, j in zip(cols, range(i, i + 5)):
                    if j < len(recommendations):
                        movie = recommendations.iloc[j]
                        poster_url = fetch_poster(movie['movie_id'])
                        rating = fetch_rating(movie['movie_id'])

                        with col:
                            if poster_url:
                                st.image(poster_url, width=140)
                            else:
                                st.write("Poster not available")
                            st.markdown(f"**{movie['title']}**", unsafe_allow_html=True)
                            st.markdown(f"<span style='color:gold;'>⭐ Rating: {rating}</span>", unsafe_allow_html=True)

# ---------------- RUN APP ----------------
if st.session_state.logged_in:
    main_app()
else:
    login()
