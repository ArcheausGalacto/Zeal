# /home/daniel/Desktop/Zeal/brain/write_files_bot.py
import os
import datetime
import re

class WriteFilesBot:
    def __init__(self, 
                 workspace_path="/home/daniel/Desktop/Zeal/workspace", 
                 logs_path="/home/daniel/Desktop/Zeal/logs/logs.txt"):
        os.makedirs(workspace_path, exist_ok=True)
        self.workspace_path = workspace_path
        self.logs_path = logs_path

    def log(self, message):
        with open(self.logs_path, "a") as f:
            f.write(f"{datetime.datetime.now()} - WRITE_FILES_BOT: {message}\n")

    def write_to_file(self, file_contents: str):
        """
        Takes the contents as given by orchestrator.
        According to instructions:
        - Determine the filename from the first line (*filename.ext*).
        - Write the rest of the lines as content to the file.
        - Remove any lines containing triple backticks ``` before writing.
        - Overwrite the file if it already exists.
        """
        lines = file_contents.splitlines()
        if not lines:
            self.log("No file contents provided.")
            return

        first_line = lines[0].strip()
        # Expecting something like: *filename.ext*
        match = re.match(r"\*(.*?)\*", first_line)
        if not match:
            self.log("No valid filename found in the first line of file contents.")
            return

        filename = match.group(1).strip()
        # Validate filename as before
        if ".." in filename or "/" in filename or "\\" in filename:
            self.log(f"Invalid filename in write_files_bot: {filename}")
            return

        if not re.search(r"\.\w+$", filename):
            self.log(f"Invalid filename (no extension) in write_files_bot: {filename}")
            return

        file_path = os.path.join(self.workspace_path, filename)
        # Filter out lines containing triple backticks
        filtered_lines = [line for line in lines[1:] if "```" not in line]

        file_body = "\n".join(filtered_lines)

        try:
            # Open in "w" mode to overwrite if file exists
            with open(file_path, "w") as f:
                if file_body.strip():
                    f.write(file_body + "\n")
                else:
                    # If after filtering there's nothing left, just create/overwrite an empty file
                    pass
            self.log(f"Wrote to file: {file_path}, {len(file_body)} chars (after filtering ```)")
        except Exception as e:
            self.log(f"Failed to write to file '{file_path}': {str(e)}")
