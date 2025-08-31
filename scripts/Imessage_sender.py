import os
import subprocess

butler_folder = os.path.expanduser("~/Documents/Butler")
os.makedirs(butler_folder, exist_ok=True)

applescript_code = '''on run {targetNumber, textMessage}
    tell application "Messages"
        set iMessageService to 1st account whose service type is iMessage
        set targetBuddy to participant targetNumber of iMessageService
        send textMessage to targetBuddy
    end tell
end run
'''

script_path = os.path.join(butler_folder, "sent_function.scpt")

with open(script_path, "w") as f:
    f.write(applescript_code)

print(f"AppleScript saved at: {script_path}")

number = input("Enter recipient number (with +country code): ").strip()
message = input("Enter your message: ").strip()

try:
    subprocess.run(["osascript", script_path, number, message], check=True)
    print("Message sent successfully!")
except subprocess.CalledProcessError as e:
    print("Failed to send message:", e)