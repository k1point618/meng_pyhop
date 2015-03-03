from __future__ import print_function
import copy, sys, pprint

"""
Plan Tree maintains the decomposition information for any given plan. It keeps track of
the chosen decomposition and their corresponding sampling-probabilities.
It maintians strictily more information than the old (solution = (actions, states))
representation.
"""
class PlanTree():
	
	METHOD = 'METHOD'
	OPERATOR = 'OPERATOR'

	def __init__(self, name, node_type):
		self.name = name
		self.children = []
		self.parent = None
		self.before_state = None
		self.after_state = None
		self.node_type = node_type # Method or Operator
	
	def get_states(self):
		if self.node_type == PlanTree.OPERATOR:
			return [self.after_state]
		to_return = []
		for c in self.children:
			to_return+=c.get_states()
		return to_return

	def get_actions(self):
		if self.node_type == PlanTree.OPERATOR:
			return [self.name]
		to_return = []
		for c in self.children:
			to_return += c.get_actions()
		return to_return

	def set_before_state(self, state):
		self.before_state = state
		if self.after_state == None:
			self.after_state = state
		
	def set_after_state(self, state):
		self.after_state = state

	def get_after_state(self):
		return self.after_state

	def set_parent(self, parent_node):
		self.parent = parent_node

	def add_child(self, child_node):
		self.children.append(child_node)
		self.after_state = child_node.after_state

	def num_children(self):
		return len(self.children)

	def get_string(self, prefix=""):
		toReturn = prefix + str(self.name) + ":" + self.node_type  + "\n"
		for child in self.children:
			toReturn += prefix + child.get_string(prefix + " ")
		return toReturn

	def __repr__(self):
		return self.get_string()