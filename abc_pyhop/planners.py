"""
Here we have a library of planners
All planners can be Accessed from this module
Examples of using a planer can be found in planer_lib_example.py
"""
import pyhop
import rovers_world_operators
import rovers_world_methods


class Planner():

	def __init__(self, plan_func):
		self.planner = plan_func

	def plan(self, problem, agent):
		return self.planner(problem, agent)

	""" Below defines the set of possible planners currently in the lib """
	@staticmethod
	def get_HPlanner_v10():
		# Returns the out-of-the-box pyshop planner
		return Planner(pyhop.original_solver)

	@staticmethod
	def get_HPlanner_v12():		
		# This is the curernt version (temp as of 3/26)
		# - Probablistic, returns a single plan
		# - Heuristic, optimal plan not guaranteed 
		# - No Explanation
		# - Outputs 1 plan
		v12 = Planner(None)
		def v12_plan(problem, agent):
			return pyhop.pyhop(problem, agent, plantree=False)
		v12.planner = v12_plan
		return v12