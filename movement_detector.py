import cv2
import mediapipe as mp
import numpy as np
import simpleaudio as sa
import os
import logging

# Set to store paths of audio files for which a warning has already been logged
_warned_audio_files = set()

def play_sound(file_path):
    if os.path.exists(file_path):
        try:
            wave_obj = sa.WaveObject.from_wave_file(file_path)
            play_obj = wave_obj.play()
        except Exception as e:
            logging.error(f"Error playing audio file {file_path}: {e}")
    else:
        if file_path not in _warned_audio_files:
            logging.warning(f"Audio file not found: {file_path}")
            _warned_audio_files.add(file_path)

class MovementDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils
        self.counter = 0
        self.stage = None  # 'down' or 'up'
        self.feedback = ""

    def calculate_angle(self, a, b, c):
        a = np.array(a)  # First
        b = np.array(b)  # Mid
        c = np.array(c)  # End

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)

        if angle > 180.0:
            angle = 360 - angle

        return angle

    def process_frame(self, image):
        # Recolor image to RGB for mediapipe
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False

        # Make detection
        results = self.pose.process(image_rgb)

        # Recolor back to BGR for rendering
        image.flags.writeable = True

        angle = None
        try:
            landmarks = results.pose_landmarks.landmark

            # Get coordinates for pushup (left arm)
            shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]

            # Calculate elbow angle
            angle = self.calculate_angle(shoulder, elbow, wrist)

            # Pushup counter logic
            if angle > 160:
                self.stage = "down"
                self.feedback = "Elbows too straight!"
                play_sound("audio/go_deeper.wav") # Placeholder for specific feedback sound
            elif angle < 30 and self.stage == 'down':
                self.stage = "up"
                self.counter += 1
                self.feedback = "Good form!"
                play_sound("audio/rep_count.wav") # Play sound on successful rep
            else:
                self.feedback = ""

        except:
            self.feedback = "Adjust position"

        # Render detections
        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

        return image, self.counter, angle, self.feedback

    def __del__(self):
        self.pose.close()

class SquatDetector(MovementDetector):
    def __init__(self):
        super().__init__()

    def process_frame(self, image):
        # Recolor image to RGB for mediapipe
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False

        # Make detection
        results = self.pose.process(image_rgb)

        # Recolor back to BGR for rendering
        image.flags.writeable = True

        angle = None
        try:
            landmarks = results.pose_landmarks.landmark

            # Get coordinates for squat (left leg)
            hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            ankle = [landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

            # Calculate knee angle
            angle = self.calculate_angle(hip, knee, ankle)

            # Squat counter logic
            if angle < 90:  # Assuming a squat is when the knee angle is less than 90 degrees
                self.stage = "down"
                self.feedback = "Go deeper!"
                play_sound("audio/go_deeper.wav") # Placeholder for specific feedback sound
            elif angle > 160 and self.stage == 'down': # Assuming standing up is when the knee angle is greater than 160 degrees
                self.stage = "up"
                self.counter += 1
                self.feedback = "Good form!"
                play_sound("audio/rep_count.wav") # Play sound on successful rep
            else:
                self.feedback = ""

        except:
            self.feedback = "Adjust position"

        # Render detections
        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

        return image, self.counter, angle, self.feedback