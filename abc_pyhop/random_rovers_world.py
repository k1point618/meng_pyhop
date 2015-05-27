""" 
We actually keep anything related to the Rover's world state in this file. Including
- Generat a random world
- Visualize a given world
- Generate uncertainty to a given world

We generate a random rover's world from a set of parameters. 
The resulting world will be represented as a State object with variable bindings.

Author: Keren Gu (kgu@mit.edu)
"""

from __future__ import print_function
from pyhop import *
import random
import time
import math
import rovers_world_operators
import rovers_world_methods
import numpy

"""
Make a Random World AND Random Uncertainties
"""
def make_random_problem(BOARD_X, BOARD_Y, rand_range=None, max_cost=None, name=None, a_prob=0.5):
    PROBLEM = get_random_world(BOARD_X=BOARD_X, BOARD_Y=BOARD_Y, num_agent=3, a_star=True, name=name) # with default width and height (10 x 10)
    if rand_range != None:
        PROBLEM.RAND_RANGE = rand_range
        if max_cost == None:
            PROBLEM.MAX_COST = 3 * rand_range
    if max_cost != None:
        PROBLEM.MAX_COST = max_cost
    UNCERTAINTIES = get_uncertainty_fun(PROBLEM, num_step=BOARD_X*BOARD_Y, a_prob=a_prob)
    PROBLEM.uncertainties = UNCERTAINTIES
    return PROBLEM

"""
Make a Semi-Random World AND Random Uncertainties
"""
# def make_semi_random_problem(BOARD_X, BOARD_Y, rand_range=None, max_cost=None, name=None, a_prob=0.3):
#     PROBLEM = get_semi_random_world(BOARD_X=BOARD_X, BOARD_Y=BOARD_Y, num_agent=2, name=name) # with default width and height (10 x 10)
#     if rand_range != None:
#         PROBLEM.RAND_RANGE = rand_range
#         if max_cost == None:
#             PROBLEM.MAX_COST = 3 * rand_range
#     if max_cost != None:
#         PROBLEM.MAX_COST = max_cost
#     UNCERTAINTIES = get_uncertainty_fun(PROBLEM, num_step=BOARD_X*BOARD_Y, a_prob=a_prob)
#     PROBLEM.uncertainties = UNCERTAINTIES
#     return PROBLEM

"""
Make World where agents starts in the middle of the world and soils and distributed equal-distance from
the agents. Lab and Lander are distributed randomly in the world
"""
# def get_semi_random_world(BOARD_X=10, BOARD_Y=10, num_agent=1, name=None):
#     if name == None:
#         name = str(time.time())

#     ##############################
#     # Below, we generate the world with pre-defined randomness.

#     # General and Miscellaneous World info
#     world = State("InitialWorld")
#     world.name = name
#     world.prop = {"num_col":BOARD_Y, "num_row":BOARD_X}
#     available_spaces = range(1,(BOARD_X*BOARD_Y+1))
#     world.at = {}
#     world.store_has = {}
#     world.has_soil_sample = {}
#     world.soil_sample = {}
#     world.has_rock_sample = {}
#     world.rock_sample = {}
#     world.has_soil_analysis = {}
#     world.soil_analysis = {}
#     world.has_rock_analysis = {}
#     world.rock_analysis = {}


#     # Agents
#     world.is_agent = {}
#     world.visited = {}
#     world.available = {}
#     world.stores = {}
#     world.store_has = {}
#     world.empty = {}
#     world.equipped_for_imaging = {}
#     world.equipped_for_rock_analysis = {}
#     world.equipped_for_soil_analysis = {}
#     for agent_id in range(num_agent):

#         agent = "A" + str(agent_id+1)

#         world.is_agent[agent] = True
#         # Put agent somewhere in the center of the board.
#         x = random.choice(range(int(BOARD_X*0.25), int(math.ceil(BOARD_X*0.75))))
#         y = random.choice(range(int(BOARD_Y*0.25), int(math.ceil(BOARD_Y*0.75))))
#         loc = (x)*BOARD_X + (y+1)
#         world.at[agent] = loc
#         if loc in available_spaces:
#             available_spaces.remove(loc)
#         world.visited[agent] = set()
#         world.visited[agent].add(loc)

#         # Agent's capabilities
#         world.equipped_for_imaging[agent] = True
#         world.equipped_for_rock_analysis[agent] = True
#         world.equipped_for_soil_analysis[agent] = True

#         world.available[agent] = True

#         # Agent's Storage
#         store = agent + "store"
#         world.stores[agent] = store
#         world.empty[store] = True

#         world.has_rock_analysis[agent] = False
#         world.has_soil_analysis[agent] = False
#         world.has_soil_sample[agent] = False
#         world.has_rock_sample[agent] = False
#         # Agent's Camera? TODO

#     # Lander
#     world.is_lander = {LANDER:True}
#     loc = random.choice(available_spaces)
#     available_spaces.remove(loc)
#     world.at[LANDER] = loc
#     world.channel_free = {LANDER:True}

#     # Lab
#     world.is_lab = {LAB:True}
#     loc = random.choice(available_spaces)
#     available_spaces.remove(loc)
#     world.at[LAB] = loc
#     world.lab_ready = {LAB:[]}

#     # Rocks and Soils
#     world.soils = set()
#     for i in range(NUM_SOILS):
#         soil = "S" + str(i+1)
#         world.soils.add(soil)
#         loc = random.choice(available_spaces)
#         available_spaces.remove(loc)
#         world.at[soil] = loc

#     world.rocks = set()
#     for i in range(NUM_ROCKS):
#         rock = "R" + str(i+1)
#         world.rocks.add(rock)
#         loc = random.choice(available_spaces)
#         available_spaces.remove(loc)
#         world.at[rock] = loc

#     # World's Location definition
#     world.loc = {}
#     world.loc_available = {}
#     world.cost = {}
#     idx = 1
#     for i in range(BOARD_X):
#         for j in range(BOARD_Y):
#             world.loc[idx] = (i, j)
#             world.loc_available[idx] = True
#             world.cost[idx] = 0
#             idx += 1

#     world.goals = {}
#     for agent_id in range(num_agent):
#         agent_name = "A" + str(agent_id+1)
#         world.goals[agent_name] = [('get_sample_data', agent_name)]

#     world.cost_func = cost_function
#     return world



"""
Goals are purily navigation from one point to another.
If A* is true, then the planner simply runs A* and makes no decision on decomposing the task
"""
def make_rand_nav_problem(BOARD_X, BOARD_Y, name=None):
    NUM_ROCKS = 0
    NUM_SOILS = 0
    PROBLEM = get_random_world(BOARD_X=BOARD_X, BOARD_Y=BOARD_Y, num_agent=2, a_star=True, name=name)
    for key, value in PROBLEM.goals.items():
        PROBLEM.goals[key] = [('navigate', key, random.choice(range(1, BOARD_X * BOARD_Y)))]
    UNCERTAINTIES = get_uncertainty_fun(PROBLEM, num_step=int(BOARD_X*BOARD_Y), a_prob=0.8)
    PROBLEM.uncertainties = UNCERTAINTIES
    return PROBLEM

"""
Below is the new uncertainty generating method for running experiment that 
simulates agents with different mental models. The method returns a function of the form
func(world, idx), where world is the current state (of the real-world) and the idx is 
the global time-step of the simulation.
"""
def get_uncertainty_fun(state, num_step, a_prob, sequence=None, randoms=None):

    if sequence == None and randoms == None:
        sequence = [] # Locations of interest
        randoms = [random.random() * state.RAND_RANGE for i in range(num_step)]

        # TODO: get gaussian dist around rand-range
        # randoms = [state.RAND_RANGE for i in range(num_step)]

        for idx in range(num_step):
            toggle = (random.random() < a_prob)
            if toggle:
                available_spaces = state.loc.keys()
                occupied = set()
                for (obj, loc) in state.at.items(): 
                    if loc != None:
                        occupied.add(loc)
                for loc in occupied: 
                    available_spaces.remove(loc)

                sequence.append(random.choice(available_spaces))
            else: sequence.append(None)

        state.RAND_PROB = a_prob

    state.sequence = sequence
    state.randoms = randoms
    def to_return(in_state, in_idx):
        # Get all the uncertainties at the first time step
        if in_idx == 0:
            # Make all uncertainties
            for idx in range(len(state.sequence)):
                if state.sequence[idx] != None:
                    in_state.cost[state.sequence[idx]] += state.randoms[idx]

    return to_return

"""
This method takes in an existing state and with some probability, changes 
something about the world. Possible changes are: 
- a_prob : Making a block in-accessible
- (Later) Changing the goal
- (Later) Change of capabilities
- (later) Change of communication Cost
"""
def generate_uncertainty(state, a_prob=1, verbose=False):
    
    toggle_state = (random.random() < a_prob)

    if toggle_state:
        # First find available spaces
        available_spaces =range(1,(state.prop['num_row']*state.prop['num_col']+1))
        occupied = set()
        for (obj, loc) in state.at.items(): 
            if loc != None:
                occupied.add(loc)
        for loc in occupied: 
            available_spaces.remove(loc)

        # Find a random location and flip the boolean
        rand_loc = random.choice(available_spaces)
        state.loc_available[rand_loc] = not state.loc_available[rand_loc]

        if verbose: print('changed location {} availability to {}'.format(rand_loc, state.loc_available[rand_loc]))

    # Changes the state, no need to return. 

"""
Returns a new state that is the result of after taking the action)
Does NOT modify existing State
"""
def act(state, action):
    task_name = action[0]
    global operators
    assert(task_name in operators)
    operator = operators[task_name]
    new_state = operator(copy.deepcopy(state), *action[1:])
    return new_state

"""
NOTE: Obsolete
Given an agent and its position in the real-world, check the set of observable locaitons for
differences in world state
agent_bs : agent's belief state
returns whether the agent should re-plan or not.
"""
def get_observation(agent, agent_bs, next_action, real_world):
    # The agent re-plans when the pre-conditions of the next-action is no longer met
    print('next_action: ', next_action)
    task_name = next_action[0]

    if act(real_world, next_action) == False:
        print('must replan!!!!')
        return True


"""
Below is a helper function that takes in the state and prints it in a board
"""
def print_board(state):
    print(print_board_str(state))

def print_board_str(state): # Makes the string output
    if state == None:
        return 'State is None'
        
    x = state.prop["num_row"]
    y = state.prop["num_col"]

    occupied = {}
    for (thing, loc) in state.at.items():
        if loc != None:
            (i, j) = state.loc[loc]
            if((i, j) in occupied):
                occupied[(i, j)].append(thing)
            else:
                occupied[(i, j)] = [thing]

    to_print = ""
    idx = 1
    for i in range(x):
        to_print += str(idx) + "\t"
        for j in range(y):
            if (i, j) in occupied:
                to_print += str(occupied[(i, j)]) + "\t"
            else:
                to_print += "[{0:.2f}]\t".format(state.cost[idx])

            idx += 1
        to_print += "\n"

    return to_print

"""
Main funciton for generating random world
Randomly allocate objects onto the world
"""
def get_random_world(BOARD_X=10, BOARD_Y=10, num_agent=1, a_star=True, name=None):

    if name == None:
        name = str(time.time())

    ##############################
    # Below, we generate the world with pre-defined randomness.

    # General and Miscellaneous World info
    world = State("InitialWorld")
    world.name = name
    world.BOARD_Y = BOARD_Y
    world.BOARD_X = BOARD_X
    world.NUM_SOILS = NUM_SOILS
    world.NUM_ROCKS = NUM_ROCKS
    world.prop = {"num_col":BOARD_Y, "num_row":BOARD_X}
    available_spaces = range(1,(BOARD_X*BOARD_Y+1))
    world.at = {}
    world.store_has = {}
    world.has_soil_sample = {}
    world.soil_sample = {}
    world.has_rock_sample = {}
    world.rock_sample = {}
    world.has_soil_analysis = {}
    world.soil_analysis = {}
    world.has_rock_analysis = {}
    world.rock_analysis = {}


    # Agents
    world.is_agent = {}
    world.visited = {}
    world.available = {}
    world.stores = {}
    world.store_has = {}
    world.empty = {}
    world.equipped_for_imaging = {}
    world.equipped_for_rock_analysis = {}
    world.equipped_for_soil_analysis = {}
    for agent_id in range(num_agent):

        agent = "A" + str(agent_id+1)

        world.is_agent[agent] = True
        loc = random.choice(available_spaces)
        world.at[agent] = loc
        available_spaces.remove(loc)
        world.visited[agent] = set()
        world.visited[agent].add(loc)

        # Agent's capabilities
        if agent == 'A1':
            world.equipped_for_imaging[agent] = True
            world.equipped_for_rock_analysis[agent] = True
            world.equipped_for_soil_analysis[agent] = False
        elif agent == 'A2':
            world.equipped_for_imaging[agent] = True
            world.equipped_for_rock_analysis[agent] = False
            world.equipped_for_soil_analysis[agent] = True
        else:
            world.equipped_for_imaging[agent] = True
            world.equipped_for_rock_analysis[agent] = True
            world.equipped_for_soil_analysis[agent] = True
        world.available[agent] = True

        # Agent's Storage
        store = agent + "store"
        world.stores[agent] = store
        world.empty[store] = True

        world.has_rock_analysis[agent] = False
        world.has_soil_analysis[agent] = False
        world.has_soil_sample[agent] = False
        world.has_rock_sample[agent] = False
        # Agent's Camera? TODO

    # Lander
    world.is_lander = {LANDER:True}
    loc = random.choice(available_spaces)
    available_spaces.remove(loc)
    world.at[LANDER] = loc
    world.channel_free = {LANDER:True}

    # Lab
    world.is_lab = {LAB:True}
    loc = random.choice(available_spaces)
    available_spaces.remove(loc)
    world.at[LAB] = loc
    world.lab_ready = {LAB:[]}

    # Rocks and Soils
    world.soils = set()
    for i in range(NUM_SOILS):
        soil = "S" + str(i+1)
        world.soils.add(soil)
        loc = random.choice(available_spaces)
        available_spaces.remove(loc)
        world.at[soil] = loc

    world.rocks = set()
    for i in range(NUM_ROCKS):
        rock = "R" + str(i+1)
        world.rocks.add(rock)
        loc = random.choice(available_spaces)
        available_spaces.remove(loc)
        world.at[rock] = loc

    # Objectives and Cameras ?? TODO for later

    # World's Location definition
    world.loc = {}
    world.loc_available = {}
    world.cost = {}
    idx = 1
    for i in range(BOARD_X):
        for j in range(BOARD_Y):
            world.loc[idx] = (i, j)
            world.loc_available[idx] = True
            world.cost[idx] = 0
            idx += 1


    world.goals = {}
    for agent_id in range(num_agent):
        agent_name = "A" + str(agent_id+1)
        world.goals[agent_name] = [('get_sample_data', agent_name)]

    # For other miscellaneous settings
    world.settings = {}
    world.settings['a-star'] = a_star

    # Default costs
    world.COST_OF_COMM = 1
    world.COST_REPLAN = 1
    world.COST_ACTION = 1
    world.MAX_COST = 20
    world.RAND_RANGE = 10
    world.RAND_PROB = 0

    world.cost_func = cost_function
    return world

# What is the cost of an action assuming that it can be done.
# This cost fucntion is also used by A* during navigation.
def cost_function(state, task):
    to_return = 1
    if task[0] == 'navigate_op':
        agent, source, sink = task[1:]
        to_return = state.cost[sink]
    if task[0] == 'visit' or task[0] == 'unvisit':
        to_return = 0
    return to_return

######## End for Generating world

# Make non-random world
def make_world(name, BOARD_X, BOARD_Y, NUM_S, NUM_R, \
    MAX_COST, RAND_RANGE, RAND_PROB, AT, GOALS, SEQ=None, RANDs=None):


    # General and Miscellaneous World info
    world = State("InitialWorld")
    world.name = name
    world.BOARD_Y = BOARD_Y
    world.BOARD_X = BOARD_X
    world.NUM_SOILS = NUM_S
    world.NUM_ROCKS = NUM_R

    world.prop = {"num_col":BOARD_Y, "num_row":BOARD_X}
    world.at = {}
    world.store_has = {}
    world.has_soil_sample = {}
    world.soil_sample = {}
    world.has_rock_sample = {}
    world.rock_sample = {}
    world.has_soil_analysis = {}
    world.soil_analysis = {}
    world.has_rock_analysis = {}
    world.rock_analysis = {}


    # Agents
    world.is_agent = {}
    world.visited = {}
    world.available = {}
    world.stores = {}
    world.store_has = {}
    world.empty = {}
    world.equipped_for_imaging = {}
    world.equipped_for_rock_analysis = {}
    world.equipped_for_soil_analysis = {}
    world.soils = set()
    world.rocks = set()

    # World's Location definition
    world.loc = {}
    world.loc_available = {}
    world.cost = {}
    idx = 1
    for i in range(BOARD_X):
        for j in range(BOARD_Y):
            world.loc[idx] = (i, j)
            world.loc_available[idx] = True
            world.cost[idx] = 0
            idx += 1
    
    # Set Locations
    for obj, loc in AT.items():
        world.at[obj] = loc

        if 'A' in obj:
            # Add Agent
            world.is_agent[obj] = True
            world.visited[obj] = set()
            world.visited[obj].add(loc)

            # Agent's capabilities
            if obj == 'A1':
                world.equipped_for_imaging[obj] = True
                world.equipped_for_rock_analysis[obj] = True
                world.equipped_for_soil_analysis[obj] = False
            elif obj == 'A2':
                world.equipped_for_imaging[obj] = True
                world.equipped_for_rock_analysis[obj] = False
                world.equipped_for_soil_analysis[obj] = True
            else:
                world.equipped_for_imaging[obj] = True
                world.equipped_for_rock_analysis[obj] = True
                world.equipped_for_soil_analysis[obj] = True

            world.available[obj] = True

            # Agent's Storage
            store = obj + "store"
            world.stores[obj] = store
            world.empty[store] = True

            world.has_rock_analysis[obj] = False
            world.has_soil_analysis[obj] = False
            world.has_soil_sample[obj] = False
            world.has_rock_sample[obj] = False
        elif LANDER == obj:
            # Add Lander
            world.is_lander = {obj:True}
            world.channel_free = {obj:True}

        elif LAB == obj:
            # Add Lab
            world.is_lab = {obj:True}
            world.lab_ready = {obj:[]}

        elif 'R' in obj:
            # Add Rover
            world.rocks.add(obj)
        elif 'S' in obj:
            # Add Soil
            world.soils.add(obj)


    world.goals = {}
    for agent, goal in GOALS.items():
        if goal != str([('get_sample_data', agent)]):
            assert False, "Cannot read problems with different goals: {}".format(goal)
        else:
            world.goals[agent] = [('get_sample_data', agent)]

    # For other miscellaneous settings
    world.settings = {}
    # world.settings['a-star'] = a_star

    # Default costs
    world.COST_OF_COMM = 1
    world.COST_REPLAN = 1
    world.COST_ACTION = 1
    world.MAX_COST = MAX_COST
    world.RAND_RANGE = RAND_RANGE
    world.RAND_PROB = RAND_PROB

    world.cost_func = cost_function

    # Set uncertainty
    world.uncertainties = get_uncertainty_fun(world, None, None, 
        sequence=SEQ, randoms=RANDs)
    return world

# Here, we set the parameters necesary for generating a world. 
CAPABILITIES = ["equipped_for_imaging", "equipped_for_rock_analysis", "equipped_for_soil_analysis"]
AGENTS = ['A1', 'A2', 'A3']
LANDER = "G"
LAB = "L"
NUM_ROCKS = 2
NUM_SOILS = 2
NUM_OBJECTIVES = 0


if __name__ == "__main__":
    world = get_random_world(5, 5)
    print('')
    print('*** World Generated ***')
    print_state(world)
    print('')
    print('Board: ')
    print_board(world)
    world.settings['a-star'] = True
    world.settings['verbose'] = False
    world.settings['sample'] = True
    pyhop(world, 'A1', 3, all_solutions=False, plantree=True, rand=False) # only one solution



