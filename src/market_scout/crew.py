from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from .tools.stock_screen_tool import stock_screener_tool
# from .tools.candidate_selection_tool import select_research_candidates
from .tools.serper_search_tool import serper_search
from .models import ResearchReport
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class MarketScout():
    """MarketScout crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def stock_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['stock_researcher'], # type: ignore[index]
            verbose=True, 
            tools=[
                stock_screener_tool],
        )

    @agent
    def company_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['company_researcher'], # type: ignore[index]
            verbose=True, tools=[serper_search],
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def screen_stocks_task(self) -> Task:
        return Task(
            config=self.tasks_config['screen_stocks_task'], # type: ignore[index]
        )
    
    @task
    def select_candidates_task(self) -> Task:
        return Task(
            config=self.tasks_config['select_candidates_task'], # type: ignore[index]
        )

    @task
    def research_companies_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_companies_task'], # type: ignore[index]
            output_pydantic=ResearchReport
        )

    @crew
    def crew(self) -> Crew:
        """Creates the MarketScout crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
