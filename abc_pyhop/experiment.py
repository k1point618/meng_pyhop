"""
Runs various simulations with different agent mental models
For each world, we want to run simulation for multiple agent types

The experiment environment needs to make sure that the same problem and the same
uncertainties are applied to all simulations
"""

from simulate_rovers_world import *
import problem_bank, time, logging
import models
import random_rovers_world as rrw
from planners import * 

""" *************** Simple simulaiton for 1 agent-type, 1 problem ****************
Navigation: maze_1, ... maze_5
navigate_replan_team    - Different Agent Models will behave differently.
navigate_replan
decompose_replan        - Test Method definition such that agent doesn't start over.
random                  - Need to set uncertainty parameter
"""

# # A single agent with probablistic planning and re-planning
# simulation = Simulation(problem_bank.decompose_replan(), AgentNoComm,
#                       use_tree=True,
#                       gui=True, 
#                       re_plan=True, 
#                       uncertainty=0.5, 
#                       verbose=0)

# simulation = Simulation(problem_bank.navigate_replan_team_2(), AgentNoComm,
#                       use_tree=True,
#                       gui=True, 
#                       re_plan=True, 
#                       uncertainty=0.5, 
#                       verbose=0)

# simulation = Simulation(problem_bank.navigate_replan_team_2(), AgentFullComm,
#                       use_tree=True,
#                       gui=True, 
#                       re_plan=True, 
#                       uncertainty=0.5, 
#                       verbose=0)

# simulation = Simulation(problem_bank.navigate_replan_team_2(), AgentSmartComm,
#                       use_tree=True,
#                       gui=True, 
#                       re_plan=True, 
#                       uncertainty=0.5, 
#                       verbose=0)

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
MODELS += [models.AgentSmartCommII]
MODELS += [models.AgentFullComm]


"""
Pick which Planners to use
"""
PLANNERS = []
# PLANNERS += [Planner.get_HPlanner_v14()] # Quick sampling using A* 
# PLANNERS += [Planner.get_HPlanner_v13()] # Quick Sampling no A*
PLANNERS += [Planner.get_HPlanner_bb()]

"""
Cost of Communication
"""
COSTS = [1]

"""
Choose any problem from problem bank
"""
PROBLEMS = []
random = True
if not random:
    PROBLEMS.append(problem_bank.maze_0())
    PROBLEMS.append(problem_bank.maze_1())
    PROBLEMS.append(problem_bank.maze_2())
    PROBLEMS.append(problem_bank.maze_4())
    PROBLEMS.append(problem_bank.maze_5())
    PROBLEMS.append(problem_bank.navigate_replan_team_2())
    PROBLEMS.append(problem_bank.navigate_replan_team_3())
    # PROBLEMS.append(problem_bank.navigate_replan_team_4()) # Two observations that have joint-effect that is greate than the effect of each
    PROBLEMS.append(problem_bank.navigate_replan_team_5())
    PROBLEMS.append(problem_bank.navigate_replan_team_6())
    PROBLEMS.append(problem_bank.navigate_replan_team_7())

if random:
    num_problems = 1
    PROBLEMS = [rrw.make_random_problem(BOARD_X, BOARD_Y, \
        name=str(time.time()) + '.' + str(i)) for i in range(num_problems)]

"""
Begin Simulations.
"""
for PLANNER in PLANNERS:
    # Each planner result in a different plot

    simulations = {}
    for AGENT_TYPE in MODELS:
        # Each agent is a line in the plot

        simulations[AGENT_TYPE.__name__] = {}
        for COC in COSTS:
            # Each cost is a data point

            simulations[AGENT_TYPE.__name__][COC] = []
            for PROBLEM in PROBLEMS:
                # Each point is the average over all problems
                PROBLEM.COST_OF_COMM = COC
                PROBLEM.COST_REPLAN = 0

                # Run
                logger.info("*** Running simulations for [PROBLEM: {}]\t[MODEL: {}]\t[PLANNER: {}]".format(PROBLEM.name, AGENT_TYPE.__name__, PLANNER.planner.__name__))
                simulation = Simulation(PROBLEM, AGENT_TYPE, PLANNER, gui=GUI)
                simulation.run()
                
                # Add
                simulations[AGENT_TYPE.__name__][COC].append(simulation)


    # Plot/Show
    if show_summary:
        logger.info("*** SUMMARY for Problem {} Summary for Models: {}".format(PROBLEM.name, [m.__name__ for m in MODELS]))

        for (model, sims_m) in simulations.items():
            for (coc, sims_m_c) in sims_m.items():
                for sim_m_c_p in sims_m_c:
                    logger.info(sim_m_c_p.get_summary(cost=True, cost_bd=False, obs=False, comm=True, void=True))
                









# """
# Start simulations for each problem
# """
# while len(PROBLEMS) != 0:
#     PROBLEM = PROBLEMS.pop(0)
#     if random:
#         PROBLEM = rrw.make_random_problem(BOARD_X, BOARD_Y)


#     # Set costs
#     PROBLEM.COST_OF_COMM = 1
#     PROBLEM.COST_REPLAN = 0
    
#     """
#     Run Multiple Simulations for a given problem
#     """
#     simulations = []
    
    
#     logger.info("*** Running simulations for Problem {} for models: {}".format(PROBLEM.name, [m.__name__ for m in MODELS]))
#     for AGENT_TYPE in MODELS:
#         for PLANNER in PLANNERS:
#             logger.info("*** Running simulations for [PROBLEM: {}]\t[MODEL: {}]\t[PLANNER: {}]".format(PROBLEM.name, AGENT_TYPE.__name__, PLANNER.planner.__name__))
#             simulation = Simulation(PROBLEM, AGENT_TYPE, PLANNER, gui=False, re_plan=True, use_tree=False)
#             simulation.run()

            
#             if sum(simulation.cost_p_agent()) > sys.maxint/2: 
#                 # Trying to minimize the uncertainties that makes it impossible
#                 if random:
#                     PROBLEMS.append(make_random_problem)
#                 show_summary = False
#                 logger.info("Incomplete World")
#                 break

#             # If we care to re-play simulations where agents communicated
#             # if simulation.total_messages_sent() != 0 and sum(simulation.cost_p_agent()) > sum(simulations[-1].cost_p_agent()):
#             #     logger.info("communicated AND performed worse... re-running simulaiton with GUI")
#             #     Simulation(PROBLEM, AGENT_TYPE, PLANNER, gui=True, re_plan=True, use_tree=False)
            
#             simulations.append(simulation)




#     # Output summary 
#     if show_summary:
#         logger.info("*** SUMMARY for Problem {} Summary for Models: {}".format(PROBLEM.name, [m.__name__ for m in MODELS]))
#         for sim in simulations:
#             logger.info(sim.get_summary(cost=True, cost_bd=False, obs=False, comm=True, void=True))

#         Simulation.write_to_file(PROBLEM, simulations)

