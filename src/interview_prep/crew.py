from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai_tools import SerperDevTool, ScrapeWebsiteTool


@CrewBase
class InterviewPrepCrew():
    """Crew for preparing for job interviews"""

    # Mantieni le annotazioni di tipo per il decoratore @CrewBase
    agents: List[BaseAgent]
    tasks: List[Task]

    def __init__(self):
        super().__init__()
        # Questo viene fatto nel decoratore ma assicuriamoci che sia inizializzato
        if not hasattr(self, 'agents'):
            self.agents = []
        if not hasattr(self, 'tasks'):
            self.tasks = []
        # Debug
        print(
            f"InterviewPrepCrew inizializzato con {len(self.agents)} agenti e {len(self.tasks)} task")

    @agent
    def research_agent(self) -> Agent:
        """Create a research agent with tools."""
        # Create agent WITHOUT referencing tools from config
        agent = Agent(
            config=self.agents_config['research_agent'],
            verbose=True
        )

        # Add tools directly to the agent
        agent.tools = [SerperDevTool(), ScrapeWebsiteTool()]

        return agent

    @agent
    def interview_coach(self) -> Agent:
        """Create an interview coach agent."""
        return Agent(
            config=self.agents_config['interview_coach'],
            verbose=True
        )

    @agent
    def interview_agent(self) -> Agent:
        """Create an interviewer agent."""
        return Agent(
            config=self.agents_config['interview_agent'],
            verbose=True
        )

    @task
    def research_company_task(self) -> Task:
        """Create a task to research the company."""
        return Task(
            config=self.tasks_config['research_company_task']
        )

    @task
    def research_person_task(self) -> Task:
        """Create a task to research the interviewer."""
        return Task(
            config=self.tasks_config['research_person_task']
        )

    @task
    def define_questions_task(self) -> Task:
        """Create a task to define interview questions."""
        task_config = self.tasks_config['define_questions_task'].copy()

        # Rimuovi l'output_file dalla configurazione se presente
        if 'output_file' in task_config:
            del task_config['output_file']

        return Task(
            config=task_config,
            context=[self.research_company_task(), self.research_person_task()]
        )

    @task
    def interview_prep_task(self) -> Task:
        """Create a task for interview preparation."""
        return Task(
            config=self.tasks_config['interview_prep_task'],
            context=[self.define_questions_task()]
        )

    @task
    def feedback_task(self) -> Task:
        """Create a task for feedback on interview answers."""
        return Task(
            config=self.tasks_config['feedback_task'],
            context=[self.interview_prep_task()]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Interview Preparation crew"""
        # Assicurati che agenti e task siano inizializzati
        if not self.agents or len(self.agents) == 0:
            self.agents = [self.research_agent(
            ), self.interview_coach(), self.interview_agent()]

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

    def research_crew(self) -> Crew:
        """Creates a crew specifically for research and question generation"""
        # Assicurati che gli agenti siano stati inizializzati
        if not self.agents or len(self.agents) == 0:
            self.agents = [self.research_agent(
            ), self.interview_coach(), self.interview_agent()]

        research_tasks = [
            self.research_company_task(),
            self.research_person_task(),
            self.define_questions_task()
        ]

        return Crew(
            agents=self.agents,
            tasks=research_tasks,
            process=Process.sequential,
            verbose=True,
        )

    def practice_crew(self) -> Crew:
        """Creates a crew specifically for interview practice"""
        # Assicurati che gli agenti siano stati inizializzati
        if not self.agents or len(self.agents) == 0:
            self.agents = [self.research_agent(
            ), self.interview_coach(), self.interview_agent()]

        practice_tasks = [
            self.interview_prep_task(),
            self.feedback_task()
        ]

        return Crew(
            agents=self.agents,
            tasks=practice_tasks,
            process=Process.sequential,
            verbose=True,
        )

    def feedback_crew(self) -> Crew:
        """Creates a crew specifically for feedback generation"""
        # Assicurati che gli agenti siano stati inizializzati
        if not self.agents or len(self.agents) == 0:
            self.agents = [self.research_agent(
            ), self.interview_coach(), self.interview_agent()]

        feedback_tasks = [
            self.feedback_task()
        ]

        return Crew(
            agents=self.agents,
            tasks=feedback_tasks,
            process=Process.sequential,
            verbose=True,
        )
