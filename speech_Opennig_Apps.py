import os
import subprocess
import difflib
import speech_recognition as sr
import re

def speak(text, rate=200):
    print(text)
    subprocess.run(["say", "-r", str(rate), text])

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

def get_display_name(app_path):
    """Return the nicely cased app name from the .app path."""
    return os.path.basename(app_path).replace(".app", "")

def listen_for_command(timeout=None, phrase_time_limit=None):
    """Listen and return recognized text (lowercased), or None on failure."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Say the application name...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

    try:
        text = recognizer.recognize_google(audio)
        text = text.lower().strip()
        speak(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        speak("Sorry, I could not understand your voice.")
    except sr.RequestError:
        speak("Could not request results. Please check your internet connection.")
    except Exception as e:
        speak("Listening timed out or failed.")
    return None

def spoken_to_number(spoken, max_choice=None):
    """
    Convert a spoken phrase into an integer choice, or None.
    Handles digits, number words, ordinals, and simple phrases.
    If max_choice is provided, we only accept results <= max_choice.
    """
    if not spoken:
        return None

    s = spoken.lower().strip()
    s_clean = re.sub(r'[^\w\s]', ' ', s)
    tokens = s_clean.split()

    m = re.search(r'\d+', s_clean)
    if m:
        val = int(m.group())
        if max_choice is None or 1 <= val <= max_choice:
            return val

    word_map = {
        "zero":0, "oh":0,
        "one":1, "two":2, "three":3, "four":4, "five":5,
        "six":6, "seven":7, "eight":8, "nine":9, "ten":10,
        "eleven":11, "twelve":12, "thirteen":13, "fourteen":14, "fifteen":15,
        "sixteen":16, "seventeen":17, "eighteen":18, "nineteen":19, "twenty":20
    }
    ord_map = {
        "first":1, "second":2, "third":3, "fourth":4, "fifth":5,
        "sixth":6, "seventh":7, "eighth":8, "ninth":9, "tenth":10,
        "1st":1, "2nd":2, "3rd":3, "4th":4, "5th":5, "6th":6, "7th":7, "8th":8, "9th":9, "10th":10
    }

    for t in reversed(tokens):
        if t in word_map:
            val = word_map[t]
            if max_choice is None or 1 <= val <= max_choice:
                return val
        if t in ord_map:
            val = ord_map[t]
            if max_choice is None or 1 <= val <= max_choice:
                return val
        if t in ("to", "too") and (max_choice is None or max_choice >= 2):
            return 2

    for word, val in word_map.items():
        if f" {word} " in f" {s_clean} ":
            if max_choice is None or 1 <= val <= max_choice:
                return val

    return None

def open_app(app_name):
    app_name = app_name.lower().strip()

    if app_name in apps:
        display = get_display_name(apps[app_name])
        speak(f"Opening {display}")
        subprocess.run(["open", "-a", apps[app_name]])
        return

    matches = [name for name in apps if app_name in name]

    if not matches:
        matches = difflib.get_close_matches(app_name, apps.keys(), n=5, cutoff=0.4)

    if len(matches) == 1:
        display = get_display_name(apps[matches[0]])
        speak(f"Did you mean {display}? Opening it.")
        subprocess.run(["open", "-a", apps[matches[0]]])
        return

    if len(matches) > 1:
        speak("I found multiple matches.")
        for i, m in enumerate(matches, 1):
            speak(f"{i}. {get_display_name(apps[m])}")

        speak("Please say the number of the app you want to open, or repeat the app name.")
        choice = listen_for_command()

        if not choice:
            speak("Cancelled.")
            return

        num_choice = spoken_to_number(choice, max_choice=len(matches))
        if num_choice and 1 <= num_choice <= len(matches):
            selected = matches[num_choice - 1]
            speak(f"Opening {get_display_name(apps[selected])}")
            subprocess.run(["open", "-a", apps[selected]])
            return

        choice_clean = re.sub(r'[^\w\s]', ' ', choice).strip()
        for m in matches:
            if choice_clean in m or choice_clean in get_display_name(apps[m]).lower():
                speak(f"Opening {get_display_name(apps[m])}")
                subprocess.run(["open", "-a", apps[m]])
                return

        disp_names = [get_display_name(apps[m]).lower() for m in matches]
        close = difflib.get_close_matches(choice_clean, disp_names, n=1, cutoff=0.6)
        if close:
            idx = disp_names.index(close[0])
            selected = matches[idx]
            speak(f"Opening {get_display_name(apps[selected])}")
            subprocess.run(["open", "-a", apps[selected]])
            return

        speak("Could not resolve the choice. Cancelled.")
        return

    speak("Application not found!")

if __name__ == "__main__":
    spoken_app = listen_for_command()
    if spoken_app:
        if spoken_app.startswith("open "):
            spoken_app = spoken_app.replace("open ", "").strip()
        open_app(spoken_app)
