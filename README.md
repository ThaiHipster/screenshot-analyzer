# Screenshot Analyzer

A powerful tool for analyzing screen time, productivity, and work patterns through automated screenshot analysis.

## Usage Instructions

1. Allow the script to access your screen
2. Run the script ```screenshot_taker.py```
3. Select the folder containing screenshots in the code
4. Wait for the analysis to complete
5. Save the results to a file

## Features

### Basic Features
- [x] Local screenshots 
- [x] deployment and data storage
- [x] Automated screenshot capture and analysis
- [x] Multi-screen support and monitoring
- [x] Screen usage tracking and analytics
- [x] Time spent per application/screen

#### Screen Management
- [x] View all connected screens
   - [x] detects all connected monitors
   - [x] Works on both macOS (using system_profiler) and Windows (using win32api if available)
- [x] Track active vs. inactive screens
   - [x] detects if the screen is active or inactive
- [x] Screen usage statistics
- [x] Multi-monitor support
   - [x] A specific monitor (using --monitor [ID])
   - [x] All monitors simultaneously (using --all-monitors)
   - [x] Just the active monitor (default behavior)

#### Time Tracking and Analysis
- [x] Smart system state detection
   - [x] Pause tracking when computer is closed/locked
   - [x] Auto-start tracking when computer is opened
   - [x] Dynamic day start time based on first computer usage
- [x] Daily reports with detailed breakdowns
- [x] Activity patterns and trends
- [x] Productivity metrics and insights
- [x] End-of-day analysis (configurable, default 5:00 PM)
- [x] System notifications
   - [x] Running status notification
   - [x] Analysis completion notification

#### 3. Productivity Analysis
- [ ] Screenshot-based activity tracking
- [ ] Application usage patterns
- [ ] Focus time vs. distraction metrics
- [ ] Productivity score calculations

#### 4. Company Questions Integration
- [ ] Built-in questionnaire system
- [ ] Progress tracking
- [ ] Response analysis
- [ ] Performance metrics

## Getting Started

### Prerequisites
- macOS (currently supported on darwin 24.2.0)
- Python (version 3.11.1)

### Installation
1. Clone the repository
```bash
git clone [repository-url]
cd screenshot-analyzer
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the application
```bash
python screenshot_taker.py
python image_processor.py
```

## Usage

### Time Tracking Features
1. The system automatically starts tracking when you open your computer for the first time each day
2. You'll receive a notification when the tracking system is running
3. The system automatically pauses when your computer is closed or locked
4. At 5:00 PM (configurable), the system will:
   - Generate a daily analysis report
   - Send a notification when the analysis is complete
   - Save detailed metrics about your day

## Contributing

Guidelines for contributing will be added as the project develops.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Roadmap

1. Phase 1: Core Screenshot Analysis ✓
   - Basic screenshot capture
   - Local storage implementation
   - Multi-screen detection

2. Phase 2: Time Tracking ✓
   - Daily report generation
   - Time breakdown analytics
   - Activity patterns
   - Smart system state detection
   - Notification system

3. Phase 3: Productivity Features
   - Screen usage analysis
   - Application tracking
   - Productivity metrics

4. Phase 4: Company Questions Integration
   - Question framework
   - Response tracking
   - Analysis tools
