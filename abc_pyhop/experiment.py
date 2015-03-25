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


# Run forever
num_problem = 0
while not models.END_EXPERIMENT:
    logger.info("********** Exeperiment problem number: {} **********".format(num_problem))

    # Setting up a Problem and its corresponding Uncertainties
    """
    Random World and Random Uncertainties
    """
    PROBLEM = get_random_world(BOARD_X=7, BOARD_Y=7, num_agent=2, a_star=True) # with default width and height (10 x 10)
    PROBLEM.ID = int(time.time())
    AGENT_TYPE = models.AgentNoComm
    UNCERTAINTIES = get_uncertainty_fun(PROBLEM, num_step=100, a_prob=1)
    PROBLEM.uncertainties = UNCERTAINTIES
    
    """
    Choose any problem from problem bank
    """
    # PROBLEM = problem_bank.navigate_replan_team_2()

    """
    Run Simulaitons for a given problem
    """
    simulations = []
    MODELS = []
    MODELS += [models.AgentNoComm]
    MODELS += [models.AgentSmartComm]
    MODELS += [models.AgentFullComm]
    for AGENT_TYPE in MODELS:
        logger.info("Initiating simulaiton for AGENT_TYPE:{};".format(AGENT_TYPE.__name__))
        simulation = Simulation(PROBLEM, AGENT_TYPE, gui=False, re_plan=True, use_tree=True)
        logger.info("running simulaiton ...".format(AGENT_TYPE))
        simulation.run()
        simulations.append((AGENT_TYPE, simulation))

    print('\n***** Experiment Summary *****\n')
    for (AGENT_TYPE, simulation) in simulations:
        print('\nProblem Name: {} \nAgent Type: {}'.format(PROBLEM.name, AGENT_TYPE))
        print('simulation total cost {}'.format(sum(simulation.cost_p_agent())))
        print('simulation cost breakdown: ', simulation.cost_p_agent())
        for (agent_name, agent) in simulation.agents.items():
            print(agent_name, agent.get_histories())


