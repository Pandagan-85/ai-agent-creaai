import sys
import importlib.util

# Check if pysqlite3 is available and use it to replace sqlite3
if importlib.util.find_spec("pysqlite3"):
    import pysqlite3
    sys.modules["sqlite3"] = pysqlite3
    print("Successfully replaced sqlite3 with pysqlite3")
else:
    print("pysqlite3 not found, using system sqlite3 which might cause issues")

# Now proceed with other imports
import re
import time
import random
import streamlit as st
import os
import traceback


# IMPORTANTE: set_page_config DEVE essere la prima istruzione Streamlit
st.set_page_config(
    page_title="AI Interview Preparation",
    page_icon="🎯",
    layout="wide"
)

# Gestione combinata delle variabili d'ambiente:
# 1. Prima tenta di caricare da file .env in ambiente locale
# 2. Se non disponibile o fallisce, cerca nelle secrets di Streamlit

# Funzione per impostare la variabile d'ambiente da varie fonti


def set_api_key(key_name):
    # Se la chiave è già nell'ambiente, non facciamo nulla
    if key_name in os.environ:
        return True

    # Prova a caricare da .env (funziona solo in locale)
    try:
        from dotenv import load_dotenv
        load_dotenv()
        if key_name in os.environ:
            return True
    except ImportError:
        # Se dotenv non è installato, continuiamo con Streamlit secrets
        pass

    # Prova a caricare da Streamlit secrets (funziona in produzione)
    if hasattr(st, 'secrets') and key_name in st.secrets:
        os.environ[key_name] = st.secrets[key_name]
        return True

    return False


# Imposta le chiavi API necessarie
openai_key_set = set_api_key('OPENAI_API_KEY')
serper_key_set = set_api_key('SERPER_API_KEY')

# Verifica se le chiavi necessarie sono disponibili
api_keys_valid = True

if not openai_key_set:
    st.error("⚠️ OPENAI_API_KEY non trovata! Aggiungi questa chiave al tuo file .env o ai secrets di Streamlit.")
    api_keys_valid = False

if not serper_key_set:
    st.warning(
        "⚠️ SERPER_API_KEY non trovata! Alcune funzionalità di ricerca potrebbero non funzionare correttamente.")

# Se non abbiamo le chiavi API necessarie, mostriamo un form per inserirle manualmente
if not api_keys_valid:
    st.write("## Configurazione API Keys")
    st.write(
        "Per utilizzare questa applicazione, è necessario configurare le chiavi API di OpenAI.")

    with st.form("api_keys_form"):
        openai_key = st.text_input(
            "OpenAI API Key", type="password", help="La tua chiave API di OpenAI")
        serper_key = st.text_input("Serper API Key (opzionale)", type="password",
                                   help="La tua chiave API di Serper per la ricerca web")
        submit_keys = st.form_submit_button("Salva API Keys")

        if submit_keys:
            if openai_key:
                os.environ['OPENAI_API_KEY'] = openai_key
                st.session_state['OPENAI_API_KEY'] = openai_key
                api_keys_valid = True
                st.success("OpenAI API Key salvata per questa sessione!")

            if serper_key:
                os.environ['SERPER_API_KEY'] = serper_key
                st.session_state['SERPER_API_KEY'] = serper_key
                st.success("Serper API Key salvata per questa sessione!")

            st.rerun()

# Continua solo se abbiamo le API keys
if not api_keys_valid:
    st.stop()

# Add current directory to path to help with imports
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Add src directory to path if it exists
src_path = os.path.join(project_root, "src")
if os.path.exists(src_path) and src_path not in sys.path:
    sys.path.insert(0, src_path)

# Ora facciamo gli import DOPO set_page_config e setup path
try:
    from src.interview_prep.crew import InterviewPrepCrew
    st.success("Import riuscito con percorso src.interview_prep")
except ImportError as e:
    try:
        # Try direct import if package is installed
        from interview_prep.crew import InterviewPrepCrew
        st.success("Import riuscito con percorso interview_prep")
    except ImportError as e:
        st.error(f"Errore di importazione: {e}")
        st.write("Struttura delle directory:")
        st.code(os.listdir())
        st.write("Struttura della directory src:")
        if os.path.exists("src"):
            st.code(os.listdir("src"))
        else:
            st.write("La directory src non esiste!")
        # Show Python path for debugging
        st.write("Python path:")
        st.code("\n".join(sys.path))
        st.stop()  # Stop execution if import fails

# Create a simplified InterviewManager


class InterviewManager:
    """Manager for the interview process."""

    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "feedback"), exist_ok=True)

    def sanitize_filename(self, name):
        """Remove or replace invalid characters for filenames."""
        sanitized = re.sub(r'[\\/*?:"<>|,]', '_', str(name))
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
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
    os.makedirs("output", exist_ok=True)
    possible_filenames = [
        f"{job_position}_questions.md",
        f"{job_position}_report.md",
        f"{job_position}_report.txt"
    ]
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
        st.write("Files disponibili nella directory output:")
        st.code(os.listdir("output"))
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        numbered_pattern = re.compile(r'^\d+\.\s+(.+)$', re.MULTILINE)
        bullet_pattern = re.compile(r'^[-*]\s+(.+)$', re.MULTILINE)
        numbered_matches = numbered_pattern.findall(content)
        bullet_matches = bullet_pattern.findall(content)
        # Debug
        st.write(
            f"Trovate {len(numbered_matches)} domande numerate e {len(bullet_matches)} con bullet points")
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
    available_questions = [q for i, q in enumerate(st.session_state.questions)
                           if i not in st.session_state.asked_questions]
    if not available_questions:
        return None
    question = random.choice(available_questions)
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
    os.makedirs("output", exist_ok=True)
    manager = InterviewManager()

    try:
        crew = InterviewPrepCrew().crew()
        crew.tasks = [task for task in crew.tasks if task.name in [
            "research_company_task",
            "research_person_task",
            "define_questions_task"
        ]]

        inputs = {
            'company': company,
            'interviewer': interviewer,
            'job_position': job_position,
            'industry': industry,
            'country': country,
            'job_description': job_description
        }

        with st.spinner("Researching and generating questions... This may take several minutes."):
            result = crew.kickoff(inputs=inputs)

        for i, task_output in enumerate(result.tasks_output):
            if i == 0:
                company_file = manager.save_company_report(
                    task_output.raw, company)
            elif i == 1:
                interviewer_file = manager.save_interviewer_report(
                    task_output.raw, interviewer)
            elif i == 2:
                questions_file = manager.save_questions(
                    task_output.raw, job_position)
            else:
                continue

        st.session_state.questions = load_questions(job_position)
        st.session_state.asked_questions = set()
        st.session_state.question_number = 1
        return len(st.session_state.questions)

    except Exception as e:
        error_message = str(e)
        error_traceback = traceback.format_exc()

        # Controlla se è un errore di autenticazione
        if "AuthenticationError" in error_message or "Incorrect API key" in error_message:
            st.error(
                "⚠️ Errore di autenticazione API: La chiave API di OpenAI non è valida o è scaduta.")
            st.warning(
                "Per favore, controlla la tua chiave API di OpenAI e assicurati che sia corretta e attiva.")
            # Rimuovi la chiave dalla sessione così l'utente può inserirla di nuovo
            if 'OPENAI_API_KEY' in st.session_state:
                del st.session_state['OPENAI_API_KEY']
            os.environ.pop('OPENAI_API_KEY', None)
            st.rerun()
        else:
            st.error(
                f"Si è verificato un errore durante la ricerca: {error_message}")
            with st.expander("Dettagli errore"):
                st.code(error_traceback)

        return 0


def get_feedback(company, interviewer, job_position, industry, question, answer):
    """Get AI feedback on the answer."""
    try:
        crew = InterviewPrepCrew().crew()
        crew.tasks = [task for task in crew.tasks if task.name in [
            "interview_prep_task",
            "feedback_task"
        ]]

        inputs = {
            'company': company,
            'interviewer': interviewer,
            'job_position': job_position,
            'industry': industry,
            'job_position_report': question,  # Assuming this is where the question text goes
            'user_answer': answer
        }

        with st.spinner("Generating feedback..."):
            result = crew.kickoff(inputs=inputs)

        save_feedback(st.session_state.question_number,
                      question, answer, result.raw)
        return result.raw

    except Exception as e:
        error_message = str(e)
        error_traceback = traceback.format_exc()

        # Controlla se è un errore di autenticazione
        if "AuthenticationError" in error_message or "Incorrect API key" in error_message:
            st.error(
                "⚠️ Errore di autenticazione API: La chiave API di OpenAI non è valida o è scaduta.")
            st.warning(
                "Per favore, controlla la tua chiave API di OpenAI e assicurati che sia corretta e attiva.")
            # Rimuovi la chiave dalla sessione così l'utente può inserirla di nuovo
            if 'OPENAI_API_KEY' in st.session_state:
                del st.session_state['OPENAI_API_KEY']
            os.environ.pop('OPENAI_API_KEY', None)
            st.rerun()
        else:
            st.error(
                f"Si è verificato un errore durante la generazione del feedback: {error_message}")
            with st.expander("Dettagli errore"):
                st.code(error_traceback)

        return "Si è verificato un errore durante la generazione del feedback. Per favore, prova di nuovo."


def main():
    """Main Streamlit application."""
    st.title("AI Interview Preparation Assistant")

    # Tentativo di caricare informazioni sessione precedente (se necessario)
    if ('company' not in st.session_state or
        'interviewer' not in st.session_state or
        'job_position' not in st.session_state or
            'industry' not in st.session_state):
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
        report_files = []
        if os.path.exists("output"):
            for file in os.listdir("output"):
                if file.endswith(".md") and not file.startswith("."):
                    report_files.append(file)

        if not report_files:
            st.warning("No reports found. Please run the Research phase first.")
        else:
            selected_report = st.selectbox(
                "Select a report to view:", report_files)
            if selected_report:
                file_path = os.path.join("output", selected_report)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                st.markdown(content)
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
            company = st.text_input("Company Name", value=st.session_state.get(
                'company', ''), help="Enter the name of the company you're applying to")
            interviewer = st.text_input("Interviewer Name", value=st.session_state.get(
                'interviewer', ''), help="Enter the name of the interviewer if known")
            job_position = st.text_input("Job Position", value=st.session_state.get(
                'job_position', ''), help="Enter the specific job position you're applying for")
            industry = st.text_input("Industry", value=st.session_state.get(
                'industry', ''), help="Enter the industry or sector of the company")
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
                # Salva le info inserite nella sessione per usarle dopo nel feedback
                st.session_state['company'] = company
                st.session_state['interviewer'] = interviewer
                st.session_state['job_position'] = job_position
                st.session_state['industry'] = industry

                # Salva anche in un file per persistere tra sessioni
                session_dir = os.path.join("output", ".session")
                os.makedirs(session_dir, exist_ok=True)
                session_file = os.path.join(session_dir, "last_session.txt")
                try:
                    with open(session_file, "w") as f:
                        f.write(f"company={company}\n")
                        f.write(f"interviewer={interviewer}\n")
                        f.write(f"job_position={job_position}\n")
                        f.write(f"industry={industry}\n")
                except Exception as e:
                    st.warning(f"Could not save session info: {e}")

                num_questions = run_research(
                    company, interviewer, job_position, industry, country, job_description)
                if num_questions > 0:
                    st.success(
                        f"Research completed! Generated {num_questions} interview questions.")
                    st.write(
                        "Go to the 'Practice' page to start practicing with these questions.")
                else:
                    st.error(
                        "Failed to generate questions. Please check the logs or try again with more detailed information.")

    elif page == "Practice":
        st.write("## Practice Phase")
        if not st.session_state.questions:
            st.warning(
                "No questions loaded. Please load existing questions or run the Research phase first.")
            job_pos_load = st.text_input("Job Position", value=st.session_state.get(
                'job_position', ''), help="Enter the job position to load questions for")
            if st.button("Load Existing Questions") and job_pos_load:
                st.session_state.questions = load_questions(job_pos_load)
                if st.session_state.questions:
                    st.success(
                        f"Loaded {len(st.session_state.questions)} questions for {job_pos_load}!")
                    # Carica anche gli altri dettagli se non presenti
                    if 'company' not in st.session_state:
                        st.session_state['company'] = "Unknown"  # Placeholder
                    if 'interviewer' not in st.session_state:
                        st.session_state['interviewer'] = ""  # Placeholder
                    if 'job_position' not in st.session_state:
                        st.session_state['job_position'] = job_pos_load
                    if 'industry' not in st.session_state:
                        st.session_state['industry'] = "Unknown"  # Placeholder
                    st.rerun()
                else:
                    st.error(
                        f"No questions found for {job_pos_load}. Please run the Research phase first.")
            return

        st.write("### Interview Practice")
        remaining = max(0, MAX_PRACTICE_QUESTIONS -
                        (st.session_state.question_number - 1))
        st.write(f"Questions remaining in this session: {remaining}")

        if not st.session_state.current_question:
            st.session_state.current_question = get_random_question()

        if not st.session_state.current_question:
            if len(st.session_state.asked_questions) >= len(st.session_state.questions):
                st.info(
                    "You've answered all available questions! Generate new ones in the Research phase or restart the session.")
                if st.button("Restart Practice Session"):
                    st.session_state.asked_questions = set()
                    st.session_state.question_number = 1
                    st.session_state.current_question = None
                    st.session_state.feedback = ""
                    st.rerun()
            else:
                st.warning("Could not get a new question. Trying again...")
                time.sleep(1)  # Piccola pausa
                st.rerun()
            return

        st.markdown(
            f"### Question {st.session_state.question_number}:\n**{st.session_state.current_question}**")

        with st.form("answer_form"):
            answer = st.text_area("Your Answer", value="", height=200)
            submit_answer = st.form_submit_button("Submit Answer")

        if submit_answer:
            if not answer:
                st.error("Please provide an answer before submitting.")
            else:
                # Assicurati che i dettagli necessari per il feedback siano presenti
                company = st.session_state.get('company', 'Unknown Company')
                interviewer = st.session_state.get('interviewer', '')
                job_position = st.session_state.get(
                    'job_position', 'Unknown Position')
                industry = st.session_state.get('industry', 'Unknown Industry')

                if company == 'Unknown Company' or job_position == 'Unknown Position':
                    st.warning(
                        "Some job details are missing (Company/Job Position). Feedback might be less specific. Please ensure you ran the Research phase or loaded questions correctly.")

                feedback = get_feedback(
                    company,
                    interviewer,
                    job_position,
                    industry,
                    st.session_state.current_question,
                    answer
                )
                st.session_state.feedback = feedback
                st.session_state.question_number += 1
                st.session_state.current_question = None
                st.rerun()

        if st.session_state.feedback:
            st.write("### Feedback on Your Previous Answer")
            st.markdown(st.session_state.feedback)
            st.download_button(
                label="Download Feedback",
                data=st.session_state.feedback,
                file_name=f"feedback_question_{st.session_state.question_number-1}.md",
                mime="text/markdown"
            )

            # Bottone "Next Question" o "Finish Session"
            next_button_label = "Next Question"
            if st.session_state.question_number > MAX_PRACTICE_QUESTIONS:
                next_button_label = "Finish Practice Session"

            if st.button(next_button_label, key="next_question"):
                st.session_state.feedback = ""
                st.session_state.current_question = None
                if st.session_state.question_number > MAX_PRACTICE_QUESTIONS:
                    st.success(
                        "Congratulations! You've completed the practice session.")
                    st.session_state.question_number = 1  # Reset for next session
                    st.session_state.asked_questions = set()  # Reset for next session
                st.rerun()


if __name__ == "__main__":
    main()
