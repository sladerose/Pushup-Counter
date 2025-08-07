import cv2
import mediapipe as mp
import numpy as np
import argparse
from movement_detector import MovementDetector, SquatDetector

# --- Configuration ---
# Set to True to use the webcam, False to use a video file.
USE_WEBCAM = True
# If USE_WEBCAM is False, specify the absolute path to your video file.
VIDEO_PATH = r"C:\Users\slade\Documents\pushup_counter\pushup.mp4"

# --- Main Application Logic ---
def main():
    parser = argparse.ArgumentParser(description="Movement counter for various exercises.")
    parser.add_argument("--exercise", type=str, default="pushup",
                        help="Specify the exercise to track: 'pushup' or 'squat'.")
    parser.add_argument("--target_reps", type=int, default=0,
                        help="Set a target number of repetitions for the exercise. 0 for no target.")
    args = parser.parse_args()

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

    # --- Initialize MovementDetector based on exercise ---
    if args.exercise == "pushup":
        detector = MovementDetector()
        exercise_name = "Push-ups"
    elif args.exercise == "squat":
        detector = SquatDetector()
        exercise_name = "Squats"
    else:
        print(f"Error: Unknown exercise '{args.exercise}'. Please choose 'pushup' or 'squat'.")
        return

    # --- Main Loop for Video Processing ---
    while True:
        # Read a frame from the video source.
        ret, frame = cap.read()
        # If frame was not read successfully, it means the video has ended or an error occurred.
        if not ret:
            print("End of video stream or error reading frame. Exiting.")
            break

        # Process frame with the detector
        image, counter, angle, feedback = detector.process_frame(frame)

        # --- Visualize Angle (for debugging/feedback) ---
        if angle is not None:
            cv2.putText(image, str(int(angle)),
                        (50, 50), # Adjust position as needed
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA
                        )
            print(f"Angle: {angle:.2f}")

        # --- Display Counter and Feedback on Screen ---
        if args.target_reps > 0:
            display_text = f'{exercise_name}: {counter}/{args.target_reps}'
        else:
            display_text = f'{exercise_name}: {counter}'
        cv2.putText(image, display_text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        if feedback:
            cv2.putText(image, feedback, (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

        # --- Game Loop Logic ---
        if args.target_reps > 0 and counter >= args.target_reps:
            print(f"Congratulations! You reached your target of {args.target_reps} {exercise_name}!")
            break

        # --- Display the Output Frame ---
        # Show the processed image in a window.
        cv2.imshow('Webcam Feed with Movement Counter' if USE_WEBCAM else 'Video Feed with Movement Counter', image)

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