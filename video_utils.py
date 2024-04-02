import numpy as np
import math
import tempfile

import cv2
import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

N_LANDMARKS_HAND = 21
N_LANDMARKS_POSE = 33


def process_video_to_landmarks_json(video_file, frame_interval=1, frame_limit=None, rear_camera=True,  min_detection_confidence=0.5, min_tracking_confidence=0.5 ):

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(video_file.getbuffer())
        video_path = tmp.name


    cap = cv2.VideoCapture(video_path, cv2.CAP_ANY)
    if not cap.isOpened():
        print(f"Error opening video file '{video_path}'")

    json_data = []
    frame_number = 0
    processed_frames = 0

    base_options_hands = BaseOptions(model_asset_path='mediapipe/hand_landmarker.task')
    options_hands = HandLandmarkerOptions(base_options=base_options_hands,
                                          min_hand_detection_confidence=min_detection_confidence,
                                          min_tracking_confidence=min_tracking_confidence,
                                          min_hand_presence_confidence=0.3,
                                          num_hands=2,
                                          running_mode=VisionRunningMode.VIDEO)

    base_options_pose = python.BaseOptions(model_asset_path='mediapipe/pose_landmarker.task')
    options_pose = vision.PoseLandmarkerOptions(base_options=base_options_pose,
                                                output_segmentation_masks=False,
                                                running_mode=VisionRunningMode.VIDEO)

    try:
        # Initialize an empty NormalizedLandmarkList for hand and pose
        empty_hand_landmarks_list = create_empty_landmarks_list(N_LANDMARKS_HAND)
        empty_pose_landmarks_list = create_empty_landmarks_list(N_LANDMARKS_POSE)

        with vision.HandLandmarker.create_from_options(options_hands) as hands_landmarker, \
            vision.PoseLandmarker.create_from_options(options_pose) as pose_landmarker:

             while cap.isOpened():
                success, frame = cap.read()
                if not success:
                    break

                # Skip frames based on frame_interval
                if frame_number % frame_interval != 0:
                    frame_number += 1
                    continue

                frame_timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))

                # Convert the BGR image to RGB
                image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)

                # hands_result = hands_landmarker.detect(mp_image)
                hands_result = hands_landmarker.detect_for_video(mp_image, frame_timestamp_ms)
                pose_result = pose_landmarker.detect_for_video(mp_image, frame_timestamp_ms)

                # Check if there are any pose landmarks detected
                if pose_result is None or len(pose_result.pose_landmarks) == 0:
                    pose_landmarks = empty_pose_landmarks_list
                else:
                    pose_landmarks = pose_result.pose_landmarks[0]

                # Initialize empty hand landmarkks, then overwrite if it finds it
                landmarks_left_hand = empty_hand_landmarks_list
                landmarks_right_hand = empty_hand_landmarks_list

                # Check if there are any hand landmarks detected

                if hands_result.hand_landmarks:
                    hand_landmarks_list = hands_result.hand_landmarks
                    hand_sides_list = get_hand_sides(hands_result)

                    for idx in range(len(hand_landmarks_list)):
                        hand_side = hand_sides_list[idx]

                        if hand_side == 'left':
                            landmarks_left_hand = hands_result.hand_landmarks[idx]
                        elif hand_side == 'right':
                            landmarks_right_hand = hands_result.hand_landmarks[idx]


                serialized_pose = serialize_landmarks(pose_landmarks)
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

    except KeyboardInterrupt:
        print("Process interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cap.release()  # Close video file

        return json_data




def serialize_landmarks(landmarks_list):
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

    if isinstance(landmarks_list, landmark_pb2.NormalizedLandmarkList):
        landmarks_list = landmarks_list.landmark # take the list inside NormalizedLandmarkList

    for idx, landmark in enumerate(landmarks_list):
        landmarks.append({
            'landmark_index': idx,
            'x': None if math.isnan(landmark.x) else landmark.x,
            'y': None if math.isnan(landmark.y) else landmark.y,
            'z': None if math.isnan(landmark.z) else landmark.z
        })
    return landmarks


def get_hand_sides(hands_result):
    # Get handedness of each hand
    hand_landmarks_list = hands_result.hand_landmarks
    handedness_list = hands_result.handedness

    if len(hand_landmarks_list) == 0:
        return []

    elif len(hand_landmarks_list) == 1:
        hand_side = handedness_list[0][0].category_name.lower()
        return [hand_side]

    elif len(hand_landmarks_list) == 2:
#         hand_side0 = handedness_list[0][0].category_name.lower()
#         hand_side1 = handedness_list[1][0].category_name.lower()

#         if hand_side0!= hand_side1:
#             return [hand_side0, hand_side1]

#         else: # 2 same hands detected (not correct as we assume there is only 1 person)
            # import ipdb; ipdb.set_trace()
        x_min0 = min([landmark.x for landmark in hand_landmarks_list[0]])
        x_min1 = min([landmark.x for landmark in hand_landmarks_list[1]])

        if x_min0 < x_min1:
            return ["right", "left"]
        else:
            return ["left", "right"]


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
