import sys
import cv2
from database_manager import DatabaseManager
import datetime
import configparser
import logging
import os

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QLineEdit, QHBoxLayout, QDialog, QTableWidget, QTableWidgetItem, QFileDialog, QRadioButton, QButtonGroup
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QIntValidator

from movement_detector import MovementDetector, SquatDetector

# Set up logging
log_file = "application.log"
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    update_counter_signal = pyqtSignal(int, str)
    update_feedback_signal = pyqtSignal(str)
    workout_completed_signal = pyqtSignal(str, int) # exercise_type, completed_reps

    def __init__(self, exercise_type, target_reps, db_name, video_source_type, video_source_path):
        super().__init__()
        self._run_flag = True
        self.exercise_type = exercise_type
        self.target_reps = target_reps
        self.db_name = db_name # Pass db_name instead of db_manager
        self.video_source_type = video_source_type
        self.video_source_path = video_source_path
        self.start_time = None

        # Create DatabaseManager instance within the thread
        self.db_manager = DatabaseManager(self.db_name)

        if self.exercise_type == "Pushup":
            self.detector = MovementDetector()
        elif self.exercise_type == "Squat":
            self.detector = SquatDetector()
        else:
            self.detector = MovementDetector() # Default

    def run(self):
        if self.video_source_type == "webcam":
            cap = cv2.VideoCapture(0) # Webcam
        else:
            cap = cv2.VideoCapture(self.video_source_path) # Video file

        if not cap.isOpened():
            logging.error("Error: Could not open video source.")
            self._run_flag = False
            return

        self.start_time = datetime.datetime.now()

        while self._run_flag:
            ret, frame = cap.read()
            if ret:
                image, counter, angle, feedback = self.detector.process_frame(frame)

                # Convert image to PyQt format
                h, w, ch = image.shape
                bytes_per_line = ch * w
                convert_to_Qt_format = QImage(image.data, w, h, bytes_per_line, QImage.Format_BGR888)
                p = convert_to_Qt_format.scaled(640, 480, Qt.KeepAspectRatio)
                self.change_pixmap_signal.emit(p)
                self.update_counter_signal.emit(counter, self.exercise_type)
                self.update_feedback_signal.emit(feedback)

                if self.target_reps > 0 and counter >= self.target_reps:
                    self.update_feedback_signal.emit(f"Congratulations! Target {self.target_reps} reached!")
                    self.stop()

        cap.release()
        self._save_workout_data()
        self.workout_completed_signal.emit(self.exercise_type, self.detector.counter)

    def stop(self):
        self._run_flag = False
        self.wait()

    def _save_workout_data(self):
        if self.start_time:
            end_time = datetime.datetime.now()
            duration = (end_time - self.start_time).total_seconds()
            try:
                self.db_manager.save_workout(self.exercise_type, self.detector.counter, int(duration))
                logging.info(f"Workout saved: {self.exercise_type}, {self.detector.counter} reps, {int(duration)} seconds")
            except Exception as e:
                logging.error(f"Error saving workout data: {e}")

class PushupCounterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Movement Coach")
        self.setGeometry(100, 100, 800, 600)
        self.thread = None
        self.config = configparser.ConfigParser()
        self.settings_file = "settings.ini"
        self.load_app_settings()
        self.db_name = "workout_history.db" # Define db_name here
        self.db_manager = DatabaseManager(self.db_name) # Initialize db_manager here
        self.initUI()

    def load_app_settings(self):
        self.config.read(self.settings_file)
        if not self.config.has_section("VideoSource"):
            self.config.add_section("VideoSource")
            self.config["VideoSource"]["type"] = "webcam"
            self.config["VideoSource"]["path"] = ""
            self.save_app_settings()

    def save_app_settings(self):
        with open(self.settings_file, "w") as configfile:
            self.config.write(configfile)

    def initUI(self):
        main_layout = QVBoxLayout()

        # Top controls layout
        control_layout = QHBoxLayout()

        # Exercise Selection
        exercise_group_layout = QVBoxLayout()
        self.exercise_label = QLabel("Select Exercise:")
        exercise_group_layout.addWidget(self.exercise_label)
        self.exercise_combo = QComboBox()
        self.exercise_combo.addItem("Pushup")
        self.exercise_combo.addItem("Squat")
        exercise_group_layout.addWidget(self.exercise_combo)
        control_layout.addLayout(exercise_group_layout)

        # Target Reps
        target_reps_group_layout = QVBoxLayout()
        self.target_reps_label = QLabel("Target Reps (0 for no target):")
        target_reps_group_layout.addWidget(self.target_reps_label)
        self.target_reps_input = QLineEdit()
        self.target_reps_input.setPlaceholderText("e.g., 10")
        self.target_reps_input.setValidator(QIntValidator(0, 9999, self))
        target_reps_group_layout.addWidget(self.target_reps_input)
        control_layout.addLayout(target_reps_group_layout)

        # Start/Stop Button
        self.start_button = QPushButton("Start Workout")
        self.start_button.clicked.connect(self.start_workout)
        control_layout.addWidget(self.start_button)

        # History Button
        self.history_button = QPushButton("View History")
        self.history_button.clicked.connect(self.show_history)
        control_layout.addWidget(self.history_button)

        # Achievements Button
        self.achievements_button = QPushButton("View Achievements")
        self.achievements_button.clicked.connect(self.show_achievements)
        control_layout.addWidget(self.achievements_button)

        # Settings Button
        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.show_settings)
        control_layout.addWidget(self.settings_button)

        main_layout.addLayout(control_layout)

        # Video Feed
        self.image_label = QLabel(self)
        self.image_label.resize(640, 480)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: black;")
        main_layout.addWidget(self.image_label)

        # Real-time Feedback
        self.counter_label = QLabel("Reps: 0")
        self.counter_label.setAlignment(Qt.AlignCenter)
        self.counter_label.setStyleSheet("font-size: 48px; font-weight: bold;")
        main_layout.addWidget(self.counter_label)

        self.feedback_label = QLabel("Feedback: ")
        self.feedback_label.setAlignment(Qt.AlignCenter)
        self.feedback_label.setStyleSheet("font-size: 24px; color: red;")
        main_layout.addWidget(self.feedback_label)

        self.setLayout(main_layout)

    def start_workout(self):
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.start_button.setText("Start Workout")
            return

        exercise_type = self.exercise_combo.currentText()
        target_reps_text = self.target_reps_input.text()
        target_reps = int(target_reps_text) if target_reps_text.isdigit() else 0

        video_source_type = self.config["VideoSource"]["type"]
        video_source_path = self.config["VideoSource"]["path"]

        self.thread = VideoThread(exercise_type, target_reps, self.db_manager.db_name, video_source_type, video_source_path)
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.update_counter_signal.connect(self.update_counter)
        self.thread.update_feedback_signal.connect(self.update_feedback)
        self.thread.workout_completed_signal.connect(self.check_achievements)
        self.thread.start()
        self.start_button.setText("Stop Workout")

    def update_image(self, qt_image):
        self.image_label.setPixmap(QPixmap.fromImage(qt_image))

    def update_counter(self, count, exercise_name):
        self.counter_label.setText(f'{exercise_name}: {count}')

    def update_feedback(self, feedback_text):
        self.feedback_label.setText(f"Feedback: {feedback_text}")

    def check_achievements(self, exercise_type, completed_reps):
        if exercise_type == "Pushup" and completed_reps >= 100:
            try:
                self.db_manager.save_achievement("First 100 Pushups!")
                logging.info("Achievement unlocked: First 100 Pushups!")
            except Exception as e:
                logging.error(f"Error saving achievement: {e}")

    def closeEvent(self, event):
        if self.thread and self.thread.isRunning():
            self.thread.stop()
        self.db_manager.close()
        event.accept()

    def show_history(self):
        history_dialog = HistoryDialog(self.db_name)
        history_dialog.exec_()

    def show_achievements(self):
        achievements_dialog = AchievementsDialog(self.db_name)
        achievements_dialog.exec_()

    def show_settings(self):
        settings_dialog = SettingsDialog(self)
        settings_dialog.exec_()

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(250, 250, 400, 300)
        self.parent = parent
        self.config = configparser.ConfigParser()
        self.settings_file = "settings.ini"
        self.load_settings()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Video Source Selection
        video_source_group = QButtonGroup(self)
        self.webcam_radio = QRadioButton("Use Webcam")
        self.video_file_radio = QRadioButton("Use Video File")
        video_source_group.addButton(self.webcam_radio)
        video_source_group.addButton(self.video_file_radio)

        layout.addWidget(self.webcam_radio)
        layout.addWidget(self.video_file_radio)

        self.video_file_path_input = QLineEdit()
        self.video_file_path_input.setPlaceholderText("Path to video file")
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_video_file)

        file_path_layout = QHBoxLayout()
        file_path_layout.addWidget(self.video_file_path_input)
        file_path_layout.addWidget(self.browse_button)
        layout.addLayout(file_path_layout)

        self.webcam_radio.toggled.connect(self.toggle_video_file_input)
        self.video_file_radio.toggled.connect(self.toggle_video_file_input)

        # Apply/Cancel Buttons
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_settings)
        button_layout.addWidget(self.apply_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.update_ui_from_settings()

    def toggle_video_file_input(self):
        enable = self.video_file_radio.isChecked()
        self.video_file_path_input.setEnabled(enable)
        self.browse_button.setEnabled(enable)

    def browse_video_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "Video Files (*.mp4 *.avi *.mov)")
        if file_path:
            self.video_file_path_input.setText(file_path)

    def load_settings(self):
        self.config.read(self.settings_file)
        if not self.config.has_section("VideoSource"):
            self.config.add_section("VideoSource")
            self.config["VideoSource"]["type"] = "webcam"
            self.config["VideoSource"]["path"] = ""
            self.save_settings()

    def save_settings(self):
        with open(self.settings_file, "w") as configfile:
            self.config.write(configfile)

    def update_ui_from_settings(self):
        source_type = self.config["VideoSource"]["type"]
        if source_type == "webcam":
            self.webcam_radio.setChecked(True)
        else:
            self.video_file_radio.setChecked(True)
            self.video_file_path_input.setText(self.config["VideoSource"]["path"])
        self.toggle_video_file_input()

    def apply_settings(self):
        if self.webcam_radio.isChecked():
            self.config["VideoSource"]["type"] = "webcam"
            self.config["VideoSource"]["path"] = ""
        else:
            self.config["VideoSource"]["type"] = "file"
            self.config["VideoSource"]["path"] = self.video_file_path_input.text()
        self.save_settings()
        self.accept()

class HistoryDialog(QDialog):
    def __init__(self, db_name):
        super().__init__()
        self.setWindowTitle("Workout History")
        self.setGeometry(200, 200, 700, 500)
        self.db_name = db_name
        self.db_manager = DatabaseManager(self.db_name)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Date", "Exercise Type", "Reps", "Duration (s)"])
        layout.addWidget(self.history_table)

        self.load_history()

        self.setLayout(layout)

    def load_history(self):
        try:
            workouts = self.db_manager.get_all_workouts()
            self.history_table.setRowCount(len(workouts))

            for row_idx, workout in enumerate(workouts):
                self.history_table.setItem(row_idx, 0, QTableWidgetItem(workout[1])) # Date
                self.history_table.setItem(row_idx, 1, QTableWidgetItem(workout[2])) # Exercise Type
                self.history_table.setItem(row_idx, 2, QTableWidgetItem(str(workout[3]))) # Completed Reps
                self.history_table.setItem(row_idx, 3, QTableWidgetItem(str(workout[4]) if workout[4] is not None else "N/A")) # Duration
        except Exception as e:
            logging.error(f"Error loading workout history: {e}")

        self.history_table.resizeColumnsToContents()

class AchievementsDialog(QDialog):
    def __init__(self, db_name):
        super().__init__()
        self.setWindowTitle("Achievements")
        self.setGeometry(250, 250, 600, 400)
        self.db_name = db_name
        self.db_manager = DatabaseManager(self.db_name)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.achievements_list = QTableWidget()
        self.achievements_list.setColumnCount(2)
        self.achievements_list.setHorizontalHeaderLabels(["Date Unlocked", "Achievement"])        
        layout.addWidget(self.achievements_list)

        self.load_achievements()

        self.setLayout(layout)

    def load_achievements(self):
        try:
            achievements = self.db_manager.get_all_achievements()
            self.achievements_list.setRowCount(len(achievements))

            for row_idx, achievement in enumerate(achievements):
                self.achievements_list.setItem(row_idx, 0, QTableWidgetItem(achievement[1])) # Date
                self.achievements_list.setItem(row_idx, 1, QTableWidgetItem(achievement[2])) # Name
        except Exception as e:
            logging.error(f"Error loading achievements: {e}")

        self.achievements_list.resizeColumnsToContents()

if __name__ == "__main__":
    # Redirect stdout and stderr to log file
    sys.stdout = open(log_file, 'a')
    sys.stderr = open(log_file, 'a')

    app = QApplication(sys.argv)
    ex = PushupCounterApp()
    ex.show()
    sys.exit(app.exec_())