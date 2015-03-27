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

import rovers_world_operators
import rovers_world_methods


"""
Below is the new uncertainty generating method for running experiment that 
simulates agents with different mental models. The method returns a function of the form
func(world, idx), where world is the current state (of the real-world) and the idx is 
the global time-step of the simulation.
"""
def get_uncertainty_fun(state, num_step, a_prob):

    sequence = []
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

    def to_return(in_state, in_idx):
        if in_idx >= len(sequence):
            return
        rand_loc = sequence[in_idx]
        if rand_loc != None:
            # in_state.loc_available[rand_loc] = not in_state.loc_available[rand_loc] # This allows flipping
            in_state.loc_available[rand_loc] = False # This means if a location turns into a trap, it will stay as a trap

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
    return operator(copy.deepcopy(state), *action[1:])

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
                if (state.loc_available[idx]):
                    to_print += "[\t]\t"
                else:
                    to_print += "[++++++]\t"

            idx += 1
        to_print += "\n"
    return to_print

"""
Main funciton for generating random world
"""
def get_random_world(BOARD_X=10, BOARD_Y=10, num_agent=1, 
                    a_star=True):

    ##############################
    # Below, we generate the world with pre-defined randomness.

    # General and Miscellaneous World info
    world = State("InitialWorld")
    world.name = "RandomWorld"
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
    idx = 1
    for i in range(BOARD_X):
        for j in range(BOARD_Y):
            world.loc[idx] = (i, j)
            world.loc_available[idx] = True
            idx += 1

        # Allocate goals to each agent
    # TODO: For now, we manually allocate the goals
    world.goals = {}
    for agent_id in range(num_agent):
        agent_name = "A" + str(agent_id+1)
        world.goals[agent_name] = [('get_sample_data', agent_name)]

    # For other miscellaneous settings
    world.settings = {}
    world.settings['a-star'] = a_star
    world.ID = int(time.time())

    # Default costs
    world.COST_OF_COMM = 1
    world.COST_REPLAN = 1
    world.COST_ACTION = 1

    return world

######## End for Generating world


# Here, we set the parameters necesary for generating a world. 
CAPABILITIES = ["equipped_for_imaging", "equipped_for_rock_analysis", "equipped_for_soil_analysis"]
AGENTS = ['A1', 'A2']
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



