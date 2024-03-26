#from io import BytesIO
#import json
import streamlit as st
#import cv2
import requests
#from PIL import Image
#import mediapipe as mp
#import av
#from utils import *
#from utils import process_video_to_landmarks_json
from video_utils  import process_video_to_landmarks_json
NUM_CLASSES=10
st.set_page_config(page_title="SignLens Demo",
                                    page_icon="🎭", layout="centered",
                                    #initial_sidebar_state="expanded"
                                    )
#video_json = video_utils.process_video_to_landmarks_json()
st.title("SignLens please!...")
st.subheader("Sign Language translation")
st.caption("using Mediapipe for Landmark extraction  and an RNN model for translation")

# Open video file if uploaded
video = st.file_uploader("Upload a video", type=["mp4", "mov", "avi", "mkv", "asf",
    #"m4v", "mkv", "wmv", "flv", "webm", "3gp", "ogg", "ogv", "gif", "mpg", "mpeg",
    "m2v", "ts", "m2ts", "mts", "vob"], accept_multiple_files=False)

if video:
    with st.spinner("extracting landmarks... 🐢"):
        landmarks = process_video_to_landmarks_json(video)
        st.json(landmarks)
    #json_data = process_video_to_landmarks_json(video) #, json_output=False,
        #save_annotated_video=False, show_preview=False, frame_interval=1,
        #frame_limit=None, rear_camera=True, output_dir=None)
#response = requests.post("http://127.0.0.1:8000/api, json=json_data)
#result = response.json()["result"]
#st.success(f"Result: {result}")

# Adjust color based on probability
#color = f"rgb({int(api_results['probability'] * 255)}, 0, 0)"
#st.markdown(f'<p style="color:{color}; font-size: 24px;">{api_results["word"]}</p>', unsafe_allow_html=True)





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
