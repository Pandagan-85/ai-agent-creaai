import os
import sys
from dotenv import load_dotenv
from interview_prep.crew import InterviewPrepCrew
from interview_prep.utils.interview_manager import InterviewManager

# Load environment variables
load_dotenv()

# Constants
MAX_PRACTICE_QUESTIONS = 5  # Maximum number of questions in a practice session


def run_research():
    """Run the research and question generation phase."""
    # Create interview manager
    manager = InterviewManager()

    print("\nStarting research and question generation...\n")

    # Get user inputs with no defaults
    company = input("Enter the company name: ")
    while not company:
        company = input("Company name is required. Please enter: ")

    interviewer = input("Enter the interviewer name: ")
    while not interviewer:
        interviewer = input("Interviewer name is required. Please enter: ")

    job_position = input("Enter the job position: ")
    while not job_position:
        job_position = input("Job position is required. Please enter: ")

    industry = input("Enter the industry: ")
    while not industry:
        industry = input("Industry is required. Please enter: ")

    # Job description input
    print("\nEnter job description (press Enter twice when finished):")
    job_description_lines = []

    while True:
        line = input()
        if not line and job_description_lines and not job_description_lines[-1]:
            # Two consecutive empty lines
            break
        job_description_lines.append(line)

    job_description = '\n'.join(job_description_lines)

    if not job_description.strip():
        print("Job description is required.")
        return

    print(f"\nCompany: {company}")
    print(f"Interviewer: {interviewer}")
    print(f"Job Position: {job_position}")
    print(f"Industry: {industry}")

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
        'job_description': job_description
    }

    result = crew.kickoff(inputs=inputs)

    # Save outputs to files
    for i, task_output in enumerate(result.tasks_output):
        if i == 0:  # Company research
            manager.save_company_report(task_output.raw, company)
        elif i == 1:  # Interviewer research
            manager.save_interviewer_report(task_output.raw, interviewer)
        elif i == 2:  # Questions
            manager.save_questions(task_output.raw, job_position)
        else:
            continue

    print("\nResearch and question generation complete!")
    print("Check the output directory for results.")

    # Store these values for the practice session
    store_session_info(company, interviewer, job_position, industry)


def store_session_info(company, interviewer, job_position, industry):
    """Store session information for the practice session."""
    session_info = {
        "company": company,
        "interviewer": interviewer,
        "job_position": job_position,
        "industry": industry
    }

    # Create a simple session file
    try:
        session_dir = os.path.join("output", ".session")
        os.makedirs(session_dir, exist_ok=True)

        with open(os.path.join(session_dir, "last_session.txt"), "w") as f:
            for key, value in session_info.items():
                f.write(f"{key}={value}\n")
    except Exception as e:
        print(f"Warning: Could not save session info: {e}")


def load_session_info():
    """Load previous session information."""
    session_file = os.path.join("output", ".session", "last_session.txt")

    if not os.path.exists(session_file):
        return {}

    session_info = {}
    try:
        with open(session_file, "r") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    session_info[key] = value
    except Exception as e:
        print(f"Warning: Could not load session info: {e}")

    return session_info


def run_practice():
    """Run the interview practice session."""
    # Create interview manager
    manager = InterviewManager()

    print("\nStarting interview practice...\n")

    # Get user inputs with no defaults
    company = input("Enter the company name: ")
    while not company:
        company = input("Company name is required. Please enter: ")

    interviewer = input("Enter the interviewer name: ")
    while not interviewer:
        interviewer = input("Interviewer name is required. Please enter: ")

    job_position = input("Enter the job position: ")
    while not job_position:
        job_position = input("Job position is required. Please enter: ")

    industry = input("Enter the industry: ")
    while not industry:
        industry = input("Industry is required. Please enter: ")

    # Load questions
    if not manager.load_questions(job_position):
        print("Please run research first or check if questions file exists.")
        return

    if not manager.questions:
        print("No questions found in the file.")
        return

    print(f"Loaded {len(manager.questions)} questions.\n")

    # Create crew for interview practice
    crew = InterviewPrepCrew().crew()
    crew.tasks = [task for task in crew.tasks if task.name in [
        "interview_prep_task",
        "feedback_task"
    ]]

    # Practice loop
    print("=== Interview Practice ===")
    print("Answer each question as if you were in a real interview.")
    print("Type 'quit' to end the session.")
    print(
        f"You will be asked up to {MAX_PRACTICE_QUESTIONS} questions in random order.\n")

    question_num = 1

    while question_num <= MAX_PRACTICE_QUESTIONS:
        # Get random question
        question = manager.get_random_question()
        if not question:
            print("No more questions available.")
            break

        print(f"\nQuestion {question_num}: {question}")
        print("\nYour answer (type 'quit' to end):")

        # Get user's answer as a single line
        answer = input("> ")

        if answer.lower() == 'quit':
            print("\nEnding interview practice...")
            return

        # Get feedback
        print("\nGetting feedback on your answer...")

        inputs = {
            'company': company,
            'interviewer': interviewer,
            'job_position': job_position,
            'industry': industry,
            'job_position_report': question,
            'user_answer': answer
        }

        try:
            result = crew.kickoff(inputs=inputs)

            print("\n=== Feedback ===\n")
            print(result.raw)

            # Save feedback
            manager.save_feedback(question_num, question, answer, result.raw)

        except Exception as e:
            print(f"Error in feedback generation: {e}")

        # Next question
        question_num += 1

        if question_num <= MAX_PRACTICE_QUESTIONS:
            cont = input("\nPress Enter to continue or type 'quit' to end: ")
            if cont.lower() == 'quit':
                break

    print("\nInterview practice complete!")
    print(f"Saved feedback to {os.path.join('output', 'feedback')}")


def run():
    """Main entry point to the interview preparation system."""
    # Create output directory
    os.makedirs("output", exist_ok=True)

    print("\n=== Interview Preparation Assistant ===\n")
    print("What would you like to do?")
    print("1. Run research and generate interview questions")
    print("2. Practice interview with AI")
    print("3. Exit")

    choice = input("\nEnter your choice (1-3): ")

    if choice == "1":
        run_research()
    elif choice == "2":
        run_practice()
    elif choice == "3":
        print("Exiting...")
        sys.exit(0)
    else:
        print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    run()
