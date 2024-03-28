import time
import streamlit as st
import requests
#import json
#import cv2
from video_utils import process_video_to_landmarks_json

#import base64
#from streamlit_webrtc import webrtc_streamer, VideoHTMLAttributes

st.set_page_config(page_title="SignLens Demo",
                   page_icon="resources/signlens-favicon-black.png", layout="wide",
                   initial_sidebar_state="collapsed",
                   menu_items={
            'Report a bug': "https://github.com/benoitfrisque/signlens",
            'About': "# This is our final project for Le Wagon Data Science Bootcamp!"

            })

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

NUM_CLASSES = 250

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
    color: #A980D6;
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
if 'new_video' not in st.session_state:
    st.session_state.new_video = False

# Function to update the value in session state
def clicked(button):
    '''Update the value in session state when a button is clicked.'''
    st.session_state.clicked[button] = True

# Sidebar content
# logo = "https://img.freepik.com/free-photo/sign-language-collage-design_23-2150528183.jpg?t=st=1711466807~exp=1711470407~hmac=c1c1a9a378d0a17254e6cf298fb262c2883e305f2ee08999e0771f76be98eeb4&w=900"
#logo = "https://www.freepik.com/free-vector/technology-circle-ai-abstract-vector-computer-vision-design_18236528.htm#query=cyborg%20eye&position=6&from_view=keyword&track=ais&uuid=6aae1df3-0c6e-49d5-a59f-300d5c4bd73d"
logo = "resources/signlens-high-resolution-logo-transparent_green.png"
#st.sidebar.image(logo,use_column_width=True)
st.sidebar.title("About SignLens")
st.sidebar.caption("An app for translating sign language, but also aid in learning it. Upload a video of sign language gestures and click the button to translate the signs to text!")

# Main content
#st.title("SignLens Demo")
st.image(logo,width=300)
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
        st.session_state.b2_disabled = True
        st.session_state.new_video = True

    if video:
        st.session_state.b2_disabled = False
        holder.video(video, start_time=0)
        title1.write(":green[Video uploaded successfully!] :tada:")
        # webrtc_streamer(
        #     key="mute_sample",
        #     video_html_attrs=VideoHTMLAttributes(
        #         autoPlay=True, controls=True, style={"width": "100%"}, muted=muted
        #     ),
        # )

with col2:
    with st.expander("Advanced settings", expanded=False):
        min_detection_confidence = st.slider('Minimum detection confidence:', 0.1, 1.0, 0.5, 0.1)
        min_tracking_confidence = st.slider('Minimum tracking confidence:', 0.1, 1.0, 0.5, 0.1)
    front_on = st.toggle('Front camera (mirrored)', False, key="front_on")
    pixabay = st.checkbox("Show pixabay image of the sign", key="pixabay", value=True)
    #if front_on:
    #    st.write('(not mirrored)')
    st.subheader("Sign translation")
    #expander = st.expander("Optional controls")
    #expander.radio("Options", ["Translate", "Learn", "Live"])
    #if st.button("Push to translate"):
    # Add a button to start the prediction
    # Conditional based on value in session state, not the output
    button_trans = st.button("Start Translation", on_click=clicked, args=[2],
              type="primary", disabled=st.session_state.b2_disabled)
    if video: #st.session_state.clicked[1]:
        if st.session_state.clicked[2]:
            st.session_state.new_video = False
            st.session_state.clicked[2] = False  # Reset the clicked state of the second button
            state = "running"

            # Create a status container
            status_text = st.empty()

            try:
                start_time = time.time()

                with st.spinner("⏱️ Extracting landmarks... 🐢"):
                    # Display the status
                    #status_text.status("Extracting landmarks")

                    # Call the process_video_to_landmarks_json function
                    json_landmarks = process_video_to_landmarks_json(video, rear_camera=not front_on,
                                        min_detection_confidence=min_detection_confidence,
                                        min_tracking_confidence=min_tracking_confidence)
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
                    status_text.text(f"Video processing complete! 🎉  \n   (Elapsed time: {elapsed_time:.2f} seconds)")
                    result = response.json()
                    #result
                    sign = result['sign']
                    proba = result['probability']
                    proba = round(100*(proba),2)
                    state = "complete"
                    time.sleep(1)


                    # probc = ":%s[%s]" % (probability_color, f"{100*(proba):.2f}%")
                    # #st.metric("probability",f"{100*(proba):.2f}%", probability_color)
                    st.title(sign)
                    #st.write(:green["Translation guess"])
                    #probability_color
                    #"probability:"
                    #st.metric(value=proba,label="probability")
                    #st.text_area("Translation guess", sign, height=100)
                    probability_color = "green" if proba > 70 else "red" if proba < 50 else "yellow"
                    if probability_color == "green":
                        st.write("is our best guess with probability", f":green[{proba}%]")
                    elif probability_color == "yellow":
                        st.write("is our best guess with probability", f":yellow[{proba}%]")
                    else:
                        st.write("is our best guess with probability", f":red[{proba}%]")

                    search_term = result['sign']
                    # Pixabay API
                    if pixabay:
                        api_key = str(st.secrets.api_key)
                        url = "https://pixabay.com/api/?key=%s&q=%s&image_type=photo&pretty=true" % (str(api_key),search_term)
                        response = requests.get(url, timeout=60)
                        image_data = response.json()
                        #image_data
                        img_url = image_data["hits"][0]["webformatURL"]
                        st.image(img_url)

                else:
                    status_text.text(f"API Error: {response.status_code}")
                    st.error(f"API Error: {response.status_code}")
                    state = "error"

            except Exception as e:
                status_text.text(f"API Error: {e}")
                st.error(f"API Error: {e}")
                state = "error"
