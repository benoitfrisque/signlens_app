import base64
import streamlit as st
import os
import numpy as np
import pandas as pd
import time
import random
from streamlit_extras.let_it_rain import rain

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
with open("resources/signlens-favicon-white.png", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode()
side_logo = f"data:image/png;base64,{encoded_string}"
background_image = "resources/background_signlens.png"

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

#url = "https://img.freepik.com/free-photo/sign-language-collage-design_23-2150528183.jpg?t=st=1711466807~exp=1711470407~hmac=c1c1a9a378d0a17254e6cf298fb262c2883e305f2ee08999e0771f76be98eeb4&w=900"
#url = "resources/signlens-high-resolution-logo-black.png"

st.markdown(
        f"""
        <style>
            [data-testid="stSidebarNav"] + div {{
                position:absolute;
                bottom: 0;
                height:50%;
                background-image: url({side_logo});
                background-size: 50% auto;
                background-repeat: no-repeat;
                background-position-x: center;
                background-position-y: bottom;
                border-bottom: 2px solid black;
                background-color: rgba(255, 255, 255, 0.08); /* Add this line for light background */
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.5); /* Add this line for shading */
            }}

            [data-testid="stAppViewContainer"] > .main {{
            background-image: url({background_image});
            background-size: 100vw 100vh;  # This sets the size to cover 100% of the viewport width and height
            background-position: center;
            background-repeat: no-repeat;
            }}

                        .stApp > div:first-child {{
                background-image: url({background_image});
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
            }}
            [data-testid="stAppViewContainer"] {{
            background-color: transparent;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

st.title("ASL Learning Game")

st.sidebar.title("About SignLens")
st.sidebar.caption("An app for translating sign language, but also aid in learning it. Upload a video of sign language gestures and click the button to translate the signs to text!")

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

def submit_answer(option,position=None):
    #with st.container():
    #position = st.empty()
    if option == st.session_state.correct_option:
        position.write("<center><span style='color:green; font-size:x-large'>Correct!</span></center>", unsafe_allow_html=True)
        st.balloons()
    else:  #<br>
        position.write(f"<center>You selected: \t <span style='color:red; font-size:x-large'>{option.capitalize()}</span> &nbsp;&nbsp;&nbsp;&nbsp; \n \
            The correct option was: \t <span style='color:green; font-size:x-large'>{st.session_state.correct_option.capitalize()}</span></center>",
            unsafe_allow_html=True)
        #position.write(f"#, unsafe_allow_html=True)
        #st.snow()
        # import time
        # start_time = time.time()
        # if time.time() - start_time < 3:
        #     time.sleep(0.1)
        #     rain(
        #     emoji="👎        💩",
        #     font_size=44,
        #     falling_speed=3,
        #     animation_length=1
        #     )

    st.session_state.answer_submitted = True



# Function to display the game options
def display_game():
    #container.video(data=VIDEO_DATA)
    st.subheader("Watch the Sign")
    col1, col2, _ = st.columns([0.25, 0.7, 0.3])
    #with col2:
        #st.video(st.session_state.url)
    #col1.subheader("Watch the Sign")
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
