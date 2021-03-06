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
import problems as ProblemLib
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
BOARD_X = 5
BOARD_Y = 5
GUI = False


"""
Board Size - Indicates length of the tasks
"""
# BOARD_SIDES = [0.5 * x for x in range(8,22)]
BOARD_SIDES = [4, 6, 8]


"""
Pick which Models to compare
"""
MODELS = []
MODELS += [models.AgentNoComm]
MODELS += [models.AgentSmartComm]
MODELS += [models.AgentSmartCommII]
# MODELS += [models.AgentSmartEstimate]
# MODELS += [models.AgentRandComm]
MODELS += [models.AgentFullComm]


"""
Pick which Planners to use
"""
PLANNERS = []
PLANNERS += [Planner.get_HPlanner_v14()] # Quick sampling using A* NOT Random
# PLANNERS += [Planner.get_HPlanner_v15()] # Quick sampling using A* Random
# PLANNERS += [Planner.get_HPlanner_v13()] # Quick Sampling no A*
# PLANNERS += [Planner.get_HPlanner_bb()]
# PLANNERS += [Planner.get_HPlanner_bb_prob()] # Reason with expected cost of communication

"""
Cost of Communication
"""
RAND_RANGE = 10
MAX_COST = 20
RAND_PROB = 0.5
COC = 1.5

"""
Choose any problem from problem bank
"""
PROBLEMS = []
NUM_PROBLEMS = 5
    
def SimulateVaryingBoard(COC):
    lines = []
    base_line = None
    base_line_name = None

    # First make the same set of NUM_PROBLEMS for a given Board-size for all models
    PROBLEMS_dict = {}
    for SIDE in BOARD_SIDES:
        PROBLEMS_dict[SIDE] = ProblemLib.find_problems(int(math.floor(SIDE)), int(math.ceil(SIDE)),\
            RAND_RANGE=RAND_RANGE, RAND_PROB=RAND_PROB, limit=NUM_PROBLEMS)


    simulations = {}
    plot_lines = {}
    raw_lines = {}
    percent_improv = {}
    for PLANNER in PLANNERS:
        # Each planner result in a different plot
        
        for AGENT_TYPE in MODELS:
            # Each agent is a line in the plot
            line_name = PLANNER.name + '_' + AGENT_TYPE.__name__
            logger.info("*** Running simulations for [MODEL: {}]".format(line_name))
                    
            simulations[line_name] = {}
            cur_line = (BOARD_SIDES, []) # X, Y

            for SIDE in BOARD_SIDES:
                # Each cost is a data point
                sys.stdout.write('SIDE : {}\t'.format(SIDE))
                sys.stdout.flush()

                simulations[line_name][SIDE] = []
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
                    simulations[line_name][SIDE].append(simulation)
                    costs += simulation.get_total_cost()
                    # logger.info(simulation.get_summary(cost=True, cost_bd=False, obs=False, comm=True, void=True))

                    sys.stdout.write('>')
                    sys.stdout.flush()

                avg_cost = costs * 1.0 / len(simulations[line_name][SIDE])
                cur_line[1].append(avg_cost)

                sys.stdout.write('\n')
                sys.stdout.flush()

            if base_line == None:
                plot_lines[line_name] = cur_line
                base_line_name = line_name
                base_line = plot_lines[line_name]
            else:
                plot_lines[line_name] = (cur_line[0], [x-y for x, y in zip(cur_line[1], base_line[1])])
                percent_improv[line_name] = (cur_line[0], [(x-y) * 1.0 / y for x, y in zip(cur_line[1], base_line[1])])
            raw_lines[line_name] = cur_line

    # Renormalizing based on the no-comm baseline.
    plot_lines[base_line_name] = (BOARD_SIDES, [0]*len(BOARD_SIDES)) 
    percent_improv[base_line_name] = (BOARD_SIDES, [0]*len(BOARD_SIDES)) 
    # Plot lines
    logger.info("Plot Lines: {}".format(plot_lines))


    # Adjust Plotting
    exp_id = int(time.time())

    """
    First we plot the lines relative to no-comm
    """
    fig = plt.figure()
    ax = plt.subplot(111)

    for (name, line) in plot_lines.items():
        lines.append(ax.plot([x * x for x in line[0]], line[1], label=name))

    # Locate Legend
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.2,
             box.width, box.height * 0.8])

    legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.13),
      fancybox=True, shadow=True, ncol=2, prop={'size':9})
    for legobj in legend.legendHandles:
        legobj.set_linewidth(2.0)
    
    # Labels
    plt.xlabel("Board Size")
    plt.ylabel("Average Cost-differences relative to no-comm")
    plt.title('Planner:{} COC:{} -- Averaged over {} Random Problem'.format(PLANNER.name, COC, NUM_PROBLEMS))
    plt.setp(lines, linewidth=2.0)

    plt.savefig("images/VaryingBoardSize_{}.png".format(exp_id))

    """
    Same plot but x-axis is board-length
    """
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
    for legobj in legend.legendHandles:
        legobj.set_linewidth(2.0)
    
    # Labels
    plt.xlabel("Board Size")
    plt.ylabel("Average Cost-differences relative to no-comm")
    plt.title('Planner:{} COC:{} -- Averaged over {} Random Problem'.format(PLANNER.name, COC, NUM_PROBLEMS))
    plt.setp(lines, linewidth=2.0)

    plt.savefig("images/VaryingBoardLength_{}.png".format(exp_id))



    # """
    # Second plot, we plot the raw lines
    # """
    # fig = plt.figure()
    # ax = plt.subplot(111)

    # for (name, line) in raw_lines.items():
    #     lines.append(ax.plot([x * x for x in line[0]], line[1], label=name))

    # # Locate Legend
    # box = ax.get_position()
    # ax.set_position([box.x0, box.y0 + box.height * 0.2,
    #          box.width, box.height * 0.8])

    # legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.13),
    #   fancybox=True, shadow=True, ncol=2, prop={'size':9})
    # for legobj in legend.legendHandles:
    #     legobj.set_linewidth(2.0)
    
    # # Labels
    # plt.xlabel("Board Size")
    # plt.ylabel("Average Costs over {} Random Problems".format(NUM_PROBLEMS))
    # plt.title('Planner:{} COC:{} -- Raw Costs'.format(PLANNER.name, COC))
    # plt.setp(lines, linewidth=2.0)

    # plt.savefig("images/VaryingBoardSize_raw{}.png".format(exp_id))

    # """
    # Same plot but x-axis is board-length
    # """
    # fig = plt.figure()
    # ax = plt.subplot(111)

    # for (name, line) in raw_lines.items():
    #     lines.append(ax.plot(line[0], line[1], label=name))

    # # Locate Legend
    # box = ax.get_position()
    # ax.set_position([box.x0, box.y0 + box.height * 0.2,
    #          box.width, box.height * 0.8])

    # legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.13),
    #   fancybox=True, shadow=True, ncol=2, prop={'size':9})
    # for legobj in legend.legendHandles:
    #     legobj.set_linewidth(2.0)
    
    # # Labels
    # plt.xlabel("Board Size")
    # plt.ylabel("Average Costs over {} Random Problems".format(NUM_PROBLEMS))
    # plt.title('Planner:{} COC:{} -- Raw Costs'.format(PLANNER.name, COC))
    # plt.setp(lines, linewidth=2.0)

    # plt.savefig("images/VaryingBoardLength_raw{}.png".format(exp_id))

    """
    third plot, we plot the percent-increase
    """
    fig = plt.figure()
    ax = plt.subplot(111)

    for (name, line) in percent_improv.items():
        lines.append(ax.plot([x * x for x in line[0]], line[1], label=name))

    # Locate Legend
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.2,
             box.width, box.height * 0.8])

    legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.13),
      fancybox=True, shadow=True, ncol=2, prop={'size':9})
    for legobj in legend.legendHandles:
        legobj.set_linewidth(2.0)
    
    # Labels
    plt.xlabel("Board Size")
    plt.ylabel("Average Costs over {} Random Problems".format(NUM_PROBLEMS))
    plt.title('Planner:{} COC:{} -- Improvement over Baseline'.format(PLANNER.name, COC))
    plt.setp(lines, linewidth=2.0)

    plt.savefig("images/VaryingBoardLength_percImprov_{}.png".format(exp_id))

    """
    Same plot but x-axis is board-length
    """
    fig = plt.figure()
    ax = plt.subplot(111)

    for (name, line) in percent_improv.items():
        lines.append(ax.plot(line[0], line[1], label=name))

    # Locate Legend
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.2,
             box.width, box.height * 0.8])

    legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.13),
      fancybox=True, shadow=True, ncol=2, prop={'size':9})
    for legobj in legend.legendHandles:
        legobj.set_linewidth(2.0)
    
    # Labels
    plt.xlabel("Board Size")
    plt.ylabel("Average Costs over {} Random Problems".format(NUM_PROBLEMS))
    plt.title('Planner:{} COC:{} -- Improvement over Baseline'.format(PLANNER.name, COC))
    plt.setp(lines, linewidth=2.0)

    plt.savefig("images/VaryingBoardLength_percImprov_{}.png".format(exp_id))

    plt.show()

def CompareDetVsRand_BoardSize(COC):
    global MODELS
    # First make the same set of NUM_PROBLEMS for a given Board-size for all models
    PROBLEMS_dict = {}
    for SIDE in BOARD_SIDES:
        PROBLEMS_dict[SIDE] = [rrw.make_random_problem(int(math.floor(SIDE)), int(math.ceil(SIDE)), rand_range=RAND_RANGE, \
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
        if PLANNER.name == Planner.get_HPlanner_v15().name:
            MODELS = [models.AgentNoComm, models.AgentSmartEstimate]
            
        for AGENT_TYPE in MODELS:
            # Each agent is a line in the plot
            line_name = AGENT_TYPE.__name__ + '_' + PLANNER.name
            logger.info("*** Running simulations for [MODEL: {}]".format(line_name))
            
            simulations[line_name] = {}
            plot_lines[line_name] = [BOARD_SIDES, []]
            relative_to_noComm[PLANNER.name] = [BOARD_SIDES, []]
            percent_improv[PLANNER.name] = [BOARD_SIDES, []]
            
            for SIDE in BOARD_SIDES:

                # Each cost is a data point
                sys.stdout.write('SIDE : {}\t'.format(SIDE))
                sys.stdout.flush()

                simulations[line_name][SIDE] = []
                costs = 0
                for PROBLEM in PROBLEMS_dict[SIDE]:
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
                        simulations[line_name][SIDE].append(simulation)
                        costs += simulation.get_total_cost()
                        # logger.info(simulation.get_summary(cost=True, cost_bd=False, obs=False, comm=True, void=True))

                        sys.stdout.write('{},'.format(int(simulation.get_total_cost())))
                        sys.stdout.flush()
                
                avg_cost = costs * 1.0 / len(simulations[line_name][SIDE])
                plot_lines[line_name][1].append(avg_cost)

                if AGENT_TYPE.__name__ == 'AgentNoComm':
                    baseline_avg[(PLANNER.name, SIDE)] = avg_cost
                else:
                    b = baseline_avg[(PLANNER.name, SIDE)]
                    relative_to_noComm[PLANNER.name][1].append(b-avg_cost) 
                    percent_improv[PLANNER.name][1].append((b-avg_cost)/b)
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
    plt.xlabel("Board Size")
    plt.ylabel("Average Costs over {} Random Problems".format(NUM_PROBLEMS))
    plt.title('Planner:{} Board-Size:{}'.format(PLANNER.name, BOARD_X*BOARD_Y))
    
    # write simulation parameters to file.
    filename = "images/CompareDetVsRandBoard_raw_{}".format(time.time()%1000)
    plt.savefig(filename+".png")



    """
    Plot Improvement of Cost
    """
    fig = plt.figure()
    ax = plt.subplot(111)

    for (name, line) in relative_to_noComm.items():
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
    plt.xlabel("Board Size")
    plt.ylabel("SmartComm Improvement")
    # plt.title('Planner:{} Board-Size:{}'.format(PLANNER.name, BOARD_X*BOARD_Y))
    
    # write simulation parameters to file.
    filename = "images/CompareDetVsRandBoard_diff_{}".format(time.time()%1000)
    plt.savefig(filename+".png")


    """
    Plot percent improved
    """
    fig = plt.figure()
    ax = plt.subplot(111)

    for (name, line) in percent_improv.items():
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
    plt.xlabel("Board Size")
    plt.ylabel("SmartComm Improvement")
    # plt.title('Planner:{} Board-Size:{}'.format(PLANNER.name, BOARD_X*BOARD_Y))
    
    # write simulation parameters to file.
    filename = "images/CompareDetVsRandBoard_perImprov_{}".format(time.time()%1000)
    plt.savefig(filename+".png")

    plt.show()



# DELAY for overnight runs
# for i in range(120):
#     time.sleep(60)
#     print('starting in {} minutes ... ...'.format(119-i))

SimulateVaryingBoard(COC)
# CompareDetVsRand_BoardSize(COC)

