
import pyhop
from plantree import orNode, andNode
class Solution(object):

	def __init__(self, problem, agent_name, actions, states):
		self.problem = problem
		self.agent = agent_name
		self.actions = actions
		self.states = states
		self.cost = sum([problem.cost_func(problem, a) for a in self.actions])

	def __repr__(self):
		return "Solution Object for Problem:{}; Agent:{}; Expected-Cost:{}\n\tActions:{}"\
			.format(self.problem.name, self.agent, self.get_cost(), self.actions)

	def get_cost(self):
		return self.cost

	# Get Expected Cost relative to a given world belief
	def get_exp_cost(self, world):
		return sum([world.cost_func(world, a) for a in self.actions])

	def get_actions(self):
		return self.actions

	def get_states(self):
		return self.states

	def get_cur_plan(self):
		return (self.actions, self.states)

	# Linear Solution has only 1 plan
	def get_all_plans(self):
		return [(self.actions, self.states)]

class SolutionTree(Solution):

	def __init__(self, root, agent_name, rand=False):
		# root must of type Node
		super(SolutionTree, self).__init__(root.state, agent_name, [], [])
		self.root = root
		self.actions, self.states = self.root.get_plan(rand=rand)
		self.cost = sum([self.problem.cost_func(self.problem, a) for a in self.actions])
		

	def __repr__(self):
		to_return = super(SolutionTree, self).__repr__()
		to_return += "\nroot: {}".format(self.root)
		return to_return

	def get_all_plans(self):
		return self.root.get_all_opt_plans()

	def get_cost(self):
		return self.root.cost

	def get_exp_cost_helper(self, node, world):
		
		assert(node.success)
		if isinstance(node, orNode):
			# Base Cases
			if node.task[0] in pyhop.operators and len(node.children) == 0:
				# Leaf that is an operator
				to_return =  world.cost_func(world, node.task)
			elif len(node.good_children) == 0:
				# dangling leaft with no operator. Precondition already satisfied, no action needed
				to_return = 0
			else:
				# Or node with children: weight them equally.
				k = 1.0/len(node.good_children)
				to_return = sum(k * self.get_exp_cost_helper(c, world) for c in node.good_children)

		elif isinstance(node, andNode):
			to_return = sum(self.get_exp_cost_helper(c, world) for c in node.children)

		else:
			assert(False), "Node is neither OR nor AND: {}".format(node)
		
		return to_return

	def get_exp_cost(self, world):
		return self.get_exp_cost_helper(self.root, world)

