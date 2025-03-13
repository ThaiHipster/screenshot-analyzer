import os
import base64
from datetime import datetime
import json
from typing import List, Dict
import openai
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TimeStudyAnalyzer:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("Please set OPENAI_API_KEY in your .env file")
        
        openai.api_key = self.api_key
        self.data_folder = "data"
        self.supported_formats = ('.png', '.jpg', '.jpeg')
        
    def encode_image(self, image_path: str) -> str:
        """Convert image to base64 string."""
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

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
            
            # Fallback to filename (format: @screenshot_YYYYMMDDHHMMSS.png)
            filename = os.path.basename(image_path)
            timestamp_str = filename.split('@screenshot_')[1].split('.')[0]
            return datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')
        except:
            # If all fails, use file modification time
            return datetime.fromtimestamp(os.path.getmtime(image_path))

    def analyze_image(self, image_path: str) -> Dict:
        """Analyze a single image using ChatGPT Vision API."""
        base64_image = self.encode_image(image_path)
        timestamp = self.get_image_timestamp(image_path)

        try:
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-4.5-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this screenshot and tell me what activities are being performed. Focus on: 1) Main activity 2) Any applications or software visible 3) Estimated level of focus/productivity. Provide a structured response."
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
                "analysis": response.choices[0].message.content
            }

        except Exception as e:
            return {
                "timestamp": timestamp.isoformat(),
                "error": str(e)
            }

    def analyze_folder(self, limit=None) -> List[Dict]:
        """
        Analyze screenshots in the data folder.
        
        Args:
            limit: Optional integer to limit the number of images processed
        """
        results = []
        
        # Get all image files from data folder
        image_files = [
            f for f in os.listdir(self.data_folder)
            if f.lower().endswith(self.supported_formats)
        ]
        
        # Sort by timestamp
        image_files.sort()
        
        # Apply limit if specified
        if limit is not None:
            image_files = image_files[:limit]
        
        for image_file in image_files:
            image_path = os.path.join(self.data_folder, image_file)
            result = self.analyze_image(image_path)
            results.append(result)
            
        return results

    def generate_report(self, analyses: List[Dict]) -> str:
        """Generate a time study report from the analyses."""
        if not analyses:
            return "No analyses to report."

        report = "Time Study Analysis Report\n"
        report += "========================\n\n"

        for analysis in analyses:
            timestamp = datetime.fromisoformat(analysis['timestamp'])
            report += f"Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            report += "-" * 50 + "\n"
            
            if 'error' in analysis:
                report += f"Error analyzing image: {analysis['error']}\n"
            else:
                report += f"{analysis['analysis']}\n"
            
            report += "\n"

        return report

def main():
    analyzer = TimeStudyAnalyzer()
    
    print("Starting time study analysis...")
    # Only analyze the first image
    analyses = analyzer.analyze_folder(limit=1)
    
    # Generate and save report
    report = analyzer.generate_report(analyses)
    
    # Save detailed JSON results
    with open('time_study_results.json', 'w') as f:
        json.dump(analyses, f, indent=2)
    
    # Save human-readable report
    with open('time_study_report.txt', 'w') as f:
        f.write(report)
    
    print("Analysis complete! Check time_study_report.txt for the detailed report.")

if __name__ == "__main__":
    main()