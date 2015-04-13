"""
Runs various simulations with different agent mental models
For each world, we want to run simulation for multiple agent types

The experiment environment needs to make sure that the same problem and the same
uncertainties are applied to all simulations
"""

# from __future__ import print_function
from simulate_rovers_world import *
import problem_bank, time, logging
import models
import random_rovers_world as rrw
from planners import * 
import numpy as np
import matplotlib.pyplot as plt

""" *************** Simple simulaiton for 1 agent-type, 1 problem ****************
Navigation: maze_1, ... maze_5
navigate_replan_team    - Different Agent Models will behave differently.
navigate_replan
decompose_replan        - Test Method definition such that agent doesn't start over.
random                  - Need to set uncertainty parameter

To run a simulation with GUI
simulation = Simulation(problem_bank.decompose_replan(), AgentNoComm, Planner.get_HPlanner_v14(),
                      gui=True)
Or without GUI:
simulation.run()
"""


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
Board Size - Indicates length of the tasks
"""
BOARD_SIDES = [7, 9, 11, 13]


"""
Pick which Models to compare
"""
MODELS = []
# MODELS += [models.AgentNoComm]
MODELS += [models.AgentSmartComm]
# MODELS += [models.AgentSmartCommII]
# MODELS += [models.AgentRandComm]
# MODELS += [models.AgentFullComm]


"""
Pick which Planners to use
"""
PLANNERS = []
# PLANNERS += [Planner.get_HPlanner_v14()] # Quick sampling using A* NOT Random
PLANNERS += [Planner.get_HPlanner_v15()] # Quick sampling using A* Random
# PLANNERS += [Planner.get_HPlanner_v13()] # Quick Sampling no A*
# PLANNERS += [Planner.get_HPlanner_bb()]
PLANNERS += [Planner.get_HPlanner_bb_prob()] # Reason with expected cost of communication

"""
Cost of Communication
"""
# COSTS = range(50)
COSTS = [1, 3, 9, 12]
COC = 1

"""
Choose any problem from problem bank
"""
PROBLEMS = []
NUM_PROBLEMS = 10
    

"""
Simulation Functions
"""
def write_params_to_file(filename, simulations, plot_lines):
    # f = open(filename)
    # f.write(PLANNERS)
    pass

def SimulateVaryingCosts(BOARD_X, BOARD_Y):
    PROBLEMS = [rrw.make_random_problem(BOARD_X, BOARD_Y, \
        name=str(time.time()) + '.' + str(i)) for i in range(NUM_PROBLEMS)]
    
    lines = []
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
    write_params_to_file(filename+".params", simulations, plot_lines)

    plt.show()


def SimulateVaryingBoard(COC):
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
            plot_lines[line_name] = ([x * x for x in BOARD_SIDES], []) # X, Y

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

                    sys.stdout.write('>\t')
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
        plt.xlabel("Board Size")
        plt.ylabel("Average Costs over {} Random Problems".format(NUM_PROBLEMS))
        plt.title('Planner:{} COC:{}'.format(PLANNER.planner.__name__, COC))
        plt.setp(lines, linewidth=2.0)
        plt.savefig("images/SimulateVaryingBoardSize_{}.png".format(time.time()%1000))
        plt.show()


def TestOnProblemBank():
    PROBLEMS = []
    
    # PROBLEMS.append(problem_bank.maze_0())
    # PROBLEMS.append(problem_bank.maze_1())
    # PROBLEMS.append(problem_bank.maze_2())
    # PROBLEMS.append(problem_bank.maze_3())
    # PROBLEMS.append(problem_bank.maze_4())
    # PROBLEMS.append(problem_bank.maze_5())
    # PROBLEMS.append(problem_bank.test_exp_cost())
    
    # PROBLEMS.append(problem_bank.navigate_replan_team_2())
    # PROBLEMS.append(problem_bank.navigate_replan_team_3())
    # # PROBLEMS.append(problem_bank.navigate_replan_team_4()) # Two observations that have joint-effect that is greate than the effect of each
    # PROBLEMS.append(problem_bank.navigate_replan_team_5())
    # PROBLEMS.append(problem_bank.navigate_replan_team_6())
    # PROBLEMS.append(problem_bank.navigate_replan_team_7())

    PROBLEMS = [rrw.make_rand_nav_problem(4, 4, \
        name=str(time.time()) + '.' + str(i)) for i in range(5)]

    for PROBLEM in PROBLEMS:
        for AGENT_TYPE in MODELS:
            for PLANNER in PLANNERS:
                # Each point is the average over all problems
                PROBLEM.COST_OF_COMM = COC
                PROBLEM.COST_REPLAN = 0

                # Run
                simulation = Simulation(PROBLEM, AGENT_TYPE, PLANNER, gui=True)
                simulation.run()
                
                
                # Show result
                logger.info(simulation.get_summary(cost=True, cost_bd=True, obs=True, comm=True, void=True))
                print([a.get_histories() for a in simulation.agents.values()])

"""
This reproduces the baseline with parameters:
    PLANNER: Any planner
    MODEL: no-comm, full-comm, smart-comm, or more
    MAX_COST: 100
    COC: range(50)
    Input: Fix Board-Size
"""
# SimulateVaryingCosts(BOARD_X, BOARD_Y)

"""
Input: Fix COC
"""
# SimulateVaryingBoard(COC)



TestOnProblemBank()










"""
Graveyard
"""
    # Plot/Show
    # if show_summary:
    #     logger.info("*** SUMMARY for Problem {} Summary for Models: {}".format(PROBLEM.name, [m.__name__ for m in MODELS]))

    #     for (model_name, sims_m) in simulations.items():
    #         for (coc, sims_m_c) in sims_m.items():
    #             for sim_m_c_p in sims_m_c:
    #                 logger.info(sim_m_c_p.get_summary(cost=True, cost_bd=False, obs=False, comm=True, void=True))


#             # If we care to re-play simulations where agents communicated
#             # if simulation.total_messages_sent() != 0 and sum(simulation.cost_p_agent()) > sum(simulations[-1].cost_p_agent()):
#             #     logger.info("communicated AND performed worse... re-running simulaiton with GUI")
#             #     Simulation(PROBLEM, AGENT_TYPE, PLANNER, gui=True, re_plan=True, use_tree=False)
            
#             simulations.append(simulation)





#         Simulation.write_to_file(PROBLEM, simulations)

