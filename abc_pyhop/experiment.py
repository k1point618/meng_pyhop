"""
Runs various simulations with different agent mental models
For each world, we want to run simulation for multiple agent types

The experiment environment needs to make sure that the same problem and the same
uncertainties are applied to all simulations
"""

from simulate_rovers_world import *
import problem_bank
import models, random_rovers_world

# """
# Navigation: maze_1, ... maze_5
# navigate_replan_team    - Different Agent Models will behave differently.
# navigate_replan
# decompose_replan        - Test Method definition such that agent doesn't start over.
# random                  - Need to set uncertainty parameter
# """
simulation = Simulation(problem_bank.random(), AgentNoComm, gui=True, re_plan=True, uncertainty=0.3)




# # Setting up a Problem and its corresponding Uncertainties
# PROBLEM = get_random_world(num_agent=2, a_star=True) # with default width and height (10 x 10)
# AGENT_TYPE = models.AgentNoComm
# UNCERTAINTIES = get_uncertainty_fun(PROBLEM, num_step=100, a_prob=0)
# PROBLEM.uncertainties = UNCERTAINTIES
# print("UNCERTAINTIES: ", UNCERTAINTIES)


# # Run Simulaitons for a given problem
# simulations = []
# for AGENT_TYPE in [models.AgentNoComm, models.AgentFullComm]:
# 	simulation = Simulation(PROBLEM, AGENT_TYPE, gui=False, re_plan=True)
# 	simulation.run()
# 	simulations.append((AGENT_TYPE, simulation))

# print('\n***** Experiment Summary *****\n')
# for (AGENT_TYPE, simulation) in simulations:
# 	print('\nProblem Name: {} \nAgent Type: {}'.format(PROBLEM.name, AGENT_TYPE))
# 	print('simulation total cost {}'.format(sum(simulation.cost_p_agent())))
# 	print('simulation cost breakdown: ', simulation.cost_p_agent())
# 	for (agent_name, agent) in simulation.agents.items():
# 	    print(agent_name, agent.get_histories())






# TODO: Given a problem, run multiple simulations and get the average score for the success runs
# And count the number of failed runs.

