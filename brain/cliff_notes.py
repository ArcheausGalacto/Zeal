# /home/daniel/Desktop/Zeal/brain/cliff_notes.py
import os
import datetime

class CliffNotesBot:
    def __init__(self, 
                 notes_path="/home/daniel/Desktop/Zeal/instructions/cliff_notes.txt", 
                 logs_path="/home/daniel/Desktop/Zeal/logs/logs.txt"):
        os.makedirs(os.path.dirname(notes_path), exist_ok=True)
        self.notes_path = notes_path
        self.logs_path = logs_path

    def log(self, message):
        with open(self.logs_path, "a") as f:
            f.write(f"{datetime.datetime.now()} - CLIFF_NOTES_BOT: {message}\n")

    def process_notes(self, notes: str):
        """
        Writes the given notes to cliff_notes.txt in instructions.
        Appends the notes so multiple notes can accumulate.
        """
        try:
            with open(self.notes_path, "a") as f:
                f.write(notes + "\n")
            self.log(f"Wrote notes to {self.notes_path}: {notes}")
        except Exception as e:
            self.log(f"Failed to write notes: {str(e)}")
