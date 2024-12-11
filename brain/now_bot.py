# /home/daniel/Desktop/Zeal/brain/now_bot.py
import datetime
import os
from orchestrator_bot import OrchestratorBot

class NowBot:
    def __init__(self, 
                 tasks_path="/home/daniel/Desktop/Zeal/instructions/tasks.txt",
                 goals_path="/home/daniel/Desktop/Zeal/instructions/goals.txt",
                 now_path="/home/daniel/Desktop/Zeal/instructions/now.txt",
                 logs_path="/home/daniel/Desktop/Zeal/logs/logs.txt"):
        self.tasks_path = tasks_path
        self.goals_path = goals_path
        self.now_path = now_path
        self.logs_path = logs_path
        self.orchestrator = OrchestratorBot(logs_path=logs_path)

    def log(self, message):
        with open(self.logs_path, "a") as f:
            f.write(f"{datetime.datetime.now()} - NOW_BOT: {message}\n")

    def decide_next_step(self):
        """
        Decide what must be done first based on the available tasks and goals.
        A simple approach: 
        - Load all tasks from tasks.txt
        - Load all goals from goals.txt
        - Pick the first task and the first goal
        - Write them to now.txt
        - Then call orchestrator_bot to process now.txt
        """
        tasks = self._read_file_lines(self.tasks_path)
        goals = self._read_file_lines(self.goals_path)

        if not tasks:
            self.log("No tasks found. Cannot decide next step.")
            return

        if not goals:
            self.log("No goals found. Cannot decide next step.")
            return

        # For simplicity, just pick the first task and the first goal
        first_task = tasks[0]
        first_goal = goals[0]

        # Write the chosen task and goal to now.txt
        now_content = f"{first_task}\n{first_goal}\n"
        with open(self.now_path, "w") as f:
            f.write(now_content)

        self.log(f"Set now.txt with task and goal:\n{now_content}")

        # After setting now.txt, call orchestrator to process it
        self.log("Calling orchestrator_bot to process now.txt.")
        self.orchestrator.process_now_file(self.now_path)

    def _read_file_lines(self, filepath):
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                return [line.strip() for line in f if line.strip()]
        return []
