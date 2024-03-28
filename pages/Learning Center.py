import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(
        page_title="SignLens Learn",
        page_icon="resources/signlens-favicon-black.png",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Report a bug': "https://github.com/benoitfrisque/signlens",
            'About': "# This is our final project for Le Wagon Data Science Bootcamp!"
            }
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
