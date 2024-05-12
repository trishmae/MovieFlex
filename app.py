import streamlit as st
from main import load_data, preprocess_dataframes, cluster_movies_by_genre, recommend_movies_nearest_updated_cosine, select_language
from tmdbv3api import TMDb, Movie
import random
import os
import sys
# from dotenv import load_dotenv

# Initialize the TMDb object with your API key
# load_dotenv()

tmdb = TMDb()
tmdb.api_key =  os.getenv("TMDB_API_KEY")
movie_search = Movie()

BASE_TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500/"
DEFAULT_POSTER = "https://via.placeholder.com/500x750.png?text=No+Poster+Available"

def fetch_movie_details(movie_title):
    movie_id = None
    try:
        search_results = movie_search.search(movie_title)
        
        # Check if there are search results
        if not search_results:
            return {
                "id": movie_id,  
                "poster": DEFAULT_POSTER,
                "release_date": "Unknown",
                "rating": "N/A",
                "overview": "No overview available",
                "genres": "Unknown"
            }

        movie_id = search_results[0].id
        movie_details = movie_search.details(movie_id)

        # Extract the required details from the movie details
        return {
            "id": movie_id,  
            "poster": BASE_TMDB_IMAGE_URL + movie_details.poster_path if movie_details.poster_path else DEFAULT_POSTER,
            "release_date": movie_details.release_date if hasattr(movie_details, 'release_date') else "Unknown",
            "rating": str(movie_details.vote_average) if hasattr(movie_details, 'vote_average') else "N/A",
            "overview": movie_details.overview if hasattr(movie_details, 'overview') else "No overview available",
            "genres": ", ".join([genre['name'] for genre in movie_details.genres]) if hasattr(movie_details, 'genres') else "Unknown"
        }

    except Exception as e:
        print(f"An error occurred while fetching details for {movie_title}: {e}")
        return {
            "id": movie_id,  
            "poster": DEFAULT_POSTER,
            "release_date": "Unknown",
            "rating": "N/A",
            "overview": "No overview available",
            "genres": "Unknown"
        }

def main():
    st.markdown(
        """
        <style>
            body {
                background-color: #434343;
                background-image: linear-gradient(315deg, #434343 0%, #000000 74%);
            }
            .css-hby737, .css-17eq0hr {
                background-color: #666;
                color: white;
            }
            input, textarea, button {
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            }
            .movie-card {
                background-color: #222;
                border-radius: 10px;
                box-shadow: 2px 2px 10px #000;
                transition: transform 0.2s;
                padding: 10px;
            }
            .movie-card:hover {
                transform: scale(1.05);
            }
            .movie-title {
                color: white;
                font-size: 14px;  
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                max-width: 95%;  
                margin-top: 8px;
                margin-bottom: 4px;
            }
            .movie-info {
                color: silver;
                margin-top: 4px;
            }
            details {
                color: silver;
            }
            details summary {
                cursor: pointer;
                outline: none;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    st.title("🎬💪 MovieFlex: Movie Recommendation System")

    print(sys.maxsize)

    tmdb_df = load_data()
    newtmdb_df = preprocess_dataframes(tmdb_df)

    st.write("Welcome to MovieFlex!✨ Get started by entering your favorite movie!")
    auto_trigger = False
    
    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = []
    if 'potential_matches' not in st.session_state:
        st.session_state.potential_matches = []
    if 'movie_input' not in st.session_state:
        st.session_state.movie_input = ""
    if 'reset_triggered' not in st.session_state:
        st.session_state.reset_triggered = False
    if 'surprise_triggered' not in st.session_state:
        st.session_state.surprise_triggered = False

    # Choose a language for the movie results
    language = st.radio(
        "Choose a language for the movie results:",
        ("English", "Filipino", "Korean", "Japanese")
    )
    
    newtmdb_df = select_language(language, newtmdb_df)
    newtmdb_df, genres_encoded = cluster_movies_by_genre(newtmdb_df)

    # Display the selected option
    st.write("You selected:", language)

    # If reset was triggered, set the default value of the input widget to an empty string
    default_value = "" if st.session_state.reset_triggered else st.session_state.movie_input

    new_input = st.text_input("🔍 Enter your favorite movie:", value=default_value, key="movie_input")

    # If there's a change in input, update the session state
    if new_input != st.session_state.movie_input:
        st.session_state.movie_input = new_input
        st.session_state.reset_triggered = False  

    movie_title = st.session_state.movie_input

    if movie_title:
        exact_match = newtmdb_df[newtmdb_df['title'] == movie_title]
        
        if exact_match.empty:  # If exact match doesn't exist, then suggest potential matches
            st.session_state.potential_matches = newtmdb_df[newtmdb_df['title'].str.contains(movie_title, case=False, na=False)]['title'].tolist()
            
            if st.session_state.potential_matches:
                selected_title = st.selectbox("Did you mean one of these?", st.session_state.potential_matches)
                if selected_title:
                    movie_title = selected_title
                    auto_trigger = True  # Setting the flag to trigger automatic recommendations
    col1, col2, col3 = st.columns(3)

    if col1.button('Get Recommendations', key='btn_get_recommendations') or auto_trigger:
        with st.spinner('Fetching recommendations...'):
            st.session_state.recommendations = recommend_movies_nearest_updated_cosine(
                movie_title, genres_encoded=genres_encoded, newtmdb_df=newtmdb_df
            )
        display_chosen_movie(st.session_state.movie_input)
        display_recommendations(st.session_state.recommendations)

    if col2.button('Surprise Me!', key='btn_surprise_me'):
        st.session_state.recommendations = []
        st.session_state.potential_matches = []  # Clearing potential matches on reset
        st.session_state.reset_triggered = True 

        movie_title = random.choice(newtmdb_df['title'].tolist())
        with st.spinner('Fetching recommendations...'):
            st.session_state.recommendations = recommend_movies_nearest_updated_cosine(
                movie_title, genres_encoded=genres_encoded, newtmdb_df=newtmdb_df
            )
        display_recommendations(st.session_state.recommendations)

    if col3.button("Reset", key="btn_reset"):
        st.session_state.recommendations = []
        st.session_state.potential_matches = []  # Clearing potential matches on reset
        st.session_state.reset_triggered = True  # Set the reset flag
        st.experimental_rerun()

def display_chosen_movie(movie_title):
    st.write("You have chosen", movie_title)

    movie_details = fetch_movie_details(movie_title)

    st.markdown(
                f"""
                <div class="movie-card" style="display: flex; align-items: center;">
                    <div style="overflow: hidden; border-radius: 10px; margin-right: 10px;">
                        <img src="{movie_details['poster']}" alt="{movie_title}" style="width: 150px; height: 225px; object-fit: cover;">
                    </div>
                    <div>
                        <a href="https://www.themoviedb.org/tv/{movie_details['id']}" target="_blank">
                            <div class="movie-title">{movie_title}</div>
                        </a>
                        <p class="movie-info">{movie_details['release_date']} | {movie_details['genres']} | Rating: {movie_details['rating']}</p>
                        <details>
                            <summary>Overview</summary>
                            {movie_details['overview']}
                        </details>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

def display_recommendations(recommendations):
    if recommendations:
        st.subheader("Recommended Movies:")
        for movie in recommendations:
            movie_details = fetch_movie_details(movie)

            # Display movie details for each row
            st.markdown(
                f"""
                <div class="movie-card" style="display: flex; align-items: center;">
                    <div style="overflow: hidden; border-radius: 10px; margin-right: 10px;">
                        <img src="{movie_details['poster']}" alt="{movie}" style="width: 150px; height: 225px; object-fit: cover;">
                    </div>
                    <div>
                        <a href="https://www.themoviedb.org/movie/{movie_details['id']}" target="_blank">
                            <div class="movie-title">{movie}</div>
                        </a>
                        <p class="movie-info">{movie_details['release_date']} | {movie_details['genres']} | Rating: {movie_details['rating']}</p>
                        <details>
                            <summary>Overview</summary>
                            {movie_details['overview']}
                        </details>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.error("Couldn't find any recommendations for that movie.")


if __name__ == "__main__":
    main()
