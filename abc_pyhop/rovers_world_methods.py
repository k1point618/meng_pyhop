""" 
This is an attempt to encode the Mars Rover world for pyhop1.1.
Each method returns all decompositions sorted based on heuristic

Technically, there are 3 ways to ask for decompositions:
1) return 1 random decomp, (in a list)
2) return the decompositions with the min hueristic 
	(if there are multiple, deterministically pick 1)
3) return all decompositions sorted based on heuristic 
We leave this decision to the planner

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

def can_traverse(state, source, sink):
	num_col = state.prop["num_col"]
	num_row = state.prop["num_row"]
	a = min(source, sink)
	b = max(source, sink)
	if (b-a == 1) and (a % num_col != 0):
		return True
	elif (b-a == num_col):
		return True

def navigate_m(state, agent, sink, rand=False):
	if state.a_star:
		return [navigation.a_star(state, agent, sink)]
		
	possible_decomp = []
	if state.is_agent[agent]:
		source = state.at[agent]
		possible_decomp.append([('visit', agent, source), ('navigate2', agent, source, sink), ('unvisit', agent, source)])
	else:
		possible_decomp.append(False) # No possible Decomp

	return possible_decomp

pyhop.declare_methods('navigate',navigate_m)

# Multiple Decomp: Yes
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

		sorted_n = sorted(neighbors, key=lambda n: navigation.heuristic(state, n, sink))

		for mid in sorted_n:
			possible_decomp.append([('navigate_op', agent, source, mid), ('visit', agent, mid), ('navigate2', agent, mid, sink), ('unvisit',agent, mid)])

	if possible_decomp == []: return [False]

	return possible_decomp

pyhop.declare_methods('navigate2',navigate2_m)

# Multiple Decomp : Yes
def get_sample_data_m(state, agent, rand=False):
	# Consider two cases here, rock OR soil
	rock_score = int(state.has_rock_sample[agent]) + int(state.has_rock_analysis[agent])
	soil_score = int(state.has_soil_sample[agent]) + int(state.has_soil_analysis[agent])
	# print("\t\tAgent{} -- RockScore: {} \t Soil Score: {}".format(agent, rock_score, soil_score))
	# print("\t\tIs Agent: {}".format(state.is_agent))
	# print("\t\tEquipped (Rock): {}".format(state.equipped_for_rock_analysis))
	# print("\t\tEquipped (Soil): {}".format(state.equipped_for_rock_analysis))

	possible_decomp = []
	if state.is_agent[agent] and state.equipped_for_rock_analysis[agent]:
		# print("\t\tis agent AND equipped for rock analysis")
		possible_decomp.append([('get_rock_data', agent)])
		
	if state.is_agent[agent] and state.equipped_for_soil_analysis[agent]:
		# print("\t\tis agent AND equipped for soil analysis")
		if rock_score > soil_score:
			# Rock in front
			possible_decomp = possible_decomp + [[('get_soil_data', agent)]]
		elif rock_score <= soil_score:
			possible_decomp = [[('get_soil_data', agent)]] + possible_decomp

	if len(possible_decomp) == 0: return [False]
	if rock_score == soil_score and rand:
		random.shuffle(possible_decomp)
	# print("\t\tMethod:get_sample_data\t toreturn: Possible_decomp={}".format(possible_decomp))
	return possible_decomp

pyhop.declare_methods('get_sample_data',get_sample_data_m)


# Multiple Decomp : yes
def get_soil_data_m(state, agent, rand=False):
	keys = []
	to_return = []
	for (key, val) in state.at.items():
		if val != None:
			if (key in state.soils):
				# Using heapq
				keys.append(key)

	if state.has_soil_sample[agent]:
		to_return += [[('get_a_soil_data', agent, state.soil_sample[agent])]] # First

	if rand: 
		random.shuffle(keys)
	sorted_keys = sorted(keys, key=lambda n: navigation.heuristic(state, state.at[agent], state.at[n]))
	for k in sorted_keys:
		to_return.append([('get_a_soil_data', agent, k)])

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

# Multiple Decomp
def get_rock_data_m(state, agent, rand=False):
	keys = []
	to_return = []
	for (key, val) in state.at.items():
		if val != None:
			if (key in state.rocks):
				# Using heapq
				keys.append(key)

	if state.has_rock_sample[agent]:
		to_return = [[('get_a_rock_data', agent, state.rock_sample[agent])]]

	if rand: 
		random.shuffle(keys)
	sorted_keys = sorted(keys, key=lambda n: navigation.heuristic(state, state.at[agent], state.at[n]))
	for k in sorted_keys:
		to_return.append([('get_a_rock_data', agent, k)])

	if len(to_return) == 0: return [False] # If there is no soil anywhere
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

