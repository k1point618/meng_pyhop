""" 
This is an attempt to encode the Mars Rover world for pyhop1.1.
Each method returns the set of ALL possible decompositions. This means...
- Finding all variable bindings that satisfies the preconditions
- Different types of decomposition depending on the Case

Author: Kgu@mit.edu
"""
import random, pyhop, navigation, heapq
from rovers_world_operators import *

def empty_store_m(state, store, rover, rand=False):
	possible_decomp = []
	if state.empty[store]:
		possible_decomp.append([])
	else:
		possible_decomp.append([('drop', rover, store)])

	return possible_decomp

pyhop.declare_methods('empty_store',empty_store_m)


def navigate_m(state, agent, sink, rand=False):
	if 'a-star' in state.settings and state.settings['a-star']:
		return [navigation.a_star(state, agent, sink)]
		
	possible_decomp = []
	if state.is_agent[agent]:
		source = state.at[agent]
		possible_decomp.append([('visit', agent, source), ('navigate2', agent, source, sink), ('unvisit', agent, source)])
	else:
		possible_decomp.append(False) # No possible Decomp

	return possible_decomp

pyhop.declare_methods('navigate',navigate_m)

# 
def navigate2_m(state, agent, source, sink, rand=False):
	possible_decomp = []
	source_y, source_x = state.loc[source]
	sink_y, sink_x = state.loc[sink]

	if state.at[agent] == sink:
		# already at destination
		possible_decomp.append([])
	elif can_traverse(state, source, sink):
		# Next to the destination
		possible_decomp.append([('navigate_op', agent, source, sink)])
	else:
		# Look for possible neighbors
		neighbors = []
		for n in navigation.get_neighbors(state, source):
			if n not in state.visited[agent]: 
				neighbors.append(n)

		sorted_n = sorted(neighbors, key=lambda n: navigation.heuristic(state,n, sink))

		for mid in sorted_n:
			possible_decomp.append([('navigate_op', agent, source, mid), ('visit', agent, mid), ('navigate2', agent, mid, sink), ('unvisit',agent, mid)])

		# Below is the old implemention that doesn't know how to plan around obstacles
		# if(source_x < sink_x): # move right
		# 	mid = source + 1
		# 	possible_decomp.append([('navigate_op', agent, source, mid), ('visit', mid), ('navigate2', agent, mid, sink), ('unvisit', mid)])
		# if(source_x > sink_x): # move left
		# 	mid = source - 1
		# 	possible_decomp.append([('navigate_op', agent, source, mid), ('visit', mid), ('navigate2', agent, mid, sink), ('unvisit', mid)])
		# if(source_y < sink_y): # move down
		# 	mid = source + state.prop["num_col"]
		# 	possible_decomp.append([('navigate_op', agent, source, mid), ('visit', mid), ('navigate2', agent, mid, sink), ('unvisit', mid)])
		# if(source_y > sink_y): # move up
		# 	mid = source - state.prop["num_col"]
		# 	possible_decomp.append([('navigate_op', agent, source, mid), ('visit', mid), ('navigate2', agent, mid, sink), ('unvisit', mid)])
	if possible_decomp == []: return [False]

	return possible_decomp

pyhop.declare_methods('navigate2',navigate2_m)


def get_sample_data_m(state, agent, rand=False):
	# Consider two cases here, rock OR soil
	possible_decomp = []
	if state.is_agent[agent] and state.equipped_for_rock_analysis[agent]:
		possible_decomp.append([('get_rock_data', agent)])
	if state.is_agent[agent] and state.equipped_for_soil_analysis[agent]:
		possible_decomp.append([('get_soil_data', agent)])

	if len(possible_decomp) == 0: return [False]

	return possible_decomp

pyhop.declare_methods('get_sample_data',get_sample_data_m)


def get_soil_data_m(state, agent, rand=False):
	possible_decomp = []
	to_return = []
	for (key, val) in state.at.items():
		if (key in state.soils):
			# Using heapq
			decomp = [('get_a_soil_data', agent, key)]
			heuristic = navigation.heuristic(state, state.at[agent], state.at[key])
			heapq.heappush(possible_decomp, (heuristic, decomp))
			
	if state.has_soil_sample[agent]:
		to_return += [[('get_a_soil_data', agent, state.soil_sample[agent])]]

	num_result = len(possible_decomp)
	to_return += [heapq.heappop(possible_decomp)[1] for i in range(num_result)]
	if len(to_return) == 0: return [False] # If there is no soil anywhere
	return to_return

pyhop.declare_methods('get_soil_data',get_soil_data_m)


def get_a_soil_data_m(state, agent, soil_obj, rand=False):
	possible_decomp = []

	if state.is_agent[agent] and state.equipped_for_soil_analysis[agent] and (agent in state.stores):
		store = state.stores[agent]
		possible_decomp.append([('retrieve_sample', agent, soil_obj), 
				('analyze_soil_sample_m', agent, store), 
				('send_soil_data', agent)])
	else: return [False]

	return possible_decomp

pyhop.declare_methods('get_a_soil_data',get_a_soil_data_m)


def analyze_soil_sample_m(state, rover, store, rand=False):
	if state.has_soil_analysis[rover]:
		return [[]]

	possible_decomp = []
	lab = random.choice(state.is_lab.keys())
	possible_decomp.append([('navigate', rover, state.at[lab]), 
			('set_up_soil_experiment', rover, lab),
			('analyze_soil_sample', rover, store, lab)])

	return possible_decomp

pyhop.declare_methods('analyze_soil_sample_m',analyze_soil_sample_m)


def send_soil_data_m(state, rover, rand=False):
	possible_decomp = []
	if state.has_soil_analysis[rover]:
		lander = random.choice(state.is_lander.keys())
		lander_loc = state.at[lander]
		possible_decomp.append([('navigate', rover, lander_loc), ('communicate_data', rover, lander)])
	else: return [False]

	return possible_decomp
pyhop.declare_methods('send_soil_data',send_soil_data_m)


def get_rock_data_m(state, agent, rand=False):
	possible_decomp = []
	to_return =[]

	for (key, val) in state.at.items():
		if (key in state.rocks):
			# Using heapq
			decomp = [('get_a_rock_data', agent, key)]
			heuristic = navigation.heuristic(state, state.at[agent], state.at[key])
			heapq.heappush(possible_decomp, (heuristic, decomp))

	if state.has_rock_sample[agent]:
		to_return = [[('get_a_rock_data', agent, state.rock_sample[agent])]]

	num_result = len(possible_decomp)
	to_return += [heapq.heappop(possible_decomp)[1] for i in range(num_result)]
	if len(to_return) == 0: return [False]
	return to_return

pyhop.declare_methods('get_rock_data',get_rock_data_m)


def get_a_rock_data_m(state, agent, rock_obj, rand=False):
	
	possible_decomp = []
	if state.is_agent[agent] and state.equipped_for_rock_analysis[agent] and (agent in state.stores):
		store = state.stores[agent]
		possible_decomp.append([('retrieve_sample', agent, rock_obj), 
				('analyze_rock_sample_m', agent, store), # analize whatever is in the store.
				('send_rock_data', agent)])
	else: return [False]

	return possible_decomp
pyhop.declare_methods('get_a_rock_data',get_a_rock_data_m)


def analyze_rock_sample_m(state, rover, s, rand=False):
	if state.has_rock_analysis[rover]:
		return [[]]

	possible_decomp = []
	lab = random.choice(state.is_lab.keys())
	possible_decomp.append([('navigate', rover, state.at[lab]), 
			('set_up_rock_experiment', rover, lab),
			('analyze_rock_sample', rover, s, lab)])

	return possible_decomp
pyhop.declare_methods('analyze_rock_sample_m',analyze_rock_sample_m)


def send_rock_data_m(state, rover, rand=False):
	possible_decomp = []
	if state.has_rock_analysis[rover]:
		lander = random.choice(state.is_lander.keys())
		lander_loc = state.at[lander]
		possible_decomp.append([('navigate', rover, lander_loc), ('communicate_data', rover, lander)])
	else: return [False]

	return possible_decomp

pyhop.declare_methods('send_rock_data',send_rock_data_m)


def retrieve_sample_m(state, agent, obj, rand=False):

	if (obj in state.rocks) and (state.has_rock_sample[agent]) and state.has_rock_sample[agent]:
		return [[]] # Do nothing
	if (obj in state.soils) and (state.has_soil_sample[agent]) and state.has_soil_sample[agent]:
		return [[]] # Do nothing

	possible_decomp = []
	waypoint = state.at[obj]
	if state.is_agent[agent] and (agent in state.stores):
		store = state.stores[agent]
		possible_decomp.append([('navigate', agent, waypoint), 
				('empty_store', store, agent), 
				('sample', agent, store, waypoint, obj)])

	return possible_decomp

pyhop.declare_methods('retrieve_sample',retrieve_sample_m)


def send_image_data_m(state, rover, objective, mode):
	pass

pyhop.declare_methods('send_image_data',send_image_data_m)


def get_image_data_m(state, objective, mode):
	pass

pyhop.declare_methods('get_image_data',get_image_data_m)


def calibrate_m(state, rover, camera):
	pass

pyhop.declare_methods('calibrate',calibrate_m)

