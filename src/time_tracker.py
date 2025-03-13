#!/usr/bin/env python3
import time
import datetime
import subprocess
import platform
import plyer
import os
import json

# Configuration
ANALYSIS_TIME = "17:00"  # Default analysis time (5:00 PM)

# Base directories
DATA_DIR = "data"
REPORTS_DIR = "reports"

def get_daily_folder(date_str=None):
    """
    Get the folder path for a specific day's data.
    If date_str is None, uses current day.
    """
    if date_str is None:
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    daily_dir = os.path.join(DATA_DIR, date_str)
    return daily_dir

def get_activity_file(date_str=None):
    """
    Get the activity file path for a specific day.
    """
    daily_dir = get_daily_folder(date_str)
    return os.path.join(daily_dir, "activity.json")

# Check if the system is active
def is_system_active():
    system = platform.system().lower()
    if system == 'darwin':
        result = subprocess.run(['ioreg', '-n', 'IODisplayWrangler', '|', 'grep', '-i', 'IOPowerManagement'], capture_output=True, text=True)
        return 'DevicePowerState"=4' in result.stdout
    elif system == 'windows':
        import ctypes
        user32 = ctypes.windll.User32
        return user32.GetForegroundWindow() != 0
    return True

# Notify user
def notify(title, message):
    """Send a system notification with fallback options."""
    system = platform.system().lower()
    
    if system == 'darwin':  # macOS specific notification
        try:
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(["osascript", "-e", script], check=True)
            print(f"Notification sent: {title} - {message}")
            return
        except Exception as e:
            print(f"macOS notification error: {e}")
    
    # Try plyer as fallback for other systems
    try:
        from plyer import notification
        notification.notify(
            title=title,
            message=message,
            app_name="Screenshot Analyzer"
        )
        return
    except Exception as e:
        print(f"Plyer notification error: {e}")
    
    # Last resort: just print to console
    print(f"Notification (console only): {title} - {message}")

# Main tracking loop
def main():
    notify("Screenshot Analyzer", "Time tracking system is running.")
    day_started = False
    start_time = None

    while True:
        if is_system_active():
            if not day_started:
                start_time = datetime.datetime.now()
                day_started = True
                print(f"Day started at {start_time}")

            current_time = datetime.datetime.now().strftime("%H:%M")
            if current_time == ANALYSIS_TIME:
                perform_daily_analysis(start_time)
                notify("Screenshot Analyzer", "Daily analysis completed.")
                break
        else:
            print("System inactive, pausing tracking...")

        time.sleep(60)

# Perform daily analysis
def perform_daily_analysis(start_time):
    """
    Perform daily analysis and save results to the appropriate daily folder.
    """
    end_time = datetime.datetime.now()
    duration = end_time - start_time
    print(f"Analysis from {start_time} to {end_time}, total duration: {duration}")
    
    # Get today's folder
    daily_dir = get_daily_folder()
    reports_dir = os.path.join(daily_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    # Save analysis results
    report_file = os.path.join(reports_dir, "daily_analysis.txt")
    with open(report_file, 'w') as f:
        f.write(f"Daily Analysis Report\n")
        f.write(f"===================\n\n")
        f.write(f"Start Time: {start_time}\n")
        f.write(f"End Time: {end_time}\n")
        f.write(f"Total Duration: {duration}\n")
    
    print(f"Daily analysis report saved to: {report_file}")

def track_time(date_str=None):
    """
    Track time based on activity data for a specific day.
    """
    activity_file = get_activity_file(date_str)
    if not os.path.exists(activity_file):
        print(f"No activity data found for date: {date_str or 'today'}")
        return
    
    daily_dir = get_daily_folder(date_str)
    reports_dir = os.path.join(daily_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    try:
        with open(activity_file, 'r') as f:
            activities = json.load(f)
        
        # Generate time tracking report
        report_file = os.path.join(reports_dir, "time_tracking_report.txt")
        with open(report_file, 'w') as f:
            f.write("Time Tracking Report\n")
            f.write("===================\n\n")
            
            for activity in activities:
                f.write(f"Time: {activity['timestamp']}\n")
                for monitor in activity['monitors']:
                    status = "Active" if monitor['active'] else "Inactive"
                    f.write(f"  Monitor {monitor['name']}: {status}\n")
                f.write("\n")
        
        print(f"Time tracking report saved to: {report_file}")
        
    except Exception as e:
        print(f"Error generating time tracking report: {e}")

if __name__ == "__main__":
    main()
