# main_team.py

from promptpal.agent import AgentFactory
from promptpal.team import Team, TeamConfig


# Example of creating and using a team of agents to solve a coding task.
# Scratch Delete Before Merge

def main():

    # Need to rework this, not sure if the team should take in the agent names and a factory or
    # the actual agent objects. Probbably the agent objects, easier to test and we have the widget
    # for ergonomics. TODO

    factory = AgentFactory()

    team = Team(
        agents=['developer', 'data_visualization', 'unit_test', 'writer'],
        factory = AgentFactory()
        config=TeamConfig(),
    )

    team.chat("Think of a number between 1 and 10")
    team.chat("Write a python function that takes in an input number and then adds it to the number you came up with.")
    
    team.new_thread()
    
    team.chat("What was the number you came up with before?")


if __name__ == '__main__':
    main()