# /home/daniel/Desktop/Zeal/brain/orchestrator_bot.py
import datetime
import os
import re

from query import query_ollama
from cliff_notes import CliffNotesBot
from create_file_bot import CreateFileBot
from write_files_bot import WriteFilesBot
from proc_complete_bot import ProcCompleteBot

class OrchestratorBot:
    def __init__(self, logs_path="/home/daniel/Desktop/Zeal/logs/logs.txt"):
        self.logs_path = logs_path
        self.instructions_path = "/home/daniel/Desktop/Zeal/instructions"
        self.cliff_notes_path = os.path.join(self.instructions_path, "cliff_notes.txt")
        self.workspace_path = "/home/daniel/Desktop/Zeal/workspace"

    def log(self, message):
        with open(self.logs_path, "a") as f:
            f.write(f"{datetime.datetime.now()} - ORCHESTRATOR_BOT: {message}\n")

    def remove_empty_files(self):
        """
        Removes any empty files from the workspace directory.
        """
        for root, dirs, files in os.walk(self.workspace_path):
            for fname in files:
                fpath = os.path.join(root, fname)
                if os.path.isfile(fpath) and os.path.getsize(fpath) == 0:
                    try:
                        os.remove(fpath)
                        self.log(f"Removed empty file: {fpath}")
                    except Exception as e:
                        self.log(f"Failed to remove empty file {fpath}: {str(e)}")

    def process_now_file(self, now_path):
        # Remove empty files in the workspace before starting
        self.remove_empty_files()

        if not os.path.exists(now_path):
            self.log("now.txt does not exist. Nothing to process.")
            return

        with open(now_path, "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        if len(lines) < 2:
            self.log("now.txt is missing expected lines for task and goal.")
            return

        task_line = lines[0]
        goal_line = lines[1]

        self.log(f"Processing now.txt with task: {task_line} and goal: {goal_line}")

        prompt = f"""
You are a sophisticated orchestrator assistant. You have a current task and a current goal you must work on.

Task:
{task_line}

Goal:
{goal_line}

Your instructions:
1. If you have any summary notes or important points to keep track of regarding this task and goal, output them enclosed as follows:
*cliff* your notes here *cliff*
If you have no new notes, output nothing for notes. If tasked with generating information, output them as cliff notes. *cliff* your notes here *cliff*

2. If you must create a new file to accomplish this goal, output a line with the format:
*create* filename.ext *create*
If no file creation is needed, output nothing. Replace .ext with the actual extension you decide to use. Never output '.pseudo'. Always adhere to the filename which is in the cliff notes.
If you ever create a file, you must write to it.

3. If you must write contents to a file, output them as:
*write*
*filename.ext*
your file contents here
*write*
If no writing is needed, output nothing.
Code should always be written to a file with *write*...*write*
You should only accomplish the goal. The task is given for context such that you can achieve the goal. Do not work ahead. If the goal is to output filenames, come up with a filename to represent the work in progress script(s) and write the name(s) to the cliff notes.

Do not provide any explanation outside of these constructs.
Do not output anything else.
Output all constructs necessary in one output.
Notes should always go into cliff notes.
        """

        self.log("Querying model for orchestrator instructions...")
        response = query_ollama(prompt)
        self.log(f"Model response:\n{response}")

        cliff_pattern = re.compile(r"\*cliff\*(.*?)\*cliff\*", re.DOTALL)
        create_pattern = re.compile(r"\*create\*(.*?)\*create\*", re.DOTALL)
        write_pattern = re.compile(r"\*write\*(.*?)\*write\*", re.DOTALL)

        cliff_match = cliff_pattern.search(response)
        create_match = create_pattern.search(response)
        write_match = write_pattern.search(response)

        # Process cliff notes
        if cliff_match:
            notes = cliff_match.group(1).strip()
            self.log(f"Extracted cliff notes: {notes}")
            self.send_to_cliff_notes(notes)

        # Process file creation
        if create_match:
            filename = create_match.group(1).strip()
            self.log(f"Extracted create file request: {filename}")
            self.send_to_create_file_bot(filename)

        # Process file writing
        if write_match:
            # The write block includes a line with *filename.ext* followed by content.
            write_content = write_match.group(1).strip()
            wlines = write_content.splitlines()
            if wlines:
                file_line = wlines[0].strip()
                file_match = re.match(r"\*(.*?)\*", file_line)
                if file_match:
                    write_filename = file_match.group(1).strip()
                    file_body = "\n".join(wlines[1:]).strip()
                    # Combine filename and file contents into one string for WriteFilesBot
                    complete_file_contents = f"*{write_filename}*\n{file_body}"
                    self.log(f"Extracted write request for file: {write_filename} with contents:\n{file_body}")
                    self.send_to_write_files_bot(complete_file_contents)
                else:
                    self.log("No filename found in write block.")
            else:
                self.log("Empty write block encountered.")

        # After performing all actions, call proc_complete_bot to verify completion
        self.log("Calling proc_complete_bot to verify completion...")
        proc_bot = ProcCompleteBot()
        completed, explanation = proc_bot.run_check()
        # If not completed, proc_complete_bot will handle calling orchestrator with explanation.

    def send_to_cliff_notes(self, notes):
        cliff_notes_bot = CliffNotesBot()
        cliff_notes_bot.process_notes(notes)
        self.log(f"Sent notes to cliff_notes_bot: {notes}")

    def send_to_create_file_bot(self, filename):
        create_bot = CreateFileBot()
        create_bot.create_file(filename)
        self.log(f"Called create_file_bot to create file: {filename}")

    def send_to_write_files_bot(self, complete_file_contents):
        # Now we pass only one argument to match WriteFilesBot's write_to_file method signature
        write_bot = WriteFilesBot()
        write_bot.write_to_file(complete_file_contents)
        self.log("Called write_files_bot to write contents to file determined by write_files_bot.")

    def handle_unachieved_goal_explanation(self, explanation: str):
        self.log(f"Received unachieved goal explanation: {explanation}")
        if explanation.strip():
            # Append the explanation to cliff_notes so it becomes part of the context
            with open(self.cliff_notes_path, "a") as f:
                f.write("\n" + explanation + "\n")
            self.log("Appended unachieved goal explanation to cliff_notes.txt.")

        # Now re-run the process with the updated notes
        now_path = os.path.join(self.instructions_path, "now.txt")
        if os.path.exists(now_path) and os.path.getsize(now_path) > 0:
            self.log("Re-running process_now_file with updated context.")
            self.process_now_file(now_path)
        else:
            self.log("now.txt is empty, cannot re-run process. Possibly generate a new task/goal pair or end.")
