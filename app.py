# CRITICAL: SQLite fix - MUST be at the very top before ANY other imports
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
    print("Successfully replaced sqlite3 with pysqlite3")
except ImportError:
    print("pysqlite3 not found, using system sqlite3 which might cause issues")

# Now continue with normal imports
import re
import time
import random
import streamlit as st
import sys
import os
import traceback
import shutil
from src.interview_prep.utils.interview_manager import InterviewManager

# Gestione delle sessioni - aggiungi questo dopo gli import
import uuid

# Genera un ID di sessione univoco se non esiste già
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    # time dovrebbe essere già importato
    st.session_state.session_start_time = time.time()

# IMPORTANTE: set_page_config MUST be the first Streamlit instruction
st.set_page_config(
    page_title="Assistente AI per la Preparazione ai Colloqui",
    page_icon="🎯",
    layout="wide"
)


def sanitize_input(text):
    """
    Sanitize user input by removing potentially problematic characters and trimming whitespace.

    Args:
        text (str): The input text to sanitize

    Returns:
        str: The sanitized text
    """
    if not text:
        return ""

    # Convert to string if not already
    text = str(text)

    # Replace HTML tags with spaces
    text = re.sub(r'<[^>]*>', ' ', text)

    # Remove potentially dangerous characters
    text = re.sub(r'[\\\'";%]', '', text)

    # Remove multiple spaces and trim
    text = re.sub(r'\s+', ' ', text).strip()

    return text

# Funzione per ottenere il percorso specifico della sessione


def get_session_path():
    """Ottiene il percorso della directory specifica per questa sessione."""
    base_dir = "output"
    # Se non stiamo più usando gli ID di sessione, restituisci direttamente la directory di base
    # session_dir = os.path.join(base_dir, st.session_state.session_id)
    session_dir = base_dir  # Semplificato

    # Crea la directory se non esiste
    os.makedirs(session_dir, exist_ok=True)
    os.makedirs(os.path.join(session_dir, "feedback"), exist_ok=True)

    return session_dir


def clear_all_data():
    """
    Cancella completamente tutti i dati generati nella directory di output.
    Garantisce che nessun dato rimanga accessibile ad altri utenti.
    """
    # Ottieni il percorso della directory di output
    output_dir = get_session_path()

    try:
        # 1. Cancella tutti i file nella directory principale
        for filename in os.listdir(output_dir):
            file_path = os.path.join(output_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Rimosso file: {file_path}")
            elif os.path.isdir(file_path) and filename != ".session":
                # Rimuovi le sottodirectory, ma preserva .session
                shutil.rmtree(file_path)
                print(f"Rimossa directory: {file_path}")

        # 2. Ricrea le directory necessarie
        os.makedirs(os.path.join(output_dir, "feedback"), exist_ok=True)

        # 3. Opzionale: scrivi un file vuoto o di placeholder
        with open(os.path.join(output_dir, ".clean"), "w") as f:
            f.write(f"Directory cleaned on {time.ctime()}")

        return True, "Tutti i dati sono stati cancellati con successo."

    except Exception as e:
        error_message = f"Errore durante la pulizia dei dati: {str(e)}"
        print(error_message)
        return False, error_message


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
                # Sanitize the API key
                openai_key = sanitize_input(openai_key)
                os.environ['OPENAI_API_KEY'] = openai_key
                st.session_state['OPENAI_API_KEY'] = openai_key
                api_keys_valid = True
                st.success("OpenAI API Key salvata per questa sessione!")

            if serper_key:
                # Sanitize the API key
                serper_key = sanitize_input(serper_key)
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
    # st.success("Import riuscito con percorso src.interview_prep")
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
# Inizializza l'InterviewManager nella sessione
if 'interview_manager' not in st.session_state:
    st.session_state.interview_manager = InterviewManager(
        output_dir=get_session_path())


def load_questions(job_position):
    """Load questions from markdown files."""
    # Sanitize job position for filename
    job_position = sanitize_input(job_position)

    # Usa l'InterviewManager dalla sessione
    manager = st.session_state.interview_manager
    # Aggiorna la directory di output se necessario
    manager.output_dir = get_session_path()

    # Debug info
    st.write("Cercando domande per:", job_position)

    # Carica le domande usando l'InterviewManager
    success = manager.load_questions(job_position)

    if success:
        st.write(f"Trovate {len(manager.questions)} domande")
        return manager.questions
    else:
        st.warning(f"Nessun file per le domande trovato per {job_position}")
        st.write("Files disponibili nella directory della sessione:")
        # Elenca i file nella directory della sessione
        st.code(os.listdir(get_session_path()))
        return []


def get_random_question():
    """Get a random question that hasn't been asked yet."""
    if not st.session_state.questions:
        return None

    # Usa l'InterviewManager dalla sessione
    manager = st.session_state.interview_manager

    # Sincronizza lo stato delle domande con quello nella sessione
    manager.questions = st.session_state.questions
    manager.asked_questions = st.session_state.asked_questions

    # Ottieni una domanda casuale
    question = manager.get_random_question()

    # Se c'è una nuova domanda, aggiorna lo stato della sessione
    if question:
        st.session_state.asked_questions = manager.asked_questions

    return question


def save_feedback(question_num, question, answer, feedback):
    """Save feedback for a question."""
    # Usa l'InterviewManager dalla sessione
    manager = st.session_state.interview_manager

    # Aggiorna la directory di output se necessario
    manager.output_dir = get_session_path()

    # Salva il feedback usando l'InterviewManager
    file_path = manager.save_feedback(question_num, question, answer, feedback)
    return file_path


def run_research(company, interviewer, job_position, industry, country, job_description):
    """Run the research and question generation phase."""
    output_dir = get_session_path()
    os.makedirs(output_dir, exist_ok=True)

    # Usa l'InterviewManager
    manager = st.session_state.interview_manager
    # Aggiorna la directory di output
    manager.output_dir = output_dir

    try:
        # Crea una nuova istanza per la ricerca
        crew_instance = InterviewPrepCrew()
        crew = crew_instance.research_crew()

        inputs = {
            'company': company,
            'interviewer': interviewer,
            'job_position': job_position,
            'industry': industry,
            'country': country,
            'job_description': job_description
        }

        with st.spinner("Ricerca e generazione di domande in corso... Questo potrebbe richiedere diversi minuti."):
            result = crew.kickoff(inputs=inputs)

        # Debug info
        st.write(f"Task completate: {len(result.tasks_output)}")

        for i, task_output in enumerate(result.tasks_output):
            st.write(
                f"Task {i}: {task_output.task_name if hasattr(task_output, 'task_name') else 'Unknown'}")
            st.write(f"Output length: {len(task_output.raw)}")

            if i == 0:  # Company research
                company_file = manager.save_company_report(
                    task_output.raw, company)
            elif i == 1:  # Interviewer research
                interviewer_file = manager.save_interviewer_report(
                    task_output.raw, interviewer)
            elif i == 2:  # Questions
                questions_file = manager.save_questions(
                    task_output.raw, job_position)

                # Elimina l'altro file se esiste per evitare duplicati
                default_questions_file = os.path.join(
                    output_dir, "interview_questions.md")
                if os.path.exists(default_questions_file) and default_questions_file != questions_file:
                    try:
                        os.remove(default_questions_file)
                        st.write(
                            f"Rimosso file duplicato: {default_questions_file}")
                    except Exception as e:
                        st.write(
                            f"Impossibile rimuovere il file duplicato: {e}")
            else:
                continue

        # Carica le domande
        st.write("Caricamento domande...")
        manager.load_questions(job_position)
        st.session_state.questions = manager.questions
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
        # Crea una nuova istanza per generare il feedback
        crew_instance = InterviewPrepCrew()
        # Debug
        st.write(f"Agenti disponibili: {len(crew_instance.agents)}")

        crew = crew_instance.feedback_crew()

        inputs = {
            'company': sanitize_input(company),
            'interviewer': sanitize_input(interviewer),
            'job_position': sanitize_input(job_position),
            'industry': sanitize_input(industry),
            'job_position_report': question,
            'user_answer': answer
        }

        with st.spinner("Generating feedback..."):
            result = crew.kickoff(inputs=inputs)

        # Salva e restituisci il feedback
        save_feedback(st.session_state.question_number,
                      question, answer, result.raw)
        return result.raw

    except Exception as e:
        st.error(f"Error generating feedback: {e}")
        traceback_str = traceback.format_exc()
        st.code(traceback_str)  # Mostra il traceback completo
        return f"Si è verificato un errore durante la generazione del feedback: {str(e)}"


def main():
    """Main Streamlit application."""
    st.title("Assistente AI per la Preparazione ai Colloqui")

    # MODIFICA: Esegui la pulizia solo al primo avvio dell'app, non ad ogni refresh
    if 'app_initialized' not in st.session_state:
        # NON eseguire clear_all_data() qui
        st.session_state.app_initialized = True

    # Tentativo di caricare informazioni sessione precedente (se necessario)
    # if ('company' not in st.session_state or
    #     'interviewer' not in st.session_state or
    #     'job_position' not in st.session_state or
    #         'industry' not in st.session_state):
    #     session_file = os.path.join("output", ".session", "last_session.txt")
    #     if os.path.exists(session_file):
    #         try:
    #             with open(session_file, "r") as f:
    #                 for line in f:
    #                     if "=" in line:
    #                         key, value = line.strip().split("=", 1)
    #                         if key and value and key in ['company', 'interviewer', 'job_position', 'industry']:
    #                             st.session_state[key] = sanitize_input(value)
    #         except Exception as e:
    #             st.error(f"Error loading session: {e}")

    st.sidebar.title("Navigazione")
    page = st.sidebar.radio(
        "Seleziona una pagina:", ["Benvenuto", "Ricerca", "Pratica", "Reports"])
    st.sidebar.markdown("---")
    st.sidebar.subheader("Data Management")
    st.sidebar.markdown(
        "A fine sessione usa il pulsante **clear data** per eliminare i dati della tua sessione")

    if st.sidebar.button("Clear Data"):
        # Pulisci tutti i file di output
        success, message = clear_all_data()

        if success:
            # Resetta le variabili di sessione
            st.session_state.questions = []
            st.session_state.asked_questions = set()
            st.session_state.feedback = ""
            st.session_state.question_number = 1
            st.session_state.current_question = None

            # Reinizializza l'InterviewManager
            st.session_state.interview_manager = InterviewManager(
                output_dir=get_session_path())

            st.sidebar.success("✅ " + message)
        else:
            st.sidebar.error("❌ " + message)

        st.rerun()

    if page == "Benvenuto":
        st.write("## Benvenuto all'Assistente AI per la Preparazione ai Colloqui!")
        st.write("""
        Questa applicazione ti aiuta a prepararti per i colloqui di lavoro:

        1. **Ricercando** l'azienda e l'intervistatore
        2. **Generando** domande personalizzate per il colloquio
        3. **Esercitandoti** con le tue risposte e ricevendo feedback dall'AI
        4. **Scarica il documento** con le tue risposte e feedback

        Per iniziare, seleziona 'Ricerca' dal menu di navigazione per generare
        domande specifiche per la tua posizione lavorativa.
        """)
        st.info("Questa applicazione utilizza l'AI per simulare scenari reali di colloquio. La qualità della preparazione dipende dalle informazioni che fornisci.")
        # Aggiungiamo una sezione FAQ
        with st.expander("Domande frequenti"):
            st.markdown("""
            **Quanto tempo richiede la generazione delle domande?**  
            La fase di ricerca e generazione può richiedere da 3 a 5 minuti, a seconda della complessità dell'azienda e del ruolo.
            
            **Le mie informazioni sono al sicuro?**  
            Sì! Tutti i dati vengono elaborati localmente e possono essere cancellati in qualsiasi momento utilizzando il pulsante "Cancella Dati".
            
            **Posso usare l'applicazione per più posizioni lavorative?**  
            Assolutamente! Puoi generare domande per diverse posizioni lavorative semplicemente avviando una nuova ricerca.
            
            **Come posso ottenere i migliori risultati?**  
            Inserisci informazioni dettagliate nella descrizione del lavoro e sii specifico riguardo al settore e al ruolo. Più informazioni fornisci, migliori saranno le domande generate.
            """)

    elif page == "Reports":
        st.write("## Generated Reports")
        # Use the session directory for reports
        session_dir = get_session_path()
        report_files = []
        if os.path.exists(session_dir):
            for file in os.listdir(session_dir):
                if file.endswith(".md") and not file.startswith("."):
                    report_files.append(file)

        if not report_files:
            st.warning(
                "Nessun report trovato. Per favore torna alla prima fase di ricerca.")
        else:
            selected_report = st.selectbox(
                "Seleziona un report da visionare:", report_files)
            if selected_report:
                file_path = os.path.join(session_dir, selected_report)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                st.markdown(content)
                st.download_button(
                    label="Scarica questo report",
                    data=content,
                    file_name=selected_report,
                    mime="text/markdown"
                )

    elif page == "Ricerca":
        st.write("## Fase di ricerca")
        st.write(
            "Inserisci le informazioni sulla posizione per cui vuoi fare il colloquio:")
        with st.form("research_form"):
            company = st.text_input("Nome Azienda", value=st.session_state.get(
                'company', ''), help="Inserisci il nome dell'azienda")
            interviewer = st.text_input("Nome di chi ti farà l'intervista", value=st.session_state.get(
                'interviewer', ''), help="Inserisci il nome di chi ti farà l'intervista")
            job_position = st.text_input("Job Position", value=st.session_state.get(
                'job_position', ''), help="Inserisci la specifica job position")
            industry = st.text_input("Industry", value=st.session_state.get(
                'industry', ''), help="Inserisci l'industry o il settore dell'azienda")
            country = st.text_input(
                "Country", value="Italy", help="Inserisci il country in cui si trova l'azienda")
            job_description = st.text_area(
                "Job Description", value="", height=300, help="Incolla qui la job description completa")
            submit_research = st.form_submit_button("Genera le Domande")

        if submit_research:
            # Sanitize all inputs before processing
            company = sanitize_input(company)
            interviewer = sanitize_input(interviewer)
            job_position = sanitize_input(job_position)
            industry = sanitize_input(industry)
            country = sanitize_input(country)
            job_description = sanitize_input(job_description)

            if not company or not job_position or not industry or not job_description:
                st.error(
                    "Per favore compila tutti i campi richiesti: Nome Azienda, Job Position, Industry, and Job Description.")
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
                        f"Ricerca completata! Generate {num_questions} domande per il colloquio.")
                    st.write(
                        "Vai alla pagina 'Pratica' per iniziare ad esercitarti con queste domande.")
                else:
                    st.error(
                        "Impossibile generare domande. Controlla i log o riprova con informazioni più dettagliate.")

    elif page == "Pratica":
        st.write("## Fase di Pratica")
        if not st.session_state.questions:
            st.warning(
                "Nessuna domanda caricata. Per favore carica delle domande esistenti o torna alla fase di ricerca per generarne di nuove")
            job_pos_load = st.text_input("Job Position", value=st.session_state.get(
                'job_position', ''), help="Inserisci la job position per cui caricare le domande")

            if st.button("Sto caricando le domande esistenti") and job_pos_load:
                # Sanitize input
                job_pos_load = sanitize_input(job_pos_load)

                st.session_state.questions = load_questions(job_pos_load)
                if st.session_state.questions:
                    st.success(
                        f"Caricate {len(st.session_state.questions)} domande per {job_pos_load}!")
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
                        f"Nessuna domanda trovata per {job_pos_load}. Per favore torna alla fase di ricerca")
            return

        st.write("### Pratica per l'intevista")
        remaining = max(0, MAX_PRACTICE_QUESTIONS -
                        (st.session_state.question_number - 1))
        st.write(f"Domande rimanenti in questa sessione: {remaining}")

        if not st.session_state.current_question:
            st.session_state.current_question = get_random_question()

        if not st.session_state.current_question:
            if len(st.session_state.asked_questions) >= len(st.session_state.questions):
                st.info(
                    "Hai risposto a tutte le domande disponibili per questa sessione! Generane di nuove nella fase di ricerca o ricomincia una nuova sessione")
                if st.button("Ricomincia la sessione di Pratica"):
                    st.session_state.asked_questions = set()
                    st.session_state.question_number = 1
                    st.session_state.current_question = None
                    st.session_state.feedback = ""
                    st.rerun()
            else:
                st.warning(
                    "Non sono riuscito a ottenere una nuova domanda. Provo di nuovo...")
                time.sleep(1)  # Piccola pausa
                st.rerun()
            return

        st.markdown(
            f"### Domanda {st.session_state.question_number}:\n**{st.session_state.current_question}**")

        with st.form("answer_form"):
            answer = st.text_area("La tua risposta", value="", height=200)
            submit_answer = st.form_submit_button("Invia Risposta")

        if submit_answer:
            # Sanitize the answer input
            answer = sanitize_input(answer)

            if not answer:
                st.error("Per favore dai una risposta prima di inviare.")
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
            st.write("### Feedback sulla tua risposta precedente")
            st.markdown(st.session_state.feedback)

            # Create columns for the buttons
            col1, col2 = st.columns(2)

            with col1:
                # Get the path to the saved feedback file
                feedback_file = os.path.join(
                    get_session_path(),
                    "feedback",
                    f"question_{st.session_state.question_number-1}_feedback.md"
                )

                if os.path.exists(feedback_file):
                    with open(feedback_file, 'r', encoding='utf-8') as f:
                        formatted_feedback = f.read()

                    st.download_button(
                        label="Download Feedback",
                        data=formatted_feedback,
                        file_name=f"feedback_question_{st.session_state.question_number-1}.md",
                        mime="text/markdown"
                    )
                else:
                    st.download_button(
                        label="Download Feedback",
                        data=st.session_state.feedback,
                        file_name=f"feedback_question_{st.session_state.question_number-1}.md",
                        mime="text/markdown"
                    )

            # Determine if we're at the last question
            next_button_label = "Prossima Domanda"
            if st.session_state.question_number > MAX_PRACTICE_QUESTIONS:
                next_button_label = "Concludi la sessione di Pratica"

            with col2:
                if st.button(next_button_label, key="next_question"):
                    st.session_state.feedback = ""
                    st.session_state.current_question = None

                    # If this was the last question, generate summary feedback
                    if st.session_state.question_number > MAX_PRACTICE_QUESTIONS:
                        # Generate summary feedback
                        manager = st.session_state.interview_manager
                        summary_path = manager.generate_feedback_summary()

                        # Check if summary was created successfully
                        if summary_path and os.path.exists(summary_path):
                            # We'll show the summary on the next page load
                            st.session_state.show_summary = True

                    st.rerun()
         # Check if we should show the summary
    if st.session_state.get('show_summary', False):
        st.session_state.show_summary = False  # Reset flag

        # Get the summary file
        feedback_dir = os.path.join(get_session_path(), "feedback")
        summary_file = os.path.join(feedback_dir, "feedback_summary.md")

        if os.path.exists(summary_file):
            with open(summary_file, 'r', encoding='utf-8') as f:
                summary_content = f.read()

            st.write("## Riepilogo Completo del Feedback")
            st.markdown(summary_content)

            st.download_button(
                label="Scarica il Riepilogo Completo",
                data=summary_content,
                file_name="riepilogo_feedback_colloquio.md",
                mime="text/markdown"
            )

            # Add a button to restart practice
            if st.button("Inizia una Nuova Sessione"):
                st.session_state.asked_questions = set()
                st.session_state.question_number = 1
                st.session_state.current_question = None
                st.session_state.feedback = ""
                st.rerun()


if __name__ == "__main__":
    main()
