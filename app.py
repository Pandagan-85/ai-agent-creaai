
import sys



from dotenv import load_dotenv
import streamlit as st
import random
import time
import re
import os




# IMPORTANTE: set_page_config DEVE essere la prima istruzione Streamlit
st.set_page_config(
    page_title="AI Interview Preparation",
    page_icon="🎯",
    layout="wide"
)

# Load environment variables
load_dotenv()

# Ora facciamo gli import DOPO set_page_config
try:
    from src.interview_prep.crew import InterviewPrepCrew
    st.success("Import riuscito con percorso src.interview_prep")
except ImportError as e:
    st.error(f"Errore di importazione: {e}")
    st.write("Struttura delle directory:")
    st.code(os.listdir())
    st.write("Struttura della directory src:")
    if os.path.exists("src"):
        st.code(os.listdir("src"))
    else:
        st.write("La directory src non esiste!")
    sys.exit(1)  # Esci se l'import non funziona

# Create a simplified InterviewManager


class InterviewManager:
    """Manager for the interview process."""

    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
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

    def save_company_report(self, content, company):
        """Save the company research report."""
        file_name = self.sanitize_filename(f"{company}_report.md")
        file_path = os.path.join(self.output_dir, file_name)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return file_path

    def save_interviewer_report(self, content, interviewer):
        """Save the interviewer research report."""
        file_name = self.sanitize_filename(f"{interviewer}_report.md")
        file_path = os.path.join(self.output_dir, file_name)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return file_path

    def save_questions(self, content, job_position):
        """Save the interview questions."""
        file_name = self.sanitize_filename(f"{job_position}_questions.md")
        file_path = os.path.join(self.output_dir, file_name)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return file_path


# Load environment variables
load_dotenv()

# Constants
MAX_PRACTICE_QUESTIONS = 5  # Maximum number of questions in a practice session

# Initialize session state variables if they don't exist
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'asked_questions' not in st.session_state:
    st.session_state.asked_questions = set()
if 'feedback' not in st.session_state:
    st.session_state.feedback = ""
if 'question_number' not in st.session_state:
    st.session_state.question_number = 1
if 'current_question' not in st.session_state:
    st.session_state.current_question = None


def load_questions(job_position):
    """Load questions from markdown files."""
    # Create output directories if they don't exist
    os.makedirs("output", exist_ok=True)

    # Try different possible filename patterns
    possible_filenames = [
        f"{job_position}_questions.md",  # Prima cerca questo
        f"{job_position}_report.md",
        f"{job_position}_report.txt"
    ]

    # Sanitize filenames
    possible_filenames = [re.sub(r'[\\/*?:"<>|,]', '_', name)
                          for name in possible_filenames]

    st.write("Cercando file con i seguenti nomi:", possible_filenames)  # Debug

    file_path = None
    for filename in possible_filenames:
        path = os.path.join("output", filename)
        if os.path.exists(path):
            file_path = path
            st.write(f"Trovato file: {path}")  # Debug
            break

    if not file_path:
        st.warning(f"No question files found for {job_position}")
        # Mostra tutti i file disponibili
        st.write("Files disponibili nella directory output:")
        st.code(os.listdir("output"))
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse questions from markdown
        # Try to match both numbered list (1. Question) and bullet point lists (- Question)
        numbered_pattern = re.compile(r'^\d+\.\s+(.+)$', re.MULTILINE)
        bullet_pattern = re.compile(r'^[-*]\s+(.+)$', re.MULTILINE)

        numbered_matches = numbered_pattern.findall(content)
        bullet_matches = bullet_pattern.findall(content)

        # Debug
        st.write(
            f"Trovate {len(numbered_matches)} domande numerate e {len(bullet_matches)} con bullet points")

        # Use whichever pattern found more matches
        if len(numbered_matches) >= len(bullet_matches):
            return numbered_matches
        else:
            return bullet_matches
    except Exception as e:
        st.error(f"Error loading questions: {e}")
        return []


def get_random_question():
    """Get a random question that hasn't been asked yet."""
    if not st.session_state.questions:
        return None

    # Create a list of available questions (not yet asked)
    available_questions = [q for i, q in enumerate(st.session_state.questions)
                           if i not in st.session_state.asked_questions]

    if not available_questions:
        return None

    # Select a random question from available ones
    question = random.choice(available_questions)

    # Find the index of this question in the original list to track it
    question_index = st.session_state.questions.index(question)
    st.session_state.asked_questions.add(question_index)

    return question


def save_feedback(question_num, question, answer, feedback):
    """Save feedback for a question."""
    feedback_dir = os.path.join("output", "feedback")
    os.makedirs(feedback_dir, exist_ok=True)

    file_name = f"question_{question_num}_feedback.md"
    file_path = os.path.join(feedback_dir, file_name)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"# Question {question_num}\n\n")
        f.write(f"**Question:** {question}\n\n")
        f.write(f"**Your Answer:**\n\n{answer}\n\n")
        f.write(f"**Feedback:**\n\n{feedback}\n")

    return file_path


def run_research(company, interviewer, job_position, industry, country, job_description):
    """Run the research and question generation phase."""
    # Create output directories
    os.makedirs("output", exist_ok=True)

    # Create interview manager
    manager = InterviewManager()

    # Create crew for research only
    crew = InterviewPrepCrew().crew()
    crew.tasks = [task for task in crew.tasks if task.name in [
        "research_company_task",
        "research_person_task",
        "define_questions_task"
    ]]

    # Run crew with inputs
    inputs = {
        'company': company,
        'interviewer': interviewer,
        'job_position': job_position,
        'industry': industry,
        'country': country,
        'job_description': job_description
    }

    # Use the streamlit spinner to show progress
    with st.spinner("Researching and generating questions... This may take several minutes."):
        result = crew.kickoff(inputs=inputs)

    # Save outputs to files
    for i, task_output in enumerate(result.tasks_output):
        if i == 0:  # Company research
            company_file = manager.save_company_report(
                task_output.raw, company)
        elif i == 1:  # Interviewer research
            interviewer_file = manager.save_interviewer_report(
                task_output.raw, interviewer)
        elif i == 2:  # Questions
            questions_file = manager.save_questions(
                task_output.raw, job_position)
        else:
            continue

    # Load questions into session state
    st.session_state.questions = load_questions(job_position)
    st.session_state.asked_questions = set()
    st.session_state.question_number = 1

    return len(st.session_state.questions)


def get_feedback(company, interviewer, job_position, industry, question, answer):
    """Get AI feedback on the answer."""
    # Create crew for interview practice
    crew = InterviewPrepCrew().crew()
    crew.tasks = [task for task in crew.tasks if task.name in [
        "interview_prep_task",
        "feedback_task"
    ]]

    # Prepare inputs
    inputs = {
        'company': company,
        'interviewer': interviewer,
        'job_position': job_position,
        'industry': industry,
        'job_position_report': question,
        'user_answer': answer
    }

    # Get feedback
    with st.spinner("Generating feedback..."):
        result = crew.kickoff(inputs=inputs)

    # Save feedback to file
    save_feedback(st.session_state.question_number,
                  question, answer, result.raw)

    return result.raw


def main():
    """Main Streamlit application."""

    st.title("AI Interview Preparation Assistant")

    # Recupera le informazioni della sessione se necessario
    if ('company' not in st.session_state or
        'interviewer' not in st.session_state or
        'job_position' not in st.session_state or
            'industry' not in st.session_state):

        # Prova a caricare dalle sessioni precedenti
        session_file = os.path.join("output", ".session", "last_session.txt")
        if os.path.exists(session_file):
            try:
                with open(session_file, "r") as f:
                    for line in f:
                        if "=" in line:
                            key, value = line.strip().split("=", 1)
                            if key and value and key in ['company', 'interviewer', 'job_position', 'industry']:
                                st.session_state[key] = value
            except Exception as e:
                st.error(f"Error loading session: {e}")

    # Create sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select a page:", ["Welcome", "Research", "Practice", "Reports"])

    if page == "Welcome":
        st.write("## Welcome to the AI Interview Preparation Assistant!")
        st.write("""
        This application helps you prepare for job interviews by:
        
        1. **Researching** the company and interviewer
        2. **Generating** customized interview questions
        3. **Practicing** your answers and receiving AI feedback
        
        To get started, select 'Research' from the navigation menu to generate 
        interview questions for your specific job position.
        """)

        st.info("This application uses AI to simulate real interview scenarios. The quality of the preparation depends on the inputs you provide.")

    elif page == "Reports":
        st.write("## Generated Reports")

        # Trova tutti i file di report
        report_files = []
        for file in os.listdir("output"):
            if file.endswith(".md") and not file.startswith("."):
                report_files.append(file)

        if not report_files:
            st.warning("No reports found. Please run the Research phase first.")
        else:
            # Dropdowni per selezionare il report
            selected_report = st.selectbox(
                "Select a report to view:", report_files)

            if selected_report:
                file_path = os.path.join("output", selected_report)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Mostra il report
                st.markdown(content)

                # Opzione per scaricare
                st.download_button(
                    label="Download this report",
                    data=content,
                    file_name=selected_report,
                    mime="text/markdown"
                )

    elif page == "Research":
        st.write("## Research Phase")
        st.write("Enter information about the position you're applying for:")

        with st.form("research_form"):
            company = st.text_input(
                "Company Name", value="", help="Enter the name of the company you're applying to")
            interviewer = st.text_input(
                "Interviewer Name", value="", help="Enter the name of the interviewer if known")
            job_position = st.text_input(
                "Job Position", value="", help="Enter the specific job position you're applying for")
            industry = st.text_input(
                "Industry", value="", help="Enter the industry or sector of the company")
            country = st.text_input(
                "Country", value="Italy", help="Enter the country where the job is located")
            job_description = st.text_area(
                "Job Description", value="", height=300, help="Paste the complete job description here")

            submit_research = st.form_submit_button("Generate Questions")

        if submit_research:
            if not company or not job_position or not industry or not job_description:
                st.error(
                    "Please fill in all required fields: Company, Job Position, Industry, and Job Description.")
            else:
                num_questions = run_research(
                    company, interviewer, job_position, industry, country, job_description)
                if num_questions > 0:
                    st.success(
                        f"Research completed! Generated {num_questions} interview questions.")
                    st.write(
                        "Go to the 'Practice' page to start practicing with these questions.")
                else:
                    st.error(
                        "Failed to generate questions. Please try again with more detailed information.")

    elif page == "Practice":
        st.write("## Practice Phase")

        # Check if questions are available
        if not st.session_state.questions:
            st.warning(
                "No questions loaded. Please load existing questions or run the Research phase first.")

            job_position = st.text_input(
                "Job Position", help="Enter the job position to load questions for")
            if st.button("Load Existing Questions") and job_position:
                st.session_state.questions = load_questions(job_position)
                if st.session_state.questions:
                    st.success(
                        f"Loaded {len(st.session_state.questions)} questions!")
                    st.rerun()
                else:
                    st.error(
                        "No questions found. Please run the Research phase first.")
            return

        # Interview practice interface
        st.write("### Interview Practice")

        # Display current question count
        remaining = MAX_PRACTICE_QUESTIONS - \
            (st.session_state.question_number - 1)
        st.write(f"Questions remaining in this session: {remaining}")

        # Get current question or new random question
        if not st.session_state.current_question:
            st.session_state.current_question = get_random_question()

        if not st.session_state.current_question:
            st.info(
                "You've answered all available questions! To practice more, please generate new questions in the Research phase.")
            return

        # Display the question
        st.markdown(f"""
        ### Question {st.session_state.question_number}:
        **{st.session_state.current_question}**
        """)

        # Answer input
        with st.form("answer_form"):
            answer = st.text_area("Your Answer", value="", height=200)
            submit_answer = st.form_submit_button("Submit Answer")

        if submit_answer:
            if not answer:
                st.error("Please provide an answer before submitting.")
            else:
                # Get company and job details for feedback
                if 'company' not in st.session_state:
                    st.session_state.company = st.text_input("Company Name")
                    st.session_state.interviewer = st.text_input(
                        "Interviewer Name (if known)")
                    st.session_state.job_position = st.text_input(
                        "Job Position")
                    st.session_state.industry = st.text_input("Industry")

                # Get feedback on the answer
                feedback = get_feedback(
                    st.session_state.company,
                    st.session_state.interviewer,
                    st.session_state.job_position,
                    st.session_state.industry,
                    st.session_state.current_question,
                    answer
                )

                # Store feedback in session state
                st.session_state.feedback = feedback

                # Increment question counter
                st.session_state.question_number += 1

                # Clear current question to get a new one on next refresh
                st.session_state.current_question = None

                # Rerun to update the UI
                st.rerun()

        # Display feedback if available
        if st.session_state.feedback:
            st.write("### Feedback on Your Previous Answer")

            # Usa st.markdown invece di st.write per un rendering migliore
            st.markdown(st.session_state.feedback)

            # Aggiungi un pulsante per copiare il feedback negli appunti
            st.download_button(
                label="Download Feedback",
                data=st.session_state.feedback,
                file_name=f"feedback_question_{st.session_state.question_number-1}.md",
                mime="text/markdown"
            )

            if st.button("Next Question", key="next_question"):
                st.session_state.feedback = ""
                st.session_state.current_question = None

                # Check if we've reached the maximum questions
                if st.session_state.question_number > MAX_PRACTICE_QUESTIONS:
                    st.success(
                        "Congratulations! You've completed the practice session.")
                    st.session_state.question_number = 1
                    st.session_state.asked_questions = set()

                st.rerun()


if __name__ == "__main__":
    main()
