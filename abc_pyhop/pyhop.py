"""
Pyhop, version 1.2.2 -- a simple SHOP-like planner written in Python.
Author: Dana S. Nau, 2013.05.31

Copyright 2013 Dana S. Nau - http://www.cs.umd.edu/~nau

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
   
Pyhop should work correctly in both Python 2.7 and Python 3.2.
For examples of how to use it, see the example files that come with Pyhop.

Pyhop provides the following classes and functions:

- foo = State('foo') tells Pyhop to create an empty state object named 'foo'.
  To put variables and values into it, you should do assignments such as
  foo.var1 = val1

- bar = Goal('bar') tells Pyhop to create an empty goal object named 'bar'.
  To put variables and values into it, you should do assignments such as
  bar.var1 = val1

- print_state(foo) will print the variables and values in the state foo.

- print_goal(foo) will print the variables and values in the goal foo.

- declare_operators(o1, o2, ..., ok) tells Pyhop that o1, o2, ..., ok
  are all of the planning operators; this supersedes any previous call
  to declare_operators.

- print_operators() will print out the list of available operators.

- declare_methods('foo', m1, m2, ..., mk) tells Pyhop that m1, m2, ..., mk
  are all of the methods for tasks having 'foo' as their taskname; this
  supersedes any previous call to declare_methods('foo', ...).

- print_methods() will print out a list of all declared methods.

- pyhop(state1,tasklist) tells Pyhop to find a plan for accomplishing tasklist
  (a list of tasks), starting from an initial state state1, using whatever
  methods and operators you declared previously.

- In the above call to pyhop, you can add an optional 3rd argument called
  'verbose' that tells pyhop how much debugging printout it should provide:
- if verbose = 0 (the default), pyhop returns the solution but prints nothing;
- if verbose = 1, it prints the initial parameters and the answer;
- if verbose = 2, it also prints a message on each recursive call;
- if verbose = 3, it also prints info about what it's computing.
"""

# Pyhop's planning algorithm is very similar to the one in SHOP and JSHOP
# (see http://www.cs.umd.edu/projects/shop). Like SHOP and JSHOP, Pyhop uses
# HTN methods to decompose tasks into smaller and smaller subtasks, until it
# finds tasks that correspond directly to actions. But Pyhop differs from 
# SHOP and JSHOP in several ways that should make it easier to use Pyhop
# as part of other programs:
# 
# (1) In Pyhop, one writes methods and operators as ordinary Python functions
#     (rather than using a special-purpose language, as in SHOP and JSHOP).
# 
# (2) Instead of representing states as collections of logical assertions,
#     Pyhop uses state-variable representation: a state is a Python object
#     that contains variable bindings. For example, to define a state in
#     which box b is located in room r1, you might write something like this:
#     s = State()
#     s.loc['b'] = 'r1'
# 
# (3) You also can define goals as Python objects. For example, to specify
#     that a goal of having box b in room r2, you might write this:
#     g = Goal()
#     g.loc['b'] = 'r2'
#     Like most HTN planners, Pyhop will ignore g unless you explicitly
#     tell it what to do with g. You can do that by referring to g in
#     your methods and operators, and passing g to them as an argument.
#     In the same fashion, you could tell Pyhop to achieve any one of
#     several different goals, or to achieve them in some desired sequence.
# 
# (4) Unlike SHOP and JSHOP, Pyhop doesn't include a Horn-clause inference
#     engine for evaluating preconditions of operators and methods. So far,
#     I've seen no need for it; I've found it easier to write precondition
#     evaluations directly in Python. But I could consider adding such a
#     feature if someone convinces me that it's really necessary.
# 
# Accompanying this file are several files that give examples of how to use
# Pyhop. To run them, launch python and type "import blocks_world_examples"
# or "import simple_travel_example".


from __future__ import print_function
import copy,sys, pprint
from plantree import *

############################################################
# States and goals

class State():
    """A state is just a collection of variable bindings."""
    def __init__(self,name):
        self.__name__ = name

    """ Two states are equal if their attributes have the same face values """
    def __eq__(self, other):
        attrs_self = sorted(dir(self))
        attrs_other = sorted(dir(other))
        if attrs_self == attrs_other:
            for attr in attrs_self:
                if attr[0:2] =='__': continue
                if getattr(self, attr) != getattr(other, attr): 
                    print('not equ', attr)
                    return False
            return True
        else: return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        attrs = sorted(dir(self))
        values = []
        for attr in attrs:
            if attr[0:2] != '__':
                values.append(str(getattr(self, attr)))
        return hash(frozenset(values + attrs))

class Goal():
    """A goal is just a collection of variable bindings."""
    def __init__(self,name):
        self.__name__ = name


### print_state and print_goal are identical except for the name

def print_state(state,indent=4):
    """Print each variable in state, indented by indent spaces."""
    if state != False:
        for (name,val) in vars(state).items():
            if name != '__name__':
                for x in range(indent): sys.stdout.write(' ')
                sys.stdout.write(state.__name__ + '.' + name)
                print(' =', val)
    else: print('False')

def print_goal(goal,indent=4):
    """Print each variable in goal, indented by indent spaces."""
    if goal != False:
        for (name,val) in vars(goal).items():
            if name != '__name__':
                for x in range(indent): sys.stdout.write(' ')
                sys.stdout.write(goal.__name__ + '.' + name)
                print(' =', val)
    else: print('False')

############################################################
# Helper functions that may be useful in domain models

def forall(seq,cond):
    """True if cond(x) holds for all x in seq, otherwise False."""
    for x in seq:
        if not cond(x): return False
    return True

def find_if(cond,seq):
    """
    Return the first x in seq such that cond(x) holds, if there is one.
    Otherwise return None.
    """
    for x in seq:
        if cond(x): return x
    return None

############################################################
# Commands to tell Pyhop what the operators and methods are

operators = {}
methods = {}

def declare_operators(*op_list):
    """
    Call this after defining the operators, to tell Pyhop what they are. 
    op_list must be a list of functions, not strings.
    """
    operators.update({op.__name__:op for op in op_list})
    return operators

def declare_methods(task_name,*method_list):
    """
    Call this once for each task, to tell Pyhop what the methods are.
    task_name must be a string.
    method_list must be a list of functions, not strings.
    """
    methods.update({task_name:list(method_list)})
    return methods[task_name]

############################################################
# Commands to find out what the operators and methods are

def print_operators(olist=operators):
    """Print out the names of the operators"""
    print('OPERATORS:', ', '.join(olist))

def print_methods(mlist=methods):
    """Print out a table of what the methods are for each task"""
    print('{:<14}{}'.format('TASK:','METHODS:'))
    for task in mlist:
        print('{:<14}'.format(task) + ', '.join([f.__name__ for f in mlist[task]]))

############################################################
# The actual planner

NUM_RECURSE_CALLS = 0 # For benchmarking purpose
def get_num_recurse_calls():
    global NUM_RECURSE_CALLS
    return NUM_RECURSE_CALLS
def reset_num_recurse_calls():
    global NUM_RECURSE_CALLS
    NUM_RECURSE_CALLS = 0

def pyhop(state,agent,verbose=0, all_solutions=False, plantree=False, rand=False):
    """
    Try to find a plan that accomplishes the goal of a given @agent
    If successful, return the plan. Otherwise return False.
    """
    tasks = state.goals[agent]
    if verbose>0: print('** pyhop, verbose={}: **\n   state = {}\n    agent={}\n   tasks = {}'
        .format(verbose, state.__name__, agent, tasks))
    
    # For benchmarking
    reset_num_recurse_calls()
    reset_plan_library()
    
    # At the beginning of planning, reset "visited" from the planning world.
    if plantree:
        planTrees = seek_plantrees(state,tasks,None,0,verbose, all_plans=all_solutions, rand=rand)
        print("**** Final PlanNodes: **** \n{}".format(planTrees))
        print("found {} plans:".format(len(planTrees)))
        return planTrees
    else:
        results = seek_plan_all(state,tasks,[],0,verbose, all_plans=all_solutions, rand=rand)
        print(len(results))
        print(results)
        return results

"""
kgu: Below is the original implementation. It returns the first plan found.
"""
def seek_plan(state,tasks,plan,depth,verbose=0):
    """
    Workhorse for pyhop. state and tasks are as in pyhop.
    - plan is the current partial plan.
    - depth is the recursion depth, for use in debugging
    - verbose is whether to print debugging messages
    """
    if verbose>1: print('depth {} tasks {}'.format(depth,tasks))
    if tasks == []:
        if verbose>2: print('depth {} returns plan {}'.format(depth,plan))
        return plan
    task1 = tasks[0]
    if task1[0] in operators:
        if verbose>2: print('depth {} action {}'.format(depth,task1))
        operator = operators[task1[0]]
        newstate = operator(copy.deepcopy(state),*task1[1:])
        if verbose>2:
            print('depth {} new state:'.format(depth))
            print_state(newstate)
        if newstate:
            solution = seek_plan(newstate,tasks[1:],plan+[task1],depth+1,verbose)
            if solution != False:
                return solution
    if task1[0] in methods:
        if verbose>2: print('depth {} method instance {}'.format(depth,task1))
        relevant = methods[task1[0]]
        for method in relevant:
            subtasks = method(state,*task1[1:])
            # Can't just say "if subtasks:", because that's wrong if subtasks == []
            if verbose>2:
                print('depth {} new tasks: {}'.format(depth,subtasks))
            if subtasks != False:
                solution = seek_plan(state,subtasks+tasks[1:],plan,depth+1,verbose)
                if solution != False:
                    return solution
    if verbose>2: print('depth {} returns failure'.format(depth))
    return False

"""
Below author: kgu@mit.edu
Recursive on the order of the depth of the tree, not the length of the plan
"""
def seek_plan_2(state,tasks,plan,depth,verbose=0):
    """
    Workhorse for pyhop. state and tasks are as in pyhop.
    - plan is the current partial plan.
    - depth is the recursion depth, for use in debugging
    - verbose is whether to print debugging messages
    """

    cur_plan = []

    if tasks == []:
        return ([], state)

    task1 = tasks[0]
    if task1[0] in operators:
        operator = operators[task1[0]]
        newstate = operator(copy.deepcopy(state),*task1[1:])
        if newstate:
            # Operator Execution complete
            return ([task1], newstate) # Return (Plan, newsate) pair
        else: return False
    elif task1[0] in methods:
        relevant = methods[task1[0]]
        for method in relevant:
            subtasks = method(state,*task1[1:])
            if subtasks != False:
                backup_state = copy.deepcopy(state)
                for subtask in subtasks: # For each of the decomposed tasks:
                    solution = seek_plan_2(copy.deepcopy(state), [subtask], plan, depth+1, verbose)
                    if solution != False:
                        (partial_plan, newstate) = solution
                        state = newstate
                        cur_plan = cur_plan + partial_plan
            else: # There is no suitable decomposition
                print("there is no suitable decomposition")
                return False
        return (cur_plan, state)
    else:
        return False

"""
Below author: kgu@mit.edu
If all_plans = False, then return the first plan found deterministically. 
"""
# Returns a list of possible [(Plan, End-state)] pairs
def seek_plan_all(state,tasks,plan,depth,verbose=0, all_plans=False, rand=False):
    
    global NUM_RECURSE_CALLS 
    NUM_RECURSE_CALLS += 1 # For benchmarking 

    if verbose>2:print(depth, 'current tasks: ', tasks, 'all_plans=', all_plans)
    plans = []
    if len(tasks) > 1:
        this_solutions = seek_plan_all(copy.deepcopy(state), [tasks[0]], [], depth+1, verbose, all_plans)
        if this_solutions[0] != False:
            for solution in this_solutions:
                (plan, state_1) = solution
                prev_state = state if (len(plan) == 0) else state_1[-1]
                solutions_2 = seek_plan_all(copy.deepcopy(prev_state), tasks[1:], [], depth+1, verbose, all_plans)
                if solutions_2[0] != False:
                    for solution2 in solutions_2:
                        (plan2, state_2) = solution2
                        plans.append((plan + plan2, state_1 + state_2))
                else: return [False]
            if verbose>2: print(depth, 'returning plan {} for task {}'.format(plans, tasks))
            return plans
        else: return [False]

    elif len(tasks) == 1:
        task1 = tasks[0]
        if task1[0] in operators:
            operator = operators[task1[0]]
            newstate = operator(copy.deepcopy(state),*task1[1:])
            if newstate:
                return [([task1], [newstate])]
            else:
                return [False]
        elif task1[0] in methods:
            if verbose>2: print ('\t is method')
            relevant = methods[task1[0]]
            for method in relevant: # All related methods
                decompositions = method(state,*task1[1:], rand=rand) # Returns the set of possible decompositions

                if verbose>2: print(depth, 'decomposed {} into \n\t{}'.format(task1, decompositions))
                if decompositions[0] != False:
                    for subtasks in decompositions: # For each decomposition
                        # Solutions: the number of ways to acomplish a given sequence of subtasks
                        # All solutions have OR relationship
                        solutions = seek_plan_all(copy.deepcopy(state), subtasks, [], depth+1, verbose, all_plans)
                        if solutions[0] != False:
                            plans = plans + solutions
                            if not all_plans:
                                return plans

    if tasks == []:
        return [([], [])]

    if plans == []:
        return [False]
    else: 
        return plans

"""
Below is a rescursive seek-plan that finds all plans and keeps track of subproblems 
that have been already solved. (It was an attempt to amortization)
"""
PLAN_LIBRARY = {} # Maps (Task, state) to an array of Plans
def reset_plan_library():
    global PLAN_LIBRARY
    PLAN_LIBRARY = {}

def seek_plan_all_r(state,tasks,plan,depth,verbose=0, all_plans=False):

    if verbose>2:print(depth, 'current tasks: ', tasks, 'all_plans=', all_plans)

    global NUM_RECURSE_CALLS
    NUM_RECURSE_CALLS += 1 # For benchmarking 
    plans = []

    # When given a sequence of tasks, we reduce the problem to finding all possible 
    # solutions for each task and are linked together by the new states between the 
    # task transitions
    if len(tasks) > 1:
        this_solutions = seek_plan_all_r(copy.deepcopy(state), [tasks[0]], [], depth+1, verbose, all_plans)
        if this_solutions[0] != False:
            for solution in this_solutions:
                if verbose>2:print(depth, 'one plan:', solution)
                (plan, state_1) = solution
                if verbose>2:print('remaining tasks:', tasks[1:])
                solutions_2 = seek_plan_all_r(copy.deepcopy(state_1[-1]), tasks[1:], [], depth+1, verbose, all_plans)
                if solutions_2[0] != False:
                    for solution2 in solutions_2:
                        (plan2, state_2) = solution2
                        plans.append((plan + plan2, state_1 + state_2))
                else: return [False]
            if verbose>2: print(depth, 'returning plan {} for task {}'.format(plans, tasks))
            return plans
        else: return [False]

    # When the problem is to solve a single task
    elif len(tasks) == 1:
        task1 = tasks[0]

        # Check if the current subproblem has already been solved
        global PLAN_LIBRARY

        if (task1, state) in PLAN_LIBRARY:
            if verbose>2: print(depth, 'skipped recursion for task:{} state:{}'.format(task1, state))
            # PLAN LIBRARY maps to a list of possible plans
            return PLAN_LIBRARY[(task1, state)] 

        # When current task is an operator
        if task1[0] in operators:
            operator = operators[task1[0]]
            newstate = operator(copy.deepcopy(state),*task1[1:])
            if newstate:
                return [([task1], [newstate])]
            else:
                return [False]

        # When current task is a method
        elif task1[0] in methods:
            if verbose>2: print ('\t is method')
            relevant = methods[task1[0]]
            for method in relevant: # All related methods
                if all_plans:
                    decompositions = method(state,*task1[1:], all_decomp=all_plans) # Returns the set of possible decompositions
                else:
                    decompositions = [ method(state,*task1[1:], all_decomp=all_plans) ]
                if verbose>2: print(depth, 'decomposed {} into \n\t{}'.format(task1, decompositions))
                if decompositions[0] != False:
                    for subtasks in decompositions: # For each decomposition
                        # Solutions: the number of ways to acomplish a given sequence of subtasks
                        # All solutions have OR relationship
                        solutions = seek_plan_all_r(copy.deepcopy(state), subtasks, [], depth+1, verbose, all_plans)
                        if solutions[0] != False:
                            plans = plans + solutions


    if tasks == []:
        return [([], [state])]

    if plans == []:
        return [False]
    else: 
        # print(depth, 'found plan')
        PLAN_LIBRARY[(task1, state)] = plans
        if verbose >2: 
            print('added task {} to plan library'.format(task1))
        return plans
        


"""
Below is version of seek plan that is identical to seek_plan_all, but returns a plan-tree
as opposed to a linear solution

Returns a list of plantrees where the rootes given as input

"""
def seek_plantrees(state, tasks, root, depth, verbose=0, all_plans=False, rand=False):
    
    if root == None:
        root = PlanNode('root', PlanNode.METHOD)
    if verbose: print("depth {}; seek_plantree for task {}\n\trootnode is {}".format(depth, tasks, root))
    planTrees = []
    
    if len(tasks) > 1:
        firstNode = PlanNode(tasks[0], None)
        first_roots = seek_plantrees(copy.deepcopy(state), [tasks[0]], root, depth+1, verbose, all_plans)        
        if first_roots[0] == None:
            return [None]
        if verbose: print("\tfound {} plan(s) for first task {}".format(len(first_roots), tasks[0]))
        for new_root in first_roots:
            rest_plans = seek_plantrees(copy.deepcopy(new_root.get_after_state()), tasks[1:], new_root, depth+1, verbose, all_plans)
            if rest_plans[0] != None:
                planTrees += rest_plans
            else: return [None]
        return planTrees

    if len(tasks) == 0:
        to_return = copy.deepcopy(root)
        return [to_return]

    task = tasks[0]
    # If the task is a primitive action
    if task[0] in operators:
        if verbose: print("\t task {} is an operator".format(task[0]))
        operator = operators[task[0]]
        newstate = operator(copy.deepcopy(state),*task[1:])
        if newstate:
            # Create Leaf Node
            to_return = copy.deepcopy(root)
            leafNode = PlanNode(task, PlanNode.OPERATOR)
            leafNode.set_before_state(copy.deepcopy(state))
            leafNode.set_after_state(copy.deepcopy(newstate))
            leafNode.set_parent(to_return)
            to_return.add_child(leafNode)
            to_return.set_after_state(copy.deepcopy(newstate))
            return [to_return]

    elif task[0] in methods:
        if verbose: print("\t task {} is a method".format(task[0]))
        relevant = methods[task[0]]
        for method in relevant: # All related methods
            decompositions = method(state,*task[1:], rand=rand) # Returns the set of possible decompositions
            if decompositions[0] == False:
                # Cannot use this relevant method definition
                continue
            for subtasks in decompositions:
                if verbose: print("\tdecomposition:{}".format(subtasks))
                methodNode = PlanNode(task, PlanNode.METHOD)
                methodNode.set_before_state(state)
                methodNode.set_after_state(state)

                possible_plans = seek_plantrees(copy.deepcopy(state), subtasks, copy.deepcopy(methodNode), depth+1, verbose, all_plans)
                if verbose: 
                    print("depth {}; method task found {} new plans for task {}\
                    \n\twith decomposition {}".format(depth, len(possible_plans), task, subtasks))
                if possible_plans[0] != None:
                    for node in possible_plans: # Each node is a way of completeing the subtasks
                        to_return = copy.deepcopy(root)
                        to_return.add_child(node)
                        to_return.set_after_state(node.get_after_state())
                        planTrees.append(to_return)

        if verbose: print("\nreturning plans for {}".format(task))
        if len(planTrees) == 0:
            return [None]
        return planTrees

    return [None]

