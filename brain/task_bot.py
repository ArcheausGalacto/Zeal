# /home/daniel/Desktop/Zeal/brain/task_bot.py
import datetime
import os
from query import query_ollama

class TaskBot:
    def __init__(self, 
                 tasks_path="/home/daniel/Desktop/Zeal/instructions/tasks.txt", 
                 logs_path="/home/daniel/Desktop/Zeal/logs/logs.txt"):
        os.makedirs(os.path.dirname(tasks_path), exist_ok=True)
        self.tasks_path = tasks_path
        self.logs_path = logs_path

    def log(self, message):
        with open(self.logs_path, "a") as f:
            f.write(f"{datetime.datetime.now()} - TASK_BOT: {message}\n")

    def extract_tasks_from_text(self, text):
        """
        Uses the query_ollama function to extract tasks from user input.
        No heuristics in Python code; we rely on the model for task extraction.
        The prompt is carefully engineered to instruct the model:
        - The user’s message is provided.
        - Model should identify all actionable tasks.
        - Each task is output on its own line, wrapped as *task* <task> *task*.
        - If no tasks, model outputs nothing.

        We then write each extracted task line to tasks.txt.
        """
        prompt = f"""
You are a helpful assistant whose job is to read a user message and extract actionable tasks or instructions from it.

The user says: "{text}"

Your response:
- Identify all actionable tasks described or implied by the user's message.
- There is another bot, rules bot, which determines if the input is a rule. If it is considered a rule, ignore it. Rules are anything which are not actionable steps to accomplish a coding task.
- There is another bot which determines if the user is requesting that you begin the process. Do not add commands to begin to the task list, ignore them.
- For each task, output exactly one line, enclosed in *task* markers like this: *task* do something *task*.
- Remember that the task must have *task* before and after it. Like this, *task* do something *task*.
- Do not add any extra text or explanation.
- If no tasks can be identified, produce no output at all.
"""

        self.log("Querying model for tasks...")
        response = query_ollama(prompt)
        self.log(f"Model response:\n{response}")

        # Write each line from model response to tasks.txt if it matches the *task* format
        tasks = []
        for line in response.splitlines():
            line = line.strip()
            # We trust the model to follow the format, just record whatever it provides
            if line.startswith("*task*") and line.endswith("*task*"):
                tasks.append(line)
        
        if tasks:
            with open(self.tasks_path, "a") as f:
                for t in tasks:
                    f.write(t + "\n")
                    self.log(f"Extracted task: {t}")
        else:
            self.log("No tasks identified.")
        
        return tasks
