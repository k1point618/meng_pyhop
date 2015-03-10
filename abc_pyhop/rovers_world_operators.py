""" 
This is an attempt to encode the Mars Rover world for pyhop1.1.
Author: Kgu@mit.edu
"""

import pyhop


""" 
Below are some helper functions for implementing the operators
"""
def can_traverse(state, source, sink):
	num_col = state.prop["num_col"]
	num_row = state.prop["num_row"]
	a = min(source, sink)
	b = max(source, sink)
	if (b-a == 1) and (a % num_col != 0):
		return True
	elif (b-a == num_col):
		return True

"""
The first argument is the current state, always, and the others are the planning operator's usual arguments.
"""

def navigate_op(state, a, source, sink):
	# print('is agent', state.is_agent[a])
	# print('at', state.at[a], 'source', source)
	# print('can_traverse', can_traverse(state, source, sink));
	if state.is_agent[a] and state.at[a] == source and can_traverse(state, source, sink) and state.loc_available[sink]:
		state.at[a] = sink
		return state
	else:
		return False


def sample(state, x, s, p, obj):
	if state.is_agent[x] and (x in state.stores) and (state.at[x] == p) \
		and (obj in state.at.keys()) and (state.at[obj] == p) \
		and (obj in state.rocks) and state.equipped_for_rock_analysis[x]:
		state.empty[s] = False
		state.store_has[s] = obj
		state.at[obj] = None
		state.has_rock_sample[x] = True
		state.rock_sample[x] = obj
		return state
	elif state.is_agent[x] and (x in state.stores) and (state.at[x] == p) \
		and  (obj in state.at.keys()) and (state.at[obj] == p) \
		and (obj in state.soils) and state.equipped_for_soil_analysis[x]:
		state.empty[s] = False
		state.store_has[s] = obj
		state.at[obj] = None
		state.has_soil_sample[x] = True		
		state.soil_sample[x] = obj
		return state
	else: return False


def set_up_soil_experiment(state, agent, lab):
	if state.is_agent[agent] and (lab in state.is_lab) and (state.at[agent] == state.at[lab]):
		state.lab_ready[lab].append("SOIL");
		return state
	else: return False

def set_up_rock_experiment(state, agent, lab):
	if state.is_agent[agent] and (lab in state.is_lab) and (state.at[agent] == state.at[lab]):
		state.lab_ready[lab].append("ROCK");
		return state
	else: return False 


def analyze_soil_sample(state, agent, s, lab):
	p = state.at[lab]
	if state.is_agent[agent] and (agent in state.stores) and (s == state.stores[agent]) and (lab in state.is_lab) and (p == state.at[lab]) and (state.at[agent] == p) and (not state.empty[s]) and (state.lab_ready[lab]):
		state.empty[s] == True
		sample_obj = state.store_has[s]
		state.lab_ready[lab].remove("SOIL")
		state.has_soil_analysis[agent] = True
		state.soil_analysis[agent] = sample_obj
		return state
	else: return False


def analyze_rock_sample(state, agent, s, lab):
	p = state.at[lab]
	if state.is_agent[agent] and (agent in state.stores) and (s == state.stores[agent]) and (lab in state.is_lab) and (p == state.at[lab]) and (state.at[agent] == p) and (not state.empty[s]) and (state.lab_ready[lab]):
		state.empty[s] == True
		sample_obj = state.store_has[s]
		state.lab_ready[lab].remove("ROCK")
		state.has_rock_analysis[agent] = True
		state.rock_analysis[agent] = sample_obj
		return state
	else: return False


def drop(state, agent, store):
	if state.is_agent[agent] \
		and (agent in state.stores) \
		and (store == state.stores[agent] \
		and (not state.empty[store])):

		cur_loc = state.at[agent]
		obj = state.store_has[store]
		if(obj == None): pyhop.print_state(state)
		assert(obj != None)
		state.at[obj] = cur_loc
		state.store_has.pop(store)
		state.empty[store] = True
		return state
	else: return False


def calibrate(state, r, i, t, w):
	pass

def take_image(r, p, o, i, m):
	pass

# This action takes some amount of time, during which the channel becomes occupied and the rover is no longer available.
def communicate_data(state, agent, lander):
	return state

def visit(state, agent, waypoint):
	state.visited[agent].add(waypoint)
	return state

def unvisit(state, agent, waypoint):
	state.visited[agent].remove(waypoint)
	return state


"""
Below, 'declare_operators(pickup, unstack, putdown, stack)' tells Pyhop
what the operators are. Note that the operator names are *not* quoted.
"""

pyhop.declare_operators(navigate_op, 
	sample, 
	set_up_rock_experiment, 
	set_up_soil_experiment, 
	analyze_rock_sample, 
	analyze_soil_sample,
	drop,
	calibrate,
	take_image,
	communicate_data,
	visit,
	unvisit)


""" 
TODO: Figure out what to do if there are different preconditions for the same operator. For example: Sampling rock or soil depending on where.
"""