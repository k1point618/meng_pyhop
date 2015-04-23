"""
Here we have a library of planners
All planners can be Accessed from this module
Examples of using a planer can be found in planer_lib_example.py
"""
import pyhop
import rovers_world_operators
import rovers_world_methods
from solution import Solution, SolutionTree
import sys

class Planner():

	def __init__(self):
		self.planner = None
		self.name = None

	def plan(self, problem, agent):
		return self.planner(problem, agent)

	@staticmethod
	def make_sol_obj(solutions, problem, agent):
		# Make soluiton objects
		sol_objs = []
		for (actions, states) in solutions:
			sol_obj = Solution(problem, agent, actions, states)
			sol_objs.append(sol_obj)
		return sol_objs

	""" Below defines the set of possible planners currently in the lib """
	@staticmethod
	def get_HPlanner_v10():	# Returns the out-of-the-box pyshop planner
		v10 = Planner()
		def v10_plan(problem, agent):
			problem.a_star = False
			problem.rand = True
			return pyhop.seek_plan(problem,problem.goals[agent],[],0)
		v10.planner = v10_plan
		return v10

	@staticmethod
	def get_HPlanner_v11():	# The Out of the box pyshop + A* for navigation
		v10 = Planner()
		def v10_plan(problem, agent):
			problem.a_star = True
			problem.rand = True
			return pyhop.seek_plan(problem,problem.goals[agent],[],0)
		v10.planner = v10_plan
		return v10

	@staticmethod
	# This is the one we would like to use for planning and re-planning
	def get_HPlanner_v13(): # Modified version of original pyhop to achieve hueristic and randomness
		v13 = Planner()
		def v13_plan(problem, agent):
			problem.a_star = False # TODO: need to debug no-a-* first before using v13
			problem.rand = False
			solutions = pyhop.seek_plan_v13(problem,problem.goals[agent],[],[],0)

			# If there is no solution
			if solutions[0] == False:
				return solutions

			return Planner.make_sol_obj(solutions, problem, agent)

		v13.planner = v13_plan
		v13.name = "Det_HTN_OnePlan"
		return v13

	@staticmethod
	def get_HPlanner_v14(): # Modified version of original pyhop for sampling + A* for navigation
		v14 = Planner()
		def v14_plan(problem, agent):
			problem.a_star = True
			problem.rand = False # False for debugging
			if not hasattr(problem, 'verbose'):
				problem.verbose = 0
			elif problem.verbose == 1:
				print("Problem State: ")
				pyhop.print_state(problem)
			solutions = pyhop.seek_plan_v13(problem,problem.goals[agent],[],[],0, verbose=problem.verbose)
			
			# If there is no solution
			if solutions[0] == False:
				return solutions

			return Planner.make_sol_obj(solutions, problem, agent)
			
		v14.planner = v14_plan
		v14.name = "Det_Astar_OnePlan"
		return v14


	@staticmethod
	def get_HPlanner_v15(): # Modified version of original pyhop for sampling + A* for navigation
		v15 = Planner()
		def v15_plan(problem, agent):
			problem.a_star = True
			problem.rand = True # Only difference from v14
			if not hasattr(problem, 'verbose'):
				problem.verbose = 0
			elif problem.verbose == 1:
				print("Problem State: ")
				pyhop.print_state(problem)
			solutions = pyhop.seek_plan_v13(problem,problem.goals[agent],[],[],0, verbose=problem.verbose)
			# If there is no solution
			if solutions[0] == False:
				return solutions
			return Planner.make_sol_obj(solutions, problem, agent)
		v15.planner = v15_plan
		v15.name = "Rand_Astar_OnePlan"
		return v15


	@staticmethod
	def get_HPlanner_v17(): # Modified version of original pyhop for sampling + A* for navigation
		v17 = Planner()
		def v17_plan(problem, agent):
			problem.a_star = True
			problem.rand = True # Only difference from v14
			if not hasattr(problem, 'verbose'):
				problem.verbose = 0
			elif problem.verbose == 1:
				print("Problem State: ")
				pyhop.print_state(problem)
			solutions = pyhop.seek_plan_v13(problem,problem.goals[agent],[],[],0, verbose=problem.verbose)
			# If there is no solution
			if solutions[0] == False:
				return solutions
			return Planner.make_sol_obj(solutions, problem, agent)
		v17.planner = v17_plan
		v17.name = "Rand_Astar_OnePlan2"
		return v17


	@staticmethod
	def get_HPlanner_v12():		
		# - Probablistic: if there are multiple ways to achieve the same cost, then random;
		# 				returns a single plan
		# - Heuristic, optimal plan not guaranteed 
		# - No Explanation
		# - Outputs 1 plan
		# Comment: It uses the all-planner which is slower
		v12 = Planner()
		def v12_plan(problem, agent):
			problem.a_star = True # For performance
			problem.rand = True
			return pyhop.seek_plan_all(problem, problem.goals[agent], plan=[], depth=0, all_plans=False)
		v12.planner = v12_plan
		return v12


	@staticmethod
	def get_HPlanner_v22():		
		# Returns ALL possible plans
		# - No Explanation
		v20 = Planner()
		def v20_plan(problem, agent):
			problem.a_star = False # For performance
			problem.rand = True
			return pyhop.seek_plan_all(problem, problem.goals[agent], plan=[], depth=0, all_plans=True)
		v20.planner = v20_plan
		return v20


	@staticmethod
	def get_HPlanner_bb():		
		# Returns the first result found
		v20 = Planner()
		def v20_plan(problem, agent):
			problem.a_star = True
			problem.rand = False
			if not hasattr(problem, 'verbose'):
				problem.verbose = 0
			root = pyhop.seek_bb(problem, problem.goals[agent], verbose=problem.verbose, all_plans=False)
			return [SolutionTree(root, agent, rand=False)]
			
			# # Even though we get the root, this planner imitates the result of a linear planner.
			# solutions = [root.get_plan()]
			# if solutions[0] == False:
			# 	return solutions
			# return Planner.make_sol_obj(solutions, problem, agent)

		v20.planner = v20_plan
		v20.name = "Det_HTN_BB"
		return v20


	# Is able to reason expected cost over different decompositions.
	@staticmethod
	def get_HPlanner_bb_prob():		
		# Returns ALL possible plans
		# - No Explanation
		v20 = Planner()
		def v20_plan(problem, agent):
			problem.a_star = True
			problem.rand = True
			if not hasattr(problem, 'verbose'):
				problem.verbose = 0
			root = pyhop.seek_bb(problem, problem.goals[agent], verbose=problem.verbose, all_plans=True)
			return [SolutionTree(root, agent, rand=True)]

		v20.planner = v20_plan
		v20.name = "Rand_HTN_BB"
		return v20
