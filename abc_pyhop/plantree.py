from __future__ import print_function
import copy, sys, pprint
from pyhop import *
import rovers_world_operators
import rovers_world_methods
from random_rovers_world import *

"""
Plan Tree maintains the decomposition information for any given plan. It keeps track of
the chosen decomposition and their corresponding sampling-probabilities.
It maintians strictily more information than the old (solution = (actions, states))
representation.
"""
class PlanNode():
    
    METHOD = 'METHOD'
    OPERATOR = 'OPERATOR'

    def __init__(self, name, node_type):
        self.name = name
        self.children = []
        self.parent = None
        self.before_state = None
        self.after_state = None
        self.node_type = node_type # Method or Operator
        self.cost = 0
    
    def get_states(self):
        if self.node_type == PlanNode.OPERATOR:
            return [self.after_state]
        to_return = []
        for c in self.children:
            to_return+=c.get_states()
        return to_return

    def get_actions(self):
        if self.node_type == PlanNode.OPERATOR:
            return [self.name]
        to_return = []
        for c in self.children:
            to_return += c.get_actions()
        return to_return

    # Return the leaves of current node 
    def get_action_nodes(self):
        if self.node_type == PlanNode.OPERATOR:
            return [self]
        to_return = []
        for c in self.children:
            to_return += c.get_action_nodes()
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
        self.cost += child_node.cost

    def num_children(self):
        return len(self.children)

    def get_string(self, prefix=""):
        if self.parent == None:
            parent="NONE"
        else: parent=self.parent.name

        toReturn = prefix + str(self.name) + ":" + self.node_type  + "\tPARENT:" + str(parent) + "\n"
        for child in self.children:
            toReturn += prefix + child.get_string(prefix + " ")
        return toReturn

    """
    Given a node, return a list of explainations for what the node is trying to achieve
    """
    @staticmethod
    def explain(node):
        if node.parent == None:
            return []
        return [node.parent] + PlanNode.explain(node.parent)

    def expland(node):
        return self.children

    def __repr__(self):
        return self.get_string()

    # @staticmethod
    # def print_planTree(root):


class Node(object):
    def __init__(self, state, parent, tasks):
        self.name = str(tasks)
        self.state = state
        self.before_state = copy.deepcopy(state)
        self.post_state = self.before_state
        self.children = []
        self.cost = sys.maxint
        self.type = None
        self.tasks = tasks
        self.parent = parent
        self.left = None
        self.right = None

        self.completed = False
        self.success = False
        self.plans = None

    def get_string(self, prefix=""):
        if self.parent == None:
            parent="NONE"
        else: parent=self.parent.name

        toReturn = prefix + str(self.name) + ":" + self.type + "\tleft:" + str(self.left) + \
                    "\t cost: " + str(self.cost) + \
                    "\t pre_state: " + str(self.before_state) + \
                    "\t post_state: " + str(self.post_state) + \
                    "\n"
        for child in self.children:
            toReturn += prefix + child.get_string(prefix + " ")
        return toReturn


class andNode(Node):
    def __init__(self, state, parent, tasks):
        super(andNode, self).__init__(state,parent,  tasks)
        self.type = 'AND'

    def __repr__(self):
        return "andNode: {}".format(self.tasks)

    def update(self, child, openset):

        completed = all([c.completed for c in self.children])
        success = all([c.success for c in self.children])
        cost = sum([c.cost for c in self.children])
        if completed != self.completed or success != self.success or cost != self.cost:
            self.completed = completed
            self.success = success
            self.cost = cost
            self.post_state = self.children[len(self.children)-1].post_state
            if self.parent != None:
                self.parent.update(self, openset)

    def get_plan(self):
        actions = []
        states = []
        if self.success:
            for child in self.children:
                a, s = child.get_plan()
                actions += a
                states += s

        return (actions, states)

    def get_num_plans(self):
        if self.success:
            to_return = 1
            for c in self.children:
                to_return+=c.get_num_plans()
        return 0

class orNode(Node):
    def __init__(self, state, parent, tasks):
        super(orNode, self).__init__(state,parent,  tasks)
        assert(len(tasks) == 1)
        self.task = tasks[0]
        self.type = 'OR'

    def __repr__(self):
        return "orNode: {}".format(self.tasks)

    def set_left(self, left_node):
        self.left = left_node
        self.before_state = left_node.post_state
        left_node.right = self

    def update(self, child, openset):
        # If or-node is a single operator
        if child == None and self.task[0] in operators and len(self.children) == 0:
            print("ORNODE: ... cur_node {} is an OPERATOR".format(self))
            operator = operators[self.task[0]]
            new_state = operator(copy.deepcopy(self.before_state),*self.task[1:])
            if new_state:
                self.post_state = new_state
                self.success = True
                self.completed = True

                # Set Cost
                self.cost = self.state.cost_func(self.state, self.task[0])

                # Continue
                if self.right != None:
                    self.right.before_state = self.post_state
                    openset.append(self.right)
            else: 
                print("... ... FAILED operator {}; state:".format(self.task))
                rrw.print_board(self.before_state)
                self.post_state = False
                self.success = False
                self.completed = False
                self.cost = sys.maxint

                # No point in adding "right" node
        else:
            self.completed = any([c.completed for c in self.children])
            self.success = any([c.success for c in self.children])
            self.cost = min([c.cost for c in self.children])

            if child.completed:
                self.cost = min(self.cost, child.cost)
                self.post_state = child.post_state 
            
            

            if self.right != None and self.success:
                self.right.before_state = self.post_state
                openset.append(self.right)


        if self.parent != None:
            self.parent.update(self, openset)

    def get_plan(self):
        if len(self.children) == 0 and self.success:
            return ([self.task], [self.post_state])

        to_return = []
        if self.success:
            (actions, states) = random.choice(self.children).get_plan()
            return (actions, states)

    def get_num_plans(self):
        if self.success:
            if len(self.children) == 0 :
                return 1
            to_return = 0
            for c in self.children:
                to_return += c.get_num_plans()
        return 0