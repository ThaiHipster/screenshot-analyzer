#!/usr/bin/env python3
from company_questions import QuestionnaireSystem
import argparse
from datetime import datetime, timedelta

def main():
    parser = argparse.ArgumentParser(description='Company Questions Management System')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Add question
    add_parser = subparsers.add_parser('add', help='Add a new question')
    add_parser.add_argument('question', help='The question text')
    add_parser.add_argument('category', help='Question category')
    add_parser.add_argument('--frequency', choices=['daily', 'weekly', 'monthly'], 
                           default='daily', help='How often to ask the question')

    # Remove question
    remove_parser = subparsers.add_parser('remove', help='Remove a question')
    remove_parser.add_argument('question_id', type=int, help='ID of the question to remove')

    # List questions
    list_parser = subparsers.add_parser('list', help='List all questions')
    list_parser.add_argument('--category', help='Filter by category')

    # Add response
    respond_parser = subparsers.add_parser('respond', help='Add a response to a question')
    respond_parser.add_argument('question_id', type=int, help='ID of the question')
    respond_parser.add_argument('response', help='Your response')

    # Generate report
    report_parser = subparsers.add_parser('report', help='Generate a report')
    report_parser.add_argument('--days', type=int, help='Number of days to include in report')
    report_parser.add_argument('--start', help='Start date (YYYY-MM-DD)')
    report_parser.add_argument('--end', help='End date (YYYY-MM-DD)')

    args = parser.parse_args()
    qs = QuestionnaireSystem()

    if args.command == 'add':
        if qs.add_question(args.question, args.category, args.frequency):
            print(f"Added question successfully")
        else:
            print("Failed to add question")

    elif args.command == 'remove':
        if qs.remove_question(args.question_id):
            print(f"Removed question {args.question_id}")
        else:
            print(f"Question {args.question_id} not found")

    elif args.command == 'list':
        questions = qs.get_questions(args.category)
        if not questions:
            print("No questions found")
            return

        print("\nCompany Questions:")
        print("=================")
        for q in questions:
            print(f"\nID: {q['id']}")
            print(f"Question: {q['question']}")
            print(f"Category: {q['category']}")
            print(f"Frequency: {q['frequency']}")
            print(f"Created: {q['created_at']}")

    elif args.command == 'respond':
        if qs.add_response(args.question_id, args.response):
            print("Response recorded successfully")
        else:
            print(f"Failed to record response for question {args.question_id}")

    elif args.command == 'report':
        start_date = None
        end_date = None

        if args.days:
            end_date = datetime.now().isoformat()
            start_date = (datetime.now() - timedelta(days=args.days)).isoformat()
        else:
            if args.start:
                start_date = datetime.strptime(args.start, "%Y-%m-%d").isoformat()
            if args.end:
                end_date = datetime.strptime(args.end, "%Y-%m-%d").isoformat()

        report = qs.generate_report(start_date, end_date)
        print(report)

    else:
        parser.print_help()

if __name__ == "__main__":
    main() 