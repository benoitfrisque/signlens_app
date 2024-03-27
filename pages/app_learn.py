import streamlit as st
import pandas as pd
import os

# Load CSV data
@st.cache_data
def load_learn_video_url_list():
    resources_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')
    videos_url_csv_path = os.path.join(resources_folder, 'videos_learning_platform.csv')
    if not os.path.exists(videos_url_csv_path):
        raise FileNotFoundError(f"File not found: {videos_url_csv_path}")

    return pd.read_csv(videos_url_csv_path)

data = load_learn_video_url_list()

# Filter unique signs
unique_signs = data['sign'].unique()

# # Function to display video gallery for a sign
def display_gallery(filtered_signs, page_num, items_per_page, max_items_per_sign=None, num_cols=3):

    # start_index = (page_num - 1) * items_per_page
    # end_index = min(start_index + items_per_page, len(filtered_signs))

    # for i in range(start_index, end_index):
    for i in range(3): # rows
        sign = filtered_signs[i]
        videos = data[data['sign'] == sign]['url'].tolist()
        if max_items_per_sign is not None:
            videos = videos[:max_items_per_sign]

        cols = st.columns(num_cols) # Create a new column at each line to make sure they are aligned vertically


        for j in range(num_cols): # columns
            video_url = videos[0]
            col_index = j % num_cols
            with cols[col_index]:
                    st.video(video_url)


# # Streamlit UI
st.title("ASL Learning Center")

# Search bar
search_query = st.text_input("Search for a sign").strip()

if search_query == "":
    max_items_per_sign = 1
    filtered_signs = unique_signs

else:
    max_items_per_sign = None
    # Filter signs based on search query
    filtered_signs = [sign for sign in unique_signs if search_query.lower() in sign.lower()]

    if not filtered_signs:
        st.warning("No signs found matching the search query.")


# Pagination
page_num = st.number_input("Page Number", min_value=1, value=1)
items_per_page = 9

# Display gallery for selected sign
display_gallery(filtered_signs, page_num, items_per_page, max_items_per_sign)

# Load more button
if len(filtered_signs) > page_num * items_per_page:
    if st.button("Load More"):
        page_num += 1
        display_gallery(filtered_signs, page_num, items_per_page)
