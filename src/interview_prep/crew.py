from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators


@CrewBase
class InterviewPrepCrew():
    """Crew for preparing for job interviews"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def research_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['research_agent'],
            verbose=True,
            tools=[SerperDevTool(), ScrapeWebsiteTool()]
        )

    @agent
    def interview_coach(self) -> Agent:
        return Agent(
            config=self.agents_config['interview_coach'],
            verbose=True
        )

    @task
    def research_company_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_company_task']
        )

    @task
    def research_person_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_person_task']
        )

    @task
    def define_questions_task(self) -> Task:
        return Task(
            config=self.tasks_config['define_questions_task'],
            context=[self.research_company_task(), self.research_person_task()]
        )

    @task
    def interview_prep_task(self) -> Task:
        return Task(
            config=self.tasks_config['interview_prep_task'],
            context=[self.define_questions_task()]
        )

    @task
    def feedback_task(self) -> Task:
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
