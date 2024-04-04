import base64
import streamlit as st
import os
import numpy as np
import pandas as pd
import time
import random

st.set_page_config(
    page_title="SignLens Play",
    page_icon="resources/signlens-favicon-white.png",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        'Report a bug': "https://github.com/benoitfrisque/signlens",
        'About': "# This is our final project for Le Wagon Data Science Bootcamp!"
    }
)

# Add custom CSS
st.markdown("""
<style>
.reportview-container .main .block-container {
    padding-top: 1rem;
    padding-right: 2.5rem;
    padding-left: 2.5rem;
    padding-bottom: 1rem;
}

.sidebar .sidebar-content {
    padding-top: 1rem;
    padding-right: 1rem;
    padding-left: 1rem;
    padding-bottom: 1rem;
}

h1 {
    color: #A980D6;
}
}
</style>
""", unsafe_allow_html=True)

# Sidebar content
with open("resources/signlens-favicon-white.png", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode()
side_logo = f"data:image/png;base64,{encoded_string}"

st.sidebar.title("About SignLens")
st.sidebar.caption("An app for translating sign language, but also aid in learning it. Upload a video of sign language gestures and click the button to translate the signs to text!")

st.markdown(
    f"""
    <style>
        /* Adjust sidebar height based on its content */
        .sidebar .sidebar-content {{
            height: auto !important;
            transition: height 0.5s;
            position: relative; /* Make the sidebar content positioning relative */
        }}

        /* Text styling */
        .about-text {{
            text-align: center;
            margin-top: 10px; /* Adjust margin-top to create space between text and image */
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
        }}

        /* Logo styling */
        [data-testid="stSidebarNav"] + div {{
                position:absolute;
                bottom: 0;
                left: 0;
                width: 100%;
                height: 50%;
                background-image: url({side_logo});
                background-size: 50% auto;
                background-repeat: no-repeat;
                background-position-x: center;
                background-position-y: bottom;
                background-color: rgba(255, 255, 255, 0.08); /* Add this line for light background */
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.5); /* Add this line for shading */
            }}

        /* Hide the image when sidebar is collapsed */
        .sidebar.collapsed [data-testid="stSidebarNav"] + div {{
            display: none;
        }}
    </style>
    """,
    unsafe_allow_html=True
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
    random.shuffle(unique_options)

    # Select the first four unique options
    final_options = unique_options[:4]

    # Check if correct_option is already in final_options
    if st.session_state.correct_option not in final_options:
        # If not, replace a random element with correct_option
        replace_index = np.random.randint(0, 4)
        final_options[replace_index] = st.session_state.correct_option


    random.shuffle(final_options)
    st.session_state.options = final_options


if "random_index"  not in st.session_state:
    select_random_video()


def submit_answer(option,position=None):
    if option == st.session_state.correct_option:
        position.write("<center><span style='color:green; font-size:x-large'>Correct!</span></center>", unsafe_allow_html=True)
        st.balloons()
    else:  #<br>
        position.write(f"<center>You selected: \t <span style='color:red; font-size:x-large'>{option.capitalize()}</span> &nbsp;&nbsp;&nbsp;&nbsp; \n \
            The correct option was: \t <span style='color:green; font-size:x-large'>{st.session_state.correct_option.capitalize()}</span></center>",
            unsafe_allow_html=True)

    st.session_state.answer_submitted = True



# Function to display the game options
def display_game():
    #container.video(data=VIDEO_DATA)
    st.subheader("Watch the Sign")
    col1, col2, _ = st.columns([0.25, 0.7, 0.3])
    col2.video(st.session_state.url)

    st.subheader("Which Sign Is It?")

    # Display options in a 2x2 grid
    col1, col2 = st.columns(2)

    for i, option in enumerate(st.session_state.options):
        column = col1 if i < 2 else col2
        bottom = st.empty()
        column.button(option.capitalize(), key=option, on_click=submit_answer,args=(option,bottom), use_container_width=True)


# Initialize session state
if 'answer_submitted' not in st.session_state:
    st.session_state.answer_submitted = False

# Check if an option has been selected
if st.session_state.answer_submitted:
    time.sleep(3)
    # If an option has been selected, display the correct option and reset state
    st.session_state.answer_submitted = False
    st.session_state.correct_option = None
    select_random_video()
    display_game()

else:
    display_game()
