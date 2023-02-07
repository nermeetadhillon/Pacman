
from pacman import Directions
from game import Agent, Actions
from pacmanAgents import LeftTurnAgent


class TimidAgent(Agent):
    """
    A simple agent for PacMan
    """

    def __init__(self):
        super().__init__()  # Call parent constructor
        # Add anything else you think you need here

    def inDanger(self, pacman, ghost, dist=3):
        """inDanger(pacman, ghost) - Is the pacman in danger
        For better or worse, our definition of danger is when the pacman and
        the specified ghost are:
           in the same row or column,
           the ghost is not scared,
           and the agents are <= dist units away from one another

        If the pacman is not in danger, we return Directions.STOP
        If the pacman is in danger we return the direction to the ghost.
        """

        # Your code
        if pacman.getPosition()[0] == ghost.getPosition()[0]:
            if abs(ghost.getPosition()[1] - pacman.getPosition()[1]) > 3 or ghost.isScared():
                return Directions.STOP
            elif ghost.getPosition()[1] > pacman.getPosition()[1]:
                return Directions.NORTH
            else:
                return Directions.SOUTH
        elif pacman.getPosition()[1] == ghost.getPosition()[1]:
            if abs(ghost.getPosition()[0] - pacman.getPosition()[0]) > 3 or ghost.isScared():
                return Directions.STOP
            elif ghost.getPosition()[0] > pacman.getPosition()[0]:
                return Directions.EAST
            else:
                return Directions.WEST
        else:
            return Directions.STOP
        #raise NotImplemented




    def getAction(self, state):
        """
        state - GameState
        
        Fill in appropriate documentation
        """
        # Get the agent's state from the game state and find agent heading
        legal = state.getLegalPacmanActions ()
        agentState = state.getPacmanState ()
        heading = agentState.getDirection ()
        ghosts = state.getGhostStates ()

        danger_found = False
        danger_heading = None
        for ghost in ghosts:
            danger_heading = self.inDanger (agentState, ghost)
            if danger_heading != Directions.STOP:
                danger_found = True
                break

        if danger_found:
            if Directions.REVERSE[danger_heading] in legal:
                action = Directions.REVERSE[danger_heading]
            elif Directions.LEFT[danger_heading] in legal:
                action = Directions.LEFT[danger_heading] # Turn left
            elif Directions.RIGHT[danger_heading] in legal:
                action = Directions.RIGHT[danger_heading]# Turn right
            else:
                action = Directions.STOP  # Can't move!
        else:
            # List of directions the agent can choose from
            legal = state.getLegalPacmanActions()

            agentState = state.getPacmanState ()
            heading = agentState.getDirection ()

            if heading == Directions.STOP:
                # Pacman is stopped, assume North (true at beginning of game)
                heading = Directions.NORTH

            # Turn left if possible
            left = Directions.LEFT[heading]  # What is left based on current heading
            if left in legal:
                action = left
            else:
                # No left turn
                if heading in legal:
                    action = heading  # continue in current direction
                elif Directions.RIGHT[heading] in legal:
                    action = Directions.RIGHT[heading]  # Turn right
                elif Directions.REVERSE[heading] in legal:
                    action = Directions.REVERSE[heading]  # Turn around
                else:
                    action = Directions.STOP  # Can't move!
        return action
