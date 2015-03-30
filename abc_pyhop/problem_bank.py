from __future__ import print_function
from pyhop import *
import random
import time
import random_rovers_world as rrw

def random(num_agent=2):
	return rrw.get_random_world(num_agent=num_agent, a_star=True)

def maze_0():
	rrw.NUM_ROCKS=0
	rrw.NUM_SOILS=0
	world = rrw.get_random_world(3, 3, num_agent=1, name='maze_0')

	# Set Goal
	world.goals['A1'] = [('navigate', 'A1', 9)]

	# Set Lander Location
	world.at[rrw.LANDER] = 9
	
	# Set Rover Location
	world.at['A1'] = 1
	world.visited['A1'] = set()
	world.visited['A1'].add(1)
	
	return world

def maze_1():
	rrw.NUM_ROCKS=0
	rrw.NUM_SOILS=0
	world = rrw.get_random_world(5, 5, num_agent=1, name='maze_1')

	# Set Goal
	world.goals['A1'] = [('navigate', 'A1', 5)]

	# Set Lander Location
	world.at[rrw.LANDER] = 5
	
	# Set Rover Location
	world.at['A1'] = 17
	world.visited['A1'] = set()
	world.visited['A1'].add(17)

	# Set Traps
	world.cost[12] = sys.maxint
	world.cost[13] = sys.maxint
	world.cost[18] = sys.maxint

	return world

def maze_2():
	rrw.NUM_ROCKS=0
	rrw.NUM_SOILS=0
	world = rrw.get_random_world(5, 5, num_agent=1, name='maze_2')

	# Set Goal
	world.goals['A1'] = [('navigate', 'A1', 15)]

	# Set Lander Location
	world.at[rrw.LANDER] = 15
	
	# Set Rover Location
	world.at['A1'] = 12
	world.visited['A1'] = set()
	world.visited['A1'].add(12)

	# Set Traps
	world.cost[7] = sys.maxint
	world.cost[8] = sys.maxint
	world.cost[13] = sys.maxint
	world.cost[18] = sys.maxint
	world.cost[17] = sys.maxint

	return world

# No Solution
def maze_3():
	rrw.NUM_ROCKS=0
	rrw.NUM_SOILS=0
	world = rrw.get_random_world(5, 5, num_agent=1, name='maze_3')

	# Set Goal
	world.goals['A1'] = [('navigate', 'A1', 15)]

	# Set Lander Location
	world.at[rrw.LANDER] = 15
	
	# Set Rover Location
	world.at['A1'] = 12
	world.visited['A1'] = set()
	world.visited['A1'].add(12)

	# Set Traps
	world.cost[4] = sys.maxint
	world.cost[7] = sys.maxint
	world.cost[8] = sys.maxint
	world.cost[13] = sys.maxint
	world.cost[18] = sys.maxint
	world.cost[17] = sys.maxint
	world.cost[22] = sys.maxint
	
	return world

# large
def maze_4():
	rrw.NUM_ROCKS=0
	rrw.NUM_SOILS=0
	world = rrw.get_random_world(num_agent=1, name='maze_4')

	# Set Lander Location
	world.at[rrw.LANDER] = 78
	
	# Set Rover Location
	world.at['A1'] = 23
	world.visited['A1'] = set()
	world.visited['A1'].add(23)

	# Set Goal
	world.goals['A1'] = [('navigate', 'A1', 78)]

	# Set Traps
	world.cost[43] = sys.maxint
	world.cost[34] = sys.maxint
	world.cost[25] = sys.maxint
	world.cost[37] = sys.maxint
	world.cost[47] = sys.maxint
	world.cost[57] = sys.maxint
	world.cost[67] = sys.maxint
	world.cost[77] = sys.maxint
	world.cost[87] = sys.maxint
	world.cost[97] = sys.maxint

	return world

# large 2
def maze_5():
	rrw.NUM_ROCKS=0
	rrw.NUM_SOILS=0
	world = rrw.get_random_world(num_agent=1, name='maze_5')

	# Set Lander Location
	world.at[rrw.LANDER] = 51
	
	# Set Rover Location
	world.at['A1'] = 67
	world.visited['A1'] = set()
	world.visited['A1'].add(67)

	# Set Goal
	world.goals['A1'] = [('navigate', 'A1', 51)]

	# Set Traps
	world.cost[49] = sys.maxint
	world.cost[57] = sys.maxint
	world.cost[58] = sys.maxint
	world.cost[59] = sys.maxint
	world.cost[66] = sys.maxint
	world.cost[68] = sys.maxint
	world.cost[75] = sys.maxint
	world.cost[85] = sys.maxint
	world.cost[86] = sys.maxint
	world.cost[53] = sys.maxint

	return world


# Replan for navigation
def navigate_replan():
	rrw.NUM_ROCKS=0
	rrw.NUM_SOILS=0
	world = rrw.get_random_world(5, 5, num_agent=1, name='navigate_replan')

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
	world = rrw.get_random_world(5, 5, num_agent=2, name='navigate_replan_team')

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
	rrw.LANDER='X'
	rrw.LAB = 'X'
	world = rrw.get_random_world(6, 6, num_agent=2, name='navigate_replan_team_2')

	# Set Goal
	world.goals['A1'] = [('navigate', 'A1', 31)]
	world.goals['A2'] = [('navigate', 'A2', 36)]

	# Set Soil Location
	world.at['S1'] = 31
	world.at['S2'] = 36

	# Set Lander
	world.at[rrw.LANDER] = 13
	world.at[rrw.LAB] = 19

	# Set Rover Locations
	world.at['A1'] = 1
	world.visited['A1'] = set()
	world.visited['A1'].add(1)
	world.at['A2'] = 21
	world.visited['A2'] = set()
	world.visited['A1'].add(21)

	traps = [7, 8, 10, 11, 13, 14, 16, 17, 19, 20, 22, 23, 25, 26, 28, 29]
	for t in traps:
		world.cost[t] = sys.maxint

	world.uncertainties = replan_2_rand
	return world




def navigate_replan_team_3():
	rrw.NUM_ROCKS=0
	rrw.NUM_SOILS=0
	rrw.LANDER='X'
	rrw.LAB = 'X'
	world = rrw.get_random_world(6, 6, num_agent=2, name='navigate_replan_team_3')

	# Set Goal
	world.goals['A1'] = [('navigate', 'A1', 31)]
	world.goals['A2'] = [('navigate', 'A2', 36)]

	# Set Soil Location
	world.at['S1'] = 31
	world.at['S2'] = 36

	# Set Lander
	world.at[rrw.LANDER] = 13
	world.at[rrw.LAB] = 19

	# Set Rover Locations
	world.at['A1'] = 1
	world.visited['A1'] = set()
	world.visited['A1'].add(1)
	world.at['A2'] = 21
	world.visited['A2'] = set()
	world.visited['A1'].add(21)

	traps = [7, 8, 10, 11, 13, 14, 16, 17, 19, 20, 22, 23, 25, 26, 27, 28, 29]
	for t in traps:
		world.cost[t] = sys.maxint

	world.uncertainties = replan_3_rand
	world.ID = "navigate_replan_team_3"
	return world

def navigate_replan_team_4():
	rrw.NUM_ROCKS=0
	rrw.NUM_SOILS=0
	rrw.LANDER='X'
	rrw.LAB = 'X'
	world = rrw.get_random_world(7, 7, num_agent=2, name='navigate_replan_team_4')

	# Set Goal
	world.goals['A1'] = [('navigate', 'A1', 43)]
	world.goals['A2'] = [('navigate', 'A2', 49)]

	# Set Soil Location
	world.at['S1'] = 43
	world.at['S2'] = 49

	# Set Lander
	world.at[rrw.LANDER] = 15
	world.at[rrw.LAB] = 22

	# Set Rover Locations
	world.at['A1'] = 1
	world.visited['A1'] = set()
	world.visited['A1'].add(1)
	world.at['A2'] = 31
	world.visited['A2'] = set()
	world.visited['A1'].add(31)

	traps = [15, 16, 19, 20, 22, 23, 26, 27, 29, 30, 33, 34, 36, 37, 40, 41]
	for t in traps:
		world.cost[t] = sys.maxint

	world.uncertainties = replan_4_rand
	world.ID = "navigate_replan_team_4"
	return world

def navigate_replan_team_5():
	rrw.NUM_ROCKS=0
	rrw.NUM_SOILS=0
	rrw.LANDER='X'
	rrw.LAB = 'X'
	world = rrw.get_random_world(7, 7, num_agent=2, name='navigate_replan_team_4')

	# Set Goal
	world.goals['A1'] = [('navigate', 'A1', 43)]
	world.goals['A2'] = [('navigate', 'A2', 49)]

	# Set Soil Location
	world.at['S1'] = 43
	world.at['S2'] = 49

	# Set Lander
	world.at[rrw.LANDER] = 15
	world.at[rrw.LAB] = 22

	# Set Rover Locations
	world.at['A1'] = 1
	world.visited['A1'] = set()
	world.visited['A1'].add(1)
	world.at['A2'] = 31
	world.visited['A2'] = set()
	world.visited['A1'].add(31)

	traps = [15, 16, 19, 18, 22, 23, 26, 25, 29, 30, 33, 32, 36, 37, 40, 39]
	for t in traps:
		world.cost[t] = sys.maxint

	world.uncertainties = replan_5_rand
	world.ID = "navigate_replan_team_5"
	return world


def navigate_replan_team_6():
	rrw.NUM_ROCKS=0
	rrw.NUM_SOILS=0
	rrw.LANDER='X'
	rrw.LAB = 'X'
	world = rrw.get_random_world(5, 9, num_agent=2, name='navigate_replan_team_6')

	# Set Goal
	world.goals['A1'] = [('navigate', 'A1', 27)]
	world.goals['A2'] = [('navigate', 'A2', 41)]

	# Set Lander
	world.at[rrw.LANDER] = 23
	world.at[rrw.LAB] = 23

	# Set Rover Locations
	world.at['A1'] = 19
	world.visited['A1'] = set()
	world.visited['A1'].add(19)
	world.at['A2'] = 5
	world.visited['A2'] = set()
	world.visited['A2'].add(5)

	traps = [23]
	for t in traps:
		world.cost[t] = sys.maxint

	world.uncertainties = replan_6_rand
	world.ID = "navigate_replan_team_6"
	return world


# Replan for get_a_soil_data: 
def decompose_replan():
	rrw.NUM_ROCKS=0
	rrw.NUM_SOILS=1
	world = rrw.get_random_world(5, 6, num_agent=1)

	# Set Rover Location
	world.at['A1'] = 1
	world.visited['A1'] = set()
	world.visited['A1'].add(1)

	# Set Soil Locations
	world.at['S1'] = 14

	# Set Lander
	world.at[rrw.LANDER] = 28

	# Set Lab
	world.at[rrw.LAB] = 18

	# Set Goal
	world.goals['A1'] = [('get_a_soil_data', 'A1', 'S1')]

	# Add Uncertainties
	world.uncertainties = replan_decompose_1
	print_state(world)
	return world

def dummy_world():
	rrw.NUM_ROCKS=4
	rrw.NUM_SOILS=4
	world = rrw.get_random_world(10, 10, num_agent=1)

	# Set Rover Locaitons
	world.at['A1'] = 85
	world.visited['A1'] = set()
	world.visited['A1'].add(85)
	world.at['A2'] = 85
	world.visited['A2'] = set()
	world.visited['A2'].add(85)

	# Set Soil Locations
	world.at['S1'] = 12
	world.at['S2'] = 34
	world.at['S3'] = 19
	world.at['S4'] = 37

	world.at['R1'] = 14
	world.at['R2'] = 32
	world.at['R3'] = 17
	world.at['R4'] = 39
	
	# Set Lander
	world.at[rrw.LANDER] = 62

	# Set Lab
	world.at[rrw.LAB] = 69

	# Set Goal
	world.goals['A1'] = [('get_soil_data', 'A1')]
	world.goals['A2'] = [('get_rock_data', 'A1')]

	# Set Traps
	world.cost[41] = sys.maxint
	world.cost[42] = sys.maxint
	world.cost[43] = sys.maxint
	world.cost[44] = sys.maxint
	world.cost[47] = sys.maxint
	world.cost[48] = sys.maxint
	world.cost[49] = sys.maxint
	world.cost[50] = sys.maxint

	return world

# Uncertainties Library
def replan_1_rand(world, idx):
	print("*** *** Calling replan_1_rand *** ")
	if idx == 0:
		world.cost[14] = sys.maxint

def replan_2_rand(world, idx):
	if idx == 0:
		world.cost[27] = sys.maxint

def replan_3_rand(world, idx):
	if idx == 0:
		world.cost[27] = 1

def replan_4_rand(world, idx):
	if idx == 0:
		world.cost[2] = sys.maxint
		world.cost[4] = sys.maxint
		world.cost[6] = sys.maxint
		world.cost[38] = sys.maxint
		world.cost[39] = sys.maxint

def replan_5_rand(world, idx):
	if idx == 0:
		world.cost[2] = sys.maxint
		world.cost[4] = sys.maxint
		world.cost[6] = sys.maxint
		world.cost[38] = sys.maxint
		world.cost[21] = sys.maxint
		world.cost[35] = sys.maxint

def replan_6_rand(world, idx):
	if idx == 1:
		world.cost[14] = world.MAX_COST/2
		world.cost[13] = world.MAX_COST/2
		world.cost[15] = world.MAX_COST/2

def replan_decompose_1(world, idx):
	print("*** Calling re-lan_decompose_1 for uncertainties ***")
	if world.has_soil_analysis['A1']:
		print("*** *** hadding uncertainties, case 3 ***")
		world.cost[17] = sys.maxint
		world.cost[23] = sys.maxint
		world.cost[29] = sys.maxint
		return
	if world.has_soil_sample['A1']:
		print("*** *** hadding uncertainties, case 2 ***")
		world.cost[16] = sys.maxint
		return
	if idx == 1:
		print("*** *** hadding uncertainties, case 1 ***")
		world.cost[13] = sys.maxint
		world.cost[8] = sys.maxint
		return






