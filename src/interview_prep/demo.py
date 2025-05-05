#!/usr/bin/env python
import os
import time
import re  # Add explicit import for re module
from dotenv import load_dotenv
from interview_prep.crew import InterviewPrepCrew

# Load environment variables
load_dotenv()

# Default values
COMPANY = "aitho.it"
INTERVIEWER = "Carla Naselli"
JOB_POSITION = "ML Engineering, GenAI / AI Agent"
INDUSTRY = "AI and Technology"  # Define INDUSTRY as a constant
JOB_DESCRIPTION = """
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
    # Replace problematic characters with underscore
    sanitized = re.sub(r'[\\/*?:"<>|,]', '_', str(name))
    # Remove extra spaces and trim if too long
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    # Limit maximum filename length
    max_length = 100
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    return sanitized


def run_demo():
    """Run a complete demo of the interview preparation system."""
    # Create output directory
    os.makedirs("output", exist_ok=True)
    os.makedirs(os.path.join("output", "feedback"), exist_ok=True)

    print("\n=== INTERVIEW PREPARATION DEMO ===\n")
    print(f"Company: {COMPANY}")
    print(f"Interviewer: {INTERVIEWER}")
    print(f"Job Position: {JOB_POSITION}")
    print("Using simplified job description for demo")

    # Step 1: Research phase
    print("\n=== STEP 1: RESEARCH PHASE ===\n")

    # Create research crew
    research_crew = InterviewPrepCrew().crew()
    research_crew.tasks = [task for task in research_crew.tasks if task.name in [
        "research_company_task",
        "research_person_task",
        "define_questions_task"
    ]]

    # Run research crew
    research_inputs = {
        'company': COMPANY,
        'interviewer': INTERVIEWER,
        'job_position': JOB_POSITION,
        'industry': INDUSTRY,  # Include industry parameter
        'job_description': JOB_DESCRIPTION
    }

    try:
        research_result = research_crew.kickoff(inputs=research_inputs)

        # Save research outputs
        company_report = research_result.tasks_output[0].raw
        interviewer_report = research_result.tasks_output[1].raw
        questions_report = research_result.tasks_output[2].raw

        # Use sanitized filenames
        company_file = os.path.join(
            "output", sanitize_filename(f"{COMPANY}_report.md"))  # Use .md extension instead of .txt
        interviewer_file = os.path.join(
            "output", sanitize_filename(f"{INTERVIEWER}_report.md"))  # Use .md extension
        questions_file = os.path.join(
            "output", sanitize_filename(f"{JOB_POSITION}_questions.md"))  # Use .md extension and "_questions" suffix

        with open(company_file, 'w', encoding='utf-8') as f:
            f.write(company_report)

        with open(interviewer_file, 'w', encoding='utf-8') as f:
            f.write(interviewer_report)

        with open(questions_file, 'w', encoding='utf-8') as f:
            f.write(questions_report)

        print(f"Research outputs saved to output directory")

        # Parse questions using a regular expression for numbered lists
        # This pattern looks for lines like "1. Question text" or "20. Question text"
        questions = []
        numbered_pattern = re.compile(r'^\d+\.\s+(.+)$', re.MULTILINE)
        numbered_matches = numbered_pattern.findall(questions_report)
        questions = [match for match in numbered_matches]

        print(f"Found {len(questions)} questions in the report")

    except Exception as e:
        print(f"Error in research phase: {e}")
        # Create some sample questions for demo purposes if research fails
        questions = [
            "Tell me about your experience with machine learning models and AI systems.",
            "How do you approach complex challenges in AI development?",
            "How do you stay current with the rapidly evolving field of AI?"
        ]
        print("Using sample questions for demo purposes.")

    # Step 2: Practice phase
    print("\n=== STEP 2: INTERVIEW PRACTICE ===\n")

    if not questions:
        print("No questions available. Demo cannot continue.")
        return

    print(f"Using {len(questions)} interview questions")

    # Select a few questions for demo
    demo_questions = questions[:3]  # Just use the first 3 questions

    # Sample answers for demo
    sample_answers = [
        "I have extensive experience with machine learning models, particularly in fine-tuning LLMs. In my previous role, I implemented a recommendation system that increased user engagement by 25%.",
        "I'm passionate about using AI to solve real-world problems. My approach to challenges is to break them down into manageable components and address each systematically.",
        "I stay current with AI developments by reading research papers, participating in online communities, and implementing new techniques in side projects."
    ]

    # Create practice crew
    practice_crew = InterviewPrepCrew().crew()
    practice_crew.tasks = [task for task in practice_crew.tasks if task.name in [
        "interview_prep_task",
        "feedback_task"
    ]]

    # Run practice for each question
    for i, (question, answer) in enumerate(zip(demo_questions, sample_answers)):
        question_num = i + 1

        print(f"\nQuestion {question_num}: {question}")
        print(f"\nSample Answer: {answer}")

        # Get feedback
        practice_inputs = {
            'company': COMPANY,
            'interviewer': INTERVIEWER,
            'job_position': JOB_POSITION,
            'industry': INDUSTRY,  # Include industry parameter
            'job_position_report': question,  # This is needed for interview phase
            'user_answer': answer
        }

        try:
            print("\nGetting AI feedback...")
            feedback_result = practice_crew.kickoff(inputs=practice_inputs)

            print("\n=== Feedback ===\n")
            print(feedback_result.raw)

            # Save feedback
            feedback_file = os.path.join(
                "output", "feedback", f"question_{question_num}_demo.md")

            with open(feedback_file, 'w', encoding='utf-8') as f:
                f.write(f"# Question {question_num}\n\n")
                f.write(f"**Question:** {question}\n\n")
                f.write(f"**Sample Answer:**\n\n{answer}\n\n")
                f.write(f"**Feedback:**\n\n{feedback_result.raw}\n")

        except Exception as e:
            print(f"Error getting feedback for question {question_num}: {e}")

        # Small delay between questions
        if i < len(demo_questions) - 1:
            print("\nMoving to next question...")
            time.sleep(2)

    print("\n=== DEMO COMPLETE ===\n")
    print("All outputs have been saved to the output directory:")
    print(f"- Company research: {company_file}")
    print(f"- Interviewer research: {interviewer_file}")
    print(f"- Interview questions: {questions_file}")
    print(f"- Feedback on sample answers: output/feedback/")


if __name__ == "__main__":
    run_demo()
