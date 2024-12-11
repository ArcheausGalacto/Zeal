# /home/daniel/Desktop/Zeal/brain/proc_complete_bot.py
import datetime
import os
import re
from query import query_ollama

class ProcCompleteBot:
    def __init__(self, 
                 workspace_path="/home/daniel/Desktop/Zeal/workspace",
                 instructions_path="/home/daniel/Desktop/Zeal/instructions",
                 logs_path="/home/daniel/Desktop/Zeal/logs/logs.txt"):
        self.workspace_path = workspace_path
        self.instructions_path = instructions_path
        self.logs_path = logs_path

    def log(self, message):
        with open(self.logs_path, "a") as f:
            f.write(f"{datetime.datetime.now()} - PROC_COMPLETE_BOT: {message}\n")

    def run_check(self):
        """
        Steps:
        1. Gather all info.
        2. Query the model.
        3. Check if the model's entire response contains "YES" or "NO" using regex.
           - If "YES": goal achieved, remove goal, clear now.txt, rerun now_bot.
           - If "NO": goal not achieved, extract explanation and then rerun orchestrator_bot.
           - If neither: consider not achieved and rerun orchestrator_bot with a generic explanation.
        """
        self.log("Running completion check...")

        # 1. List structure of workspace
        workspace_structure = self._list_dir_structure(self.workspace_path)

        # 2. Read cliff_notes.txt
        cliff_notes = self._read_file(os.path.join(self.instructions_path, "cliff_notes.txt"))
        
        # 3. Read all workspace file contents
        all_files_contents = self._read_all_workspace_files()

        # 4. Extract task and goal lines from now.txt
        now_path = os.path.join(self.instructions_path, "now.txt")
        now_contents = self._read_file(now_path)
        if not now_contents.strip():
            self.log("now.txt is empty or missing. No completion check needed.")
            return True, ""

        # Regex patterns
        task_pattern = re.compile(r"\*task\*(.*?)\*task\*", re.DOTALL)
        goal_pattern = re.compile(r"\*goal\*(.*?)\*goal\*", re.DOTALL)

        task_match = task_pattern.search(now_contents)
        goal_match = goal_pattern.search(now_contents)

        if not goal_match:
            self.log("No goal found in now.txt. Nothing to check.")
            return True, ""

        goal_line = goal_match.group(0).strip()
        if not task_match:
            self.log("No task found in now.txt. Using goal only.")
            task_line = "(no task found)"
        else:
            task_line = task_match.group(0).strip()

        # 5. Query model
        prompt = f"""
You have the following information:

Task: {task_line}
Goal: {goal_line}

Directory structure of workspace:
{workspace_structure}

Cliff notes (if any):
{cliff_notes if cliff_notes else "(no cliff notes)"}

Contents of each file in the workspace:
{all_files_contents if all_files_contents else "(no files or empty workspace)"}

Given the task and goal, and the current state of the files and cliff notes, has the goal been accomplished? Note that specifications may occur in the cliff notes.
Remember that the task is not the objective, only information provided so that you understand the goal. Only output NO if the goal is unachieved. If asked to contemplate information, if it is present in the cliff notes, output YES.
Definitions and thinking steps may reside in the cliff notes and must not always be in the workspace folder, which may remain empty if the step does not necessitate that it is populated.
Output:
- "YES" if the goal was met.
- "NO" if not met.
You may provide an explanation after NO if you wish.
Do not provide anything else beyond YES/NO and optional explanation if NO.
"""

        self.log("Querying model to check completion...")
        response = query_ollama(prompt)
        self.log(f"Model completion check response:\n{response}")

        # 6. Check for YES or NO in the entire response
        yes_found = re.search(r"\bYES\b", response, re.IGNORECASE)
        no_found = re.search(r"\bNO\b", response, re.IGNORECASE)

        if yes_found and not no_found:
            # Goal achieved
            self.log("Goal achieved. Removing goal from goals.txt and clearing now.txt.")
            self._remove_goal_from_goals_file(goal_line)
            self._clear_now_file()

            # After success, re-run now_bot
            self.log("Re-running now_bot to determine next steps.")
            from now_bot import NowBot
            now_bot = NowBot()
            now_bot.decide_next_step()

            return True, ""
        elif no_found:
            # Goal not achieved, extract explanation if any
            lines = response.splitlines()
            explanation = ""
            no_line_index = None
            for i, line in enumerate(lines):
                if re.search(r"\bNO\b", line, re.IGNORECASE):
                    no_line_index = i
                    break
            if no_line_index is not None and no_line_index < len(lines)-1:
                explanation = "\n".join(l.strip() for l in lines[no_line_index+1:] if l.strip())
            if not explanation.strip():
                explanation = ""

            self.log("Goal not achieved. Explanation:\n" + explanation)
            # Rerun orchestrator_bot
            self.log("Re-running orchestrator_bot since goal not achieved.")
            from orchestrator_bot import OrchestratorBot
            orch = OrchestratorBot(logs_path=self.logs_path)
            orch.handle_unachieved_goal_explanation(explanation)

            return False, explanation
        else:
            # Neither YES nor NO found, consider not achieved
            self.log("No YES or NO found in response. Considering NO.")
            explanation = "No definitive answer found."
            # Rerun orchestrator_bot with explanation
            self.log("Re-running orchestrator_bot since no definitive answer.")
            from orchestrator_bot import OrchestratorBot
            orch = OrchestratorBot(logs_path=self.logs_path)
            orch.handle_unachieved_goal_explanation(explanation)

            return False, explanation

    def _remove_goal_from_goals_file(self, goal_line):
        goals_path = os.path.join(self.instructions_path, "goals.txt")
        if not os.path.exists(goals_path):
            self.log("goals.txt not found, cannot remove goal.")
            return

        with open(goals_path, "r") as f:
            lines = f.readlines()

        target = goal_line.strip()
        self.log(f"Attempting to remove goal line: {repr(target)}")
        found = False
        new_lines = []
        for l in lines:
            line_stripped = l.strip()
            self.log(f"Comparing {repr(line_stripped)} to {repr(target)}")
            if line_stripped == target:
                self.log(f"Match found. Removing line: {repr(line_stripped)}")
                found = True
            else:
                new_lines.append(l)

        with open(goals_path, "w") as f:
            f.writelines(new_lines)

        if found:
            self.log(f"Removed goal line from goals.txt: {goal_line}")
        else:
            self.log("No matching goal line found in goals.txt to remove.")

    def _clear_now_file(self):
        now_path = os.path.join(self.instructions_path, "now.txt")
        try:
            with open(now_path, "w") as f:
                f.write("")
            self.log("Cleared now.txt.")
        except Exception as e:
            self.log(f"Failed to clear now.txt: {str(e)}")

    def _list_dir_structure(self, directory):
        structure = []
        for root, dirs, files in os.walk(directory):
            level = root.replace(directory, '').count(os.sep)
            indent = ' ' * (4 * level)
            structure.append(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * (4 * (level + 1))
            for f in files:
                structure.append(f"{subindent}{f}")
        return "\n".join(structure)

    def _read_file(self, filepath):
        if os.path.exists(filepath):
            try:
                with open(filepath, "r") as f:
                    return f.read()
            except Exception as e:
                self.log(f"Failed to read file {filepath}: {str(e)}")
        return ""

    def _read_lines(self, filepath):
        if os.path.exists(filepath):
            try:
                with open(filepath, "r") as f:
                    return [l.strip() for l in f if l.strip()]
            except Exception as e:
                self.log(f"Failed to read lines from {filepath}: {str(e)}")
        return []

    def _read_all_workspace_files(self):
        output = []
        for root, dirs, files in os.walk(self.workspace_path):
            for fname in files:
                fpath = os.path.join(root, fname)
                content = self._read_file(fpath)
                output.append(f"Filename: {fpath}\n{content}\n")
        return "\n".join(output)
