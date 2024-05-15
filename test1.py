import streamlit as st
import pandas as pd

genres = ['action', 'science fiction', 'adventure', 'drama', 'crime', 'thriller', 'fantasy', 'comedy', 'romance', 'western', 'mystery', 'war', 'animation', 'family', 'horror', 'music', 'history', 'tv movie', 'documentary']
# selected_genres = st.multiselect("Select Genres:", genres, default='all')
    
# if st.button("Filter movies"):
#     # Store the selected genres in session state
#     st.session_state.selected_genres = selected_genres
#     st.write("You select", selected_genres)

# Function to handle "Select All" and "Clear Selection" logic
def handle_special_options(selected_genres):
    if 'All' in selected_genres:
        return genres
    else:
        return selected_genres

def main():
    st.title("Movie Recommendation System: Test")

    if 'search_button' not in st.session_state:
        st.session_state.search_button = False

    if st.button("Search Movie", on_click=callback) or st.session_state.search_button:
        st.write("Display movies")
        display_reco(st.session_state.search_button)
        # st.session_state.search_button = True
        st.write("Search button:", st.session_state.search_button)

def filter_movies_by_genre(recommendations, selected_genres):

    newtmdb_df = pd.read_csv("ph_movies.csv")

    if selected_genres == genres:
        return recommendations
    
    # filtered_recommendations = [movie for movie in recommendations if any(genre in newtmdb_df["genres"] for genre in selected_genres)]
    # return filtered_recommendations
    filtered_recommendations = []
    for movie_title in recommendations:
        # Find the row in newtmdb_df corresponding to the movie title
        movie_row = newtmdb_df[newtmdb_df['title'] == movie_title]
        if not movie_row.empty:
            # Extract genres for the movie from the DataFrame
            genres_for_movie = movie_row['genres'].values[0]
            # Check if any of the selected genres is in the genres for the movie
            if all(genre in genres_for_movie for genre in selected_genres):
                filtered_recommendations.append(movie_title)
    return filtered_recommendations

def get_genres_for_recommendations(recommendations, newtmdb_df):
    genres_for_recommendations = []
    for movie_title in recommendations:
        # Find the row in newtmdb_df corresponding to the movie title
        movie_row = newtmdb_df[newtmdb_df['title'] == movie_title]
        if not movie_row.empty:
            # Extract genres for the movie from the DataFrame
            genres_for_movie = movie_row['genres'].values[0]
            genres_for_recommendations.append(genres_for_movie)
    return genres_for_recommendations

def display_reco(search_btn):
    recommendations = ["Hello, Love, Goodbye", "Alone/Together"]

    if 'selected_genres' not in st.session_state:
        st.session_state.selected_genres = ['All']
    
    # Initialize selected_genres as an empty list
    selected_genres = []

    # Multiselect widget with additional options
    selected_genres = st.multiselect("Select Genres:", ['All'] + genres, default='All')

    # Handle special options
    st.session_state.selected_genres = handle_special_options(selected_genres)

    newtmdb_df = pd.read_csv("ph_movies.csv")
    st.write("Search button:", search_btn)

    if st.button("Filter movies"):
        # Display selected genres
        # st.write("Selected Genres:", st.session_state.selected_genres)
        # st.write("Recommendations:", recommendations)
        st.session_state.filter_movies = filter_movies_by_genre(recommendations, st.session_state.selected_genres)
        st.balloons()
    
    if 'filter_movies' in st.session_state:
        st.write("Selected Genres:", st.session_state.selected_genres)
        st.write("Recommendations:", recommendations)
        st.write("Filtered Movies", st.session_state.filter_movies)
        reco = get_genres_for_recommendations(recommendations, newtmdb_df)
        st.write("Genres of the movies in recommendations:", reco)

def callback():
    st.session_state.search_button = True

if __name__ == "__main__":
    main()