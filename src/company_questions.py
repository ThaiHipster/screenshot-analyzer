from typing import List, Dict, Optional
from datetime import datetime
import json
import os

class QuestionnaireSystem:
    def __init__(self, questions_file: str = "company_questions.json"):
        self.questions_file = questions_file
        self.questions = self._load_questions()
        self.responses_file = "question_responses.json"
        self.responses = self._load_responses()

    def _load_questions(self) -> List[Dict]:
        """Load questions from the JSON file or create default if not exists."""
        if os.path.exists(self.questions_file):
            with open(self.questions_file, 'r') as f:
                return json.load(f)
        return []

    def _load_responses(self) -> Dict:
        """Load previous responses from JSON file."""
        if os.path.exists(self.responses_file):
            with open(self.responses_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_questions(self):
        """Save questions to JSON file."""
        with open(self.questions_file, 'w') as f:
            json.dump(self.questions, f, indent=4)

    def _save_responses(self):
        """Save responses to JSON file."""
        with open(self.responses_file, 'w') as f:
            json.dump(self.responses, f, indent=4)

    def add_question(self, question: str, category: str, frequency: str = "daily") -> bool:
        """
        Add a new question to track.
        
        Args:
            question: The question text
            category: Category of the question (e.g., "Productivity", "Work-Life Balance")
            frequency: How often to ask ("daily", "weekly", "monthly")
        
        Returns:
            bool: True if question was added successfully
        """
        if not question or not category:
            return False
            
        new_question = {
            "id": len(self.questions) + 1,
            "question": question,
            "category": category,
            "frequency": frequency,
            "created_at": datetime.now().isoformat()
        }
        
        self.questions.append(new_question)
        self._save_questions()
        return True

    def remove_question(self, question_id: int) -> bool:
        """Remove a question by its ID."""
        for i, q in enumerate(self.questions):
            if q["id"] == question_id:
                self.questions.pop(i)
                self._save_questions()
                return True
        return False

    def get_questions(self, category: Optional[str] = None) -> List[Dict]:
        """Get all questions or filter by category."""
        if category:
            return [q for q in self.questions if q["category"].lower() == category.lower()]
        return self.questions

    def add_response(self, question_id: int, response: str) -> bool:
        """
        Add a response to a question.
        
        Args:
            question_id: The ID of the question being answered
            response: The response text
        
        Returns:
            bool: True if response was recorded successfully
        """
        # Find the question
        question = next((q for q in self.questions if q["id"] == question_id), None)
        if not question:
            return False

        # Create response entry
        response_entry = {
            "response": response,
            "timestamp": datetime.now().isoformat()
        }

        # Add to responses
        if str(question_id) not in self.responses:
            self.responses[str(question_id)] = []
        self.responses[str(question_id)].append(response_entry)
        
        self._save_responses()
        return True

    def get_responses(self, question_id: Optional[int] = None) -> Dict:
        """Get all responses or filter by question ID."""
        if question_id is not None:
            return {str(question_id): self.responses.get(str(question_id), [])}
        return self.responses

    def generate_report(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:
        """
        Generate a report of responses within the specified date range.
        
        Args:
            start_date: Optional ISO format date string for start of range
            end_date: Optional ISO format date string for end of range
        
        Returns:
            str: Formatted report of responses
        """
        report = "Company Questions Report\n"
        report += "======================\n\n"

        # Convert dates if provided
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None

        for question in self.questions:
            qid = str(question["id"])
            report += f"Question {qid}: {question['question']}\n"
            report += f"Category: {question['category']}\n"
            report += f"Frequency: {question['frequency']}\n\n"

            if qid in self.responses:
                responses = self.responses[qid]
                filtered_responses = []

                for resp in responses:
                    resp_date = datetime.fromisoformat(resp["timestamp"])
                    if start and resp_date < start:
                        continue
                    if end and resp_date > end:
                        continue
                    filtered_responses.append(resp)

                if filtered_responses:
                    report += "Responses:\n"
                    for resp in filtered_responses:
                        date = datetime.fromisoformat(resp["timestamp"]).strftime("%Y-%m-%d %H:%M")
                        report += f"- [{date}] {resp['response']}\n"
                else:
                    report += "No responses in specified date range.\n"
            else:
                report += "No responses yet.\n"
            
            report += "\n" + "-"*50 + "\n\n"

        return report 