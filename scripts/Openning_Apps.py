import os
import subprocess
import difflib

app_paths = [
    "/Applications",
    os.path.expanduser("~/Applications"),
    "/System/Applications",
    "/Applications/Utilities",
    "/System/Applications/Utilities"
]

apps = {}

for path in app_paths:
    if os.path.exists(path):
        for item in os.listdir(path):
            if item.endswith(".app"):
                app_name = item.replace(".app", "")
                apps[app_name.lower()] = os.path.join(path, item)

user_input = input("Enter the application name to open: ").lower()

if user_input in apps:
    print(f"Opening {user_input}...")
    subprocess.run(["open", "-a", apps[user_input]])
else:
    matches = [name for name in apps if user_input in name]

    if not matches:
        matches = difflib.get_close_matches(user_input, apps.keys(), n=5, cutoff=0.4)

    if len(matches) == 1:
        confirm = input(f"Did you mean '{matches[0]}'? (yes/no): ").lower()
        if confirm in ["yes", "y"]:
            print(f"Opening {matches[0]}...")
            subprocess.run(["open", "-a", apps[matches[0]]])
        else:
            print("Cancelled.")
    elif len(matches) > 1:
        print("Multiple matches found:")
        for i, m in enumerate(matches, 1):
            print(f"{i}. {m}")
        choice = input("Enter the number of the app to open (or press Enter to cancel): ")
        if choice.isdigit() and 1 <= int(choice) <= len(matches):
            selected = matches[int(choice) - 1]
            print(f"Opening {selected}...")
            subprocess.run(["open", "-a", apps[selected]])
        else: 
            print("Cancelled.")
    else:
        print("Application not found!")
