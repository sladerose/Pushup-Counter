import sqlite3
import datetime

class DatabaseManager:
    def __init__(self, db_name="workout_history.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_table()
        self._create_achievements_table()

    def _connect(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")

    def _create_table(self):
        if self.conn:
            try:
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS workouts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        exercise_type TEXT NOT NULL,
                        completed_reps INTEGER NOT NULL,
                        duration_seconds INTEGER
                    )
                """)
                self.conn.commit()
            except sqlite3.Error as e:
                print(f"Error creating table: {e}")

    def _create_achievements_table(self):
        if self.conn:
            try:
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS achievements (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        name TEXT NOT NULL UNIQUE
                    )
                """)
                self.conn.commit()
            except sqlite3.Error as e:
                print(f"Error creating achievements table: {e}")

    def save_workout(self, exercise_type, completed_reps, duration_seconds=None):
        if self.conn:
            try:
                date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.cursor.execute("""
                    INSERT INTO workouts (date, exercise_type, completed_reps, duration_seconds)
                    VALUES (?, ?, ?, ?)
                """, (date_str, exercise_type, completed_reps, duration_seconds))
                self.conn.commit()
                print(f"Workout saved: {exercise_type}, {completed_reps} reps")
            except sqlite3.Error as e:
                print(f"Error saving workout: {e}")

    def save_achievement(self, name):
        if self.conn:
            try:
                date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.cursor.execute("""
                    INSERT OR IGNORE INTO achievements (date, name)
                    VALUES (?, ?)
                """, (date_str, name))
                self.conn.commit()
                print(f"Achievement unlocked: {name}")
            except sqlite3.Error as e:
                print(f"Error saving achievement: {e}")

    def get_all_workouts(self):
        if self.conn:
            try:
                self.cursor.execute("SELECT * FROM workouts ORDER BY date DESC")
                return self.cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Error retrieving workouts: {e}")
        return []

    def get_all_achievements(self):
        if self.conn:
            try:
                self.cursor.execute("SELECT * FROM achievements ORDER BY date DESC")
                return self.cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Error retrieving achievements: {e}")
        return []

    def close(self):
        if self.conn:
            self.conn.close()

if __name__ == "__main__":
    db_manager = DatabaseManager()
    # Example usage:
    # db_manager.save_workout("Pushup", 20, 120)
    # db_manager.save_workout("Squat", 15)
    
    # workouts = db_manager.get_all_workouts()
    # for workout in workouts:
    #     print(workout)
    
    db_manager.close()