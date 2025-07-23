import cv2
import mediapipe as mp
import numpy as np

# --- Configuration ---
# Set to True to use the webcam, False to use a video file.
USE_WEBCAM = True
# If USE_WEBCAM is False, specify the absolute path to your video file.
VIDEO_PATH = r"C:\Users\slade\Documents\pushup_counter\pushup.mp4"

# --- MediaPipe Setup ---
# Initialize MediaPipe Drawing utilities for visualizing landmarks.
mp_drawing = mp.solutions.drawing_utils
# Initialize MediaPipe Pose model for pose estimation.
mp_pose = mp.solutions.pose

# --- Helper Function: Calculate Angle ---
def calculate_angle(a, b, c):
    """
    Calculates the angle between three points (landmarks).
    This is used to determine the angle of joints like the elbow.

    Args:
        a (list): Coordinates of the first point (e.g., shoulder).
        b (list): Coordinates of the mid point (e.g., elbow).
        c (list): Coordinates of the end point (e.g., wrist).

    Returns:
        float: The calculated angle in degrees.
    """
    a = np.array(a)  # First point (e.g., shoulder)
    b = np.array(b)  # Mid point (e.g., elbow)
    c = np.array(c)  # End point (e.g., wrist)

    # Calculate radians using arctan2, then convert to degrees.
    # The order of points in arctan2 determines the angle direction.
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    # Adjust angle to be within 0-180 degrees for easier interpretation.
    if angle > 180.0:
        angle = 360 - angle

    return angle

# --- Main Application Logic ---
def main():
    # --- Video Capture Initialization ---
    if USE_WEBCAM:
        print("Attempting to open webcam...")
        cap = cv2.VideoCapture(0)  # 0 for default webcam
    else:
        print(f"Attempting to open video file: {VIDEO_PATH}")
        cap = cv2.VideoCapture(VIDEO_PATH) # Use the specified video file

    # Check if the video source was opened successfully.
    if not cap.isOpened():
        print("Error: Could not open video source. Please check:")
        if USE_WEBCAM:
            print("- If a webcam is connected and not in use by another application.")
            print("- If you have granted camera permissions to the application.")
        else:
            print(f"- If the video file path is correct: {VIDEO_PATH}")
            print("- If the video file exists and is not corrupted.")
        return

    print("Video source opened successfully. Press 'q' to quit.")

    # --- Push-up Counter Variables ---
    counter = 0  # Stores the total number of push-ups completed.
    stage = None # Tracks the current stage of the push-up: 'up' or 'down'.

    # --- MediaPipe Pose Instance Setup ---
    # Initialize the MediaPipe Pose model.
    # min_detection_confidence: Minimum confidence value ([0.0, 1.0]) for pose detection to be considered successful.
    # min_tracking_confidence: Minimum confidence value ([0.0, 1.0]) for the pose landmarks to be considered tracked successfully.
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        # --- Main Loop for Video Processing ---
        while True:
            # Read a frame from the video source.
            ret, frame = cap.read()
            # If frame was not read successfully, it means the video has ended or an error occurred.
            if not ret:
                print("End of video stream or error reading frame. Exiting.")
                break

            # --- Image Processing for MediaPipe ---
            # Recolor the image from BGR (OpenCV default) to RGB (MediaPipe required).
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Set image as not writeable to improve performance.
            image.flags.writeable = False

            # Process the image with MediaPipe Pose to detect landmarks.
            results = pose.process(image)

            # Recolor the image back to BGR for OpenCV rendering.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # --- Landmark Extraction and Angle Calculation ---
            try:
                # Extract landmarks from the detected pose.
                landmarks = results.pose_landmarks.landmark

                # Get coordinates for the left arm landmarks (shoulder, elbow, wrist).
                shoulder_l = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow_l = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist_l = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                # Get coordinates for the right arm landmarks (shoulder, elbow, wrist).
                shoulder_r = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                elbow_r = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                wrist_r = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

                # Calculate the angle for both left and right elbows.
                angle_l = calculate_angle(shoulder_l, elbow_l, wrist_l)
                angle_r = calculate_angle(shoulder_r, elbow_r, wrist_r)

                # For simplicity, we'll use the left elbow angle for counting.
                # You could average both or choose based on which is more visible.
                elbow_angle = angle_l

                # --- Visualize Elbow Angle (for debugging/feedback) ---
                # Display the elbow angle on the image.
                cv2.putText(image, str(int(elbow_angle)),
                            tuple(np.multiply(elbow_l, [image.shape[1], image.shape[0]]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                            )
                # Print the elbow angle to the console/log.
                print(f"Elbow Angle: {elbow_angle:.2f}")

                # --- Push-up Counting Logic ---
                # Define thresholds for "down" and "up" positions.
                # These values might need adjustment based on individual form and camera angle.
                DOWN_THRESHOLD = 90  # Angle when arm is bent (down position)
                UP_THRESHOLD = 140   # Angle when arm is relatively straight (up position)

                # Logic to detect push-up stages and count repetitions.
                if elbow_angle < DOWN_THRESHOLD and stage == 'up':
                    # Transition from 'up' to 'down' stage.
                    if stage != "down":
                        print("Stage: DOWN")
                    stage = "down"
                elif elbow_angle > UP_THRESHOLD and stage == 'down':
                    # Transition from 'down' to 'up' stage, indicating a completed push-up.
                    if stage != "up":
                        print("Stage: UP")
                    stage = "up"
                    counter += 1  # Increment the push-up counter.
                    print(f"Push-up Count: {counter}") # Print the new count.
                elif elbow_angle > UP_THRESHOLD and stage != 'up':
                    # Handles the initial 'up' state or if the user is just holding an 'up' position.
                    # Ensures 'stage' is correctly set to 'up' without incrementing the counter.
                    if stage != "up":
                        print("Stage: UP")
                    stage = "up"

            except Exception as e:
                # Handle cases where landmarks are not fully detected (e.g., person is out of frame).
                print(f"Could not detect all landmarks or an error occurred: {e}. Adjust position or lighting.")
                pass # Continue to the next frame even if detection fails for a frame.

            # --- Render MediaPipe Detections ---
            # Draw the detected pose landmarks and connections on the image.
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                    # Styling for landmarks (circles).
                                    mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2),
                                    # Styling for connections (lines).
                                    mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
                                    )

            # --- Display Push-up Counter on Screen ---
            # Overlay the current push-up count on the video feed.
            cv2.putText(image, f'Push-ups: {counter}', (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

            # --- Display the Output Frame ---
            # Show the processed image in a window.
            cv2.imshow('Webcam Feed with Push-up Counter' if USE_WEBCAM else 'Video Feed with Push-up Counter', image)

            # --- Exit Condition ---
            # Wait for 1 millisecond for a key press. If 'q' is pressed, break the loop.
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("'q' pressed. Exiting video feed.")
                break

    # --- Cleanup ---
    # Release the video capture object.
    cap.release()
    # Destroy all OpenCV windows.
    cv2.destroyAllWindows()
    print("Video feed closed.")

# --- Entry Point ---
# Ensures that main() is called only when the script is executed directly.
if __name__ == "__main__":
    main()