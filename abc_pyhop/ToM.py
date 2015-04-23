import models
import copy
import solution

class Plan(object):

	def __init__(self, self_name, actions, states):
		self.name = self_name
		self.actions = actions
		self.states = states
		self.idx = 0
		self.done = False
		self.likelihood = None

	def get_actions(self):
		return self.actions

	def get_likelihood(self):
		return self.get_likelihood

	def set_likelihood(self, prob):
		self.likelihood = prob

	def step(self):
		if self.done:
			return

		self.idx += 1

		if self.idx == len(self.actions):
			self.done = True
		
# A distribution of minds
class ToM(object):

	def __init__(self, self_name, other_name, other_solution):
		self.name = self_name, 
		self.other_name = other_name
		self.other_solution = other_solution
		self.plans = []
		for (actions, states) in other_solution.get_all_plans():
			self.plans.append(Plan(other_name, actions, states))

		for p in self.plans:
			p.set_likelihood(1.0/len(self.plans))

	def make_agent_models(self, world):
		self.agent_minds = []
		for p in self.plans:
			teammate = models.AgentMind(self.other_name, copy.deepcopy(world))
			sol = solution.Solution(world, self.name, p.actions, p.states)
			teammate.set_solution(sol)
			self.agent_minds.append(teammate)

	def get_num_plans(self):
		return len(self.plans)

	def get_plans(self):
		return self.plans

	def step(self):
		for p in self.plans:
			p.step()

	def get_agent_minds(self):
		return zip(self.agent_minds, self.plans)


