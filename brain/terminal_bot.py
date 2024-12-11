# /home/daniel/Desktop/Zeal/brain/terminal_bot.py
import datetime
import subprocess

class TerminalBot:
    def __init__(self, logs_path="/home/daniel/Desktop/Zeal/logs/logs.txt"):
        self.logs_path = logs_path

    def log(self, message):
        with open(self.logs_path, "a") as f:
            f.write(f"{datetime.datetime.now()} - TERMINAL_BOT: {message}\n")

    def run_command(self, command):
        self.log(f"Running command: {command}")
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            self.log(f"Command output: {result.stdout}")
            self.log(f"Command errors: {result.stderr}")
            return result.stdout, result.stderr
        except Exception as e:
            self.log(f"Command failed: {str(e)}")
            return "", str(e)
