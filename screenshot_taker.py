#!/usr/bin/env python3
import os
import time
import platform
from datetime import datetime
import argparse

def take_screenshot(output_dir='screenshots'):
    """
    Take a screenshot using the appropriate method based on the operating system.
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = os.path.join(output_dir, f'screenshot_{timestamp}.png')
    
    system = platform.system().lower()
    
    if system == 'darwin':  # macOS
        os.system(f'screencapture -x "{filename}"')
    elif system == 'windows':
        try:
            from PIL import ImageGrab
            screenshot = ImageGrab.grab()
            screenshot.save(filename)
        except ImportError:
            print("Please install Pillow: pip install Pillow")
            return False
    else:
        print(f"Unsupported operating system: {system}")
        return False
    
    print(f"Screenshot saved: {filename}")
    return True

def main():
    parser = argparse.ArgumentParser(description='Take screenshots at regular intervals')
    parser.add_argument('--interval', type=int, default=60,
                       help='Interval between screenshots in seconds (default: 60)')
    parser.add_argument('--output-dir', type=str, default='screenshots',
                       help='Directory to save screenshots (default: screenshots)')
    args = parser.parse_args()

    print(f"Starting screenshot capture every {args.interval} seconds...")
    print(f"Screenshots will be saved in: {os.path.abspath(args.output_dir)}")
    print("Press Ctrl+C to stop")

    try:
        while True:
            if not take_screenshot(args.output_dir):
                break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nScreenshot capture stopped by user")

if __name__ == '__main__':
    main() 