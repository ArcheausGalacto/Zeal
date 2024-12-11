#!/usr/bin/env python3
# /home/daniel/Desktop/Zeal/brain/chatbot_user.py

import sys
import os
import datetime

from task_bot import TaskBot
from rules_bot import RulesBot
from should_begin import ShouldBegin

def log(message, logs_path="/home/daniel/Desktop/Zeal/logs/logs.txt"):
    with open(logs_path, "a") as f:
        f.write(f"{datetime.datetime.now()} - USER_CHAT: {message}\n")

def main():
    task_bot = TaskBot()
    rules_bot = RulesBot()
    should_begin_bot = ShouldBegin()

    print("Welcome! You can type commands or requests here.")
    print("For example, you might say: 'Please create a prime number algorithm', or 'Can you show me the directory structure?'")
    print("Type 'exit' or 'quit' to end.")

    while True:
        user_input = input("\nUser: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        # Log the user input
        log(f"User input: {user_input}")

        # Extract tasks and rules from user input
        tasks = task_bot.extract_tasks_from_text(user_input)
        rules = rules_bot.extract_rules_from_text(user_input)

        # Decide if we should begin based on tasks and rules
        should_begin_bot.decide(user_input, tasks, rules)

        # For now, the chatbot simply responds with a generic message
        # In a real system, the orchestrator_bot or other logic would produce a meaningful response.
        response = "I have processed your input. If there are tasks or rules, they've been logged."
        print(f"Chatbot: {response}")
        log(f"Chatbot response: {response}")

if __name__ == "__main__":
    main()
