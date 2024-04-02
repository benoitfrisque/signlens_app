import math
import cv2
import mediapipe as mp
import numpy as np
import tempfile

from google.protobuf.json_format import MessageToDict
from mediapipe.framework.formats import landmark_pb2

mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands

N_LANDMARKS_HAND = 21
N_LANDMARKS_POSE = 33


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

    json_data = []
    frame_number = 0
    processed_frames = 0

    empty_landmarks_list_hand = create_empty_landmarks_list(N_LANDMARKS_HAND)
    empty_landmarks_list_pose = create_empty_landmarks_list(N_LANDMARKS_POSE)


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

            if not rear_camera: # we mirror videos from front camera
                frame = cv2.flip(frame, 1)

            # Convert the BGR image to RGB
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the image and extract landmarks
            pose_result = pose.process(image_rgb)
            hands_result = hands.process(image_rgb)

            # Extract landmarks for pose, left hand, and right hand
            landmarks_pose = pose_result.pose_landmarks

            # Check if there are any pose landmarks detected
            if landmarks_pose is None:
                landmarks_pose = empty_landmarks_list_pose

            # Initialize empty hand landmarks, then overwrite if it finds it
            landmarks_left_hand = empty_landmarks_list_hand
            landmarks_right_hand = empty_landmarks_list_hand

            # Check if there are any hand landmarks detected
            if hands_result.multi_hand_landmarks:
                hand_landmarks_list = hands_result.multi_hand_landmarks
                hand_sides_list = get_hand_sides(hands_result)

                for idx in range(len(hand_landmarks_list)):
                    hand_side = hand_sides_list[idx]

                    if hand_side == 'left':
                        landmarks_left_hand = hand_landmarks_list[idx]
                    elif hand_side == 'right':
                        landmarks_right_hand = hand_landmarks_list[idx]


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


def create_empty_landmarks_list(n_landmarks):
    """
    Create an empty NormalizedLandmarkList.

    Args:
        n_landmarks (int): The number of landmarks to create.

    Returns:
        landmark_pb2.NormalizedLandmarkList: An empty NormalizedLandmarkList.

    """
    # Initialize an empty NormalizedLandmarkList for hand
    empty_landmarks_list = landmark_pb2.NormalizedLandmarkList()

    # Add empty landmarks to the list
    for _ in range(n_landmarks):
        landmark = empty_landmarks_list.landmark.add()
        landmark.x = np.nan  # We use nan and not None because it doesn't work with None
        landmark.y = np.nan
        landmark.z = np.nan

    return empty_landmarks_list


def get_hand_sides(hands_result):
    # Get handedness of each hand
    hand_landmarks_list = hands_result.multi_hand_landmarks


    if len(hand_landmarks_list) == 0:
        return []

    elif len(hand_landmarks_list) == 1:
        handedness_dict = MessageToDict(hands_result.multi_handedness[0])
        hand_side = handedness_dict['classification'][0]['label'].lower()

        if hand_side == 'left':
            return ['right'] # inverted as this version of Mediaipe assumes mirrored videos
        else:
            return ['left']

    elif len(hand_landmarks_list) == 2:
        x_min0 = min([landmark.x for landmark in hand_landmarks_list[0]])
        x_min1 = min([landmark.x for landmark in hand_landmarks_list[1]])

        if x_min0 < x_min1:
            return ["right", "left"]
        else:
            return ["left", "right"]
