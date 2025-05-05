import os
import re
import json
from typing import List, Dict


class InterviewManager:
    """Manager for the interview process."""

    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        self.questions = []
        self.current_index = 0
        os.makedirs(output_dir, exist_ok=True)

    def sanitize_filename(self, name):
        """Remove or replace invalid characters for filenames."""
        # Replace problematic characters with underscore
        sanitized = re.sub(r'[\\/*?:"<>|,]', '_', str(name))
        # Remove extra spaces and trim if too long
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        # Limit maximum filename length
        max_length = 100
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        return sanitized

    def load_questions(self, job_position):
        """Load questions from the markdown file."""
        file_name = self.sanitize_filename(f"{job_position}_report.txt")
        file_path = os.path.join(self.output_dir, file_name)

        if not os.path.exists(file_path):
            print(f"Questions file not found: {file_path}")
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse questions from markdown
            lines = content.split('\n')
            for line in lines:
                if line.startswith('- ') or line.startswith('* '):
                    self.questions.append(line[2:].strip())

            print(f"Loaded {len(self.questions)} questions")
            return len(self.questions) > 0
        except Exception as e:
            print(f"Error loading questions: {e}")
            return False

    def get_next_question(self):
        """Get the next question for the interview."""
        if not self.questions:
            return None

        if self.current_index >= len(self.questions):
            return None

        question = self.questions[self.current_index]
        self.current_index += 1
        return question

    def save_company_report(self, content, company):
        """Save the company research report."""
        file_name = self.sanitize_filename(f"{company}_report.txt")
        file_path = os.path.join(self.output_dir, file_name)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Company report saved to {file_path}")

    def save_interviewer_report(self, content, interviewer):
        """Save the interviewer research report."""
        file_name = self.sanitize_filename(f"{interviewer}_report.txt")
        file_path = os.path.join(self.output_dir, file_name)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Interviewer report saved to {file_path}")

    def save_questions(self, content, job_position):
        """Save the interview questions."""
        file_name = self.sanitize_filename(f"{job_position}_report.txt")
        file_path = os.path.join(self.output_dir, file_name)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Questions saved to {file_path}")
