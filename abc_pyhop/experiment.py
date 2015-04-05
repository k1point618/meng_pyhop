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

######## Logging ##########
logger = logging.getLogger("experiment_logger")
channel = logging.StreamHandler()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
channel.setFormatter(formatter)
logger.addHandler(channel)

"""
Make a Random World and Random Uncertainties
"""
def make_random_problem():
    logger.info("Making random problem")
    PROBLEM = get_random_world(BOARD_X=7, BOARD_Y=7, num_agent=2, a_star=True) # with default width and height (10 x 10)
    AGENT_TYPE = models.AgentNoComm
    UNCERTAINTIES = get_uncertainty_fun(PROBLEM, num_step=100, a_prob=1)
    PROBLEM.uncertainties = UNCERTAINTIES
    return PROBLEM




"""
Choose any problem from problem bank
"""
PROBLEMS = []
random = False
if not random:
    PROBLEMS.append(problem_bank.maze_0())
    # PROBLEMS.append(problem_bank.maze_1())
    # PROBLEMS.append(problem_bank.maze_2())
    # PROBLEMS.append(problem_bank.maze_4())
    # PROBLEMS.append(problem_bank.maze_5())
    # PROBLEMS.append(problem_bank.navigate_replan_team_2())
    # PROBLEMS.append(problem_bank.navigate_replan_team_3())
    # PROBLEMS.append(problem_bank.navigate_replan_team_4()) # Two observations that have joint-effect that is greate than the effect of each
    # PROBLEMS.append(problem_bank.navigate_replan_team_5())
    # PROBLEMS.append(problem_bank.navigate_replan_team_6())
    # PROBLEMS.append(problem_bank.navigate_replan_team_7())

if random:
    num_problems = 1
    PROBLEMS = [0 for i in range(num_problems)]


"""
Start simulations for each problem
"""
while len(PROBLEMS) != 0:
    PROBLEM = PROBLEMS.pop(0)
    if random:
        PROBLEM = make_random_problem()
        print(PROBLEM.name + "=================")

    show_summary = True

    # Set costs
    PROBLEM.COST_OF_COMM = 1
    PROBLEM.COST_REPLAN = 0
    
    """
    Run Multiple Simulaitons for a given problem
    """
    simulations = []
    MODELS = []
    MODELS += [models.AgentNoComm]
    # MODELS += [models.AgentSmartComm]
    # MODELS += [models.AgentSmartCommII]
    # MODELS += [models.AgentFullComm]

    logger.info("*** Running simulations for Problem {} for models: {}".format(PROBLEM.name, [m.__name__ for m in MODELS]))
    for AGENT_TYPE in MODELS:
        simulation = Simulation(PROBLEM, AGENT_TYPE, Planner.get_HPlanner_bb(), gui=False, re_plan=True, use_tree=False)
        simulation.run()

        if sum(simulation.cost_p_agent()) > sys.maxint/2: 
            # Trying to minimize the uncertainties that makes it impossible
            if random:
                PROBLEMS.append(make_random_problem)
            show_summary = False
            logger.info("Incomplete World")
            break

        simulations.append(simulation)
        

    # Output summary 
    if show_summary:
        logger.info("*** SUMMARY for Problem {} Summary for Models: {}".format(PROBLEM.name, MODELS))
        for sim in simulations:
            logger.info(sim.get_summary(cost=True, cost_bd=False, obs=False, comm=True, void=True))

        Simulation.write_to_file(PROBLEM, simulations)

