# -*- coding: utf-8 -*-
"""
A Python script to create a calendar event with a sound alert on macOS.

This script prompts the user for an event title, date, time, and alert preference,
and then uses AppleScript to add the event with a sound alarm to the default Calendar app.
macOS will handle sending the notification and playing the sound at the specified time.
"""

import subprocess
import datetime

# MODIFICATION: Added a new parameter `alert_minutes_before` with a default value.
def set_calendar_reminder(summary, event_datetime, alert_minutes_before=5):
    """
    Creates a calendar event with a sound alarm using AppleScript.

    This version passes date components individually to avoid locale/format issues
    and adds a sound alarm to the created event.

    Args:
        summary (str): The title or description of the reminder.
        event_datetime (datetime.datetime): The date and time for the event.
        alert_minutes_before (int): How many minutes before the event to sound the alert.

    Returns:
        bool: True if the event was created successfully, False otherwise.
    """
    # Extract individual date and time components from the datetime object.
    year = event_datetime.year
    month = event_datetime.month
    day = event_datetime.day
    hour = event_datetime.hour
    minute = event_datetime.minute

    # MODIFICATION: The AppleScript is updated to add a sound alarm to the event.
    # The 'Basso' sound is a standard macOS alert sound.
    # The 'trigger interval' is negative to indicate minutes *before* the event starts.
    script = f'''
    tell application "Calendar"
        -- Create a new date object and set its properties individually.
        set theDate to current date
        set year of theDate to {year}
        set month of theDate to {month}
        set day of theDate to {day}
        set hours of theDate to {hour}
        set minutes of theDate to {minute}
        set seconds of theDate to 0

        activate
        -- Create the event in the first calendar.
        tell calendar 1
            set theEvent to make new event with properties {{summary:"{summary}", start date:theDate, end date:theDate}}
            
            -- This new block adds the sound alert to the event we just created.
            tell theEvent
                make new sound alarm with properties {{trigger interval:-{alert_minutes_before}, sound name:"Basso"}}
            end tell
        end tell
    end tell
    '''

    try:
        # The `osascript` command is used to run AppleScript from the command line.
        subprocess.run(['osascript', '-e', script], check=True, capture_output=True, text=True)
        print("\n✅ Success! Your reminder has been set in the Calendar app.")
        print(f" - Title: {summary}")
        print(f" - Time: {event_datetime.strftime('%Y-%m-%d %H:%M')}")
        # MODIFICATION: Confirmation message for the sound alert.
        print(f" - Alert: Sound alert set for {alert_minutes_before} minutes before.")
        return True
    except subprocess.CalledProcessError as e:
        # This block catches errors from the AppleScript execution.
        print("\n❌ Error: Failed to create the calendar event.")
        print("This could be a permissions issue.")
        print("Please ensure this script has permission to control the Calendar app.")
        print("Go to System Settings > Privacy & Security > Automation and check the box for your terminal.")
        print(f"\nDETAILS:\n{e.stderr}")
        return False
    except FileNotFoundError:
        # This error occurs if 'osascript' isn't found, which is highly unlikely on macOS.
        print("❌ Error: `osascript` command not found. This script can only be run on macOS.")
        return False

def main():
    """
    Main function to get user input and run the script.
    """
    print("--- Set a New Calendar Reminder ---")

    # Get reminder details from the user.
    summary = input("What do you want to be reminded about? ")
    date_str = input("Enter the date (YYYY-MM-DD): ")
    time_str = input("Enter the time (HH:MM in 24-hour format): ")
    
    # MODIFICATION: Get user input for the alert time.
    alert_minutes_str = input("How many minutes before should the alert sound? (e.g., 5): ")

    try:
        # Combine the user's date and time input into one string.
        datetime_str = f"{date_str} {time_str}"
        # Convert the string into a Python datetime object.
        event_datetime = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
        # Convert the alert minutes input to an integer.
        alert_minutes = int(alert_minutes_str)
    except ValueError:
        print("\n❌ Error: Invalid date, time, or minute format. Please run the script again.")
        return

    # MODIFICATION: Pass the new alert minutes value to the function.
    set_calendar_reminder(summary, event_datetime, alert_minutes)

if __name__ == '__main__':
    main()