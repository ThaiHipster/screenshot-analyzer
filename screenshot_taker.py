#!/usr/bin/env python3
import os
import time
import platform
from datetime import datetime
import argparse
import json
import subprocess

# For screen activity tracking
ACTIVITY_LOG_FILE = "screen_activity.json"

def get_monitors():
    """
    Get information about connected monitors.
    Returns a list of monitor information objects.
    """
    system = platform.system().lower()
    monitors = []
    
    if system == 'darwin':  # macOS
        try:
            # Get display information using system_profiler
            result = subprocess.run(
                ['system_profiler', 'SPDisplaysDataType', '-json'],
                capture_output=True, text=True, check=True
            )
            data = json.loads(result.stdout)
            
            # Extract monitor information
            for gpu in data.get('SPDisplaysDataType', []):
                for display in gpu.get('spdisplays_ndrvs', []):
                    resolution = display.get('spdisplays_resolution', 'Unknown')
                    name = display.get('_name', f"Display {len(monitors) + 1}")
                    monitors.append({
                        'id': len(monitors),
                        'name': name,
                        'resolution': resolution,
                        'active': True  # Assume all are active initially
                    })
        except (subprocess.SubprocessError, json.JSONDecodeError, KeyError) as e:
            print(f"Error getting monitor information: {e}")
            # Fallback to a default single monitor
            monitors = [{'id': 0, 'name': 'Main Display', 'active': True}]
    
    elif system == 'windows':
        try:
            # Use PyWin32 if available
            import win32api
            import win32con
            
            i = 0
            while True:
                try:
                    device = win32api.EnumDisplayDevices(None, i)
                    settings = win32api.EnumDisplaySettings(device.DeviceName, win32con.ENUM_CURRENT_SETTINGS)
                    monitors.append({
                        'id': i,
                        'name': device.DeviceName,
                        'resolution': f"{settings.PelsWidth}x{settings.PelsHeight}",
                        'active': (device.StateFlags & win32con.DISPLAY_DEVICE_ACTIVE) != 0
                    })
                    i += 1
                except Exception:
                    break
        except ImportError:
            print("For better Windows multi-monitor support, install PyWin32: pip install pywin32")
            # Fallback to a default single monitor
            monitors = [{'id': 0, 'name': 'Main Display', 'active': True}]
    
    # If no monitors were detected, at least return one default monitor
    if not monitors:
        monitors = [{'id': 0, 'name': 'Main Display', 'active': True}]
    
    return monitors

def detect_active_screen():
    """
    Attempt to detect which screen currently has focus/is active.
    This is a basic implementation and might need platform-specific improvements.
    """
    system = platform.system().lower()
    active_screen_id = 0  # Default to the first screen
    
    if system == 'darwin':
        try:
            # On macOS, we can try to get the position of the mouse cursor
            # and determine which screen contains it
            result = subprocess.run(
                ['osascript', '-e', 'tell application "System Events" to return position of mouse'],
                capture_output=True, text=True, check=True
            )
            # Result will be something like "100, 200"
            if result.stdout.strip():
                mouse_x, mouse_y = map(int, result.stdout.strip().split(', '))
                # Here you would determine which screen contains these coordinates
                # This would require additional logic to map coordinates to screens
        except subprocess.SubprocessError as e:
            print(f"Error detecting active screen: {e}")
    
    elif system == 'windows':
        try:
            import win32gui
            # Get the handle of the foreground window
            hwnd = win32gui.GetForegroundWindow()
            # Get the monitor that contains this window
            import win32api
            monitor = win32api.MonitorFromWindow(hwnd, 0)  # 0 = MONITOR_DEFAULTTONULL
            # Map this monitor to our list of monitors
            # This would require additional logic
        except ImportError:
            pass
    
    return active_screen_id

def update_screen_activity(monitors):
    """
    Update and save screen activity data.
    """
    activity_data = {}
    
    # Load existing data if available
    if os.path.exists(ACTIVITY_LOG_FILE):
        try:
            with open(ACTIVITY_LOG_FILE, 'r') as f:
                activity_data = json.load(f)
        except json.JSONDecodeError:
            activity_data = {}
    
    # Get current timestamp
    timestamp = datetime.now().isoformat()
    
    # Update activity for each monitor
    for monitor in monitors:
        monitor_id = str(monitor['id'])
        if monitor_id not in activity_data:
            activity_data[monitor_id] = {
                'name': monitor['name'],
                'activity': []
            }
        
        activity_data[monitor_id]['activity'].append({
            'timestamp': timestamp,
            'active': monitor['active']
        })
        
        # Limit the size of the activity log (keep last 1000 entries)
        if len(activity_data[monitor_id]['activity']) > 1000:
            activity_data[monitor_id]['activity'] = activity_data[monitor_id]['activity'][-1000:]
    
    # Save updated data
    with open(ACTIVITY_LOG_FILE, 'w') as f:
        json.dump(activity_data, f)

def take_screenshot(output_dir='screenshots', monitor_id=None, all_monitors=False):
    """
    Take a screenshot using the appropriate method based on the operating system.
    Can target a specific monitor or capture all monitors.
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get timestamp for filename
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    system = platform.system().lower()
    monitors = get_monitors()
    
    # Update which monitor is currently active
    active_monitor_id = detect_active_screen()
    for monitor in monitors:
        monitor['active'] = (monitor['id'] == active_monitor_id)
    
    # Update and save screen activity data
    update_screen_activity(monitors)
    
    # Determine which monitors to capture
    if monitor_id is not None:
        # Only capture the specified monitor
        monitors_to_capture = [m for m in monitors if m['id'] == monitor_id]
        if not monitors_to_capture:
            print(f"Monitor with ID {monitor_id} not found")
            return False
    elif all_monitors:
        # Capture all monitors
        monitors_to_capture = monitors
    else:
        # Default to capturing just the active monitor
        monitors_to_capture = [monitors[active_monitor_id]] if monitors else []
    
    if not monitors_to_capture:
        print("No monitors to capture")
        return False
    
    success = True
    
    for monitor in monitors_to_capture:
        # Generate filename with timestamp and monitor ID
        monitor_suffix = f"_monitor{monitor['id']}"
        filename = os.path.join(output_dir, f'screenshot_{timestamp}{monitor_suffix}.png')
        
        if system == 'darwin':  # macOS
            cmd = ['screencapture', '-x']
            
            if len(monitors) > 1 and monitor_id is not None:
                # The -D flag in screencapture specifies which display to capture
                # Note: Display IDs in macOS might not match our simple numbering
                cmd.extend(['-D', str(monitor['id'] + 1)])  # macOS typically numbers displays starting from 1
            
            cmd.append(filename)
            
            result = subprocess.run(cmd, capture_output=True)
            if result.returncode != 0:
                print(f"Error capturing screenshot for monitor {monitor['id']}: {result.stderr.decode()}")
                success = False
            else:
                print(f"Screenshot saved for monitor {monitor['id']}: {filename}")
        
        elif system == 'windows':
            try:
                from PIL import ImageGrab
                
                if len(monitors) > 1 and monitor_id is not None:
                    # For specific monitor capture on Windows, we'd need to get the monitor's bounds
                    # This is a simplified approach and might need refinement
                    try:
                        import win32api
                        device = win32api.EnumDisplayDevices(None, monitor['id'])
                        settings = win32api.EnumDisplaySettings(device.DeviceName, 0)
                        left = settings.PelsLeft
                        top = settings.PelsTop
                        width = settings.PelsWidth
                        height = settings.PelsHeight
                        bbox = (left, top, left + width, top + height)
                        screenshot = ImageGrab.grab(bbox=bbox)
                    except ImportError:
                        # Fallback to capturing the entire screen
                        screenshot = ImageGrab.grab()
                else:
                    # Capture all screens
                    screenshot = ImageGrab.grab(all_screens=True)
                
                screenshot.save(filename)
                print(f"Screenshot saved for monitor {monitor['id']}: {filename}")
            
            except ImportError:
                print("Please install Pillow: pip install Pillow")
                success = False
            except Exception as e:
                print(f"Error capturing screenshot for monitor {monitor['id']}: {e}")
                success = False
        else:
            print(f"Unsupported operating system: {system}")
            success = False
    
    return success

def generate_activity_report(output_file='screen_activity_report.html'):
    """
    Generate a simple HTML report of screen activity.
    """
    if not os.path.exists(ACTIVITY_LOG_FILE):
        print("No activity data available.")
        return False
    
    try:
        with open(ACTIVITY_LOG_FILE, 'r') as f:
            activity_data = json.load(f)
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Screen Activity Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #333; }
                .monitor { margin-bottom: 30px; }
                .active { color: green; }
                .inactive { color: red; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                tr:nth-child(even) { background-color: #f9f9f9; }
            </style>
        </head>
        <body>
            <h1>Screen Activity Report</h1>
        """
        
        for monitor_id, data in activity_data.items():
            html += f"""
            <div class="monitor">
                <h2>Monitor {monitor_id}: {data['name']}</h2>
                <table>
                    <tr>
                        <th>Timestamp</th>
                        <th>Status</th>
                    </tr>
            """
            
            for entry in reversed(data['activity'][:100]):  # Show last 100 entries
                status_class = "active" if entry['active'] else "inactive"
                status_text = "Active" if entry['active'] else "Inactive"
                html += f"""
                    <tr>
                        <td>{entry['timestamp']}</td>
                        <td class="{status_class}">{status_text}</td>
                    </tr>
                """
            
            html += """
                </table>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        with open(output_file, 'w') as f:
            f.write(html)
        
        print(f"Activity report generated: {output_file}")
        return True
    
    except Exception as e:
        print(f"Error generating activity report: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Take screenshots at regular intervals')
    parser.add_argument('--interval', type=int, default=60,
                       help='Interval between screenshots in seconds (default: 60)')
    parser.add_argument('--output-dir', type=str, default='screenshots',
                       help='Directory to save screenshots (default: screenshots)')
    parser.add_argument('--monitor', type=int, default=None,
                       help='Specific monitor ID to capture (default: active monitor)')
    parser.add_argument('--all-monitors', action='store_true',
                       help='Capture all monitors instead of just the active one')
    parser.add_argument('--list-monitors', action='store_true',
                       help='List all connected monitors and exit')
    parser.add_argument('--generate-report', action='store_true',
                       help='Generate a screen activity report and exit')
    parser.add_argument('--report-file', type=str, default='screen_activity_report.html',
                       help='File to save the screen activity report (default: screen_activity_report.html)')
    
    args = parser.parse_args()

    if args.list_monitors:
        monitors = get_monitors()
        print("Connected monitors:")
        for monitor in monitors:
            active_status = "ACTIVE" if monitor['active'] else "INACTIVE"
            print(f"  ID: {monitor['id']} - {monitor['name']} ({monitor['resolution']}) - {active_status}")
        return
    
    if args.generate_report:
        generate_activity_report(args.report_file)
        return

    print(f"Starting screenshot capture every {args.interval} seconds...")
    if args.monitor is not None:
        print(f"Capturing only monitor ID: {args.monitor}")
    elif args.all_monitors:
        print("Capturing all monitors")
    else:
        print("Capturing active monitor only")
    
    print(f"Screenshots will be saved in: {os.path.abspath(args.output_dir)}")
    print("Press Ctrl+C to stop")

    try:
        while True:
            if not take_screenshot(args.output_dir, args.monitor, args.all_monitors):
                break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nScreenshot capture stopped by user")

if __name__ == '__main__':
    main() 