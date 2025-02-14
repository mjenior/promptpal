from typing import List

from promptpal.agent import AgentConfig, AgentRole, Agent
from promptpal.clients import Client


class Coach(Agent):
    """
    Specialized agent that is use to manage other agents.
    """

    def __init__(
        self, role: AgentRole, config: AgentConfig, client: Client, agents: List[Agent]
    ):
        super().__init__(role=role, config=config, client=client)
        self._agents = agents

    def select_best_agent(self, query: str) -> Agent:
        """
        Evaluates the query and determines which agent from the available agent roles is best suited
        to handle the query.

        Args:
            query (str): The user's query/prompt to be evaluated

        Returns:
            Agent: The most suitable agent to handle the query

        Raises:
            ValueError: If no agents are available or if no suitable agent is found
        """
        if not self._agents:
            raise ValueError("No agents available for query evaluation")

        # Create a prompt to evaluate which agent role best matches the query
        evaluation_prompt = f"""
        Given the following query: "{query}"
        
        And these available agent roles:
        {[agent.role.description for agent in self._agents]}
        
        Determine which role is best suited to handle this query. Consider the expertise and 
        responsibilities of each role. Return only the index number (0-{len(self._agents) - 1}) 
        of the most suitable role."""

        # Use the coach's LLM client to evaluate the best agent
        response = self.client.complete(evaluation_prompt)

        try:
            best_agent_index = int(response.strip())
            if 0 <= best_agent_index < len(self._agents):
                return self._agents[best_agent_index]
            raise ValueError("Invalid agent index returned by LLM")
        except (ValueError, IndexError):
            # Fallback to the first agent if parsing fails
            return self._agents[0]
