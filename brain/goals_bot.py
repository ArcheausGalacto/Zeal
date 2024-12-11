# /home/daniel/Desktop/Zeal/brain/goals_bot.py
import datetime
import os
from query import query_ollama
from now_bot import NowBot

class GoalsBot:
    def __init__(self, 
                 goals_path="/home/daniel/Desktop/Zeal/instructions/goals.txt", 
                 logs_path="/home/daniel/Desktop/Zeal/logs/logs.txt",
                 tasks_path="/home/daniel/Desktop/Zeal/instructions/tasks.txt"):
        os.makedirs(os.path.dirname(goals_path), exist_ok=True)
        self.goals_path = goals_path
        self.tasks_path = tasks_path
        self.logs_path = logs_path
        self.now_bot = NowBot(tasks_path=self.tasks_path, 
                              goals_path=self.goals_path,
                              now_path="/home/daniel/Desktop/Zeal/instructions/now.txt",
                              logs_path=self.logs_path)

    def log(self, message):
        with open(self.logs_path, "a") as f:
            f.write(f"{datetime.datetime.now()} - GOALS_BOT: {message}\n")

    def generate_goals(self, tasks):
        """
        Given a list of tasks in the format:
          ["*task* task1 *task*", "*task* task2 *task*", ...]
        For each task, we query the model and produce goals as *goal* ... *goal* lines.
        After generating all goals, we call now_bot to determine the next step.
        """

        all_goals = []

        for task_line in tasks:
            task_content = self._extract_task_content(task_line)
            if not task_content:
                continue

            prompt = f"""
You are a helpful assistant. You have been given a task and you must break it down into a list of discrete sub-goals that help accomplish the task. Each sub-goal should be actionable and can be accomplished in a single prompt or a single step.

The task is: "{task_content}"

Your response:
- The first goal should always be '*goal* determine the names of any output scripts predicted *goal*'.
- Output a list of sub-goals for accomplishing this task, if it is not something which is easily achievable.
- Each sub-goal should be on its own line.
- Each line should be wrapped in *goal* markers like: *goal* do something *goal*
- No extra explanation or formatting besides the goals.
- Remember that you are incapable of doing testing.
- If no sub-goals are applicable, output the task as a goal.
- Ensure that writing to a file is always a component of your goal planning.
- Do not specify filenames in the goals
- Creating a file and writing to it should always be done in one step (this should be specified at the first step to write the file).
- The file to write to must not be a txt, it must be in a valid programming language.
"""

            self.log(f"Querying model for goals related to task: {task_content}")
            response = query_ollama(prompt)
            self.log(f"Model response for goals:\n{response}")

            # Process each line of response to find *goal* lines
            task_goals = []
            for line in response.splitlines():
                line = line.strip()
                if line.startswith("*goal*") and line.endswith("*goal*"):
                    task_goals.append(line)

            if task_goals:
                all_goals.extend(task_goals)

        # Write all extracted goals to goals.txt
        if all_goals:
            with open(self.goals_path, "a") as f:
                for g in all_goals:
                    f.write(g + "\n")
                    self.log(f"Extracted goal: {g}")
        else:
            self.log("No goals identified for any tasks.")

        # After goals are written, call now_bot to decide what to do first
        self.log("Calling now_bot to determine next steps.")
        self.now_bot.decide_next_step()

    def _extract_task_content(self, task_line):
        """
        Given a line like "*task* create prime number algorithm *task*",
        extract the content "create prime number algorithm".
        """
        parts = task_line.split("*task*")
        if len(parts) >= 3:
            return parts[1].strip()
        return None
