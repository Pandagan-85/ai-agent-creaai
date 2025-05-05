import os
from interview_prep.crew import InterviewPrepCrew


def run():
    """
    Run the interview preparation crew.
    """
    inputs = {
        'company': "aitho.it",
        'interviewer': "Carla Naselli",
        'job_position': "ML Engineering, GenAI / AI Agent",
        'industry': "AI and Technology",
        'job_description': """
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

Key outputs:
- Developing and deploying Generative AI, natural language processing and machine learning models
- Producing system design and architecture of scalable AI/ML systems
- Designing and implementing data pipelines for fine-tuning LLMs
- Solving high impact data problems and delivering business impact through data and machine learning products
- Prioritizing and communicating to technical and non-technical audiences alike

Qualifications:
- Demonstrated mastery building data products that use generative AI, RLHF and fine-tuning LLMs
- End-to-end experience of training, evaluating, testing and deploying machine learning products at scale
- Experience building data pipelines and driving ETL design decisions leveraging disparate data sources
- Experience with the following: Python, shell scripting, streaming and batch data pipelines, vector databases, DBT, BigQuery, BigTable or equivalent, orchestration tools
- Experience with running machine learning in parallel environments (e.g. distributed clusters, GPU optimization)

This role may require on-call work

About aitho
Opportunity is not evenly distributed. aitho puts independence within reach for anyone 
with a dream to start a business. We propel entrepreneurs and enterprises to scale the 
heights of their potential. Since 2006, we've grown to over 8,300 employees and 
generated over $1 trillion in sales for millions of merchants in 175 countries. This 
is life-defining work that directly impacts people's lives as much as it transforms 
your own. This is putting the power of the few in the hands of the many, is a future 
with more voices rather than fewer, and is creating more choices instead of an elite option.

About You
Moving at our pace brings a lot of change, complexity, and ambiguity—and a little bit 
of chaos. aitho folk thrive on that and are comfortable being uncomfortable. That means 
aitho is not the right place for everyone. Before you apply, consider if you can:
- Care deeply about what you do and about making commerce better for everyone
- Excel by seeking professional and personal hypergrowth
- Keep up with an unrelenting pace (the week, not the quarter)
- Be resilient and resourceful in face of ambiguity and thrive on (rather than endure) change
- Bring critical thought and opinion
- Use AI tools reflexively as part of your fundamental workflow
- Embrace differences and disagreement to get shit done and move forward
- Work digital-first for your daily work
        """
    }

    # Run the crew
    result = InterviewPrepCrew().crew().kickoff(inputs=inputs)
    print(result)


if __name__ == "__main__":
    run()
