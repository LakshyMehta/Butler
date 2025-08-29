
import subprocess
import datetime

def set_calendar_reminder(summary, event_datetime, alert_minutes_before=5):
    
    year = event_datetime.year
    month = event_datetime.month
    day = event_datetime.day
    hour = event_datetime.hour
    minute = event_datetime.minute

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
        tell calendar 1
            set theEvent to make new event with properties {{summary:"{summary}", start date:theDate, end date:theDate}}
            
            tell theEvent
                make new sound alarm with properties {{trigger interval:-{alert_minutes_before}, sound name:"Basso"}}
            end tell
        end tell
    end tell
    '''

    try:
        subprocess.run(['osascript', '-e', script], check=True, capture_output=True, text=True)
        print("\n Success! Your reminder has been set in the Calendar app.")
        print(f" - Title: {summary}")
        print(f" - Time: {event_datetime.strftime('%Y-%m-%d %H:%M')}")
        print(f" - Alert: Sound alert set for {alert_minutes_before} minutes before.")
        return True
    except subprocess.CalledProcessError as e:
        print("\nError: Failed to create the calendar event.")
        print("This could be a permissions issue.")
        print("Please ensure this script has permission to control the Calendar app.")
        print("Go to System Settings > Privacy & Security > Automation and check the box for your terminal.")
        print(f"\nDETAILS:\n{e.stderr}")
        return False
    except FileNotFoundError:
        print(" Error: `osascript` command not found. This script can only be run on macOS.")
        return False

def main():

    print("--- Set a New Calendar Reminder ---")

    summary = input("What do you want to be reminded about? ")
    date_str = input("Enter the date (YYYY-MM-DD): ")
    time_str = input("Enter the time (HH:MM in 24-hour format): ")
    
    alert_minutes_str = input("How many minutes before should the alert sound? (e.g., 5): ")

    try:
        datetime_str = f"{date_str} {time_str}"
        event_datetime = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
        alert_minutes = int(alert_minutes_str)
    except ValueError:
        print("\n Error: Invalid date, time, or minute format. Please run the script again.")
        return

    set_calendar_reminder(summary, event_datetime, alert_minutes)

if __name__ == '__main__':
    main()