"""
Mental Models for agents
"""
import copy, sys
from random_rovers_world import *
from plantree import *

class AgentMind(object):
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
		self.mental_world = copy.deepcopy(world)
		self.goal = world.goals[name]
		self.solution = None
		self.planTree = None
		self.actions = None
		self.states = None
		self.cur_step = 0
		self.global_step = 0
		self.histories = []
		self.done = False
		self.success = False

	def set_solution(self, solution):
		if solution == False or solution == None:
			# no solution found
			self.add_history(('done', sys.maxint))
			self.done = True
			self.success = False
			return
		if isinstance(solution, PlanNode):
			self.planTree = solution
			self.solution = (solution.get_actions(), solution.get_states())
		else:
			self.solution = solution
		(self.actions, self.states) = self.solution

		if len(self.actions) == 0: # Do nothing
			self.done = True
			self.success = True

	def get_solution(self): 
		if self.solution == None or self.solution[0] == False:
			return None
		return self.solution

	def get_planTree(self): return self.planTree

	def get_cur_step(self): return self.cur_step

	def add_history(self, new_action):
		self.histories.append(new_action)

	def is_done(self): return self.done

	def get_histories(self): return self.histories

	def get_name(self): return self.name

	def get_global_step(self): return self.global_step

	def is_success(self): return self.success

	# Given the set of differences observed from environment and communications, 
	# Determine whether or not to re-plan
	def replan_q(self, diffs):
		cur_world = copy.deepcopy(self.mental_world)
		# The agent re-plans when the pre-conditions for any of the future actions is violated
		for step_idx in range(self.cur_step, len(self.actions)):
			cur_action = self.actions[step_idx]
			cur_world = act(cur_world, cur_action)
			if cur_world == False:
				print('Agent Type: {}; must replan!!!!'.format(type(self)))
				return True
		return False


	# Returns the set of observations that is relevatnt to the agent
	# depending on the location of the agent
	# Reminder: Also update agent's mental_world
	# Note: Only looking at location-availability differences and .at[] differences
	def make_observations(self, real_world):

		loc_diff = [] # NOTE TODO: For now it is only location diff
		# at_diff = [] # Note TODO: For now also include object locaitons

		my_l = self.mental_world.at[self.name]
		for l in self.mental_world.loc.keys():
			if AgentMind.visible(my_l, l, real_world, range=2) and self.mental_world.loc_available[l] != real_world.loc_available[l]:
				self.mental_world.loc_available[l] = real_world.loc_available[l]
				loc_diff.append((l, real_world.loc_available[l]))
		
		for (obj, loc) in real_world.at.items():
			if loc != None and AgentMind.visible(my_l, loc, real_world, range=2) and self.mental_world.at[obj] != real_world.at[obj]:
				self.mental_world.at[obj] = real_world.at[obj]
		for (obj, loc) in self.mental_world.at.items():
			if loc != None and AgentMind.visible(my_l, loc, self.mental_world, range=2) and self.mental_world.at[obj] != real_world.at[obj]:
				self.mental_world.at[obj] = real_world.at[obj]

				# at_diff.append((obj, loc))
		print("agent {} is observing the world. Added new diffs".format(self.name))
		print_board(self.mental_world)
		
		return loc_diff#, #at_diff # TODO

	@staticmethod
	def visible(A, B, world, range=2):
		a_x, a_y = world.loc[A]
		b_x, b_y = world.loc[B]
		return((abs(a_x - b_x)**2 + abs(a_y - b_y)**2) <= range)
	
	# Process communication by updating agent's mental_world
	# Return the set of differences
	# Reminder: Also update agent's mental_world
	def incoming_comm(self, communication):
		if (self.name not in communication.keys()) or len(communication[self.name]) == 0:
			return []
		# TODO: given communication, return a set of differences that are new
		# NOTE: assume only location-availability information is given
		loc_diff = []
		inc_diff = communication[self.name]
		print inc_diff
		for (loc, avail) in inc_diff:
			if self.mental_world.loc_available[loc] != avail:
				loc_diff.append((loc, avail))
				self.mental_world.loc_available[loc] = avail
		return loc_diff



class AgentFullComm(AgentMind):
	def __init__(self, name, world):
		super(AgentFullComm, self).__init__(name, world)

	# Given the set of differences observed from environment and communication, 
	# Determine what and to-whom to communicate to.
	def communicate(self, diffs):
		print("Agent {} communicates ... {}".format(self.name, diffs))
		msg = {}
		for agent_name in self.mental_world.goals.keys():
			if agent_name != self.name:
				msg[agent_name] = diffs
		return msg # Communicate All



class AgentNoComm(AgentMind):
	def __init__(self, name, world):
		super(AgentNoComm, self).__init__(name, world)

	# Given the set of differences observed from environment and communication, 
	# Determine what and to-whom to communicate to.
	def communicate(self, diffs):
		print("Agent {} communicates ... None".format(self.name))
		return {} # No comm

	
