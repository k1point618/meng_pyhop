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
        self.min_cost = 0

        self.type = None
        self.tasks = tasks
        self.parent = parent
        self.left = None
        self.right = None

        self.completed = False
        self.success = None
        self.plans = None

    def get_string(self, prefix=""):
        if self.parent == None:
            parent="NONE"
        else: parent=self.parent.name

        toReturn = prefix + str(self.name) + ":" + self.type + \
                    "\tleft:" + str(self.left) + \
                    "\t cost: " + str(self.cost) + \
                    "\t pre_state: " + str(self.before_state) + \
                    "\t post_state: " + str(self.post_state) + \
                    "\t success: " + str(self.success) + \
                    "\n"
        for child in self.children:
            toReturn += prefix + child.get_string(prefix + " ")
        return toReturn

    def add_child(self, child):
        if len(self.children) == 0:
            self.children = [child]
        else:
            self.children[len(self.children)-1].right = child
            child.left = self.children[len(self.children)-1]
            self.children.append(child)

class andNode(Node):
    def __init__(self, state, parent, tasks):
        super(andNode, self).__init__(state,parent,  tasks)
        self.type = 'AND'

    def __repr__(self):
        return "andNode: {}".format(self.tasks)

    def add_child(self, child):
        super(andNode, self).add_child(child)
        if len(self.children) > 2:
            child.before_state = self.children[-2].post_state

    def update(self, child, openset):
        print("Updating node: {}".format(self))

        # Failed AND node
        if child.completed and child.success == False:
            print("\t FAILED")
            self.success = False
            self.completed = True
            self.cost = sum([c.cost for c in self.children])            
            if self.parent != None:
                self.parent.update(self, openset)

        # All successful
        if all([c.completed and c.success for c in self.children]):
            print("\t ALL SUCCESSFUL")
            self.completed = True
            self.success = True
            self.cost = sum([c.cost for c in self.children])  
            self.post_state = self.children[len(self.children)-1].post_state
            if self.parent != None:
                self.parent.update(self, openset)

        # Making Progress
        if child.success == True and child.completed and not all([c.completed for c in self.children]):
            print("\t MAKING PROGRESS")
            self.min_cost += child.min_cost

    def get_plan(self):
        # print("get plan for {}".format(self))
        # print("------ self.success: ", self.success)
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
                to_return*=c.get_num_plans()
            return to_return
        return 0

import random_rovers_world as rrw
class orNode(Node):
    def __init__(self, state, parent, tasks):
        super(orNode, self).__init__(state,parent,  tasks)
        assert(len(tasks) == 1)
        self.task = tasks[0]
        self.type = 'OR'

    def __repr__(self):
        return "orNode: {}".format(self.tasks)


    def update(self, child, openset):

        if child == None and self.task[0] in operators and len(self.children) == 0:
            # updating for an operator.
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

                print("Found plan for node {} as: ".format(self))
                print(self.get_plan())
            else: 
                # This is a dead node (success = False)
                print("... ... FAILED operator {}; state:".format(self.task))
                rrw.print_board(self.before_state)
                self.post_state = False
                self.success = False
                self.completed = True
                self.cost = sys.maxint

                # No point in adding "right" node
        else:
            print("Updating node: {}".format(self))

            # If failed, then look for the next
            if child.success == False and child.completed:
                print("Child failed")
                if child.right != None:
                    openset.append(child.right)
                    return

            # Most recently completed node
            if child.completed and child.success:
                self.post_state = child.post_state 

            # Best Case Scenario
            # print("self.children completed: {}".format([c.completed for c in self.children]))
            self.completed = any([c.completed for c in self.children])
            if self.completed:
                self.success = any([c.success for c in self.children])
            else:
                self.success = None
            self.cost = min([c.cost for c in self.children])

            # print("{} success: {}".format(self, self.success))
            # print("{} right: {}".format(self, self.right))
            if self.right != None and self.success:
                self.right.before_state = self.post_state
                openset.append(self.right)


        if self.parent != None:
            self.parent.update(self, openset)

    def get_plan(self):
        # print("get plan for {}".format(self))
        if len(self.children) == 0 and self.success:
            # print("... returning {}".format([self.task]))
            return ([self.task], [self.post_state])

        to_return = []
        if self.success:
            for c in self.children:
                if c.success:
                    (actions, states) = c.get_plan()
                    return (actions, states)

    def get_num_plans(self):
        if self.success:
            if len(self.children) == 0:
                return 1
            to_return = 0
            for c in self.children:
                to_return += c.get_num_plans()
            # print("get_num_plans {}: returning {}".format(self, to_return))
            return to_return
        return 0






