import os
import subprocess

butler_folder = os.path.expanduser("~/Applications/Butler")
os.makedirs(butler_folder, exist_ok=True)  

applescript_code = '''on run {targetNumber}
    set target to targetNumber
    tell application "FaceTime"
        activate
        open location "facetime:" & target
    end tell
end run
'''

script_path = os.path.join(butler_folder, "facetime_call.scpt")
with open(script_path, "w") as f:
    f.write(applescript_code)

print(f"AppleScript saved at: {script_path}")

number = input(" Enter recipient number (with +country code or Apple ID email): ").strip()

try:
    subprocess.run(["osascript", script_path, number], check=True)
    print("FaceTime call initiated successfully!")
except subprocess.CalledProcessError as e:
    print("Failed to start FaceTime call:", e)
