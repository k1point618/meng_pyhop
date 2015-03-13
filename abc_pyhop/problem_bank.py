from __future__ import print_function
from pyhop import *
import random
import time
import random_rovers_world as rrw

def random(num_agent=2):
	return rrw.get_random_world(num_agent=num_agent, a_star=True)

def maze_1():
	rrw.NUM_ROCKS=0
	rrw.NUM_SOILS=0
	world = rrw.get_random_world(5, 5, num_agent=1)

	# Set Goal
	world.goals['A1'] = [('navigate', 'A1', 5)]

	# Set Lander Location
	world.at[rrw.LANDER] = 5
	
	# Set Rover Location
	world.at['A1'] = 17
	world.visited['A1'] = set()
	world.visited['A1'].add(17)

	# Set Traps
	world.loc_available[12] = False
	world.loc_available[13] = False
	world.loc_available[18] = False

	return world

def maze_2():
	rrw.NUM_ROCKS=0
	rrw.NUM_SOILS=0
	world = rrw.get_random_world(5, 5, num_agent=1)

	# Set Goal
	world.goals['A1'] = [('navigate', 'A1', 15)]

	# Set Lander Location
	world.at[rrw.LANDER] = 15
	
	# Set Rover Location
	world.at['A1'] = 12
	world.visited['A1'] = set()
	world.visited['A1'].add(12)

	# Set Traps
	world.loc_available[7] = False
	world.loc_available[8] = False
	world.loc_available[13] = False
	world.loc_available[18] = False
	world.loc_available[17] = False

	return world

# No Solution
def maze_3():
	rrw.NUM_ROCKS=0
	rrw.NUM_SOILS=0
	world = rrw.get_random_world(5, 5, num_agent=1)

	# Set Goal
	world.goals['A1'] = [('navigate', 'A1', 15)]

	# Set Lander Location
	world.at[rrw.LANDER] = 15
	
	# Set Rover Location
	world.at['A1'] = 12
	world.visited['A1'] = set()
	world.visited['A1'].add(12)

	# Set Traps
	world.loc_available[4] = False
	world.loc_available[7] = False
	world.loc_available[8] = False
	world.loc_available[13] = False
	world.loc_available[18] = False
	world.loc_available[17] = False
	world.loc_available[22] = False
	
	return world

# large
def maze_4():
	rrw.NUM_ROCKS=0
	rrw.NUM_SOILS=0
	world = rrw.get_random_world(num_agent=1)

	# Set Lander Location
	world.at[rrw.LANDER] = 78
	
	# Set Rover Location
	world.at['A1'] = 23
	world.visited['A1'] = set()
	world.visited['A1'].add(23)

	# Set Goal
	world.goals['A1'] = [('navigate', 'A1', 78)]

	# Set Traps
	world.loc_available[43] = False
	world.loc_available[34] = False
	world.loc_available[25] = False
	world.loc_available[37] = False
	world.loc_available[47] = False
	world.loc_available[57] = False
	world.loc_available[67] = False
	world.loc_available[77] = False
	world.loc_available[87] = False
	world.loc_available[97] = False

	return world

# large 2
def maze_5():
	rrw.NUM_ROCKS=0
	rrw.NUM_SOILS=0
	world = rrw.get_random_world(num_agent=1)

	# Set Lander Location
	world.at[rrw.LANDER] = 51
	
	# Set Rover Location
	world.at['A1'] = 67
	world.visited['A1'] = set()
	world.visited['A1'].add(67)

	# Set Goal
	world.goals['A1'] = [('navigate', 'A1', 51)]

	# Set Traps
	world.loc_available[49] = False
	world.loc_available[57] = False
	world.loc_available[58] = False
	world.loc_available[59] = False
	world.loc_available[66] = False
	world.loc_available[68] = False
	world.loc_available[75] = False
	world.loc_available[85] = False
	world.loc_available[86] = False
	world.loc_available[53] = False

	return world


# Replan for navigation
def navigate_replan():
	rrw.NUM_ROCKS=0
	rrw.NUM_SOILS=0
	world = rrw.get_random_world(5, 5, num_agent=1)

	# Set Goal
	world.goals['A1'] = [('navigate', 'A1', 15)]

	# Set Lander Location
	world.at[rrw.LANDER] = 15
	
	# Set Rover Location
	world.at['A1'] = 11
	world.visited['A1'] = set()
	world.visited['A1'].add(11)

	# Add uncertainties
	world.uncertainties = replan_1_rand
	return world

# Replan for navigation
def navigate_replan_team():
	rrw.NUM_ROCKS=0
	rrw.NUM_SOILS=0
	world = rrw.get_random_world(5, 5, num_agent=2)

	# Set Goal
	world.goals['A1'] = [('navigate', 'A1', 15)]
	world.goals['A2'] = [('navigate', 'A2', 9)]

	# Set Lander Location
	world.at[rrw.LANDER] = 15
	
	# Set Rover Location
	world.at['A1'] = 11
	world.visited['A1'] = set()
	world.visited['A1'].add(11)
	world.at['A2'] = 9
	world.visited['A2'] = set()
	world.visited['A1'].add(9)

	# Add uncertainties
	world.uncertainties = replan_1_rand
	return world


# Replan for navigation for comapring different agent mental models 
def navigate_replan_team_2():
	rrw.NUM_ROCKS=0
	rrw.NUM_SOILS=0
	world = rrw.get_random_world(6, 6, num_agent=2)

	# Set Goal
	world.goals['A1'] = [('navigate', 'A1', 31)]
	world.goals['A2'] = [('navigate', 'A2', 36)]

	# Set Soil Location
	world.at['S1'] = 31
	world.at['S2'] = 36

	# Set Rover Locations
	world.at['A1'] = 1
	world.visited['A1'] = set()
	world.visited['A1'].add(1)
	world.at['A2'] = 21
	world.visited['A2'] = set()
	world.visited['A1'].add(21)

	traps = [7, 8, 10, 11, 13, 14, 16, 17, 19, 20, 22, 23, 25, 26, 28, 29]
	for t in traps:
		world.loc_available[t] = False

	world.uncertainties = replan_2_rand
	return world

# Replan for get_a_soil_data: 
def decompose_replan():
	rrw.NUM_ROCKS=0
	rrw.NUM_SOILS=2
	world = rrw.get_random_world(5, 5, num_agent=1)

	# Set Rover Location
	world.at['A1'] = 1
	world.visited['A1'] = set()
	world.visited['A1'].add(1)

	# Set Soil Locations
	world.at['S1'] = 12
	world.at['S2'] = 17

	# Set Lander
	world.at[rrw.LANDER] = 23

	# Set Lab
	world.at[rrw.LAB] = 15

	# Set Goal
	world.goals['A1'] = [('get_a_soil_data', 'A1', 'S1')]

	# Add Uncertainties
	world.uncertainties = replan_decompose_1
	print_state(world)
	return world


# Uncertainties Library
def replan_1_rand(world, idx):
	print("*** *** Calling replan_1_rand *** ")
	if idx == 0:
		world.loc_available[14] = False

def replan_2_rand(world, idx):
	if idx == 0:
		world.loc_available[27] = False
		
def replan_decompose_1(world, idx):
	print("*** Calling re-lan_decompose_1 for uncertainties ***")
	if world.has_soil_analysis['A1']:
		print("*** *** hadding uncertainties, case 3 ***")
		world.loc_available[13] = True
		world.loc_available[14] = False
		world.loc_available[19] = False
		world.loc_available[24] = False
		return
	if world.has_soil_sample['A1']:
		print("*** *** hadding uncertainties, case 2 ***")
		world.loc_available[13] = False
		return
	if idx == 1:
		print("*** *** hadding uncertainties, case 1 ***")
		world.loc_available[6] = False
		world.loc_available[7] = False
		return






