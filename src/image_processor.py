#!/usr/bin/env python3
import os
import base64
from datetime import datetime
from typing import List, Dict, Tuple
import openai
from PIL import Image
from dotenv import load_dotenv
import io
import json

# Load environment variables
load_dotenv()

# Base directories
DATA_DIR = "data"
REPORTS_DIR = "reports"

def get_daily_folder(date_str=None):
    """
    Get the folder path for a specific day's data.
    If date_str is None, uses current day.
    """
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    daily_dir = os.path.join(DATA_DIR, date_str)
    return daily_dir

def get_screenshots_dir(date_str=None):
    """
    Get the screenshots directory for a specific day.
    """
    daily_dir = get_daily_folder(date_str)
    return os.path.join(daily_dir, "screenshots")

def process_screenshots(date_str=None, limit=5):
    """
    Process screenshots for a specific day.
    If date_str is None, processes current day's screenshots.
    """
    analyzer = OptimizedTimeStudyAnalyzer()
    
    print("Starting optimized time study analysis...")
    print("Analyzing screenshots...")
    analyses = analyzer.analyze_folder(date_str, limit=limit)
    
    if not analyses:
        print("No screenshots found to analyze.")
        return
    
    # Get the reports directory for the day
    reports_dir = analyzer.get_reports_folder(date_str)
    
    # Generate and save report
    report = analyzer.generate_report(analyses)
    
    # Generate application usage table
    app_usage_table = analyzer.generate_application_usage_table(analyses)
    
    # Save detailed JSON results
    with open(os.path.join(reports_dir, 'optimized_time_study_results.json'), 'w') as f:
        json.dump(analyses, f, indent=2)
    
    # Save human-readable report
    with open(os.path.join(reports_dir, 'optimized_time_study_report.txt'), 'w') as f:
        f.write(report)
    
    with open(os.path.join(reports_dir, 'summarized_time_study_report.txt'), 'w') as f:
        f.write(app_usage_table)

    print("Analysis complete! Reports have been saved to:", reports_dir)

def generate_time_study_report(date_str=None):
    """
    Generate time study report for a specific day.
    """
    daily_dir = get_daily_folder(date_str)
    report_path = os.path.join(daily_dir, "reports", "time_study_report.txt")
    
    # ... existing code ...

class OptimizedTimeStudyAnalyzer:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("Please set OPENAI_API_KEY in your .env file")
        
        openai.api_key = self.api_key
        self.supported_formats = ('.png', '.jpg', '.jpeg')
        
        # Image optimization parameters
        self.max_dimension = 800  # Maximum width or height
        self.jpeg_quality = 85    # JPEG quality (1-100)
        
    def optimize_image(self, image_path: str) -> Tuple[str, int, int]:
        """
        Optimize image by:
        1. Resizing to reasonable dimensions while maintaining aspect ratio
        2. Converting to JPEG with reduced quality
        3. Converting to base64
        
        Returns:
        - base64 string of optimized image
        - new width
        - new height
        """
        with Image.open(image_path) as img:
            # Convert to RGB if necessary (in case of PNG with alpha channel)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Calculate new dimensions while maintaining aspect ratio
            width, height = img.size
            if width > self.max_dimension or height > self.max_dimension:
                if width > height:
                    new_width = self.max_dimension
                    new_height = int(height * (self.max_dimension / width))
                else:
                    new_height = self.max_dimension
                    new_width = int(width * (self.max_dimension / height))
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save optimized image to bytes buffer
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=self.jpeg_quality, optimize=True)
            
            # Get base64 string
            base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return base64_image, img.size[0], img.size[1]

    def get_image_timestamp(self, image_path: str) -> datetime:
        """Extract timestamp from image metadata or filename."""
        try:
            # First try to get from image metadata
            with Image.open(image_path) as img:
                exif = img._getexif()
                if exif:
                    for tag_id in exif:
                        if tag_id in Image.TAGS and Image.TAGS[tag_id] == 'DateTime':
                            return datetime.strptime(exif[tag_id], '%Y:%m:%d %H:%M:%S')
            
            # Fallback to filename (format: screenshot_YYYYMMDDHHMMSS.png)
            filename = os.path.basename(image_path)
            timestamp_str = filename.split('screenshot_')[1].split('_')[0]
            return datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')
        except:
            # If all fails, use file modification time
            return datetime.fromtimestamp(os.path.getmtime(image_path))

    def analyze_image(self, image_path: str) -> Dict:
        """Analyze a single image using ChatGPT Vision API with optimized image."""
        timestamp = self.get_image_timestamp(image_path)
        
        try:
            # Optimize image before sending to API
            base64_image, width, height = self.optimize_image(image_path)
            original_size = os.path.getsize(image_path)
            optimized_size = len(base64.b64decode(base64_image))
            
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyze this screenshot and provide a detailed assessment focusing on:
1) Main activity and purpose
2) Applications or software visible
3) Estimated level of focus/productivity
4) AI Integration potential (Low/Medium/High)
5) Automation potential (Low/Medium/High)
6) Task complexity score (1-3, where 3 is most complex)

For AI Integration and Automation, consider:
- Data processing requirements
- Decision-making complexity
- Pattern recognition needs
- Repetitive task potential
- Integration with existing AI tools

Provide a structured response with clear sections."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )

            return {
                "timestamp": timestamp.isoformat(),
                "analysis": response.choices[0].message.content,
                "optimization_stats": {
                    "original_size_kb": original_size / 1024,
                    "optimized_size_kb": optimized_size / 1024,
                    "size_reduction_percent": ((original_size - optimized_size) / original_size) * 100,
                    "final_dimensions": f"{width}x{height}"
                }
            }

        except Exception as e:
            return {
                "timestamp": timestamp.isoformat(),
                "error": str(e)
            }
            
    def get_data_folder(self, date_str=None):
        """Get the appropriate data folder for the given date."""
        return get_screenshots_dir(date_str)
        
    def get_reports_folder(self, date_str=None):
        """Get the reports folder for the given date."""
        daily_dir = get_daily_folder(date_str)
        reports_dir = os.path.join(daily_dir, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        return reports_dir

    def analyze_folder(self, date_str=None, limit=None) -> List[Dict]:
        """
        Analyze screenshots in the data folder.
        
        Args:
            date_str: Optional date string in YYYY-MM-DD format
            limit: Optional integer to limit the number of images processed
        """
        results = []
        data_folder = self.get_data_folder(date_str)
        
        if not os.path.exists(data_folder):
            print(f"No screenshots directory found for date: {date_str or 'today'}")
            return results
        
        # Get all image files from data folder
        image_files = [
            f for f in os.listdir(data_folder)
            if f.lower().endswith(self.supported_formats)
        ]
        
        # Sort by timestamp
        image_files.sort()
        
        # Apply limit if specified
        if limit is not None:
            image_files = image_files[:limit]
        
        for image_file in image_files:
            image_path = os.path.join(data_folder, image_file)
            result = self.analyze_image(image_path)
            results.append(result)
            print(f"Processed {image_file}")
            if 'optimization_stats' in result:
                stats = result['optimization_stats']
                print(f"Size reduction: {stats['size_reduction_percent']:.1f}% " +
                      f"({stats['original_size_kb']:.1f}KB → {stats['optimized_size_kb']:.1f}KB)")
            
        return results

    def generate_report(self, analyses: List[Dict]) -> str:
        """Generate a time study report from the analyses."""
        if not analyses:
            return "No analyses to report."

        report = "Time Study Analysis Report (Optimized)\n"
        report += "================================\n\n"

        total_original_size = 0
        total_optimized_size = 0

        for analysis in analyses:
            timestamp = datetime.fromisoformat(analysis['timestamp'])
            report += f"Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            report += "-" * 50 + "\n"
            
            if 'error' in analysis:
                report += f"Error analyzing image: {analysis['error']}\n"
            else:
                report += f"{analysis['analysis']}\n"
                if 'optimization_stats' in analysis:
                    stats = analysis['optimization_stats']
                    total_original_size += stats['original_size_kb']
                    total_optimized_size += stats['optimized_size_kb']
                    report += f"\nImage Stats:\n"
                    report += f"Dimensions: {stats['final_dimensions']}\n"
                    report += f"Size Reduction: {stats['size_reduction_percent']:.1f}%\n"
            
            report += "\n"

        if total_original_size > 0:
            report += "Overall Optimization Summary\n"
            report += "=========================\n"
            report += f"Total Original Size: {total_original_size:.1f}KB\n"
            report += f"Total Optimized Size: {total_optimized_size:.1f}KB\n"
            report += f"Overall Size Reduction: {((total_original_size - total_optimized_size) / total_original_size) * 100:.1f}%\n"

        return report
        
    def generate_application_usage_table(self, analyses: List[Dict]) -> str:
        """
        Generate a structured table showing application usage statistics with AI metrics.
        """
        if not analyses:
            return "No analyses to generate application usage table."
            
        # Dictionary to store application data
        # Structure: {app_name: {'use_case': str, 'count': int, 'time_spent': float, 'ai_integration': str, 'automation_potential': str, 'complexity_score': int}}
        app_data = {}
        
        # Process each analysis to extract application information
        for i, analysis in enumerate(analyses):
            if 'error' in analysis or 'analysis' not in analysis:
                continue
                
            # Extract timestamp for time calculation
            current_timestamp = datetime.fromisoformat(analysis['timestamp'])
            
            # Calculate time difference if not the first entry
            time_spent = 0
            if i > 0 and 'timestamp' in analyses[i-1]:
                prev_timestamp = datetime.fromisoformat(analyses[i-1]['timestamp'])
                time_diff = (current_timestamp - prev_timestamp).total_seconds() / 60  # in minutes
                time_spent = time_diff
            
            # Parse the analysis text to identify applications and AI metrics
            analysis_text = analysis['analysis'].lower()
            lines = analysis_text.split('\n')
            
            # Initialize variables
            app_name = "Unknown"
            use_case = "Unknown"
            ai_integration = "Low"
            automation_potential = "Low"
            complexity_score = 1
            
            # Extract AI metrics and application info
            for line in lines:
                if "ai integration" in line:
                    if "high" in line:
                        ai_integration = "High"
                    elif "medium" in line:
                        ai_integration = "Medium"
                elif "automation potential" in line:
                    if "high" in line:
                        automation_potential = "High"
                    elif "medium" in line:
                        automation_potential = "Medium"
                elif "complexity score" in line and any(str(i) in line for i in range(1, 4)):
                    for i in range(1, 4):
                        if str(i) in line:
                            complexity_score = i
                            break
                
                # Look for application mentions
                for common_app in ["Chrome", "Firefox", "VS Code", "Visual Studio", "Word", 
                                  "Excel", "PowerPoint", "Outlook", "Teams", "Zoom", 
                                  "Slack", "Terminal", "Command Prompt", "Notepad", 
                                  "Photoshop", "Illustrator", "InDesign", "Figma"]:
                    if common_app.lower() in line:
                        app_name = common_app
                        
                        # Determine use case
                        if any(keyword in line for keyword in ["coding", "programming", "development"]):
                            use_case = "Code Development"
                        elif any(keyword in line for keyword in ["browsing", "web"]):
                            use_case = "Web Browsing"
                        elif any(keyword in line for keyword in ["meeting", "call"]):
                            use_case = "Meetings"
                        elif any(keyword in line for keyword in ["design", "drawing"]):
                            use_case = "Design Work"
                        elif any(keyword in line for keyword in ["writing", "document"]):
                            use_case = "Documentation"
                        elif any(keyword in line for keyword in ["analysis", "data"]):
                            use_case = "Data Analysis"
            
            # Update the application data dictionary
            if app_name not in app_data:
                app_data[app_name] = {
                    'use_case': use_case,
                    'count': 1,
                    'time_spent': time_spent,
                    'ai_integration': ai_integration,
                    'automation_potential': automation_potential,
                    'complexity_score': complexity_score
                }
            else:
                app_data[app_name]['count'] += 1
                app_data[app_name]['time_spent'] += time_spent
                # Update metrics if higher values are found
                if ai_integration == "High" or (ai_integration == "Medium" and app_data[app_name]['ai_integration'] == "Low"):
                    app_data[app_name]['ai_integration'] = ai_integration
                if automation_potential == "High" or (automation_potential == "Medium" and app_data[app_name]['automation_potential'] == "Low"):
                    app_data[app_name]['automation_potential'] = automation_potential
                app_data[app_name]['complexity_score'] = max(app_data[app_name]['complexity_score'], complexity_score)
        
        # Generate the table
        table = "Application Usage Analysis\n"
        table += "========================\n\n"
        
        # Table header
        header = "{:<20} {:<25} {:<15} {:<20} {:<15} {:<20} {:<15}\n"
        table += header.format(
            "Application",
            "Use Case",
            "Times Used",
            "Time Spent (min)",
            "AI Integration",
            "Automation Potential",
            "Complexity Score"
        )
        table += "-" * 110 + "\n"
        
        # Table rows
        row_format = "{:<20} {:<25} {:<15} {:<20.2f} {:<15} {:<20} {:<15}\n"
        for app_name, data in sorted(app_data.items(), key=lambda x: x[1]['time_spent'], reverse=True):
            table += row_format.format(
                app_name,
                data['use_case'],
                data['count'],
                data['time_spent'],
                data['ai_integration'],
                data['automation_potential'],
                data['complexity_score']
            )
        
        # Table footer with totals
        table += "-" * 110 + "\n"
        total_count = sum(data['count'] for data in app_data.values())
        total_time = sum(data['time_spent'] for data in app_data.values())
        table += row_format.format(
            "TOTAL",
            "",
            total_count,
            total_time,
            "",
            "",
            ""
        )
        
        return table

if __name__ == "__main__":
    process_screenshots()