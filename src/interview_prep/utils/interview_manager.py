import os
import re
import json
import random
from typing import List, Dict, Optional, Set


class InterviewManager:
    """Manager for the interview process."""

    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        self.questions: List[str] = []
        # Keep track of questions we've already asked
        self.asked_questions: Set[int] = set()
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "feedback"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, ".session"), exist_ok=True)

    def sanitize_filename(self, name: str) -> str:
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

    def load_questions(self, job_position: str) -> bool:
        """Load questions from the markdown file."""
        # Try both possible filename patterns
        possible_filenames = [
            self.sanitize_filename(f"{job_position}_questions.md"),
            self.sanitize_filename(f"{job_position}_report.md"),
            self.sanitize_filename(f"{job_position}_report.txt")
        ]

        file_path = None
        for filename in possible_filenames:
            path = os.path.join(self.output_dir, filename)
            if os.path.exists(path):
                file_path = path
                print(f"Found questions file: {path}")
                break

        if not file_path:
            print(f"Questions file not found for position: {job_position}")
            # List available files to help troubleshooting
            print(f"Files in {self.output_dir}:")
            for file in os.listdir(self.output_dir):
                if os.path.isfile(os.path.join(self.output_dir, file)):
                    print(f"  - {file}")
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse questions from markdown using different patterns
            # Try to match numbered list (1. Question), bullet points (- Question), and questions with headers or inside quotations
            numbered_pattern = re.compile(r'^\d+\.\s+(.+)$', re.MULTILINE)
            bullet_pattern = re.compile(r'^[-*]\s+(.+)$', re.MULTILINE)
            quoted_pattern = re.compile(
                r'["""]([^"""]+)["""]', re.MULTILINE)  # Match quoted questions

            # Find all matches
            numbered_matches = numbered_pattern.findall(content)
            bullet_matches = bullet_pattern.findall(content)
            quoted_matches = quoted_pattern.findall(content)

            # Log results for debugging
            print(f"Found {len(numbered_matches)} numbered questions")
            print(f"Found {len(bullet_matches)} bullet point questions")
            print(f"Found {len(quoted_matches)} quoted questions")

            # Use whichever pattern found more matches
            if len(numbered_matches) >= max(len(bullet_matches), len(quoted_matches)):
                self.questions = numbered_matches
            elif len(bullet_matches) >= len(quoted_matches):
                self.questions = bullet_matches
            else:
                self.questions = quoted_matches

            # Filter out empty questions and trim whitespace
            self.questions = [q.strip() for q in self.questions if q.strip()]

            # Reset asked questions
            self.asked_questions = set()

            print(f"Loaded {len(self.questions)} questions from {file_path}")
            return len(self.questions) > 0
        except Exception as e:
            print(f"Error loading questions: {e}")
            return False

    def get_random_question(self) -> Optional[str]:
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

    def get_all_questions(self) -> List[str]:
        """Get all loaded questions."""
        return self.questions

    def save_company_report(self, content: str, company: str) -> str:
        """Save the company research report."""
        file_name = self.sanitize_filename(f"{company}_report.md")
        file_path = os.path.join(self.output_dir, file_name)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Company report saved to {file_path}")
        return file_path

    def save_interviewer_report(self, content: str, interviewer: str) -> str:
        """Save the interviewer research report."""
        file_name = self.sanitize_filename(f"{interviewer}_report.md")
        file_path = os.path.join(self.output_dir, file_name)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Interviewer report saved to {file_path}")
        return file_path

    def save_questions(self, content: str, job_position: str) -> str:
        """Save the interview questions."""
        file_name = self.sanitize_filename(f"{job_position}_questions.md")
        file_path = os.path.join(self.output_dir, file_name)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Questions saved to {file_path}")
        return file_path

    def save_feedback(self, question_num: int, question: str, answer: str, feedback: str) -> str:
        """Save feedback for a question."""
        feedback_dir = os.path.join(self.output_dir, "feedback")
        os.makedirs(feedback_dir, exist_ok=True)

        file_name = f"question_{question_num}_feedback.md"
        file_path = os.path.join(feedback_dir, file_name)

        with open(file_path, 'w', encoding='utf-8') as f:
            # Title includes the actual question
            f.write(f"# Domanda {question_num}: {question}\n\n")
            f.write(f"**La tua risposta:**\n\n{answer}\n\n")

            # Process the feedback based on its format
            if feedback.startswith("1."):
                # If feedback is in a numbered list format (1., 2., etc.)
                import re
                sections = re.split(r'\d+\.\s+', feedback)

                # Remove empty first section if it exists
                if sections and not sections[0].strip():
                    sections = sections[1:]

                # Map the sections to appropriate headers
                section_titles = [
                    "Punti di forza",
                    "Aree di miglioramento",
                    "Suggerimenti specifici",
                    "Approcci alternativi"
                ]

                f.write("## Feedback\n\n")

                # Write each section with appropriate header
                for i, (title, content) in enumerate(zip(section_titles, sections)):
                    if content.strip():
                        f.write(f"### {title}\n")
                        f.write(content.strip() + "\n\n")
            else:
                # If feedback is already structured or in a different format, keep it as is
                f.write(f"## Feedback\n\n{feedback}\n")

        print(f"Feedback saved to {file_path}")
        return file_path

    def generate_feedback_summary(self) -> str:
        """Generate a summary of all feedback files.

        Returns:
            str: Path to the generated summary file
        """
        feedback_dir = os.path.join(self.output_dir, "feedback")
        summary_file = os.path.join(feedback_dir, "feedback_summary.md")

        if not os.path.exists(feedback_dir):
            print(f"Feedback directory not found: {feedback_dir}")
            return None

        # Get all question feedback files
        feedback_files = []
        for file in os.listdir(feedback_dir):
            if file.startswith("question_") and file.endswith("_feedback.md"):
                feedback_files.append(file)

        if not feedback_files:
            print("No feedback files found to summarize")
            return None

        # Sort files by question number
        feedback_files.sort(key=lambda x: int(x.split('_')[1]))

        # Write the summary file
        with open(summary_file, 'w', encoding='utf-8') as f:
            # Header
            f.write("# Riepilogo del Feedback - Simulazione di Colloquio\n\n")

            # Table of contents
            f.write("## Indice\n\n")
            for i, file in enumerate(feedback_files):
                # Extract question from filename
                with open(os.path.join(feedback_dir, file), 'r', encoding='utf-8') as qf:
                    first_line = qf.readline().strip()
                    if first_line.startswith("# Domanda"):
                        question = first_line[first_line.find(":")+1:].strip()
                    else:
                        question = f"Domanda {i+1}"

                # Create TOC entry with link
                f.write(f"{i+1}. [{question}](#domanda-{i+1})\n")

            f.write("\n---\n\n")

            # Compile all feedback
            for i, file in enumerate(feedback_files):
                file_path = os.path.join(feedback_dir, file)

                with open(file_path, 'r', encoding='utf-8') as qf:
                    content = qf.read()

                # Add anchor for the TOC link
                f.write(f"<a id='domanda-{i+1}'></a>\n")
                f.write(content)
                f.write("\n\n---\n\n")

            # Conclusion with general tips
            f.write("## Considerazioni Finali\n\n")
            f.write(
                "Ecco alcuni suggerimenti generali per migliorare le tue risposte ai colloqui:\n\n")
            f.write("1. **Usa il metodo STAR**: Struttura le tue risposte descrivendo la Situazione, il Task (compito), l'Azione che hai intrapreso e il Risultato ottenuto.\n\n")
            f.write("2. **Preparati con esempi specifici**: Abbi pronti esempi concreti delle tue esperienze passate che dimostrino le competenze richieste.\n\n")
            f.write("3. **Allineati con i valori dell'azienda**: Mostra come i tuoi valori personali e professionali si allineano con quelli dell'organizzazione.\n\n")
            f.write("4. **Sii conciso ma completo**: Fornisci risposte che siano abbastanza dettagliate ma evita divagazioni non pertinenti.\n\n")
            f.write(
                "5. **Mostra entusiasmo**: Comunica la tua passione per il ruolo e la missione dell'azienda.\n")

        print(f"Feedback summary generated at {summary_file}")
        return summary_file
