# /home/daniel/Desktop/Zeal/brain/create_file_bot.py
import os
import datetime
import re

class CreateFileBot:
    def __init__(self, 
                 workspace_path="/home/daniel/Desktop/Zeal/workspace", 
                 logs_path="/home/daniel/Desktop/Zeal/logs/logs.txt"):
        os.makedirs(workspace_path, exist_ok=True)
        self.workspace_path = workspace_path
        self.logs_path = logs_path

    def log(self, message):
        with open(self.logs_path, "a") as f:
            f.write(f"{datetime.datetime.now()} - CREATE_FILE_BOT: {message}\n")

    def create_file(self, filename: str, content: str = ""):
        """
        Checks filename validity and creates the file in the workspace.
        """
        # Basic validation: no directory traversal, must contain an extension.
        if ".." in filename or "/" in filename or "\\" in filename:
            self.log(f"Invalid filename (directory traversal attempt): {filename}")
            return

        if not re.search(r"\.\w+$", filename):
            self.log(f"Invalid filename (no extension): {filename}")
            return

        file_path = os.path.join(self.workspace_path, filename)
        try:
            with open(file_path, "w") as f:
                f.write(content)
            self.log(f"Created file: {file_path} with content length {len(content)}")
        except Exception as e:
            self.log(f"Failed to create file '{file_path}': {str(e)}")
