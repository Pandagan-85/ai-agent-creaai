from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai_tools import SerperDevTool, ScrapeWebsiteTool


@CrewBase
class InterviewPrepCrew():
    """Crew for preparing for job interviews"""

    agents: List[BaseAgent]
    tasks: List[Task]

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
        return Task(
            config=self.tasks_config['define_questions_task'],
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
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
