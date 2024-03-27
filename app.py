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
    json_landmarks = process_video_to_landmarks_json(video)
    #json_data = process_video_to_landmarks_json(video) #, json_output=False,
        #save_annotated_video=False, show_preview=False, frame_interval=1,
        #frame_limit=None, rear_camera=True, output_dir=None)
    #response = requests.post("http://127.0.0.1:8000/predict", json=json_landmarks)
    # api returns {'Word:': word, 'Probability:': proba}
    #result = response.json()["Word"]
    #st.success(f"Predicted word: {Word} with probability {Probability}")
    #st.text(response.json())
    #st.success(f"Predicted word: {response.json()['Word']} with probability {response.json()['Probability']}")
    st.json(json_landmarks)
# Adjust color based on probability
#color = f"rgb({int(api_results['probability'] * 255)}, 0, 0)"
#st.markdown(f'<p style="color:{color}; font-size: 24px;">{api_results["word"]}</p>', unsafe_allow_html=True)
