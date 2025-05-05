import os
import re
import json
import random
from typing import List, Dict


class InterviewManager:
    """Manager for the interview process."""

    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        self.questions = []
        self.asked_questions = set()  # Keep track of questions we've already asked
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "feedback"), exist_ok=True)

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
        # Try both possible filename patterns
        possible_filenames = [
            self.sanitize_filename(f"{job_position}_report.txt"),
            self.sanitize_filename(f"{job_position}_report.md"),
            self.sanitize_filename(f"{job_position}_questions.md")
        ]

        file_path = None
        for filename in possible_filenames:
            path = os.path.join(self.output_dir, filename)
            if os.path.exists(path):
                file_path = path
                break

        if not file_path:
            print(f"Questions file not found for position: {job_position}")
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse questions from markdown
            # Try to match both numbered list (1. Question) and bullet point lists (- Question)
            numbered_pattern = re.compile(r'^\d+\.\s+(.+)$', re.MULTILINE)
            bullet_pattern = re.compile(r'^[-*]\s+(.+)$', re.MULTILINE)

            numbered_matches = numbered_pattern.findall(content)
            bullet_matches = bullet_pattern.findall(content)

            # Use whichever pattern found more matches
            if len(numbered_matches) >= len(bullet_matches):
                self.questions = numbered_matches
            else:
                self.questions = bullet_matches

            # Reset asked questions
            self.asked_questions = set()

            print(f"Loaded {len(self.questions)} questions from {file_path}")
            return len(self.questions) > 0
        except Exception as e:
            print(f"Error loading questions: {e}")
            return False

    def get_random_question(self):
        """Get a random question that hasn't been asked yet."""
        if not self.questions:
            return None

        # Create a list of available questions (not yet asked)
        available_questions = [q for i, q in enumerate(self.questions)
                               if i not in self.asked_questions]

        if not available_questions:
            print("All questions have been asked!")
            return None

        # Select a random question from available ones
        question = random.choice(available_questions)

        # Find the index of this question in the original list to track it
        question_index = self.questions.index(question)
        self.asked_questions.add(question_index)

        return question

    def save_company_report(self, content, company):
        """Save the company research report."""
        file_name = self.sanitize_filename(f"{company}_report.md")
        file_path = os.path.join(self.output_dir, file_name)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Company report saved to {file_path}")
        return file_path

    def save_interviewer_report(self, content, interviewer):
        """Save the interviewer research report."""
        file_name = self.sanitize_filename(f"{interviewer}_report.md")
        file_path = os.path.join(self.output_dir, file_name)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Interviewer report saved to {file_path}")
        return file_path

    def save_questions(self, content, job_position):
        """Save the interview questions."""
        file_name = self.sanitize_filename(f"{job_position}_questions.md")
        file_path = os.path.join(self.output_dir, file_name)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Questions saved to {file_path}")
        return file_path

    def save_feedback(self, question_num, question, answer, feedback):
        """Save feedback for a question."""
        feedback_dir = os.path.join(self.output_dir, "feedback")
        os.makedirs(feedback_dir, exist_ok=True)

        file_name = f"question_{question_num}_feedback.md"
        file_path = os.path.join(feedback_dir, file_name)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# Question {question_num}\n\n")
            f.write(f"**Question:** {question}\n\n")
            f.write(f"**Your Answer:**\n\n{answer}\n\n")
            f.write(f"**Feedback:**\n\n{feedback}\n")

        return file_path
