# /home/daniel/Desktop/Zeal/brain/rules_bot.py
import datetime
import os
from query import query_ollama

class RulesBot:
    def __init__(self, 
                 rules_path="/home/daniel/Desktop/Zeal/instructions/rules.txt", 
                 tasks_path="/home/daniel/Desktop/Zeal/instructions/tasks.txt",
                 logs_path="/home/daniel/Desktop/Zeal/logs/logs.txt"):
        os.makedirs(os.path.dirname(rules_path), exist_ok=True)
        os.makedirs(os.path.dirname(tasks_path), exist_ok=True)
        
        self.rules_path = rules_path
        self.tasks_path = tasks_path
        self.logs_path = logs_path

    def log(self, message):
        with open(self.logs_path, "a") as f:
            f.write(f"{datetime.datetime.now()} - RULES_BOT: {message}\n")

    def extract_rules_from_text(self, text):
        """
        Uses query_ollama to extract rules from user input, no heuristics in Python.
        The prompt instructions:
        - Identify all rules mentioned by the user.
        - For each rule, output exactly one line in the format: *rule* <rule content> *rule*
        - No extra text or explanation. If no rules, output nothing.

        After extracting rules, we write them to rules.txt and remove any corresponding tasks in tasks.txt.
        """

        prompt = f"""
You are a helpful assistant whose job is to read the user's message and extract any rules mentioned.
These could be instructions or guidelines the user wants to impose.

The user says: "{text}"

Your response:
- Identify all rules or guidelines stated by the user.
- Tasks are not rules. Ignore tasks, as there is another bot to handle those.
- Again, do not output tasks as rules. If you would consider it to be a task and not a general rule, output nothing.
- For each rule, output it as one line enclosed in *rule* markers like this: *rule* do not do X *rule*.
- Remember that the rule must have *rule* before and after it. Like this, *rule* do something *rule*.
- Do not add any extra text, explanations, or tasks.
- If no rules can be identified, produce no output at all.
"""

        self.log("Querying model for rules...")
        response = query_ollama(prompt)
        self.log(f"Model response for rules:\n{response}")

        # Process each line of response to find *rule* lines
        rules = []
        for line in response.splitlines():
            line = line.strip()
            if line.startswith("*rule*") and line.endswith("*rule*"):
                rules.append(line)

        # Write rules to rules.txt
        if rules:
            with open(self.rules_path, "a") as f:
                for r in rules:
                    f.write(r + "\n")
                    self.log(f"Extracted rule: {r}")

            # Remove corresponding tasks if they match the rule content
            # Extract rule content (between *rule* markers) and find matching tasks (*task* same content *task*)
            self.remove_matching_tasks(rules)
        else:
            self.log("No rules identified.")

        return rules

    def remove_matching_tasks(self, rules):
        """
        For each rule line in the form '*rule* <content> *rule*', 
        if there is a corresponding '*task* <content> *task*' line in tasks.txt, remove it.
        """
        if not os.path.exists(self.tasks_path):
            return

        # Load all tasks
        with open(self.tasks_path, "r") as f:
            tasks_lines = f.readlines()

        original_task_count = len(tasks_lines)

        # For each rule, derive the corresponding task line and remove it if present
        for rule_line in rules:
            # Extract rule content
            # rule_line is like: *rule* some content *rule*
            # Remove the leading "*rule* " and trailing " *rule*"
            rule_content = rule_line.replace("*rule*", "").strip()
            # This leaves only the content since we replaced all occurrences of *rule*
            # There might be two occurrences: beginning and end.
            # Let's be more explicit:
            # Assuming format: *rule* <content> *rule*
            # Splitting on *rule*:
            # line.split("*rule*") => ['', ' content ', '']
            # The content should be in line.split("*rule*")[1].strip()
            parts = rule_line.split("*rule*")
            if len(parts) >= 3:
                rule_content = parts[1].strip()

            # Form the corresponding task line
            corresponding_task_line = f"*task* {rule_content} *task*\n"

            # Remove this line if it appears in tasks_lines
            if corresponding_task_line in tasks_lines:
                tasks_lines.remove(corresponding_task_line)
                self.log(f"Removed corresponding task line: {corresponding_task_line.strip()}")

        # Write back updated tasks
        if len(tasks_lines) != original_task_count:
            with open(self.tasks_path, "w") as f:
                f.writelines(tasks_lines)
