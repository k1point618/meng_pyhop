"""
Here we have a library of planners
All planners can be Accessed from this module
Examples of using a planer can be found in planer_lib_example.py
"""
import pyhop
import rovers_world_operators
import rovers_world_methods


class Planner():

	def __init__(self):
		self.planner = None

	def plan(self, problem, agent):
		return self.planner(problem, agent)


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
			return pyhop.seek_plan_v13(problem,problem.goals[agent],[],[],0)
		v13.planner = v13_plan
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
			return solutions
		v14.planner = v14_plan
		return v14


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
		# Returns ALL possible plans
		# - No Explanation
		v20 = Planner()
		def v20_plan(problem, agent):
			problem.a_star = False
			problem.rand = False
			if not hasattr(problem, 'verbose'):
				problem.verbose = 0
			return pyhop.seek_bb(problem, problem.goals[agent], verbose=problem.verbose)

		v20.planner = v20_plan
		return v20

