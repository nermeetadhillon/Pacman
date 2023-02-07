import unittest
import argparse
import sys

import textDisplay
#from myAgents import TimidAgent  # student attempt
from solutionAgents import GoldTimidAgent  # gold standard agent
from ghostAgents import RandomGhost
from pacman import readCommand, ClassicGameRules, Directions
from collections import namedtuple

# Agent test.  With pacman positioned at position (x,y)
# and a current direction of currdir, what is the new
# direction (action)?
# Assumes any ghosts have been appropriately positioned.
LeftTrn = namedtuple('LeftTrnTyp', ('position', 'dir', 'action'))

# danger test.  Given pacman, ghost position, scared state (bool), distance
# threshold, and direction from which danger is coming.
InDanger = namedtuple('InDangerTyp',
                      ('pacman', 'ghost', 'scared', 'dist', 'danger'))

# action test.  Same types as InDanger, but we add the pacman direction
# as it is relevant to the outcome and change the danger direction to the
# action selected
StatefulAction = namedtuple('StatefulActionTyp',
                            ('pacman', 'pacdir',
                             'ghost', 'scared',
                             'dist', 'action'))

# Gradescope modules
import gradescope_utils.autograder_utils.json_test_runner as jsn
import gradescope_utils.autograder_utils.decorators as dec

class testProgram(unittest.TestCase):

    # This is poor form, but we want to be able to invoke the test with
    # different arguments which we will communicate throught this class
    # variable.
    argstr = ""

    def setUp(self):
        "setUp() - Initialize a Pacman board for testing"

        # Set up game arguments
        self.args = readCommand(self.argstr)


        # Initialize the agents
        self.studentAgent = self.args['pacman']
        self.goldAgent = GoldTimidAgent()

        #layout, pacmanAgent, ghostAgents, display, quiet, catchExceptions
        self.rules = ClassicGameRules(self.args['timeout'])


        self.dist = 3

    def initGame(self):
        "initGame() - Initialize game, returns game and game state"
        game = self.rules.newGame(self.args['layout'],
                                       self.studentAgent,
                                       self.args['ghosts'],
                                       self.args['display'])
        # Get game state
        return game, game.state

    TurnLeftAgentPoints = 30.0
    @dec.partial_credit(TurnLeftAgentPoints)
    def testTurnLeftAgent(self, set_score=None):
        "Ensure left turn behavior when Pacman not in danger"
        game, gstate = self.initGame()

        ghosts = gstate.getGhostStates()
        pacman = gstate.getPacmanState()

        # Check left turn behavior at several positions
        # We ensure that none of the conditions that would permit TimidAgent
        # to change behavior occur.
        resultstr = "At (%d,%d) with direction %s: expected %s, not %s"
        tests = (
            LeftTrn((5, 9), Directions.STOP, Directions.WEST),
            LeftTrn((9, 9), Directions.EAST, Directions.NORTH),
            LeftTrn((4, 7), Directions.SOUTH, Directions.EAST),
            LeftTrn((6, 1), Directions.NORTH, Directions.EAST),
            LeftTrn((3, 7), Directions.WEST, Directions.SOUTH),
            LeftTrn((1, 2), Directions.SOUTH, Directions.SOUTH)
        )

        testsN = len(tests)
        passed, failed = [], []
        for test in tests:
            # Set the pacman state
            cfg = pacman.configuration
            cfg.setPosition(test.position)
            cfg.setDirection(test.dir)
            # Determine what the next action will be
            action = self.studentAgent.getAction(gstate)
            goldAction = self.goldAgent.getAction(gstate)

            outcome = (resultstr%(test.position[0], test.position[1],
                                  test.dir, action, goldAction))

            if action == goldAction:
                passed.append(outcome)
            else:
                failed.append(outcome)

        # Determine number of points awarded
        set_score(self.TurnLeftAgentPoints -
                  len(failed)  * self.TurnLeftAgentPoints / len(tests))
        if len(failed) > 0:
            self.fail("Agent should have exhibited TurnLeftAgent behavior.\n" +
                      "Given a pristine board and only moving the pacman: \n" +
                      "\n".join(failed))


    InDangerPoints = 30.0
    @dec.partial_credit(InDangerPoints)
    def testInDanger(self, set_score=None):
        "Ensure inDanger tests for Pacman in danger work correctly"

        game, gstate = self.initGame()

        ghost = gstate.getGhostStates()[0]  # first ghost
        pacman = gstate.getPacmanState()

        # Check left turn behavior at several positions
        # We ensure that none of the conditions that would permit TimidAgent
        # to change behavior occur.
        resultstr = "At (%d,%d) with direction %s: expected %s, not %s"

        tests = (
            # pacman might get eaten
            InDanger((1, 1), (3, 1), False, 2, Directions.EAST),
            # pacman giving chase to a scared ghost
            InDanger((1, 1), (3, 1), True, 3, Directions.STOP),
            # not on same row/col
            InDanger((3, 3), (4, 2), False, 3, Directions.STOP),
            # same row, close enough
            InDanger((11, 3), (8, 3), False, 3, Directions.WEST),
            # same row too far
            InDanger((12, 3), (8, 3), False, 3, Directions.STOP),
            # danger from the south
            InDanger((3,7), (3,5), False, 2, Directions.SOUTH)
        )

        # Get agent states and configurations
        pacmanState = gstate.getPacmanState()
        ghostState = gstate.getGhostStates()[0]
        pacmanCfg = pacmanState.configuration
        ghostCfg = ghostState.configuration

        testN = len(tests)
        passed, failed = [], []
        scared_time = 10  # Make ghosts scared for N clock ticks

        msg = "Pacman at (%d,%d), %s ghost at (%d,%d), reported %s expected %s"
        for test in tests:
            # Set the pacman and ghost states based on the test
            pacmanCfg.setPosition(test.pacman)
            ghostCfg.setPosition(test.ghost)
            if test.scared:
                ghostState.scaredTimer = scared_time
            else:
                ghostState.scaredTimer = 0

            dir = self.studentAgent.inDanger(pacmanState, ghostState)
            result = msg%(test.pacman[0], test.pacman[1],
                          "fleeing" if test.scared else "chasing",
                          test.ghost[0], test.ghost[1],
                          dir, test.danger)
            if dir == test.danger:
                passed.append(result)
            else:
                failed.append(result)


        # Determine number of points awarded
        failedN = len(failed)
        set_score(self.InDangerPoints -
                  failedN * self.InDangerPoints / len(tests))
        if failedN > 0:
            self.fail("Agent reported incorrect inDanger direction:\n" +
                      "\n".join(failed))

    ActionPoints = 20.0
    @dec.partial_credit(ActionPoints)
    def test_getAction(self, set_score=None):
        """Ensure that getAction() returns expected behaviror
        The basic behavior of the agent has already been tested,
        the following simply ensures that the action taken based on when
        a Pacman might be in danger is correct.
        """
        game, gstate = self.initGame()

        ghost = gstate.getGhostStates()[0]  # first ghost
        pacman = gstate.getPacmanState()

        # Check left turn behavior at several positions
        # We ensure that none of the conditions that would permit TimidAgent
        # to change behavior occur.
        msg = "Pacman at (%d,%d) traveling %s, %s ghost at (%d,%d), " + \
              "getAction: %s, expected %s"
        tests = (
            # pacman might get eaten
            StatefulAction((1, 1), Directions.EAST,
                           (3, 1), False, 2, Directions.NORTH),
            # pacman giving chase to a scared ghost
            StatefulAction((2, 1), Directions.EAST,
                           (3, 1), True, 3, Directions.EAST),
            # not on same row/col
            StatefulAction((3, 3), Directions.NORTH,
                           (4, 2), False, 3, Directions.NORTH),
            # agent takes available left turn
            StatefulAction((3, 3), Directions.EAST,
                           (4, 2), False, 3, Directions.NORTH),
            # same row, close enough
            StatefulAction((11, 3), Directions.WEST,
                           (8, 3), False, 3, Directions.EAST),
            # same row too far
            StatefulAction((12, 3), Directions.WEST,
                           (8, 3), False, 3, Directions.WEST),
            # danger from the west, forced U-turn
            StatefulAction((13,9), Directions.NORTH,
                           (11, 9), False, 2, Directions.SOUTH),
            # same situation giving chase
            StatefulAction((13, 9), Directions.NORTH,
                (11, 9), True, 2, Directions.WEST)
        )

        # Get agent states and configurations
        pacmanState = gstate.getPacmanState()
        ghostState = gstate.getGhostStates()[0]
        pacmanCfg = pacmanState.configuration
        ghostCfg = ghostState.configuration

        testN = len(tests)
        passed, failed = [], []
        scared_time = 10  # Make ghosts scared for N clock ticks

        msg = "Pacman at (%d,%d) moving %s, %s ghost at (%d,%d), getAction: %s expected %s"
        for test in tests:
            # Set the pacman and ghost states based on the test
            pacmanCfg.setPosition(test.pacman)
            pacmanCfg.setDirection(test.pacdir)
            ghostCfg.setPosition(test.ghost)
            if test.scared:
                ghostState.scaredTimer = scared_time
            else:
                ghostState.scaredTimer = 0

            dir = self.studentAgent.getAction(gstate)
            result = msg%(test.pacman[0], test.pacman[1], test.pacdir,
                          "fleeing" if test.scared else "chasing",
                          test.ghost[0], test.ghost[1],
                          dir, test.action)
            if dir != test.action:
                failed.append(result)
            else:
                passed.append(result)

        # Determine number of points awarded
        failedN = len(failed)
        set_score(self.ActionPoints -
                  failedN * self.ActionPoints / len(tests))
        if failedN > 0:
            self.fail("Agent reported incorrect getAction direction:\n" +
                      "\n".join(failed))










if __name__ == "__main__":

    # Argument parsing
    parser = argparse.ArgumentParser(description = "Test program functionality")
    parser.add_argument('--runner', dest="testrunner", choices=['json', 'text'], default='text')
    args = parser.parse_known_args()

    # Set up test suite
    testProgram.argstr = args[1]  # test case will use this initiialization
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(testProgram)

    # Run appropriate test runner
    #pdb.set_trace()
    jsonfile = '/autograder/results/results.json'
    if args[0].testrunner == "json":
        #with open(jsonfile, 'w') as f:
        with sys.stdout as f:
            jsn.JSONTestRunner(verbosity=2, stream=f).run(suite)
    else:
        unittest.TextTestRunner(verbosity=2).run(suite)



