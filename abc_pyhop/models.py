"""
Mental Models for agents
"""
import copy
from plantree import *

class AgentMind():
	"""
	All agent should have
		- a name
		- A view of the world
		- An Idea of its solution, which should include both plan (linear or a planTree)
			and sequence of states
		- It's current position in the plan
		- A history of past steps
	"""
	def __init__(self, name, world):
		self.name = name
		self.world = copy.deepcopy(world)
		self.goal = world.goals[name]
		self.solution = None
		self.planTree = None
		self.actions = None
		self.states = None
		self.cur_step = 0
		self.global_step = 0
		self.histories = []

	def set_solution(self, solution):
		if solution == False:
			# no solution found
			return
		if type(solution) is PlanNode:
			self.planTree = solution
			self.solution = (solution.get_actions(), solution.get_states())
		else:
			self.solution = solution
		self.actions, self.states = self.solution

	def get_solution(self): return self.solution

	def get_planTree(self): return self.planTree

	def get_cur_step(self): return self.cur_step

	def add_history(self, new_action):
		self.histories.append(new_action)

	def is_done(self): return (self.cur_step >= len(self.actions))

	def get_histories(self): return self.histories

	def get_name(self): return self.name

	def get_global_step(self): return self.global_step