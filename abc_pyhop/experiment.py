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
BOARD_X = 6
BOARD_Y = 6
GUI = False


# """
# Board Size - Indicates length of the tasks
# """
# BOARD_SIDES = [4, 5, 6, 7]


"""
Pick which Models to compare
"""
MODELS = []
MODELS += [models.AgentNoComm]
MODELS += [models.AgentSmartComm]
# MODELS += [models.AgentSmartPlanRec]
# MODELS += [models.AgentSmartCommII]
# MODELS += [models.AgentSmartEstimate]
# MODELS += [models.AgentRandComm]
# MODELS += [models.AgentFullComm]


"""
Pick which Planners to use
"""
PLANNERS = []
PLANNERS += [Planner.get_HPlanner_v14()] # Quick sampling using A* NOT Random
PLANNERS += [Planner.get_HPlanner_v15()] # Quick sampling using A* Random
PLANNERS += [Planner.get_HPlanner_v17()] # copy of v15
# PLANNERS += [Planner.get_HPlanner_v13()] # Quick Sampling no A*
# PLANNERS += [Planner.get_HPlanner_bb()]
# PLANNERS += [Planner.get_HPlanner_bb_prob()] # Reason with expected cost of communication

"""
Cost of Communication
"""
RAND_RANGE = 10
MAX_COST = 20
# COSTS = [i * 0.5 for i in range(11)]
# COSTS = range(5)
COSTS = [0, 1, 2, 3]
# COSTS = [0, 0.5, 1, 1.5, 2, 2.5, 3]
# COC = 1.5

"""
Choose any problem from problem bank
"""
PROBLEMS = []
NUM_PROBLEMS = 10


def SimulateVaryingCosts_Det_Planner(BOARD_X, BOARD_Y):
    global COSTS
    PROBLEMS = [rrw.make_semi_random_problem(BOARD_X, BOARD_Y, rand_range=RAND_RANGE, max_cost=MAX_COST,\
                name=str(time.time()) + '.' + str(i)) \
                for i in range(NUM_PROBLEMS)]
    
    lines = []
    for PLANNER in PLANNERS:
        # Each planner result in a different plot

        simulations = {}
        plot_lines = {}
        for AGENT_TYPE in MODELS:
            # Each agent is a line in the plot
            line_name = AGENT_TYPE.__name__ + '_' + PLANNER.name
            logger.info("*** Running simulations for [MODEL: {}]".format(line_name))
            
            simulations[line_name] = {}
            plot_lines[line_name] = [COSTS, [0 for i in range(len(COSTS))]]

            if AGENT_TYPE.__name__ == 'AgentNoComm':
                USE_COSTS = [0]
                baseline_costs = {}
            elif AGENT_TYPE.__name__ == 'AgentFullComm':
                USE_COSTS = [COSTS[0], COSTS[-1]]
                plot_lines[line_name] = [USE_COSTS, [0 for i in range(len(USE_COSTS))]]
            else:
                USE_COSTS = COSTS
            
            for i in range(len(USE_COSTS)):
                COC = USE_COSTS[i]
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
                        print "asdfasdf!!!"
                        continue

                    # Add
                    simulations[line_name][COC].append(simulation)
                    costs += simulation.get_total_cost()
                    # logger.info(simulation.get_summary(cost=True, cost_bd=False, obs=False, comm=True, void=True))

                    if AGENT_TYPE.__name__ == 'AgentNoComm':
                        baseline_costs[PROBLEM.name] = simulation.get_total_cost()
                        sys.stdout.write('{}, '.format(int(simulation.get_total_cost())))
                    else:
                        diff = int(simulation.get_total_cost() - baseline_costs[PROBLEM.name])
                        sys.stdout.write('{}, '.format(diff))
                        # if diff > 1 and ('Smart' in AGENT_TYPE.__name__):
                        #     Simulation(PROBLEM, AGENT_TYPE, PLANNER, gui=True)

                    sys.stdout.flush()

                
                avg_cost = costs * 1.0 / len(simulations[line_name][COC])
                plot_lines[line_name][1][i] = avg_cost
                # FOr No-COMM, the cost is the same for all COC values.
                if AGENT_TYPE.__name__ == 'AgentNoComm':
                    plot_lines[line_name][1] = [avg_cost for i in range(len(COSTS))]

                sys.stdout.write('Avg: {}\n'.format(avg_cost))
                sys.stdout.flush()


    logger.info("Plot Lines: {}".format(plot_lines))
    lines = []
    # Adjust Plotting
    fig = plt.figure()
    ax = plt.subplot(111)

    for (name, line) in plot_lines.items():
        if 'NoComm' in name:
            c = 'green'
        elif 'SmartCommII' in name:
            c = 'cyan'
        elif 'SmartComm' in name:
            c = 'blue'
        elif 'FullComm' in name:
            c = 'red'
        elif 'RandComm' in name:
            c = 'purple'
        else:
            c = None
        lines.append(ax.plot(line[0], line[1], label=name, color=c))

    # Locate Legend
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.2,
             box.width, box.height * 0.8])
    legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.13),
      fancybox=True, shadow=True, ncol=2, prop={'size':9})
    
    # Set Line Width
    for legobj in legend.legendHandles:
        legobj.set_linewidth(2.0)
    plt.setp(lines, linewidth=2.0)

    # Labels
    plt.xlabel("Cost of Communication")
    plt.ylabel("Average Costs over {} Random Problems".format(NUM_PROBLEMS))
    # plt.title('Planner:{} Board-Size:{}'.format(PLANNER.name, BOARD_X*BOARD_Y))
    # plt.title('Planner:{} Board-Size:{}'.format(PLANNER.name, BOARD_X*BOARD_Y))
    
    # write simulation parameters to file.
    filename = "images/VaryingCosts_{}_{}".format(PLANNER.name, time.time()%1000)
    plt.savefig(filename+".png")

    plt.show()

"""
For Non-Deterministic Planners (Includes the extra inner loop for repeating the same problem)
"""
def SimulateVaryingCosts(BOARD_X, BOARD_Y):
    
    # PROBLEMS = [rrw.make_random_problem(BOARD_X, BOARD_Y, rand_range=RAND_RANGE, \
    #             name=str(time.time()) + '.' + str(i)) \
    #             for i in range(NUM_PROBLEMS)]

    PROBLEMS = [rrw.make_random_problem(BOARD_X, BOARD_Y, rand_range=RAND_RANGE, \
                name=str(time.time()) + '.' + str(i)) \
                for i in range(NUM_PROBLEMS)]
    
    lines = []
    simulations = {}
    plot_lines = {}
    for PLANNER in PLANNERS:
        # Each planner result in a different plot

        for AGENT_TYPE in MODELS:
            # Each agent is a line in the plot
            line_name = AGENT_TYPE.__name__ + PLANNER.name
            logger.info("*** Running simulations for [MODEL: {}]".format(line_name))
            
            simulations[line_name] = {}
            plot_lines[line_name] = [COSTS, [0 for i in range(len(COSTS))]]

            
            for i in range(len(COSTS)):
                COC = COSTS[i]
                # Each cost is a data point
                sys.stdout.write('COST : {}\t'.format(COC))
                sys.stdout.flush()

                simulations[line_name][COC] = []
                costs = 0
                for PROBLEM in PROBLEMS:
                    # Each point is the average over all problems
                    PROBLEM.COST_OF_COMM = COC
                    PROBLEM.COST_REPLAN = 0

                    if 'Det' in PLANNER.name and 'Rand' not in PLANNER.name:
                        num_iter = 1
                    elif 'Rand' in PLANNER.name and 'Det' not in PLANNER.name:
                        num_iter = 1
                    else:
                        assert(False), "PlannerName: {}".format(PLANNER.name)

                    for j in range(num_iter):
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

                        sys.stdout.write('{}, '.format(int(simulation.get_total_cost())))
                        sys.stdout.flush()

                
                avg_cost = costs * 1.0 / len(simulations[line_name][COC])
                plot_lines[line_name][1][i] = avg_cost
                
                sys.stdout.write('Avg: {}\n'.format(avg_cost))
                sys.stdout.flush()


    logger.info("Plot Lines: {}".format(plot_lines))
    lines = []
    
    # Adjust Plotting
    fig = plt.figure()
    ax = plt.subplot(111)

    for (name, line) in plot_lines.items():
        lines.append(ax.plot(line[0], line[1], label=name))

    # Locate Legend
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.2,
             box.width, box.height * 0.8])
    legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.13),
      fancybox=True, shadow=True, ncol=2, prop={'size':9})
    
    # Set Line Width
    for legobj in legend.legendHandles:
        legobj.set_linewidth(2.0)
    plt.setp(lines, linewidth=2.0)

    # Labels
    plt.xlabel("Cost of Communication")
    plt.ylabel("Average Costs over {} Random Problems".format(NUM_PROBLEMS))
    plt.title('Planner:{} Board-Size:{}'.format(PLANNER.name, BOARD_X*BOARD_Y))
    
    # write simulation parameters to file.
    filename = "images/SimulateVaryingCosts_{}".format(time.time()%1000)
    plt.savefig(filename+".png")

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
    # # PROBLEMS.append(problem_bank.maze_3())
    # PROBLEMS.append(problem_bank.maze_4())
    # PROBLEMS.append(problem_bank.maze_5())
    # PROBLEMS.append(problem_bank.test_exp_cost())
    
    # PROBLEMS.append(problem_bank.navigate_replan_team_2())
    # PROBLEMS.append(problem_bank.navigate_replan_team_3())
    # PROBLEMS.append(problem_bank.navigate_replan_team_4()) # Two observations that have joint-effect that is greate than the effect of each
    # PROBLEMS.append(problem_bank.navigate_replan_team_5())
    # PROBLEMS.append(problem_bank.navigate_replan_team_6())
    # PROBLEMS.append(problem_bank.navigate_replan_team_7())

    # PROBLEMS = [rrw.make_rand_nav_problem(4, 4, \
        # name=str(time.time()) + '.' + str(i)) for i in range(5)]

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
                logger.info(simulation.get_summary(cost=True, cost_bd=False, obs=True, comm=True, void=False))
                # print([a.get_histories() for a in simulation.agents.values()])

def TestOneRandomProb():
    # PROBLEMS = [rrw.make_random_problem(BOARD_X, BOARD_Y, \
    #     name=str(time.time()) + '.' + str(i)) for i in range(10)]

    PROBLEMS = [rrw.make_random_problem(BOARD_X, BOARD_Y, rand_range=RAND_RANGE, max_cost=MAX_COST,\
        name=str(time.time()) + '.' + str(i)) for i in range(1)]

    for PROBLEM in PROBLEMS:

        costs = {}
        for AGENT_TYPE in MODELS:
            for PLANNER in PLANNERS:
                # Each point is the average over all problems
                PROBLEM.COST_OF_COMM = COC
                PROBLEM.COST_REPLAN = 0

                for i in range(10):
                    # Run
                    simulation = Simulation(PROBLEM, AGENT_TYPE, PLANNER, gui=True)
                    simulation.run()
                    costs[AGENT_TYPE.__name__] = simulation.get_total_cost()
                    logger.info(simulation.get_summary(cost=True, cost_bd=True, obs=True, comm=True, void=True))
                    # print([a.get_histories() for a in simulation.agents.values()])

                    # if AGENT_TYPE.__name__ == 'AgentNoComm':
                    #     print('setting baseline: ')
                    #     baseline = simulation
                    # if simulation.get_total_cost() > baseline.get_total_cost() and AGENT_TYPE.__name__ != 'AgentFullComm':
                    #     simulation = Simulation(PROBLEM, AGENT_TYPE, PLANNER, gui=True)

        if costs['AgentSmartComm'] > costs['AgentNoComm']:
            Simulation(PROBLEM, models.AgentNoComm, PLANNER, gui=True)
            Simulation(PROBLEM, models.AgentSmartComm, PLANNER, gui=True)
    
"""
Assume there are two planners, one det and one rand
Assume comapring NoComm and SmartComm
"""            
def CompareDetVsRand_Cost(BOARD_X, BOARD_Y):
    global MODELS

    PROBLEMS = [rrw.make_random_problem(BOARD_X, BOARD_Y, rand_range=RAND_RANGE, \
                name=str(time.time()) + '.' + str(i)) \
                for i in range(NUM_PROBLEMS)]
    
    lines = []
    simulations = {}
    plot_lines = {}
    relative_to_noComm = {}
    baseline_avg = {}
    percent_improv = {}
    for PLANNER in PLANNERS:
        # Each planner result in a different plot
        if PLANNER.name == Planner.get_HPlanner_bb().name:
            MODELS = [models.AgentNoComm, models.AgentSmartPlanRec]
        elif PLANNER.name == Planner.get_HPlanner_v15().name:
            MODELS = [models.AgentNoComm, models.AgentSmartEstimate]
        elif PLANNER.name == Planner.get_HPlanner_v17().name:
            MODELS = [models.AgentNoComm, models.AgentSmartCommII]
        else:
            MODELS = [models.AgentNoComm, models.AgentSmartComm]

        for AGENT_TYPE in MODELS:
            # Each agent is a line in the plot
            line_name = AGENT_TYPE.__name__ + '_' + PLANNER.name
            logger.info("*** Running simulations for [MODEL: {}]".format(line_name))
            
            simulations[line_name] = {}
            plot_lines[line_name] = [COSTS, [0 for i in range(len(COSTS))]]

            if AGENT_TYPE.__name__ != 'AgentNoComm':
                relative_to_noComm[line_name] = [COSTS, [0 for i in range(len(COSTS))]]
                percent_improv[line_name] = [COSTS, [0 for i in range(len(COSTS))]]

            if AGENT_TYPE.__name__ == 'AgentNoComm':
                USE_COSTS = [0]
                baseline_costs = {}
            elif AGENT_TYPE.__name__ == 'AgentFullComm':
                USE_COSTS = [COSTS[0], COSTS[-1]]
                plot_lines[line_name] = [USE_COSTS, [0 for i in range(len(USE_COSTS))]]
            else:
                USE_COSTS = COSTS
            
            for i in range(len(USE_COSTS)):
                COC = USE_COSTS[i]
                # Each cost is a data point
                sys.stdout.write('COST : {}\t'.format(COC))
                sys.stdout.flush()

                simulations[line_name][COC] = []
                costs = 0
                for P in PROBLEMS:
                    
                    PROBLEM = copy.deepcopy(P)

                    """
                    Pretending to have elimited the other possible decompositions. Lowering the amount of uncertainty
                    """
                    if PLANNER.name == Planner.get_HPlanner_v17().name:
                        PROBLEM = copy.deepcopy(P)
                        PROBLEM.soils.remove('S1')
                        PROBLEM.rocks.remove('R1')
                    """
                    Similarly, removing uncertainties
                    """
                    # if PLANNER.name == Planner.get_HPlanner_v15().name and AGENT_TYPE.__name__ == models.AgentSmartCommII.__name__:
                    #     PROBLEM = copy.deepcopy(P)
                    #     PROBLEM.soils = []

                    # Each point is the average over all problems
                    PROBLEM.COST_OF_COMM = COC
                    PROBLEM.COST_REPLAN = 0

                    if 'Det' in PLANNER.name and 'Rand' not in PLANNER.name:
                        num_iter = 1
                    elif 'Rand' in PLANNER.name and 'Det' not in PLANNER.name:
                        num_iter = 5
                    else:
                        assert(False), "PlannerName: {}".format(PLANNER.name)

                    for j in range(num_iter):
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

                        if AGENT_TYPE.__name__ == 'AgentNoComm':
                            baseline_costs[PROBLEM.name] = simulation.get_total_cost()
                            sys.stdout.write('{}, '.format(int(simulation.get_total_cost())))
                        else:
                            diff = int(simulation.get_total_cost() - baseline_costs[PROBLEM.name])
                            sys.stdout.write('{}, '.format(diff))
                        sys.stdout.flush()

                
                avg_cost = costs * 1.0 / len(simulations[line_name][COC])
                plot_lines[line_name][1][i] = avg_cost
                if AGENT_TYPE.__name__ == 'AgentNoComm':
                    baseline_avg[PLANNER.name] = avg_cost
                    plot_lines[line_name][1] = [avg_cost for i in range(len(COSTS))]
                else:
                    relative_to_noComm[line_name][1][i] = (baseline_avg[PLANNER.name]-avg_cost) 
                    percent_improv[line_name][1][i] = (baseline_avg[PLANNER.name]-avg_cost)/baseline_avg[PLANNER.name]
                sys.stdout.write('Avg: {}\n'.format(avg_cost))
                sys.stdout.flush()


    logger.info("Plot Lines: {}".format(plot_lines))
    lines = []
    
    # Adjust Plotting
    fig = plt.figure()
    ax = plt.subplot(111)

    for (name, line) in plot_lines.items():
        lines.append(ax.plot(line[0], line[1], label=name, marker='o'))

    # Locate Legend
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.2,
             box.width, box.height * 0.8])
    legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.13),
      fancybox=True, shadow=True, ncol=2, prop={'size':9})
    
    # Set Line Width
    for legobj in legend.legendHandles:
        legobj.set_linewidth(2.0)
    plt.setp(lines, linewidth=2.0)

    # Labels
    plt.xlabel("Cost of Communication")
    plt.ylabel("Average Costs over {} Random Problems".format(NUM_PROBLEMS))
    plt.title('Planner:{} Board-Size:{}'.format(PLANNER.name, BOARD_X*BOARD_Y))
    
    # write simulation parameters to file.
    filename = "images/CompareDetVsRandCost_raw_{}".format(time.time()%1000)
    plt.savefig(filename+".png")



    """
    Plot Improvement of Cost
    """
    fig = plt.figure()
    ax = plt.subplot(111)

    for (name, line) in relative_to_noComm.items():
        lines.append(ax.plot(line[0], line[1], label=name, marker='o'))

    # Locate Legend
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.2,
             box.width, box.height * 0.8])
    legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.13),
      fancybox=True, shadow=True, ncol=2, prop={'size':9})
    
    # Set Line Width
    for legobj in legend.legendHandles:
        legobj.set_linewidth(2.0)
    plt.setp(lines, linewidth=2.0)

    # Labels
    plt.xlabel("Cost of Communication")
    plt.ylabel("SmartComm Improvement")
    # plt.title('Planner:{} Board-Size:{}'.format(PLANNER.name, BOARD_X*BOARD_Y))
    
    # write simulation parameters to file.
    filename = "images/CompareDetVsRandCost_diff_{}".format(time.time()%1000)
    plt.savefig(filename+".png")


    """
    Plot percent improved
    """
    fig = plt.figure()
    ax = plt.subplot(111)

    for (name, line) in percent_improv.items():
        lines.append(ax.plot(line[0], line[1], label=name, marker='o'))

    # Locate Legend
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.2,
             box.width, box.height * 0.8])
    legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.13),
      fancybox=True, shadow=True, ncol=2, prop={'size':9})
    
    # Set Line Width
    for legobj in legend.legendHandles:
        legobj.set_linewidth(2.0)
    plt.setp(lines, linewidth=2.0)

    # Labels
    plt.xlabel("Cost of Communication")
    plt.ylabel("SmartComm Improvement")
    # plt.title('Planner:{} Board-Size:{}'.format(PLANNER.name, BOARD_X*BOARD_Y))
    
    # write simulation parameters to file.
    filename = "images/CompareDetVsRandCost_perImprov_{}".format(time.time()%1000)
    plt.savefig(filename+".png")

    plt.show()


"""
This reproduces the baseline with parameters:
    PLANNER: Any planner
    MODEL: no-comm, full-comm, smart-comm, or more
    MAX_COST: 100
    COC: range(50)
    Input: Fix Board-Size
"""
# SimulateVaryingCosts_Det_Planner(BOARD_X, BOARD_Y)

# SimulateVaryingCosts(BOARD_X, BOARD_Y)

CompareDetVsRand_Cost(BOARD_X, BOARD_Y)

# CompareDetVsRand_BoardSize(COC)

"""
Input: Fix COC
"""
# SimulateVaryingBoard(COC)


# TestOnProblemBank()
# TestOneRandomProb()









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

