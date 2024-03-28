import streamlit as st
import os
import numpy as np
import pandas as pd
import time
import random

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


# callback function to change the random number stored in state
def select_random_video():
    st.session_state.random_index = np.random.randint(len(data))

    random_video_data = data.iloc[st.session_state.random_index]
    st.session_state.url = random_video_data['url']

    st.session_state.correct_option = random_video_data['sign']
    # Randomly choose options
    options = np.random.choice(unique_signs, size=4, replace=False)  # Choose 3 random options

    # Concatenate correct option and randomly chosen options
    options = np.append(st.session_state.correct_option, options)

    # Remove duplicates
    unique_options = list(set(options))

    # Check if correct_option is already in unique_options
    if st.session_state.correct_option not in unique_options:
        # If not, replace a random element with correct_option
        replace_index = np.random.randint(0, len(unique_options))
        unique_options[replace_index] = st.session_state.correct_option

    # Select the first four unique options
    final_options = unique_options[:4]
    random.shuffle(final_options)
    st.session_state.options = final_options

    return


if "random_index"  not in st.session_state:
    st.session_state.random_index = np.random.randint(len(data))
    print(st.session_state.random_index )

    random_video_data = data.iloc[st.session_state.random_index]
    st.session_state.url = random_video_data['url']

    st.session_state.correct_option = random_video_data['sign']
    # Randomly choose options
    options = np.random.choice(unique_signs, size=4, replace=False)  # Choose 3 random options

    # Concatenate correct option and randomly chosen options
    options = np.append(st.session_state.correct_option, options)

    # Remove duplicates
    unique_options = list(set(options))

    # Check if correct_option is already in unique_options
    if st.session_state.correct_option not in unique_options:
        # If not, replace a random element with correct_option
        replace_index = np.random.randint(0, len(unique_options))
        unique_options[replace_index] = st.session_state.correct_option

    # Select the first four unique options
    final_options = unique_options[:4]
    random.shuffle(final_options)
    st.session_state.options = final_options

def submit_answer(option):

    if option == st.session_state.correct_option:
        st.write("<span style='color:green'>Correct!</span>", unsafe_allow_html=True)
        st.balloons()
    else:
        st.write(f"You selected: <span style='color:red'>{option.capitalize()}</span>", unsafe_allow_html=True)
        st.write(f"The correct option was: <span style='color:green'>{st.session_state.correct_option.capitalize()}</span>", unsafe_allow_html=True)


    st.session_state.answer_submitted = True



# Function to display the game options
def display_game():
    st.subheader("Watch the Sign")
    col1, col2, col3 = st.columns([0.25, 0.8, 0.2])
    with col2:
        st.video(st.session_state.url)

    st.subheader("Which Sign Is It?")

    # Display options in a 2x2 grid
    col1, col2 = st.columns(2)

    for i, option in enumerate(st.session_state.options):
        column = col1 if i < 2 else col2
        column.button(option.capitalize(), key=option, on_click=submit_answer,args=(option,), use_container_width=True)


# Initialize session state
if 'answer_submitted' not in st.session_state:
    st.session_state.answer_submitted = False

# Check if an option has been selected
if st.session_state.answer_submitted:
    time.sleep(1)
    # If an option has been selected, display the correct option and reset state
    st.session_state.answer_submitted = False
    st.session_state.correct_option = None
    select_random_video()
    display_game()

else:
    display_game()
