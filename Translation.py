import base64
import time
import streamlit as st
import requests
#import json
#import cv2
from video_utils import process_video_to_landmarks_json
#from streamlit_webrtc import webrtc_streamer, VideoHTMLAttributes

st.set_page_config(page_title="SignLens Demo",
                   page_icon="resources/signlens-favicon-white.png", layout="wide",
                   initial_sidebar_state="expanded",
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

with open("resources/signlens-favicon-white.png", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode()
side_logo = f"data:image/png;base64,{encoded_string}"
background_image = "resources/background_signlens.png"

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

h1 {
    color: #A980D6;
}
}
</style>
""", unsafe_allow_html=True)

#url = "https://img.freepik.com/free-photo/sign-language-collage-design_23-2150528183.jpg?t=st=1711466807~exp=1711470407~hmac=c1c1a9a378d0a17254e6cf298fb262c2883e305f2ee08999e0771f76be98eeb4&w=900"
#url = "resources/signlens-high-resolution-logo-black.png"

st.markdown(
        f"""
        <style>
            [data-testid="stSidebarNav"] + div {{
                position:absolute;
                bottom: 0;
                height:50%;
                background-image: url({side_logo});
                background-size: 50% auto;
                background-repeat: no-repeat;
                background-position-x: center;
                background-position-y: bottom;
                border-bottom: 2px solid black;
                background-color: rgba(255, 255, 255, 0.08); /* Add this line for light background */
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.5); /* Add this line for shading */
            }}
            body {{
            background-image: url({background_image});
            background-size: cover;
            }}
            [data-testid="stAppViewContainer"] > .main {{
            background-image: url({background_image});
            background-size: 100vw 100vh;  # This sets the size to cover 100% of the viewport width and height
            background-position: center;
            background-repeat: no-repeat;
            }}

                        .stApp > div:first-child {{
                background-image: url({background_image});
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
            }}
            [data-testid="stAppViewContainer"] {{
            background-color: transparent;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


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
logo = "resources/svg/logo-no-background.svg"
#st.sidebar.image(logo,use_column_width=True)
st.sidebar.title("About SignLens")
st.sidebar.caption("An app for translating sign language, but also aid in learning it. Upload a video of sign language gestures and click the button to translate the signs to text!")

# Main content
#st.title("SignLens Demo")

col1, col2 = st.columns([2, 1])

st.session_state.b2_disabled = True

with col1:
    st.image(logo,width=300)
    st.subheader("Upload a video to translate sign to text")
    holder = st.empty()
    title1 = st.empty()
    # Open video file if uploaded
    #if st.button("Upload a video", on_click=clicked, args=[1], key="upload_video",type="primary"):
    with st.spinner("Uploading video..."):
        #time.sleep(1.5)

        video = st.file_uploader("Select video file", label_visibility="collapsed", key="upload_video", help="Upload a video file",
                                 #disabled=~st.session_state.b2_disabled,
                                 type=["mp4", "mov", "avi", "mkv", "mpg", "mpeg", "asf",], accept_multiple_files=False)
                                                         # "m2v", "ts", "m2ts", "mts", "vob","m4v", "mkv", "wmv", "flv", "webm", "3gp", "ogg", "ogv", "gif",
        st.session_state.b2_disabled = True
        st.session_state.new_video = True

    if video:
        st.session_state.b2_disabled = False
        holder.video(video, start_time=0)
        #st.session_state.url = video
        # Use st.markdown to display the video
        # st.markdown(f'''
        #     <div style="position:relative; padding-top:56.25%;">
        #         <iframe src="{st.session_state.url}?autoplay=1&loop=1" style="position:absolute; top:0; left:0; width:100%; height:100%;" frameborder="no" scrolling="no" allowfullscreen webkitallowfullscreen mozallowfullscreen oallowfullscreen msallowfullscreen>
        #         </iframe>
        #     </div>
        # ''', unsafe_allow_html=True)
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
        frame_interval = st.slider('Frame interval:', 1, 10, 1, 1)
        #frame_limit = st.number_input('Frame limit:', 0, 200, 0, 1)  #slider('Frame limit:', 0, 200, 0, 1)
        pixabay = st.checkbox("Show pixabay image of the sign", key="pixabay", value=True)
    front_on = st.toggle('Front camera / webcam', False, key="front_on")

    st.subheader("Sign translation")
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
                                        frame_interval=frame_interval, #frame_limit=frame_limit,
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
                        try:
                            response.raise_for_status()
                            image_data = response.json()
                        # exception handling
                        except KeyError:
                            st.error("Error: The API did not return valid image data.")
                        except requests.Timeout:
                            st.error("Error: Request to the API timed out. Please try again later.")
                        else:
                            # Check if the "hits" list is empty
                            if "hits" in image_data and len(image_data["hits"]) > 0:
                                img_url = image_data["hits"][0]["webformatURL"]
                                st.image(img_url)
                            else:
                                st.error("Error: No images found for the given search term.")

                else:
                    status_text.text(f"API Error: {response.status_code}")
                    st.error(f"API Error: {response.status_code}")
                    state = "error"

            except Exception as e:
                status_text.text(f"API Error: {e}")
                st.error(f"API Error: {e}")
                state = "error"
