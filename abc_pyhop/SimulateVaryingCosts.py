"""
This reproduces the baseline with parameters:
    PLANNER: Any planner
    MODEL: no-comm, full-comm, smart-comm, or more
    MAX_COST: 100
    COC: range(50)
    Input: Fix Board-Size
"""

# from __future__ import print_function
from simulate_rovers_world import *
import problem_bank, time, logging
import models
import random_rovers_world as rrw
from planners import * 
import numpy as np
import matplotlib.pyplot as plt


"""
Logging
"""
logger = logging.getLogger("experiment_logger")
channel = logging.StreamHandler()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
channel.setFormatter(formatter)
logger.addHandler(channel)


"""
Knobes to Turn
"""
show_summary = True
BOARD_X = 7
BOARD_Y = 7
GUI = False


"""
Pick which Models to compare
"""
MODELS = []
MODELS += [models.AgentNoComm]
MODELS += [models.AgentSmartComm]
# MODELS += [models.AgentSmartCommII]
MODELS += [models.AgentRandComm]
MODELS += [models.AgentFullComm]


"""
Pick which Planners to use
"""
PLANNERS = []
PLANNERS += [Planner.get_HPlanner_v14()] # Quick sampling using A* NOT Random
# PLANNERS += [Planner.get_HPlanner_v15()] # Quick sampling using A* Random
# PLANNERS += [Planner.get_HPlanner_v13()] # Quick Sampling no A*
# PLANNERS += [Planner.get_HPlanner_bb()]

"""
Cost of Communication
"""
# COSTS = range(30)
COSTS = [1, 4, 8, 12, 16]

"""
Choose any problem from problem bank
"""
PROBLEMS = []
NUM_PROBLEMS = 10
    

def SimulateVaryingCosts(BOARD_X, BOARD_Y):
    PROBLEMS = [rrw.make_random_problem(BOARD_X, BOARD_Y, \
        name=str(time.time()) + '.' + str(i)) for i in range(NUM_PROBLEMS)]

    for PLANNER in PLANNERS:
        # Each planner result in a different plot

        simulations = {}
        plot_lines = {}
        for AGENT_TYPE in MODELS:
            # Each agent is a line in the plot
            line_name = AGENT_TYPE.__name__ + PLANNER.name
            logger.info("*** Running simulations for [MODEL: {}]".format(line_name))
            
            simulations[line_name] = {}
            plot_lines[line_name] = (COSTS, []) # X, Y

            for COC in COSTS:
                # Each cost is a data point
                sys.stdout.write('COST : {}\t'.format(COC))
                sys.stdout.flush()

                simulations[line_name][COC] = []
                costs = 0
                for PROBLEM in PROBLEMS:
                    # Each point is the average over all problems
                    PROBLEM.COST_OF_COMM = COC
                    PROBLEM.COST_REPLAN = 0

                    # Run
                    simulation = Simulation(PROBLEM, AGENT_TYPE, PLANNER, gui=GUI)
                    simulation.run()
                    
                    # Do not include simulation if there is no solution
                    if simulation.get_total_cost() > sys.maxint/2: 
                        continue

                    # Add
                    simulations[line_name][COC].append(simulation)
                    costs += simulation.get_total_cost()
                    # logger.info(simulation.get_summary(cost=True, cost_bd=False, obs=False, comm=True, void=True))

                    sys.stdout.write('>')
                    sys.stdout.flush()

                avg_cost = costs * 1.0 / len(simulations[line_name][COC])
                plot_lines[line_name][1].append(avg_cost)

                sys.stdout.write('\n')
                sys.stdout.flush()


        logger.info("Plot Lines: {}".format(plot_lines))
        lines = []
        for (name, line) in plot_lines.items():
            lines.append(plt.plot(line[0], line[1], label=name))

        plt.legend(loc='lower right')    
        plt.xlabel("Cost of Communication")
        plt.ylabel("Average Costs over {} Random Problems".format(NUM_PROBLEMS))
        plt.title('Planner:{} Board-Size:{}'.format(PLANNER.planner.__name__, BOARD_X*BOARD_Y))

        plt.setp(lines, linewidth=2.0)

        # write simulation parameters to file.
        filename = "images/SimulateVaryingCosts_{}".format(time.time()%1000)
        plt.savefig(filename+".png")

        plt.show()


SimulateVaryingCosts(BOARD_X, BOARD_Y)


