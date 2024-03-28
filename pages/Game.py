import streamlit as st
import os
import numpy as np
import pandas as pd
import time

st.set_page_config(
        page_title="SignLens Play",
        page_icon="resources/signlens-favicon-black.png",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Report a bug': "https://github.com/benoitfrisque/signlens",
            'About': "# This is our final project for Le Wagon Data Science Bootcamp!"
            }
)


st.title("ASL Learning Game")


# Load CSV data
@st.cache_data
def load_learn_video_url_list():
    resources_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')
    videos_url_csv_path = os.path.join(resources_folder, 'videos_learning_platform.csv')
    if not os.path.exists(videos_url_csv_path):
        raise FileNotFoundError(f"File not found: {videos_url_csv_path}")

    df = pd.read_csv(videos_url_csv_path)

    return df

data = load_learn_video_url_list()

# Filter unique signs
unique_signs = np.sort(data['sign'].unique())

@st.cache_data
def select_random_video():
    random_index = np.random.randint(len(data))
    return data.iloc[random_index]

@st.cache_data
def generate_options(unique_signs, correct_option):
    options = np.random.choice(unique_signs, size=3, replace=False)
    options = np.append(options, correct_option)
    np.random.shuffle(options)
    return options


# Function to display the game options
def display_game(video_data):
    st.subheader("Watch the Sign")
    st.video(video_data['url'] )

    st.subheader("Which Sign Is It?")
    correct_option = video_data['sign']
    options = generate_options(unique_signs, correct_option)

    # Display options in a 2x2 grid
    col1, col2 = st.columns(2)

    # Loop through options and display buttons
    for i, option in enumerate(options):
        column = col1 if i < 2 else col2
        with column:
            if st.button(option.capitalize(), key=option, use_container_width=True):

                # Update state to indicate that an option has been selected
                st.session_state.option_selected = True
                st.session_state.correct_option = correct_option

                if option == correct_option:
                    st.write("You got it right!")
                else:
                    st.write("Sorry, that's not correct. Try again!")


# Initialize session state

if 'option_selected' not in st.session_state:
    st.session_state.option_selected = False

if 'correct_option' not in st.session_state:
    st.session_state.correct_option = None


# Check if an option has been selected
if  st.session_state.option_selected:
    # If an option has been selected, display the correct option and reset state
    if st.session_state.correct_option:
        st.write(f"The correct option was: {st.session_state.correct_option.capitalize()}")
    st.session_state.option_selected = False
    st.session_state.correct_option = None

else:
    # If no option has been selected, play the game
    random_video_data = select_random_video()
    display_game(random_video_data)
