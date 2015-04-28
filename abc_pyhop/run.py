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
    def __init__(self, planner, model, coc, num_repeat=1):
        self.planner = planner
        self.model = model
        self.coc = coc
        self.num_repeat = num_repeat

    def __repr__(self):
        return str([self.planner.name, self.model.__name__, self.coc, self.num_repeat])

class ProblemParameters(object):
    def __init__(self, BOARD_X, BOARD_Y, NUM_ROCKS, NUM_SOILS, RAND_RANGE, A_PROB):
        self.BOARD_X = BOARD_X
        self.BOARD_Y = BOARD_Y
        self.NUM_ROCKS = NUM_ROCKS
        self.NUM_SOILS = NUM_SOILS
        self.RAND_RANGE = RAND_RANGE
        self.A_PROB = A_PROB

    def get_params(self):
        return [self.BOARD_X, self.BOARD_Y, self.NUM_SOILS, self.NUM_ROCKS, self.RAND_RANGE, self.A_PROB]

    def __repr__(self):
        return str(self.get_params())

# WIth a given Planner and model and CoC
def log_problems(SIM_PARAMS, PROBLEMS_DICT, file_obj_sim, file_obj_problem, file_obj_avg=None):

    for j, params in enumerate(SIM_PARAMS):
        k = 0
        for problem_params, PROBLEMS in PROBLEMS_DICT.items():
            simulations = []
            k += 1
            for i, PROBLEM in enumerate(PROBLEMS):
                
                repeated_sims = []
                for l in range(params.num_repeat):
                    print("Running problem: {} with parameters: {}\n\tnum_repeat {}/{}; Problem {}/{}; ProblemParams: {}/{}; Param {}/{}".format(\
                            PROBLEM.name, params, l, params.num_repeat, i, len(PROBLEMS), k, len(PROBLEMS_DICT), j, len(SIM_PARAMS)))

                    PROBLEM.COST_OF_COMM = params.coc
                    PROBLEM.COST_REPLAN = 0
                    simulation = Simulation(PROBLEM, params.model, params.planner)
                    simulation.run()

                    simulations.append(simulation)
                    repeated_sims.append(simulation)
                    # Write result to file
                    write_result_by_simulation(PROBLEM, params, simulation, file_obj_sim)

                if file_obj_avg != None and params.num_repeat > 1:
                    write_result_avg_rand_planner(PROBLEM, params, repeated_sims, file_obj_avg)

            write_result_by_sim_params(params, problem_params, simulations, file_obj_problem)


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


#For random planners, this is for when num_repeat > 1
def write_result_avg_rand_planner(problem, params, simulations, file_obj_avg):

    # About this simulation
    to_write = problem.name
    to_write += "\t{}\t{}\t{}".format(params.planner.name, params.model.__name__, params.coc)

    # Results
    avg_cost = sum([s.get_total_cost() for s in simulations])/len(simulations)
    to_write += '\t' + str(avg_cost)
    avg_obs = sum([s.total_observations() for s in simulations])/len(simulations)
    to_write += '\t' + str(avg_obs)
    avg_msg_sent = sum([s.total_messages_sent() for s in simulations])/len(simulations)
    to_write += '\t' + str(avg_msg_sent)
    avg_msg_void = sum([s.total_messages_voided() for s in simulations])/len(simulations)
    to_write += '\t' + str(avg_msg_void)
    avg_steps = sum([s.total_steps() for s in simulations])/len(simulations)
    to_write += '\t' + str(avg_steps)

    to_write += '\t' + str(len(simulations))

    file_obj_avg.write(to_write + '\n')

# Write AVERAGED simulation results over n-problems with problem_param
def write_result_by_sim_params(sim_params, problem_params, simulations, file_obj):

    # Planner   Model   CoC
    to_write = "{}\t{}\t{}".format(sim_params.planner.name, sim_params.model.__name__, sim_params.coc)

    # Problem Params: boardx, y, num_soil, num_rocks, rand_range, a_prob
    for p in problem_params.get_params():
        to_write += '\t{}'.format(p)

    # Avg Cost
    avg_cost = sum([sim.get_total_cost() for sim in simulations])/len(simulations)
    to_write += '\t' + str(avg_cost)

    # Num Problems Avged
    to_write += '\t' + str(len(simulations))

    file_obj.write(to_write + '\n')




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

def get_problems_for_costs(num_repeat=1):
    NUM_PROBLEMS = 100
    param = ProblemParameters(BOARD_X=5, BOARD_Y=5, NUM_ROCKS=1, NUM_SOILS=1, RAND_RANGE=10, A_PROB=0.5, num_repeat=num_repeat)

    to_return = {}
    to_return[param] = ProblemLib.find_problems(param.BOARD_X, param.BOARD_Y, NUM_ROCKS=param.NUM_ROCKS, NUM_SOILS=param.NUM_SOILS,\
            RAND_RANGE=param.RAND_RANGE, RAND_PROB=param.A_PROB, limit=NUM_PROBLEMS)
    return to_return

# log_problems(get_params_for_costs(), get_problems_for_costs(), \
#     open("results/test_DetPlanner_over_cost_per_simulation.txt", 'a'), \
#     open("results/test_DetPlanner_over_cost_averaged.txt", 'a'))



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
    problems = {}
    for SIDE in BOARD_SIDES:
        param = ProblemParameters(BOARD_X=int(math.floor(SIDE)), BOARD_Y=int(math.ceil(SIDE)),\
            NUM_ROCKS=1, NUM_SOILS=1, RAND_RANGE=10, A_PROB=0.5)
        problems[param] = ProblemLib.find_problems(param.BOARD_X, param.BOARD_Y, NUM_ROCKS=param.NUM_ROCKS, NUM_SOILS=param.NUM_SOILS,\
            RAND_RANGE=param.RAND_RANGE, RAND_PROB=param.A_PROB, limit=NUM_PROBLEMS)
    return problems

# log_problems(get_params_for_board_sizes(), get_problems_for_board_sizes(), \
#     open("results/TestDetPlanner_over_board_per_simulation.txt", 'a'), \
#     open("results/TestDetPlanner_over_board_averaged.txt", 'a'))


"""
Testing Smart Estimate + bb_prob against SmartComm + v15 (while using averaged(noComm + v15) 
    and averaged(fullComm+v15) as basline
4 Base Simulation parameters: 
    v15+noComm, v15+smartComm, v15+FullComm, bb_prob+smartEst
6 CoC values 
1 fixed board-size: 5
50 problems per simulation parameter
5 repeatitions per problem
6,000 Total problems (for [0, 1, 2, 3, 4, 5])

4 base simulation; 8 CoC Values; 50 problems; 20 repeatitions = 32,000 total problems
4 base simulation; 13 CoC Values; 50 problems; 20 repeatitions = 32,000 total problems

"""
def get_params_for_smartEstimate():
    NUM_REPEAT = 20 # This is for random planners
    # Part 1: DONE
    # COCs = [0, 1, 2, 3, 4, 5]
    # Part 2: TOOD
    # COCs = [0.5, 1.5, 2.5, 3.5, 4.5]
    # # Part 3 CURRENT
    COCs = [0, 0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9]
    # # Part 4 TODO
    COCs += [1, 1.1, 1.2, 1.3, 1.4, 1.6, 1.7, 1.8, 1.9]
    # # Part 5 TODO
    # COCs = [2.1, 2.2, 2.3, 2.4, 2.6, 2.7, 2.8, 2.9]

    PLANNERS = []
    PLANNERS += [Planner.get_HPlanner_v15()] # Quick sampling using A* NOT Random
    MODELS = [models.AgentNoComm, models.AgentSmartComm, models.AgentFullComm]
    PARAMETERS = [SimulationParameters(p, m, c, num_repeat=NUM_REPEAT) for p in PLANNERS for m in MODELS for c in COCs]
    PARAMETERS += [SimulationParameters(Planner.get_HPlanner_bb_prob(), models.AgentSmartEstimate, c, num_repeat=NUM_REPEAT) for c in COCs]
    
    return PARAMETERS

def get_problems_for_smartEstimate():
    NUM_PROBLEMS = 50
    param = ProblemParameters(BOARD_X=5, BOARD_Y=5, NUM_ROCKS=1, NUM_SOILS=1, RAND_RANGE=10, A_PROB=0.5)

    to_return = {}
    to_return[param] = ProblemLib.find_problems(param.BOARD_X, param.BOARD_Y, NUM_ROCKS=param.NUM_ROCKS, NUM_SOILS=param.NUM_SOILS,\
            RAND_RANGE=param.RAND_RANGE, RAND_PROB=param.A_PROB, limit=NUM_PROBLEMS)
    return to_return

# for i in range(300):
#     time.sleep(60)
#     print('starting in {} minutes ... ...'.format(239-i))

# log_problems(get_params_for_smartEstimate(), get_problems_for_smartEstimate(),\
#     open("results/RandPlanner_over_cost_per_simulation_raw.txt", 'a'), \
#     open("results/RandPlanner_over_cost_avg_per_problem.txt", 'a'), \
#     open("results/RandPlanner_over_cost_per_simulation_avg.txt", 'a'))



"""
Testing Smart Estimate + bb_prob against Smart Estimate II + bb_prob over large 
2 Simulation Parameters: SmartEstimate, SmartEstimateII
12 Problem Parameters: Boardsize = 5, 5.5, ..., 10.5
30 Problems per (Sim + Problem parameter)
10 repeatitions per problem
7200 Total Problems (range over large board sizes: hence slow)
"""

def get_params_for_smartEstimateII():
    CoC = 1.5
    NUM_REPEAT = 10
    MODELS = [models.AgentSmartEstimateII, models.AgentSmartEstimate]
    PARAMETERS = [SimulationParameters(Planner.get_HPlanner_bb_prob(), m, CoC, num_repeat=NUM_REPEAT) for m in MODELS]
    return PARAMETERS

def get_problems_for_smartEstimateII():
    NUM_PROBLEMS = 30
    BOARD_SIDES = [0.5 * x for x in range(10,22)]
    problems = {}
    for SIDE in BOARD_SIDES:
        param = ProblemParameters(BOARD_X=int(math.floor(SIDE)), BOARD_Y=int(math.ceil(SIDE)),\
            NUM_ROCKS=1, NUM_SOILS=1, RAND_RANGE=10, A_PROB=0.5)
        problems[param] = ProblemLib.find_problems(param.BOARD_X, param.BOARD_Y, NUM_ROCKS=param.NUM_ROCKS, NUM_SOILS=param.NUM_SOILS,\
            RAND_RANGE=param.RAND_RANGE, RAND_PROB=param.A_PROB, limit=NUM_PROBLEMS)
    return problems

# log_problems(get_params_for_smartEstimateII(), get_problems_for_smartEstimateII(),\
#     open("results/SmartEstimateII_over_board_per_simulation_raw.txt", 'a'), \
#     open("results/SmartEstimateII_over_board_avg_per_problem.txt", 'a'), \
#     open("results/SmartEstimateII_over_board_per_simulation_avg.txt", 'a'))


"""
Testing BPR against SmartEstimate and SmartEstimateII (Over small values of cost.)
2 Simulation Parameters: SmartEstimateII, SmartBPR
8 cost-values
50 problems of 5x5 BOARD
20 repeatitions per problem
16,000 total problems
"""
def get_params_for_BPR_over_costs():
    NUM_REPEAT = 10
    COCs = [0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9]
    MODELS = [models.AgentSmartEstimateII, models.AgentSmartBPR]
    # MODELS = [models.AgentSmartBPRII]
    PLANNERS = []
    PLANNERS += [Planner.get_HPlanner_bb_prob()] # Quick sampling using A* NOT Random
    PARAMETERS = [SimulationParameters(p, m, c, num_repeat=NUM_REPEAT) for p in PLANNERS for m in MODELS for c in COCs]
    return PARAMETERS

def get_problems_for_BPR_over_costs():
    NUM_PROBLEMS = 50
    param = ProblemParameters(BOARD_X=5, BOARD_Y=5, NUM_ROCKS=1, NUM_SOILS=1, RAND_RANGE=10, A_PROB=0.5)

    to_return = {}
    problems = ProblemLib.find_problems(param.BOARD_X, param.BOARD_Y, NUM_ROCKS=param.NUM_ROCKS, NUM_SOILS=param.NUM_SOILS,\
            RAND_RANGE=param.RAND_RANGE, RAND_PROB=param.A_PROB, limit=NUM_PROBLEMS)


    # # Pick every other problem for speed
    # skip = 10
    # new_ps = [problems[i*3] for i in range(NUM_PROBLEMS/skip)]
    # to_return[param] = new_ps
    return to_return
    

# for i in range(240):
#     time.sleep(60)
#     print('starting in {} minutes ... ...'.format(239-i))


# log_problems(get_params_for_BPR_over_costs(), get_problems_for_BPR_over_costs(),\
#     open("results/SmartEstimateII_BPR_over_cost_per_simulation_raw.txt", 'a'), \
#     open("results/SmartEstimateII_BPR_over_cost_avg_per_problem.txt", 'a'), \
#     open("results/SmartEstimateII_BPR_over_cost_per_simulation_avg.txt", 'a'))


log_problems(get_params_for_BPR_over_costs(), get_problems_for_BPR_over_costs(),\
    open("results/SmartBPRII_over_cost_per_simulation_raw.txt", 'a'), \
    open("results/SmartBPRII_over_cost_avg_per_problem.txt", 'a'), \
    open("results/SmartBPRII_over_cost_per_simulation_avg.txt", 'a'))



