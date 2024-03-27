# import streamlit as st
# from PIL import Image
# import cv2
# from google.protobuf.json_format import MessageToDict

# st.title("Learn Sign Language Signs from Videos")

# # List of video links
# video_links = [
#     "https://example.com/video1.mp4",
#     "https://example.com/video2.mp4",
#     "https://example.com/video3.mp4",
#     # Add more video links here...
# ]

# for link in video_links:
#     # Download video
#     response = requests.get(link)
#     video_bytes = response.content

#     # Process video
#     video_reader = cv2.VideoCapture(BytesIO(video_bytes))
#     success, frame = video_reader.read()

#     # Show video frames
#     while success:
#         image = Image.fromarray(frame)
#         label = st.empty()
#         label.write("")
#         video_display = st.empty()
#         video_display.image(image)
#         success, frame = video_reader.read()


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
signs = data['sign'].unique()

# Function to display video gallery for a sign
def display_gallery(sign, max_videos=None):
    videos = data[data['sign'] == sign]['url'].tolist()
    if max_videos is not None:
        videos = videos[:max_videos]
    st.write(f"## {sign.capitalize()} Sign")
    for video_url in videos:
        st.write(f"### {sign.capitalize()}")
        st.video(video_url)

# Streamlit UI
st.title("Sign Language Video Gallery")

# Search bar
search_query = st.text_input("Search for a sign")

# Filter signs based on search query
filtered_signs = [sign for sign in signs if search_query.lower() in sign.lower()]

if not filtered_signs:
    st.warning("No signs found matching the search query.")
else:
    # Display search results
    if search_query == "":
        for sign in filtered_signs:
            display_gallery(sign, max_videos=1)
    else:
        for sign in filtered_signs:
            display_gallery(sign)
