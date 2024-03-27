import streamlit as st
import pandas as pd
import numpy as np
import os
import requests

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

# # Function to display video gallery for a sign
def display_gallery_one_video_per_sign(signs, page_num, items_per_page=9, num_cols=3):

    num_rows = items_per_page // num_cols
    start_index = (page_num - 1) * items_per_page
    end_index = min(start_index + items_per_page, len(filtered_signs))

    # for i in range(start_index, end_index):
    for i in range(num_rows): # rows
        cols = st.columns(num_cols)  # Create a new column at each line to make sure they are aligned vertically
        for j in range(num_cols):
            sign = signs[i*num_cols + j]
            video_url = data[data['sign'] == sign]['url'].tolist()[0] # Get the first video for the sign
            with cols[j]:
                    st.markdown(f"#### {sign.capitalize()}")
                    st.video(video_url)


# # Streamlit UI
st.title("ASL Learning Center")

# Search bar
search_query = st.text_input("Search for a sign").strip()

items_per_page = 9

if search_query == "":
    max_items_per_sign = 1
    filtered_signs = unique_signs

else:
    max_items_per_sign = None
    # Filter signs based on search query
    filtered_signs = [sign for sign in unique_signs if search_query.lower() in sign.lower()]

    if not filtered_signs:
        st.warning("No signs found matching the search query.")

# Session state
if 'page_num' not in st.session_state:
    st.session_state.page_num = 1



# Display gallery for all signs
display_gallery_one_video_per_sign(filtered_signs, st.session_state.page_num)


# # Page number button centered at the bottom
# col1, col2, col3 = st.columns([1, 2, 1])

# if st.session_state.page_num > 1:
#     with col1:
#         if st.button("Previous Page", key="prev_button"):
#             st.session_state.page_num -= 1

# if len(filtered_signs) > st.session_state.page_num * items_per_page:
#     with col3:
#         if st.button("Next Page", key="next_button"):
#             st.session_state.page_num += 1
