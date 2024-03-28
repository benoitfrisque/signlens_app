import base64
import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(
        page_title="SignLens Learn",
        page_icon="resources/signlens-favicon-white.png",
        layout="wide",
        initial_sidebar_state="auto",
        menu_items={
            'Report a bug': "https://github.com/benoitfrisque/signlens",
            'About': "# This is our final project for Le Wagon Data Science Bootcamp!"
            }
)

st.sidebar.title("About SignLens")
st.sidebar.caption("An app for translating sign language, but also aid in learning it. Upload a video of sign language gestures and click the button to translate the signs to text!")

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

# Streamlit UI
st.title("ASL Learning Center")
ITEMS_PER_PAGE = 9
SIGNS_PER_PAGE = 3
NUM_COLS = 3

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


# Function to display video gallery for all signs (one video per sign)
def display_gallery_one_video_per_sign(signs, page_num):

    num_rows = ITEMS_PER_PAGE // NUM_COLS
    start_index = (page_num - 1) * ITEMS_PER_PAGE
    end_index = min(start_index + ITEMS_PER_PAGE, len(filtered_signs))

    signs = signs[start_index:end_index]

    for i in range(num_rows): # rows
        cols = st.columns(NUM_COLS)  # Create a new column at each line to make sure they are aligned vertically
        for j in range(NUM_COLS):
            if i*NUM_COLS + j >= len(signs):
                break
            sign = signs[i*NUM_COLS + j]
            video_url = data[data['sign'] == sign]['url'].tolist()[0] # Get the first video for the sign
            with cols[j]:
                    st.markdown(f"#### {sign.capitalize()}")
                    st.video(video_url)

# Function to display video gallery for queried signs (somevideos per sign)
def display_gallery_query(query_signs, page_num):

    start_index = (page_num - 1) * SIGNS_PER_PAGE
    end_index = min(start_index + SIGNS_PER_PAGE, len(query_signs))

    query_signs_page = query_signs[start_index:end_index]

    for i, sign in enumerate(query_signs_page):
        st.title(f"{sign.capitalize()}")
        cols = st.columns(NUM_COLS)  # Create a new column at each line to make sure they are aligned vertically

        for j in range(NUM_COLS):
            video_urls = data[data['sign'] == sign]['url'].tolist()
            if j < len(video_urls):
                with cols[j]:
                    st.video(video_urls[j])


# Session states
if 'page_num' not in st.session_state:
    st.session_state.page_num = 1

if 'total_pages' not in st.session_state:
    st.session_state.total_pages = st.session_state.total_pages = len(unique_signs) // ITEMS_PER_PAGE + 1

if 'mode' not in st.session_state:
    st.session_state.mode = "one_video_per_sign"


# Search bar
search_query = st.text_input("Search for a sign").lower().strip()

if search_query == "":

    filtered_signs = unique_signs

    # Reset the mode to "one_video_per_sign" if it was changed
    if st.session_state.mode != "one_video_per_sign":
        st.session_state.mode = "one_video_per_sign"
        st.session_state.page_num = 1
        st.session_state.total_pages = len(filtered_signs) // ITEMS_PER_PAGE + 1

    display_gallery_one_video_per_sign(unique_signs,  st.session_state.page_num)

else:

    # Filter signs based on search query
    filtered_signs = [sign for sign in unique_signs if search_query in sign.lower()]

    # On search query, change the mode to "query" and reset the page number
    if st.session_state.mode != "query":
        st.session_state.mode = "query"
        st.session_state.page_num = 1


    if not filtered_signs:
        st.warning("No signs found matching the search query.")
    else:

        st.session_state.total_pages = (len(filtered_signs) -1) // SIGNS_PER_PAGE + 1
        display_gallery_query(filtered_signs, st.session_state.page_num)


# Page number button centered at the bottom
page_buttons_col = st.columns([1, 1, 1, 2, 1, 1])


def on_previous_page_click():
    st.session_state.page_num -= 1
    # st.components.v1.html(js_scroll_up)

def on_next_page_click():
    st.session_state.page_num += 1
    # st.components.v1.html(js_scroll_up)

def on_first_page_click():
    st.session_state.page_num = 1

def on_last_page_click():
    st.session_state.page_num = st.session_state.total_pages

# Check if there's a previous page available and show the "Previous Page" button
if st.session_state.page_num > 1:
    with page_buttons_col[1]:
        st.button("Previous Page", on_click=on_previous_page_click, key="prev_button")

# Check if there's a next page available and show the "Next Page" button
if st.session_state.page_num < st.session_state.total_pages:
    with page_buttons_col[4]:
        st.button("Next Page", on_click=on_next_page_click, key="next_button")


# Show the page number out of the total number of pages
with page_buttons_col[3]:
    st.markdown(f"Page {st.session_state.page_num} of {st.session_state.total_pages}")


# Show the "First Page" button
with page_buttons_col[0]:
    st.button("First Page", on_click=on_first_page_click, key="first_button")

# Show the "Last Page" button
with page_buttons_col[5]:
    st.button("Last Page", on_click=on_last_page_click, key="last_button")
