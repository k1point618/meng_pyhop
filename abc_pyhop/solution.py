
class Solution(object):

	def __init__(self, problem, agent_name, actions, states):
		self.problem = problem
		self.agent = agent_name
		self.actions = actions
		self.states = states


	def __repr__(self):
		return "Solution Object for Problem:{}; Agent:{}; Expected-Cost:{}\n\tActions:{}"\
			.format(self.problem.name, self.agent, self.get_cost(self.problem), self.actions)

	# Get Expected Cost relative to a given world belief
	def get_cost(self, world):
		return sum([world.cost_func(world, a) for a in self.actions])

	def get_actions(self):
		return self.actions

	def get_states(self):
		return self.states