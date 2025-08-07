# Project Todos

## Phase 1: Core Movement Tracking & Game Loop
- [x] Abstract Movement Detection: Refactor `main.py` to create a more generic `MovementDetector` class that can be extended for different exercises (pushups, squats, etc.).
- [x] Add Squat Detection: Implement squat detection as a new module or extension of `MovementDetector`.
- [x] Basic Game Loop: Create a simple game loop in `main.py` that allows selecting an exercise and tracks progress.
- [x] Real-time Feedback: Display real-time count and feedback (e.g., "Good form!", "Go deeper!") on the screen.

**Phase 1 Complete!**

## Phase 2: Productization & User Experience
- [ ] **Graphical User Interface (GUI):**
    - [x] Implement a modern GUI using a Python framework (e.g., PyQt).
    - [x] Allow exercise selection (pushup, squat) and target repetition setting via the UI.
    - [x] Display real-time count, angle, and feedback within the GUI.
    - [x] Add start, pause, and reset buttons for workout control.
- [ ] **Workout Tracking & History:**
    - [x] Implement a local SQLite database to store workout sessions (date, exercise type, completed reps, duration).
    - [x] Create a simple "History" view in the GUI to display past workouts.
- [ ] **Enhanced Feedback & Gamification:**
    - [x] Integrate audio cues for workout start/end, rep completion, and form feedback.
    - [x] Implement a basic achievement system (e.g., "First 100 Pushups!").
- [ ] **Application Settings:**
    - [x] Allow users to select webcam/video source from within the GUI.
    - [x] Implement saving and loading of user preferences (e.g., default exercise, sound volume).
- [ ] **Packaging & Distribution:**
    - [x] Create a standalone executable for Windows using PyInstaller.