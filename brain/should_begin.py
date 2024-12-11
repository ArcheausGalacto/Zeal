# /home/daniel/Desktop/Zeal/brain/should_begin.py
import datetime
import os
from query import query_ollama
from goals_bot import GoalsBot

class ShouldBegin:
    def __init__(self, 
                 tasks_path="/home/daniel/Desktop/Zeal/instructions/tasks.txt", 
                 rules_path="/home/daniel/Desktop/Zeal/instructions/rules.txt",
                 logs_path="/home/daniel/Desktop/Zeal/logs/logs.txt"):
        self.tasks_path = tasks_path
        self.rules_path = rules_path
        self.logs_path = logs_path
        self.goals_bot = GoalsBot()

    def log(self, message):
        with open(self.logs_path, "a") as f:
            f.write(f"{datetime.datetime.now()} - SHOULD_BEGIN: {message}\n")

    def decide(self, user_input, tasks, rules):
        tasks_content = self._read_file_content(self.tasks_path)
        rules_content = self._read_file_content(self.rules_path)

        prompt = f"""
You are a decision-making system.

The user just said:
\"\"\"{user_input}\"\"\"

If the user explicitly told you to begin processing now (which may be stated as 'begin now', 'begin processing now', 'go ahead and start', or similar),
then output 'YES'.

If the user simply mentioned tasks or gave rules but did not explicitly say to start or begin now, output 'NO'.

Output only one word on a single line:
"YES" if you should begin,
"NO" if you should not.

Do not output anything else.
"""

        self.log("Querying model to decide if we should begin...")
        response = query_ollama(prompt)
        self.log(f"Model response to begin decision:\n{response}")

        decision = self._interpret_decision(response)

        if decision == "YES":
            message = "Model decided: YES, we should begin working now."
            print(message)
            self.log(message)
            self._generate_goals_for_tasks()
        else:
            message = "Model decided: NO, we should not begin working now."
            print(message)
            self.log(message)

    def _interpret_decision(self, response):
        """
        Interpret the model's response by checking each line for a clear 'YES' or 'NO'.
        We'll ignore markdown formatting or code fences by stripping them out.
        """
        lines = [line.strip().lower() for line in response.splitlines() if line.strip()]

        # Remove code fences or backticks if present
        # For example, if a line is '```YES```', remove the backticks:
        cleaned_lines = []
        for line in lines:
            line = line.replace("`", "")  # remove backticks
            cleaned_lines.append(line.strip())

        # Now check if any line is exactly "yes" or "no"
        for line in cleaned_lines:
            if line == "yes":
                return "YES"
            if line == "no":
                return "NO"

        # If we reach here, no exact match was found, default to NO
        return "NO"

    def _generate_goals_for_tasks(self):
        if os.path.exists(self.tasks_path):
            with open(self.tasks_path, "r") as f:
                all_tasks = [line.strip() for line in f if line.strip()]
            
            if all_tasks:
                self.log("Sending tasks to goals_bot for goal generation.")
                self.goals_bot.generate_goals(all_tasks)
            else:
                self.log("No tasks found in tasks.txt.")
        else:
            self.log("tasks.txt not found. No tasks to process.")

    def _read_file_content(self, filepath):
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                return f.read().strip()
        return ""
