# AI Movement Coach

This project provides an AI-powered movement coach application that can track exercises like pushups and squats, provide real-time feedback, and keep a history of your workouts.

## Features

- **Multi-Exercise Tracking:** Detects and counts repetitions for both pushups and squats.
- **Real-time Feedback:** Provides immediate visual and audio cues on your form (e.g., "Good form!", "Go deeper!").
- **Interactive GUI:** A modern graphical user interface built with PyQt for easy interaction.
- **Workout Goals:** Set target repetitions for your workouts.
- **Workout History:** Tracks and stores your workout sessions (exercise type, reps, duration) in a local SQLite database.
- **Achievements:** Unlock achievements based on your workout milestones.
- **Configurable Video Source:** Choose between using your webcam or a video file for movement detection.
- **Standalone Executable:** Easily run the application on Windows without needing a Python environment.

## Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package installer)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/slade/Pushups.git
    cd Pushups
    ```

2.  **Create and activate a virtual environment (recommended):
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # On Windows
    # source venv/bin/activate  # On macOS/Linux
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: A `requirements.txt` file will be generated in a later step.)*

### Running the Application

#### From Source (for development)

To run the GUI application:

```bash
.\venv\Scripts\activate
python gui.py
```

#### Standalone Executable (for users)

After building the executable (see "Building the Executable" section below), you can find `gui.exe` in the `dist` folder. Simply double-click `gui.exe` to run the application.

## Usage

1.  **Select Exercise:** Choose "Pushup" or "Squat" from the dropdown menu.
2.  **Set Target Reps:** Enter a number for your target repetitions, or leave it as 0 for no target.
3.  **Start Workout:** Click the "Start Workout" button. The video feed will appear, and the counter will begin.
4.  **Real-time Feedback:** Pay attention to the on-screen feedback for form correction.
5.  **Stop Workout:** Click "Stop Workout" to end the session.
6.  **View History:** Click "View History" to see a log of your past workouts.
7.  **View Achievements:** Click "View Achievements" to see your unlocked milestones.
8.  **Settings:** Click "Settings" to change the video source (webcam or a specific video file).

## Building the Executable (for developers/distributors)

To create a standalone executable for Windows, ensure you have PyInstaller installed:

```bash
.\venv\Scripts\activate
pip install pyinstaller
```

Then, run the following command from the project root directory:

```bash
pyinstaller --onefile --windowed --add-data "movement_detector.py;." --add-data "database_manager.py;." --add-data "audio;audio" gui.py
```

The executable will be generated in the `dist` folder.

## Project Structure

-   `gui.py`: The main script for the PyQt graphical user interface.
-   `movement_detector.py`: Contains the `MovementDetector` and `SquatDetector` classes for exercise recognition.
-   `database_manager.py`: Manages interactions with the SQLite database for workout history and achievements.
-   `settings.ini`: Stores application settings (e.g., video source).
-   `audio/`: Directory containing audio files for real-time feedback.
-   `dist/`: (Generated) Contains the standalone executable after building.
-   `build/`: (Generated) PyInstaller build files.
-   `*.spec`: (Generated) PyInstaller specification file.
-   `venv/`: Python virtual environment.
-   `todos.md`: Project development roadmap.

## Future Enhancements (Phase 3 ideas)

-   More exercises (lunges, planks, etc.)
-   Advanced form analysis and personalized coaching.
-   Cloud synchronization for workout data.
-   User profiles and leaderboards.
-   Customizable audio feedback.
-   Cross-platform executables (macOS, Linux).