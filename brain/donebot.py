# /home/daniel/Desktop/Zeal/brain/donebot.py
import datetime

class DoneBot:
    def __init__(self, logs_path="/home/daniel/Desktop/Zeal/logs/logs.txt"):
        self.logs_path = logs_path

    def log(self, message):
        with open(self.logs_path, "a") as f:
            f.write(f"{datetime.datetime.now()} - DONE_BOT: {message}\n")

    def decide(self, feedback):
        # Dummy logic:
        # If feedback says success, accept. Otherwise reject.
        if "Success: True" in feedback:
            decision = "ACCEPT"
        else:
            decision = "REJECT"
        self.log(f"Decision: {decision}")
        return decision
