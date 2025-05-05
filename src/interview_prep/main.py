import os
import sys
from dotenv import load_dotenv
from interview_prep.crew import InterviewPrepCrew

# Load environment variables
load_dotenv()

# Default job description
DEFAULT_JOB_DESCRIPTION = """
About The Role Role Overview: At aitho, we are developing an innovative AI Personal 
Shopper designed to redefine the online shopping experience for buyers. Our aim is 
to provide an exceptional concierge service tailored to individual preferences and 
needs, revolutionizing how customers interact with Shop and Storefronts. Leveraging 
cutting-edge AI technology, including Large Language Models (LLM) and advanced machine 
learning algorithms, we will harness the power of data analytics and build upon the 
solid platform foundation of the Assistant projects in aitho. This enables us to deliver 
personalized recommendations, exclusive offers, and insightful suggestions that cater 
to each user's unique taste.

Our AI technology will analyze user behavior, preferences, and inventory levels in 
real-time, ensuring that shoppers receive highly relevant and customized suggestions. 
Our AI Personal Shopper will be an indispensable ally for every shopper, assisting 
with everything from curating outfits to finding the perfect gifts. To expedite this 
effort, we are seeking Machine Learning Engineering (MLE) leads and individual 
contributors to join our team and help shape the future of online shopping. Together, 
we will create an unparalleled shopping experience that exceeds customer expectations 
and redefines the e-commerce landscape.

You and your team won't just be working on theoretical concepts – you'll be at the 
forefront of implementing AI systems at scale, directly empowering our merchants. 
We're all about creating tangible solutions that make a real difference in the day 
to day lives of entrepreneurs.
"""


def sanitize_filename(name):
    """Remove or replace invalid characters for filenames."""
    import re
    # Replace problematic characters with underscore
    sanitized = re.sub(r'[\\/*?:"<>|,]', '_', str(name))
    # Remove extra spaces and trim if too long
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    # Limit maximum filename length
    max_length = 100
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    return sanitized


def run_research():
    """Run the research and question generation phase."""
    # Create output directory
    os.makedirs("output", exist_ok=True)

    print("\nStarting research and question generation...\n")

    company = "aitho.it"
    interviewer = "Carla Naselli"
    job_position = "ML Engineering, GenAI / AI Agent"

    print(f"Company: {company}")
    print(f"Interviewer: {interviewer}")
    print(f"Job Position: {job_position}")
    print("Using default job description")

    # Create crew for research only
    crew = InterviewPrepCrew().crew()
    crew.tasks = [task for task in crew.tasks if task.name in [
        "research_company_task",
        "research_person_task",
        "define_questions_task"
    ]]

    # Run crew with default inputs
    inputs = {
        'company': company,
        'interviewer': interviewer,
        'job_position': job_position,
        'industry': "AI and Technology",
        'job_description': DEFAULT_JOB_DESCRIPTION
    }

    result = crew.kickoff(inputs=inputs)

    # Save outputs to files
    for i, task_output in enumerate(result.tasks_output):
        if i == 0:  # Company research
            file_name = sanitize_filename(f"{company}_report.txt")
        elif i == 1:  # Interviewer research
            file_name = sanitize_filename(f"{interviewer}_report.txt")
        elif i == 2:  # Questions
            file_name = sanitize_filename(f"{job_position}_report.txt")
        else:
            continue

        file_path = os.path.join("output", file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(task_output.raw)
            print(f"Saved to: {file_path}")

    print("\nResearch and question generation complete!")
    print("Check the output directory for results.")


def run_practice():
    """Run the interview practice session."""
    # Create output directory for feedback
    os.makedirs(os.path.join("output", "feedback"), exist_ok=True)

    print("\nStarting interview practice...\n")

    # Load questions from file
    job_position = "ML Engineering, GenAI / AI Agent"
    file_name = sanitize_filename(f"{job_position}_report.txt")
    file_path = os.path.join("output", file_name)

    if not os.path.exists(file_path):
        print(f"No questions file found: {file_path}")
        print("Please run research first.")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse questions from markdown
        questions = []
        lines = content.split('\n')
        for line in lines:
            if line.startswith('- ') or line.startswith('* '):
                questions.append(line[2:].strip())

        if not questions:
            print("No questions found in the file.")
            return

        print(f"Loaded {len(questions)} questions.\n")

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

        question_num = 1
        # Limit to 5 questions for testing
        max_questions = min(5, len(questions))

        company = "aitho.it"
        interviewer = "Carla Naselli"

        for i in range(max_questions):
            question = questions[i]

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
                'job_position_report': question,
                'user_answer': answer
            }

            result = crew.kickoff(inputs=inputs)

            print("\n=== Feedback ===\n")
            print(result.raw)

            # Save feedback
            feedback_dir = os.path.join("output", "feedback")
            feedback_file = os.path.join(
                feedback_dir,
                f"question_{question_num}.md"
            )

            with open(feedback_file, 'w', encoding='utf-8') as f:
                f.write(f"# Question {question_num}\n\n")
                f.write(f"**Question:** {question}\n\n")
                f.write(f"**Your Answer:**\n\n{answer}\n\n")
                f.write(f"**Feedback:**\n\n{result.raw}\n")

            # Next question
            question_num += 1

            # Ask to continue
            cont = input("\nPress Enter to continue or type 'quit' to end: ")
            if cont.lower() == 'quit':
                break

        print("\nInterview practice complete!")
        print(f"Saved feedback to {feedback_dir}")

    except Exception as e:
        print(f"Error in practice session: {e}")


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
