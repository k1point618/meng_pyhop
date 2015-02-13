"""
This is an attempt to TEST PYHOP with a Mars-Rovers example
Author: Kgu@mit.edu
"""

from __future__ import print_function
from pyhop import *

import rovers_world_operators
print_operators()
import rovers_world_methods
print_methods()

####### Beginning of Tests #########
capabilities = ["equipped_for_imaging", "equipped_for_rock_analysis", "equipped_for_soil_analysis"]

X = 3
Y = 4
state1 = State("state1")
state1.is_agent = {"agent1":True}
state1.prop = {"num_col":Y, "num_row":X}

state1.at = {"agent1":8}
state1.visited = {"agent1":8}
state1.equipped_for_imaging = {"agent1":True}
state1.equipped_for_rock_analysis = {"agent1":True}
state1.equipped_for_soil_analysis = {"agent1":True}
state1.available = {"agent1": True}
state1.stores = {"agent1": "agent1store"}
state1.empty = {"agent1store":True}

state1.is_lander = {"GENERAL":True}
state1.at["GENERAL"] = 6
state1.channel_free = {"GENERAL":True}

state1.is_soil = {"soil1":True}
state1.at["soil1"] = 11
state1.is_rock = {"rock1":True}
state1.at["rock1"] = 2

state1.is_lab = {"xlab":True}
state1.at["xlab"] = 12
state1.lab_ready = {"xlab":[]}

state1.has_soil_analysis = {}
state1.soil_analysis = {}
state1.has_rock_analysis = {}
state1.rock_analysis = {}

state1.loc = {}
idx = 1
for i in range(X):
	for j in range(Y):
		state1.loc[idx] = (i, j)
		idx += 1

print_state(state1)
print('')

"""
First, we test pyhop and domain on simple tasks: navigate from a to b.
"""
pyhop(state1, [('navigate_op', 'agent1', 8, 4)], verbose=2)
pyhop(state1, [('navigate_op', 'agent1', 8, 7)], verbose=2)

# # The following tests should fail
pyhop(state1, [('navigate_op', 'agent1', 8, 9)], verbose=2)
pyhop(state1, [('navigate_op', 'agent1', 8, 1)], verbose=2)
pyhop(state1, [('navigate_op', 'agent1', 8, 11)], verbose=2)
pyhop(state1, [('navigate_op', 'agent1', 7, 6)], verbose=2)

# The following should give one of two plans
pyhop(state1, [('navigate', 'agent1', 3)], verbose=3)

""" 
Now we test for the navigation-method. Should be able to navigate to any locaiton
"""
for i in range(1, X*Y+1):
	if not pyhop(state1, [('navigate', 'agent1', i)], verbose=1):
		print ("failed to go to ", i)
		break;


""" 
We test the high-level method:
"""
pyhop(state1, [('get_sample_data', 'agent1')], verbose=1)



"""
Below we test pyhop to find all possible plans
"""
print('Below we test pyhop to find all possible plans')
print('')

for i in range(1, X*Y+1):
	task = [('navigate', 'agent1', i)]
	results = pyhop(state1, task, verbose=0, all_solutions=True)
	if not results:
		print ("failed to go to ", i)
		break;
	print('for task {}, found {} plans'.format(task, len(results)))


""" 
We test the high-level method and ALL plans
"""
pyhop(state1, 'agent1', verbose=1, all_solutions=True)

