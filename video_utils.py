import math
import cv2
import mediapipe as mp
import numpy as np
import tempfile

from google.protobuf.json_format import MessageToDict
from mediapipe.framework.formats import landmark_pb2
from mediapipe import solutions


N_LANDMARKS_HAND = 21
N_LANDMARKS_POSE = 33

mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands

# Constants for drawing landmarks on the image
MARGIN = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54)  # vibrant green


def serialize_landmarks(landmark_list):
    """
    Serialize a list of landmarks into a dictionary format.

    Args:
        landmark_list (list): A list of landmarks.

    Returns:
        list: A list of dictionaries, where each dictionary represents a landmark and contains the following keys:
            - 'landmark_index': The index of the landmark in the list.
            - 'x': The x-coordinate of the landmark. If the value is NaN, it is set to None.
            - 'y': The y-coordinate of the landmark. If the value is NaN, it is set to None.
            - 'z': The z-coordinate of the landmark. If the value is NaN, it is set to None.
    """
    landmarks = []
    for idx, landmark in enumerate(landmark_list.landmark):
        landmarks.append({
            'landmark_index': idx,
            'x': None if math.isnan(landmark.x) else landmark.x,
            'y': None if math.isnan(landmark.y) else landmark.y,
            'z': None if math.isnan(landmark.z) else landmark.z
        })
    return landmarks


def process_video_to_landmarks_json(video_file, frame_interval=1, frame_limit=None, rear_camera=True,
                                    min_detection_confidence=0.5, min_tracking_confidence=0.5):
    """
    Process a video file and extract landmarks from each frame.

    Args:
        video_file (streamlit.uploaded_file_manager.UploadedFileManager): The uploaded video file.
        frame_interval (int, optional): The interval between processed frames. Defaults to 1.
        frame_limit (int, optional): The maximum number of frames to process. Defaults to None.
        rear_camera (bool, optional): Whether the video was recorded with a rear camera. Defaults to True.

    Returns:
        list: A list of dictionaries containing the extracted landmarks for each frame.
    """
    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(video_file.getbuffer())
        video_path = tmp.name

    cap = cv2.VideoCapture(video_path, cv2.CAP_ANY) # for temp file solution
    #cap = cv2.VideoCapture(video_file, cv2.CAP_ANY)

    json_data = []
    frame_number = 0
    processed_frames = 0

    # Get the fps of the original video
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Get the frame width and height
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    with mp_pose.Pose(static_image_mode=False,
                min_detection_confidence=min_detection_confidence,
                min_tracking_confidence=min_tracking_confidence) as pose, \
            mp_hands.Hands(static_image_mode=False, max_num_hands=2,
                min_detection_confidence=min_detection_confidence,
                min_tracking_confidence=min_tracking_confidence) as hands:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            # Skip frames based on frame_interval
            if frame_number % frame_interval != 0:
                frame_number += 1
                continue

            # Convert the BGR image to RGB
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the image and extract landmarks
            results_pose = pose.process(image_rgb)
            results_hands = hands.process(image_rgb)

            # Extract landmarks for pose, left hand, and right hand
            landmarks_pose = results_pose.pose_landmarks

            # Check if there are any pose landmarks detected
            if landmarks_pose is None:
                landmarks_pose = create_empty_landmark_list(N_LANDMARKS_POSE)

            # Initialize empty hand landmarks, then overwrite if it finds it
            landmarks_left_hand = create_empty_landmark_list(N_LANDMARKS_HAND)
            landmarks_right_hand = create_empty_landmark_list(N_LANDMARKS_HAND)

            # Check if there are any hand landmarks detected
            if results_hands.multi_hand_landmarks:
                # Get handedness of each hand
                for idx, handedness in enumerate(results_hands.multi_handedness):
                    hand_side = get_hand_side(handedness, rear_camera)

                    if hand_side == 'left':
                        landmarks_left_hand = results_hands.multi_hand_landmarks[idx]
                    elif hand_side == 'right':
                        landmarks_right_hand = results_hands.multi_hand_landmarks[idx]

            serialized_pose = serialize_landmarks(landmarks_pose)
            serialized_left_hand = serialize_landmarks(landmarks_left_hand)
            serialized_right_hand = serialize_landmarks(landmarks_right_hand)

            # Write serialized landmarks to JSON
            json_data.append({
                'frame_number': frame_number,
                'pose': serialized_pose,
                'left_hand': serialized_left_hand,
                'right_hand': serialized_right_hand
            })

            frame_number += 1
            processed_frames += 1

            # Stop processing if frame_limit is reached
            if frame_limit is not None and processed_frames >= frame_limit:
                break

    cap.release()  # Close video file

    return json_data


def create_empty_landmark_list(n_landmarks):
    """
    Create an empty NormalizedLandmarkList.

    Args:
        n_landmarks (int): The number of landmarks to create.

    Returns:
        landmark_pb2.NormalizedLandmarkList: An empty NormalizedLandmarkList.

    """
    # Initialize an empty NormalizedLandmarkList for hand
    empty_landmark_list = landmark_pb2.NormalizedLandmarkList()

    # Add empty landmarks to the list
    for _ in range(n_landmarks):
        landmark = empty_landmark_list.landmark.add()
        landmark.x = np.nan  # We use nan and not None because it doesn't work with None
        landmark.y = np.nan
        landmark.z = np.nan

    return empty_landmark_list


def get_hand_side(handedness, rear_camera):
    """
    Determines the side of the hand based on the handedness classification.

    Args:
        handedness (protobuf message): The handedness classification message.
        rear_camera (bool): Flag indicating whether the input image is taken with a rear camera.

    Returns:
        str: The side of the hand ('left' or 'right').

    Notes:
        By default, mediapipe assumes the input image is mirrored, i.e., taken with a front-facing/selfie camera with images flipped horizontally.
        If you want to process images taken with a webcam/selfie, you can set rear_camera = False.
    """
    handedness_dict = MessageToDict(handedness)
    hand_side = handedness_dict['classification'][0]['label'].lower()

    if rear_camera:
        if hand_side == 'left':
            hand_side = 'right'
        elif hand_side == 'right':
            hand_side = 'left'

    return hand_side


def draw_landmarks_on_image(rgb_image, results_pose, results_hands, rear_camera):
    """
    Draws landmarks on the given RGB image based on the detected hand landmarks.

    Args:
            rgb_image (numpy.ndarray): The RGB image on which to draw the landmarks.
            results_pose (mediapipe.python.solution_base.SolutionOutputs): The output of the pose detection model.
            results_hands (mediapipe.python.solution_base.SolutionOutputs): The output of the hand detection model.
            rear_camera (bool): Flag indicating whether the camera is rear-facing or not.

    Returns:
            numpy.ndarray: The annotated image with landmarks drawn.

    Note:
            It is normal to see the left hand on the right side and the right hand on the left side if rear_camera=True.
    """

    annotated_image = np.copy(rgb_image)

    if results_hands.multi_hand_landmarks is None and results_pose is None:
        return annotated_image

    if results_hands.multi_hand_landmarks is not None:
        # Loop through the detected hands to visualize.
        for idx in range(len(results_hands.multi_hand_landmarks)):
            hand_landmarks = results_hands.multi_hand_landmarks[idx].landmark
            handedness = results_hands.multi_handedness[idx]
            hand_side = get_hand_side(handedness, rear_camera)

            hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            hand_landmarks_proto.landmark.extend([
                landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
            ])

            # Draw the hand landmarks.
            solutions.drawing_utils.draw_landmarks(
                annotated_image,
                hand_landmarks_proto,
                solutions.hands.HAND_CONNECTIONS,
                solutions.drawing_styles.get_default_hand_landmarks_style(),
                solutions.drawing_styles.get_default_hand_connections_style())

            # Get the top left corner of the detected hand's bounding box.
            height, width, _ = annotated_image.shape
            x_coordinates = [landmark.x for landmark in hand_landmarks]
            y_coordinates = [landmark.y for landmark in hand_landmarks]
            text_x = int(min(x_coordinates) * width)
            text_y = int(min(y_coordinates) * height) - MARGIN

            # Draw handedness (left or right hand) on the image.
            cv2.putText(annotated_image, f"{hand_side}",
                        (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX,
                        FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA)

        if results_pose is not None:
            pose_landmarks = results_pose.pose_landmarks.landmark

            pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            pose_landmarks_proto.landmark.extend([
                landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
            ])

          # Draw the pose landmarks.
            solutions.drawing_utils.draw_landmarks(
                annotated_image,
                pose_landmarks_proto,
                solutions.pose.POSE_CONNECTIONS,
                solutions.drawing_styles.get_default_pose_landmarks_style())

    return annotated_image

# # Streamlit test app
# def app():
#     st.title("Video to Landmarks JSON")

#     video_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mkv"])

#     if video_file:
#         landmarks = process_video_to_landmarks_json(video_file)
#         st.json(landmarks)

# if __name__ == "__main__":
#     app()
