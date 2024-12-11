# /home/daniel/Desktop/Zeal/brain/feedback_bot.py
import datetime

class FeedbackBot:
    def __init__(self, feedback_path="/home/daniel/Desktop/Zeal/logs/feedback.txt", logs_path="/home/daniel/Desktop/Zeal/logs/logs.txt"):
        self.feedback_path = feedback_path
        self.logs_path = logs_path

    def log(self, message):
        with open(self.logs_path, "a") as f:
            f.write(f"{datetime.datetime.now()} - FEEDBACK_BOT: {message}\n")

    def provide_feedback(self, goal, success):
        feedback = f"Goal: {goal}, Success: {success}"
        with open(self.feedback_path, "a") as f:
            f.write(feedback + "\n")
        self.log("Provided feedback: " + feedback)
        return feedback
