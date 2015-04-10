"""
This simulation should highlight the need for better synced mental models 
when the length of the plan is longer. 
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
GUI = False


"""
Board Size - Indicates length of the tasks
"""
BOARD_SIDES = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15]


"""
Pick which Models to compare
"""
MODELS = []
MODELS += [models.AgentNoComm]
MODELS += [models.AgentSmartComm]
MODELS += [models.AgentSmartCommII]
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
COC = 10

"""
Choose any problem from problem bank
"""
PROBLEMS = []
NUM_PROBLEMS = 100
    
def SimulateVaryingBoard(COC):
    lines = []
    base_line = None
    base_line_name = None
    for PLANNER in PLANNERS:
        # Each planner result in a different plot
        simulations = {}
        plot_lines = {}

        # First make the same set of NUM_PROBLEMS for a given Board-size for all models
        PROBLEMS_dict = {}
        for SIDE in BOARD_SIDES:
            PROBLEMS_dict[SIDE] = [rrw.make_random_problem(SIDE, SIDE, \
                name=str(time.time()) + '.' + str(i)) for i in range(NUM_PROBLEMS)]


        for AGENT_TYPE in MODELS:
            # Each agent is a line in the plot
            line_name = AGENT_TYPE.__name__ + PLANNER.name
            logger.info("*** Running simulations for [MODEL: {}]".format(line_name))
                    
            simulations[line_name] = {}
            cur_line = ([x * x for x in BOARD_SIDES], []) # X, Y

            for SIDE in BOARD_SIDES:
                # Each cost is a data point
                sys.stdout.write('SIDE : {}\t'.format(SIDE))
                sys.stdout.flush()

                simulations[line_name][COC] = []
                costs = 0

                for PROBLEM in PROBLEMS_dict[SIDE]:
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
                cur_line[1].append(avg_cost)

                sys.stdout.write('\n')
                sys.stdout.flush()

            if base_line == None:
                plot_lines[line_name] = cur_line
                base_line_name = line_name
                base_line = plot_lines[line_name]
            else:
                plot_lines[line_name] = (cur_line[0], [x-y for x, y in zip(cur_line[1], base_line[1])])

        # Renormalizing based on the no-comm baseline.
        plot_lines[base_line_name] = ([x * x for x in BOARD_SIDES], [0]*len(BOARD_SIDES))  
        

        # Plot lines
        logger.info("Plot Lines: {}".format(plot_lines))
        for (name, line) in plot_lines.items():
            lines.append(plt.plot(line[0], line[1], label=name))

        # Adjust Plotting
        plt.legend(loc='lower right')    
        plt.xlabel("Board Size")
        plt.ylabel("Average Costs over {} Random Problems".format(NUM_PROBLEMS))
        plt.title('Planner:{} COC:{}'.format(PLANNER.planner.__name__, COC))
        plt.setp(lines, linewidth=2.0)
        plt.savefig("images/SimulateVaryingBoardSize_{}.png".format(time.time()%1000))
        plt.show()



SimulateVaryingBoard(COC)


