"""
This simulation should highlight the need for better synced mental models 
when the length of the plan is longer. 
"""

# from __future__ import print_function
from simulate_rovers_world import *
import random_rovers_world as rrw
import models
from planners import * 
import problems as ProblemLib

class SimulationParameters(object):
    def __init__(self, planner, model, coc):
        self.planner = planner
        self.model = model
        self.coc = coc
    def __repr__(self):
        return str([self.planner.name, self.model.__name__, self.coc])


# WIth a given Planner and model and CoC
def log_problems(SIM_PARAMS, PROBLEMS, file_obj_sim, file_obj_avg):
    for j, params in enumerate(SIM_PARAMS):
        simulations = []
        for i, PROBLEM in enumerate(PROBLEMS):
            
            print("Running problem: {} with parameters: {} Problem {}/{}; Param {}/{}".format(PROBLEM.name, params, i, len(PROBLEMS), j, len(SIM_PARAMS)))
            PROBLEM.COST_OF_COMM = params.coc
            PROBLEM.COST_REPLAN = 0
            simulation = Simulation(PROBLEM, params.model, params.planner)
            simulation.run()

            simulations.append(simulation)
            # Write result to file
            write_result_by_simulation(PROBLEM, params, simulation, file_obj_sim)

        write_result_by_sim_params(params, PROBLEMS, simulations, file_obj_avg)


# Write averaged simulation results over n-problems
def write_result_by_sim_params(params, PROBLEMS, simulations, file_obj):

    # Planner   Model   CoC
    to_write = "{}\t{}\t{}".format(params.planner.name, params.model.__name__, params.coc)

    # Avg Cost
    avg_cost = sum([sim.get_total_cost() for sim in simulations])/len(simulations)
    to_write += '\t' + str(avg_cost)

    # Num Problems Avged
    to_write += '\t' + str(len(simulations))

    file_obj.write(to_write + '\n')


# Write simulation results in results directory
def write_result_by_simulation(problem, params, simulation, file_obj):

    # About this simulation
    to_write = problem.name
    to_write += "\t{}\t{}\t{}".format(params.planner.name, params.model.__name__, params.coc)

    # Results
    to_write += '\t' + str(simulation.get_total_cost())
    to_write += '\t' + str(simulation.total_observations())
    to_write += '\t' + str(simulation.total_messages_sent())
    to_write += '\t' + str(simulation.total_messages_voided())
    to_write += '\t' + str(simulation.total_steps())

    file_obj.write(to_write + '\n')


"""
Pick which Models to compare
"""
MODELS = []
MODELS += [models.AgentNoComm]
MODELS += [models.AgentSmartComm]
MODELS += [models.AgentSmartCommII]
# MODELS += [models.AgentSmartEstimate]
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
# PLANNERS += [Planner.get_HPlanner_bb_prob()] # Reason with expected cost of communication




"""
Running 100 problems for a total of 141 parameter configurations.
All using deterministic planner. This is to show results for smartComm and smartCommII
over nocomm, randcomm, and fullcomm
"""
def get_params_for_costs():
    PLANNERS = []
    PLANNERS += [Planner.get_HPlanner_v14()] # Quick sampling using A* NOT Random
    PARAMETERS = [SimulationParameters(p, models.AgentNoComm, 0) for p in PLANNERS]

    MODELS = [models.AgentSmartComm, models.AgentSmartCommII, models.AgentRandComm, models.AgentFullComm]
    COCs = [i * 0.1 for i in range(30)]
    COCs += [i * 0.5 + 3 for i in range(5)]
    PARAMETERS += [SimulationParameters(p, m, c) for p in PLANNERS for m in MODELS for c in COCs]
    return PARAMETERS

def get_problems_for_costs():
    NUM_PROBLEMS = 100
    BOARD_X = 5
    BOARD_Y = 5
    return ProblemLib.find_problems(BOARD_X, BOARD_Y, NUM_ROCKS=1, NUM_SOILS=1,\
            RAND_RANGE=10, RAND_PROB=0.5, limit=NUM_PROBLEMS)

# log_problems(get_params_for_costs(), get_problems_for_costs(), \
#     open("results/DetPlanner_over_cost_per_simulation.txt", 'a'), \
#     open("results/DetPlanner_over_cost_averaged.txt", 'a'))



"""
Running __ problems for a total of __ parameter configurations.
All using determinis planner (v_14). This is used to show how smart comm and smartCommII
diverge over larger boards
"""
def get_params_for_board_sizes():
    CoC = 1.5
    PLANNERS = [Planner.get_HPlanner_v14()]
    MODELS = [models.AgentNoComm, models.AgentSmartComm, models.AgentSmartCommII, models.AgentFullComm]
    PARAMETERS = [SimulationParameters(p, m, CoC) for p in PLANNERS for m in MODELS]

    # Last parameter is for show "optimal"
    PARAMETERS += [SimulationParameters(p, models.AgentFullComm, 0) for p in PLANNERS]
    return PARAMETERS


def get_problems_for_board_sizes():
    NUM_PROBLEMS = 30
    BOARD_SIDES = [0.5 * x for x in range(10,27)]
    problems = []
    for SIDE in BOARD_SIDES:
        problems += ProblemLib.find_problems(int(math.floor(SIDE)), int(math.ceil(SIDE)),\
            RAND_RANGE=10, RAND_PROB=0.5, limit=NUM_PROBLEMS)
    return problems

import sys
sys.stdout = open('04262102.log', 'w')

# DELAY for overnight runs
for i in range(240*12):
    time.sleep(5)
    print('starting in {} minutes ... ...'.format(239-i))

log_problems(get_params_for_board_sizes(), get_problems_for_board_sizes(), \
    open("results/DetPlanner_over_board_per_simulation.txt", 'a'), \
    open("results/DetPlanner_over_board_averaged.txt", 'a'))


