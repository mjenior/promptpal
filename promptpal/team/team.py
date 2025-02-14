# promptpal/team/team.py

from dataclasses import dataclass
from typing import List


from promptpal.agent import Agent, AgentFactory
from promptpal.team.coach import Coach


@dataclass
class TeamConfig:
    strategy: str = "coach"  # options, coach, more to come....


class Team:
    """
    A Team represents a group of Agents that work together with a shared context.
    """

    def __init__(self, client, agents: List[Agent], config: TeamConfig):
        self._agents = agents
        self._strategy = config.strategy
        self._thread = None
        self._coach = Coach()

    def chat(self, query: str):
        best_agent_idx = self.coach.select_best_agent(query)
        best_agent = self._agents[best_agent_idx]
        best_agent.handle_request(query)
