# main.py

from promptpal.agent.agent_factory import AgentFactory
from promptpal.agent.agent_config import AgentConfig


def main():
    # Create agent factory
    factory = AgentFactory()

    # Create shared configuration
    config = AgentConfig(
        logging=True,
        verbose=True,
        model="gpt-4o-mini",
        temperature=0.7,
        use_chain_of_thought=True,
    )

    # Create developer agent for initial code generation
    developer_agent = factory.create_agent(config, role_name="developer")

    # Create code review agent using same thread
    reviewer_agent = factory.create_agent(config, role_name="refactor")
    reviewer_agent.client.thread = developer_agent.client.thread

    # Initial code generation request
    prompt = """
    Write Python code that calculates the GC content of an input DNA sequence.
    Requirements:
    - Function should accept a DNA string as input
    - Calculate percentage of G and C bases in the sequence
    - Handle invalid inputs appropriately
    - Include docstring and type hints
    - Add basic unit tests
    """

    initial_code = developer_agent.request(prompt)
    print("\n=== Initial Code Generation ===")
    print(initial_code)

    # Code review and optimization request
    review_prompt = f"""
    Review and optimize the following code implementation. Focus on:
    - Performance optimization
    - Error handling
    - Code style and documentation
    - Test coverage
    
    Code to review:
    {initial_code}
    """

    optimized_code = reviewer_agent.request(review_prompt)
    print("\n=== Code Review and Optimization ===")
    print(optimized_code)


if __name__ == "__main__":
    main()
