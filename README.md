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
- [ ] Daily reports with detailed breakdowns
- [ ] Activity patterns and trends
- [ ] Productivity metrics and insights

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

2. Install dependencies (to be added)
```bash
pip install -r requirements.txt
```

3. Run the application (to be implemented)
```bash
python screenshot_taker.py
python image_processor.py
```

## Usage

Detailed usage instructions will be added as features are implemented.

## Contributing

Guidelines for contributing will be added as the project develops.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Roadmap

1. Phase 1: Core Screenshot Analysis
   - Basic screenshot capture
   - Local storage implementation
   - Multi-screen detection

2. Phase 2: Time Tracking
   - Daily report generation
   - Time breakdown analytics
   - Activity patterns

3. Phase 3: Productivity Features
   - Screen usage analysis
   - Application tracking
   - Productivity metrics

4. Phase 4: Company Questions Integration
   - Question framework
   - Response tracking
   - Analysis tools
