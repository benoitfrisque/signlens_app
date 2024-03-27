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
def display_gallery_one_video_per_sign(signs, page_num, items_per_page=9, num_cols=3):

    num_rows = items_per_page // num_cols
    start_index = (page_num - 1) * items_per_page
    end_index = min(start_index + items_per_page, len(filtered_signs))

    signs = signs[start_index:end_index]
    # for i in range(start_index, end_index):
    for i in range(num_rows): # rows
        cols = st.columns(num_cols)  # Create a new column at each line to make sure they are aligned vertically
        for j in range(num_cols):
            sign = signs[i*num_cols + j]
            video_url = data[data['sign'] == sign]['url'].tolist()[0] # Get the first video for the sign
            with cols[j]:
                    st.markdown(f"#### {sign.capitalize()}")
                    st.video(video_url)

# Function to display video gallery for queried signs (somevideos per sign)
def display_gallery_query(query_signs, page_num, items_per_page=9, num_cols=3):

    start_index = (page_num - 1) * items_per_page
    end_index = min(start_index + items_per_page, len(query_signs))

    query_signs_page = query_signs[start_index:end_index]

    for i, sign in enumerate(query_signs_page):
        st.title(f"{sign.capitalize()}")
        cols = st.columns(num_cols)  # Create a new column at each line to make sure they are aligned vertically

        for j in range(num_cols):
            video_urls = data[data['sign'] == sign]['url'].tolist()
            if j < len(video_urls):
                with cols[j]:
                    st.video(video_urls[j])

# Streamlit UI
st.title("ASL Learning Center")

# Session state
if 'page_num' not in st.session_state:
    st.session_state.page_num = 1

# Search bar
search_query = st.text_input("Search for a sign").lower().strip()

items_per_page = 9

if search_query == "":
    max_items_per_sign = 1
    filtered_signs = unique_signs
    display_gallery_one_video_per_sign(unique_signs,  st.session_state.page_num)


else:
    # Filter signs based on search query
    filtered_signs = [sign for sign in unique_signs if search_query in sign.lower()]

    if not filtered_signs:
        st.warning("No signs found matching the search query.")
    else:
        max_items_per_sign = 3
        st.session_state.page_num = 1
        display_gallery_query(filtered_signs, st.session_state.page_num)


# # Javascript to scroll up
# js_scroll_up = '''
# <script>

#     // Get the body element
#     var body = window.parent.document.querySelector(".main");

#     // Set the scroll top to 0
#     body.scrollTop = 0;

#     body.style.backgroundColor = '#4931c'; // Adjust this color according to your dark theme
#     }
# </script>
# '''

# Page number button centered at the bottom
page_buttons_col = st.columns([1, 1, 2, 1, 1])

# Define your function to be called when the "Previous Page" button is clicked
def on_previous_page_click():
    st.session_state.page_num -= 1
    # st.components.v1.html(js_scroll_up)

# Define your function to be called when the "Next Page" button is clicked
def on_next_page_click():
    st.session_state.page_num += 1
    # st.components.v1.html(js_scroll_up)

# Check if there's a previous page available and show the "Previous Page" button
if st.session_state.page_num > 1:
    with page_buttons_col[1]:
        st.button("Previous Page", on_click=on_previous_page_click, key="prev_button")

# Check if there's a next page available and show the "Next Page" button
if len(filtered_signs) > st.session_state.page_num * items_per_page:
    with page_buttons_col[3]:
        st.button("Next Page", on_click=on_next_page_click, key="next_button")
