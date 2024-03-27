import time
import streamlit as st
import requests
import json
import cv2
from video_utils import process_video_to_landmarks_json
from streamlit_extras.app_logo import add_logo

import base64


st.set_page_config(page_title="SignLens Demo",
                   page_icon="⚙︎", layout="wide",
                   initial_sidebar_state="expanded")


# @st.cache_resource(allow_output_mutation=True)
# def get_base64_of_bin_file(bin_file):
#     with open(bin_file, 'rb') as f:
#         data = f.read()
#     return base64.b64encode(data).decode()

# def set_png_as_page_bg(png_file):
#     bin_str = get_base64_of_bin_file(png_file)
#     page_bg_img = '''
#     <style>
#     body {
#     background-image: url("data:image/png;base64,%s");
#     background-size: cover;
#     }
#     </style>
#     ''' % bin_str

#     st.markdown(page_bg_img, unsafe_allow_html=True)
#     return

# set_png_as_page_bg('resources/background_signlens.png')

NUM_CLASSES = 10

# def set_background(png_file):
#     bin_str = get_base64(png_file)
#     page_bg_img = '''
#     <style>
#     .stApp {
#     background-image: url("data:image/png;base64,%s");
#     background-size: cover;
#     }
#     </style>
#     ''' % bin_str
#     st.markdown(page_bg_img, unsafe_allow_html=True)
# set_background('resources/background_signlens.png')

# url("https://images.unsplash.com/photo-1542281286-9e0a16bb7366");

# @st.cache_data
# def get_img_as_base64(file):
#     with open(file, "rb") as f:
#         data = f.read()
#     return base64.b64encode(data).decode()

# img_background = get_img_as_base64("resources/background_signlens.png")

#https://drive.google.com/file/d/1kzhZnny42X52bbAehiN94USuLKowmiJk/view?usp=drive_link
#https://1drv.ms/i/s!AokgWCkazMPtpiqzTu31KLHslEj-?e=HNTSKG
# Add custom CSS
st.markdown("""
<style>
[data-testid="stAppViewContainer"] > .main {
    background-image: url("resources/background_signlens.png");
    background-size: 100vw 100vh;  # This sets the size to cover 100% of the viewport width and height
    background-position: center;
    background-repeat: no-repeat;

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
    color: #adffb7;
}
<!--
body {
background-image: url("https://images.unsplash.com/photo-1542281286-9e0a16bb7366");
background-size: cover;
-->
}
</style>
""", unsafe_allow_html=True)

# .stButton > button:hover {
#     background-color: #c91a2c; #4caf50;
#     color: purple;
# }


# Initialize the key in session state
if 'clicked' not in st.session_state:
    st.session_state.clicked = {1:False,2:False}

# Function to update the value in session state
def clicked(button):
    '''Update the value in session state when a button is clicked.'''
    st.session_state.clicked[button] = True

# Sidebar content
logo = "https://img.freepik.com/free-photo/sign-language-collage-design_23-2150528183.jpg?t=st=1711466807~exp=1711470407~hmac=c1c1a9a378d0a17254e6cf298fb262c2883e305f2ee08999e0771f76be98eeb4&w=900"
#logo = "https://www.freepik.com/free-vector/technology-circle-ai-abstract-vector-computer-vision-design_18236528.htm#query=cyborg%20eye&position=6&from_view=keyword&track=ais&uuid=6aae1df3-0c6e-49d5-a59f-300d5c4bd73d"
logo = "resources/signlens-high-resolution-logo-transparent.png"
st.sidebar.image(logo,use_column_width=True)
#add_logo(logo_url=logo,height=10)
st.sidebar.title("About SignLens")
st.sidebar.caption("An app for translating sign language, but also aid in learning it.")
st.sidebar.info("This is a demo app using computer vision and deep learning. Upload a video of sign language gestures and click the button to translate the signs to text. The app uses the Mediapipe library to extract landmarks from the video frames and sends the landmarks to a FastAPI server running a pre-trained RNN model to predict the sign language word.")
#placeholder = st.empty()

st.title("SignLens Demo")
# Main content
col1, col2 = st.columns([2, 1])

st.session_state.b2_disabled = True

with col1:
    st.subheader("Upload a video to translate sign to text")
    holder = st.empty()
    title1 = st.empty()
    # Open video file if uploaded
    #if st.button("Upload a video", on_click=clicked, args=[1], key="upload_video",type="primary"):
    with st.spinner("Uploading video..."):
        #time.sleep(1.5)
        video = st.file_uploader("Select video file", label_visibility="collapsed", key="upload_video", help="Upload a video file",
                                 #disabled=~st.session_state.b2_disabled,
                                 type=["mp4", "mov", "avi", "mkv",
                                                         #"m4v", "mkv", "wmv", "flv", "webm", "3gp", "ogg", "ogv", "gif", "mpg", "mpeg",
                                                         "asf", "m2v", "ts", "m2ts", "mts", "vob"], accept_multiple_files=False)
    if video:
        st.session_state.b2_disabled = False
        holder.video(video)
        title1.write(":green[Video uploaded successfully!] :tada:")

with col2:
    st.subheader("Sign translation")
    #expander = st.expander("Optional controls")
    #expander.radio("Options", ["Translate", "Learn", "Live"])
    #if st.button("Push to translate"):
    # Add a button to start the prediction
    # Conditional based on value in session state, not the output
    st.button("Start Translation", on_click=clicked, args=[2],
              type="primary", disabled=st.session_state.b2_disabled)
    if video: #st.session_state.clicked[1]:
        if st.session_state.clicked[2]:
            state = "running"

            # Create a status container
            status_text = st.empty()

            try:
                start_time = time.time()

                with st.spinner("⏱️ Extracting landmarks... 🐢"):
                    # Display the status
                    #status_text.status("Extracting landmarks")

                    # Call the process_video_to_landmarks_json function
                    json_landmarks = process_video_to_landmarks_json(video)

                    # st.json(json_landmarks, expanded=False) # just for debugging

                with st.spinner("⏱️ Requesting API response... 🐢"):
                    #status_text.status("Requesting API response...")

                    headers = {'Content-Type': 'application/json'}
                    response = requests.post(#"http://127.0.0.1:8000/predict",
                                            'https://signlens-pait7pkgma-oa.a.run.app/predict',
                                            headers=headers, json=json_landmarks, timeout=120)

                elapsed_time = time.time() - start_time

                # Check the response code and handle accordingly
                if response.ok:  # 200 <= response.status_code < 300
                    status_text.text(f"Video processing complete! 🎉     (Elapsed time: {elapsed_time:.2f} seconds)")
                    result = response.json()
                    #result
                    sign = result['sign']
                    proba = result['probability']
                    proba = round(100*(proba),2)
                    #st.write(result['sign'])
                    #st.success(f"Our model predicts the following sign: {result['sign']} with a probability of {100*(result['probability']):.2f}%")
                    #st.write(f"sign: {result['sign:']}")
                    #st.metric("probability", f"{100*(result['probability']):.2f}%")
                    state = "complete"
                    time.sleep(1)
                    st.balloons()

                    #"Translation guess:"
                    #st.header(f"{result['sign']}")

                    # probc = ":%s[%s]" % (probability_color, f"{100*(proba):.2f}%")
                    # #st.metric("probability",f"{100*(proba):.2f}%", probability_color)
                    st.title(sign)
                    #st.write(:green["Translation guess"])
                    #probability_color
                    #"probability:"
                    #st.metric(value=proba,label="probability")
                    #st.text_area("Translation guess", sign, height=100)
                    probability_color = "green" if proba > 50 else "yellow" if proba < 80 else "red"
                    if probability_color == "green":
                        st.write("is our best guess with probability", f":green[{proba}%]")
                    elif probability_color == "yellow":
                        st.write("is our best guess with probability", f":yellow[{proba}%]")
                    else:
                        st.write("is our best guess with probability", f":red[{proba}%]")

                    search_term = result['sign']
                    # Pixabay API
                    api_key = str(st.secrets.api_key)
                    url = "https://pixabay.com/api/?key=%s&q=%s&image_type=photo&pretty=true" % (str(api_key),search_term)
                    response = requests.get(url, timeout=60)
                    image_data = response.json()
                    #image_data
                    img_url = image_data["hits"][0]["webformatURL"]

                    # Lookup an image of the result['sign'] using Unsplash API
                    #unsplash_access_key = "YOUR_UNSPLASH_ACCESS_KEY"
                    #url = f"https://api.unsplash.com/photos/random/?query={result['sign']}&client_id={unsplash_access_key}"
                    # response = requests.get(url)
                    # image_data = response.json()
                    # image_url = image_data["urls"]["small"]

                    # Lookup a GIF of the result['sign'] using Tenor API
                    # ckey = "signlens_app"
                    # tenor_access_key = "AIzaSyAJPjaf0y_8RtvPm-xJ5xsitGDDy-oAfmc"
                    # url = "https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % (search_term, tenor_access_key, ckey,  1)

                    # response = requests.get(url, timeout=60)
                    # gif_data = response.json()
                    # gif_data
                    # gif_url = gif_data["results"][0]["media_formats"]["gif"]["url"]

#                     api_key ="AIzaSyAJPjaf0y_8RtvPm-xJ5xsitGDDy-oAfmc"
# # GET https://customsearch.googleapis.com/customsearch/v1?imgSize=SMALL&q=glasswindow&safe=medium&searchType=image&key=[YOUR_API_KEY] HTTP/1.1
#                     url = f"https://www.googleapis.com/customsearch/v1?imgSize=SMALL&q={search_term}&safe=medium&searchType=image&key={api_key}"
#                     response = requests.get(url)
#                     image_data = response.json()
#                     img_url = image_data["items"][0]["link"]
                    st.image(img_url)
                        #st.image(gif_url)

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
