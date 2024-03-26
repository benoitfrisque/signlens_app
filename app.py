import time
import streamlit as st
import requests
import json
import cv2
from video_utils import process_video_to_landmarks_json

NUM_CLASSES = 10

st.set_page_config(page_title="SignLens Demo",
                   page_icon="🎭", layout="wide",
                   initial_sidebar_state="expanded")

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

.stButton > button:hover {
    background-color: #4caf50;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# Sidebar content
logo = "https://raw.githubusercontent.com/robmarkcole/Holistic-Video-Understanding/main/docs/images/logo.png"
logo = "https://www.freepik.com/free-vector/technology-circle-ai-abstract-vector-computer-vision-design_18236528.htm#query=cyborg%20eye&position=6&from_view=keyword&track=ais&uuid=6aae1df3-0c6e-49d5-a59f-300d5c4bd73d"
logo = "signlens-high-resolution-logo.png"
st.sidebar.image("logo", width=200)
st.sidebar.title("About SignLens")
st.sidebar.caption("An app for sign language translation using Mediapipe and an RNN model.")

# Main content
col1, col2 = st.columns([1, 2])

with col1:
    st.title("SignLens Demo")
    st.subheader("Sign Language translation")

with col2:
    # Open video file if uploaded
    video = st.file_uploader("Upload a video", type=["mp4", "mov", "avi", "mkv",
                                                         "m4v", "mkv", "wmv", "flv", "webm", "3gp", "ogg", "ogv", "gif", "mpg", "mpeg",
                                                         "asf", "m2v", "ts", "m2ts", "mts", "vob"], accept_multiple_files=False)

if video:
    # Display video preview
    st.video(video)

    state = "running"

    # Create a status container
    status_text = st.empty()

    try:
        start_time = time.time()

        with st.spinner("⏱️ ... 🐢"):
            # Display the status
            status_text.text("Extracting landmarks")

            # Call the process_video_to_landmarks_json function
            json_landmarks = process_video_to_landmarks_json(video)

            st.json(json_landmarks, expanded=False)

        with st.spinner("Requesting API response..."):
            headers = {'Content-Type': 'application/json'}
            response = requests.post(#"http://127.0.0.1:8000/predict",
                                     'https://signlens-pait7pkgma-oa.a.run.app/predict',
                                     headers=headers, json=json_landmarks, timeout=120)

        elapsed_time = time.time() - start_time

        # Check the response code and handle accordingly
        if response.ok:  # 200 <= response.status_code < 300
            status_text.text(f"Video processing complete! 🎉 (Elapsed time: {elapsed_time:.2f} seconds)")
            result = response.json()
            st.success(f"Result: {result}")
            st.write(f"Word: {result['Word:']}")
            st.write(f"Probability: {result['Probability:']}")
            state = "complete"
            st.balloons()
        else:
            status_text.text(f"API Error: {response.status_code}")
            st.error(f"API Error: {response.status_code}")
            state = "error"

    except Exception as e:
        status_text.text(f"API Error: {e}")
        st.error(f"API Error: {e}")
        state = "error"






#cap = cv2.VideoCapture(video_stream)


# if video_stream:
#     while True:
#         frame = video_stream.video_receiver
#         img = frame.to_ndarray(format="bgr24")
#         img = av.VideoFrame(frame.to_ndarray(format="bgr24"), format="bgr24")
#         #img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#         with mp_holistic.Holistic(min_detection_confidence=min_detection_confidence, min_tracking_confidence=min_tracking_confidence) as holistic:
#             results = holistic.process(img)

#             mp_drawing.draw_landmarks(
#                 img,
#                 results.face_landmarks,
#                 mp_holistic.FACEMESH_TESSELATION,
#                 mp_drawing.DrawingSpec(color=(80, 110, 10), thickness=1, circle_radius=1),
#                 mp_drawing.DrawingSpec(color=(80, 256, 121), thickness=1, circle_radius=1)
#             )

#             mp_drawing.draw_landmarks(
#                 img,
#                 results.right_hand_landmarks,
#                 mp_holistic.HAND_CONNECTIONS,
#                 mp_drawing.DrawingSpec(color=(80, 22, 10), thickness=2, circle_radius=4),
#                 mp_drawing.DrawingSpec(color=(80, 44, 121), thickness=2, circle_radius=2)
#             )

#             mp_drawing.draw_landmarks(
#                 img,
#                 results.left_hand_landmarks,
#                 mp_holistic.HAND_CONNECTIONS,
#                 mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
#                 mp_drawing.DrawingSpec(color=(121, 44, 250), thickness=2, circle_radius=2)
#             )

#             mp_drawing.draw_landmarks(
#                 img,
#                 results.pose_landmarks,
#                 mp_holistic.POSE_CONNECTIONS,
#                 mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=4),
#                 mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2)
#             )

#         #st.img(img, channels="RGB")
#         av.VideoFrame.from_ndarray(img, format="bgr24")
