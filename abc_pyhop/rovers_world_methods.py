""" 
This is an attempt to encode the Mars Rover world for pyhop1.1.
Author: Kgu@mit.edu
"""
import random
import pyhop
from rovers_world_operators import *

def empty_store_m(state, store, rover, all_decomp=False):
	possible_decomp = []
	if state.empty[store]:
		possible_decomp.append([])
	else:
		possible_decomp.append([('drop', rover, store)])

	if all_decomp: return possible_decomp
	else: return random.choice(possible_decomp)

pyhop.declare_methods('empty_store',empty_store_m)


def navigate_m(state, agent, sink, all_decomp=False):
	possible_decomp = []
	if state.is_agent[agent]:
		source = state.at[agent]
		possible_decomp.append([('visit', source), ('navigate2', agent, source, sink), ('unvisit', source)])
	else:
		possible_decomp.append(False) # No possible Decomp

	if all_decomp: return possible_decomp
	else: return random.choice(possible_decomp)

pyhop.declare_methods('navigate',navigate_m)


def navigate2_m(state, agent, source, sink, all_decomp=False):
	possible_decomp = []
	source_y, source_x = state.loc[source]
	sink_y, sink_x = state.loc[sink]

	if state.at[agent] == sink: # already at destination
		possible_decomp.append([])
	elif can_traverse(state, source, sink):
		possible_decomp.append([('navigate_op', agent, source, sink)])
	else:
		if(source_x < sink_x): # move right
			mid = source + 1
			possible_decomp.append([('navigate_op', agent, source, mid), ('visit', mid), ('navigate2', agent, mid, sink), ('unvisit', mid)])
		if(source_x > sink_x): # move left
			mid = source - 1
			possible_decomp.append([('navigate_op', agent, source, mid), ('visit', mid), ('navigate2', agent, mid, sink), ('unvisit', mid)])
		if(source_y < sink_y): # move down
			mid = source + state.prop["num_col"]
			possible_decomp.append([('navigate_op', agent, source, mid), ('visit', mid), ('navigate2', agent, mid, sink), ('unvisit', mid)])
		if(source_y > sink_y): # move up
			mid = source - state.prop["num_col"]
			possible_decomp.append([('navigate_op', agent, source, mid), ('visit', mid), ('navigate2', agent, mid, sink), ('unvisit', mid)])
	
	if all_decomp: return possible_decomp
	else: return random.choice(possible_decomp)

pyhop.declare_methods('navigate2',navigate2_m)


def get_sample_data_m(state, agent, all_decomp=False):
	# Consider two cases here, rock OR soil
	possible_decomp = []
	if state.is_agent[agent] and state.equipped_for_rock_analysis[agent]:
		possible_decomp.append([('get_rock_data', agent)])
	if state.is_agent[agent] and state.equipped_for_soil_analysis[agent]:
		possible_decomp.append([('get_soil_data', agent)])

	if len(possible_decomp) == 0: possible_decomp.append(False)

	if all_decomp: return possible_decomp
	else: return random.choice(possible_decomp)

pyhop.declare_methods('get_sample_data',get_sample_data_m)


def get_soil_data_m(state, agent, all_decomp=False):

	# if agent in state.has_rock_sample:
	# 	state.has_rock_sample[agent]:
	# 	return ('analyze_soil_sample_m', agent, waypoint, store), 
	# 			('send_soil_data', agent, waypoint)])]]

	possible_decomp = []
	for (key, val) in state.at.items():
		if (key in state.is_soil) and state.is_soil[key]:
			possible_decomp.append([('get_a_soil_data', agent, key)])

	if len(possible_decomp) == 0: return [False] # If there is no soil anywhere

	if all_decomp: return possible_decomp
	else: return random.choice(possible_decomp)

pyhop.declare_methods('get_soil_data',get_soil_data_m)


def get_a_soil_data_m(state, agent, soil_obj, all_decomp=False):
	possible_decomp = []
	if state.is_agent[agent] and state.equipped_for_soil_analysis[agent] and (agent in state.stores):
		store = state.stores[agent]
		waypoint = state.at[soil_obj]
		possible_decomp.append([('retrieve_sample', agent, waypoint, soil_obj), 
				('analyze_soil_sample_m', agent, store), 
				('send_soil_data', agent)])
	else: return [False]

	if all_decomp: return possible_decomp
	else: return random.choice(possible_decomp)

pyhop.declare_methods('get_a_soil_data',get_a_soil_data_m)


def analyze_soil_sample_m(state, rover, s, all_decomp=False):
	if state.has_rock_analysis[rover]:
		return [[]]

	possible_decomp = []
	lab = random.choice(state.is_lab.keys())
	possible_decomp.append([('navigate', rover, state.at[lab]), 
			('set_up_soil_experiment', rover, lab),
			('analyze_soil_sample', rover, s, lab)])

	if all_decomp: return possible_decomp
	else: return random.choice(possible_decomp)

pyhop.declare_methods('analyze_soil_sample_m',analyze_soil_sample_m)


def send_soil_data_m(state, rover, all_decomp=False):
	possible_decomp = []
	if state.has_soil_analysis[rover]:
		lander = random.choice(state.is_lander.keys())
		lander_loc = state.at[lander]
		possible_decomp.append([('navigate', rover, lander_loc), ('communicate_data', rover, lander)])
	else: return [False]

	if all_decomp: return possible_decomp
	else: return random.choice(possible_decomp)

pyhop.declare_methods('send_soil_data',send_soil_data_m)


def get_rock_data_m(state, agent, all_decomp=False):

	
	possible_decomp = []
	for (key, val) in state.at.items():
		if (key in state.is_rock) and state.is_rock[key]:
			possible_decomp.append([('get_a_rock_data', agent, key)])

	if len(possible_decomp) == 0: return [False]

	if all_decomp: return possible_decomp
	else: return random.choice(possible_decomp)

pyhop.declare_methods('get_rock_data',get_rock_data_m)


def get_a_rock_data_m(state, agent, rock_obj, all_decomp=False):
	
	possible_decomp = []
	if state.is_agent[agent] and state.equipped_for_rock_analysis[agent] and (agent in state.stores):
		store = state.stores[agent]
		waypoint = state.at[rock_obj]
		possible_decomp.append([('retrieve_sample', agent, waypoint, rock_obj), 
				('analyze_rock_sample_m', agent, store), # analize whatever is in the store.
				('send_rock_data', agent)])
	else: return [False]

	if all_decomp: return possible_decomp
	else: return random.choice(possible_decomp)

pyhop.declare_methods('get_a_rock_data',get_a_rock_data_m)


def analyze_rock_sample_m(state, rover, s, all_decomp=False):
	if state.has_rock_analysis[rover]:
		return [[]]

	possible_decomp = []
	lab = random.choice(state.is_lab.keys())
	possible_decomp.append([('navigate', rover, state.at[lab]), 
			('set_up_rock_experiment', rover, lab),
			('analyze_rock_sample', rover, s, lab)])

	if all_decomp: return possible_decomp
	else: return random.choice(possible_decomp)

pyhop.declare_methods('analyze_rock_sample_m',analyze_rock_sample_m)


def send_rock_data_m(state, rover, all_decomp=False):
	possible_decomp = []
	if state.has_rock_analysis[rover]:
		lander = random.choice(state.is_lander.keys())
		lander_loc = state.at[lander]
		possible_decomp.append([('navigate', rover, lander_loc), ('communicate_data', rover, lander)])
	else: return [False]

	if all_decomp: return possible_decomp
	else: return random.choice(possible_decomp)

pyhop.declare_methods('send_rock_data',send_rock_data_m)


def retrieve_sample_m(state, agent, waypoint, obj, all_decomp=False):

	if 'rock' in obj and agent in state.has_rock_sample and state.has_rock_sample[agent]:
		return [[]] # Do nothing
	if 'soil' in obj and agent in state.has_soil_sample and state.has_soil_sample[agent]:
		return [[]] # Do nothing

	possible_decomp = []
	if state.is_agent[agent] and (agent in state.stores):
		store = state.stores[agent]
		possible_decomp.append([('navigate', agent, waypoint), 
				('empty_store', store, agent), 
				('sample', agent, store, waypoint, obj)])

	if all_decomp: return possible_decomp
	else: return random.choice(possible_decomp)

pyhop.declare_methods('retrieve_sample',retrieve_sample_m)


def send_image_data_m(state, rover, objective, mode, all_decomp=False):
	pass

pyhop.declare_methods('send_image_data',send_image_data_m)


def get_image_data_m(state, objective, mode, all_decomp=False):
	pass

pyhop.declare_methods('get_image_data',get_image_data_m)


def calibrate_m(state, rover, camera, all_decomp=False):
	pass

pyhop.declare_methods('calibrate',calibrate_m)

