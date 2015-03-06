"""
Test the various implementations of handling Cost.
- Brute Force Method for finding minimum Cost
- Using Heuristics (Sorting of preconditions) for finding min cost
- Using Branch and Bound
"""
from __future__ import print_function
from pyhop import *
import random, time
from random_rovers_world import *


if __name__ == "__main__":
	world = get_random_world(5, 5)
	print('')
	print('*** World Generated ***')
	print_state(world)
	print('')
	print('Board: ')
	print_board(world)
	# We argue that implementing heuristics for sorting decomposition is equivalent to a*
	world.settings['a-star'] = False 
	world.settings['verbose'] = False
	world.settings['sample'] = True
	pyhop(world, 'A1', 0, all_solutions=False, plantree=False, rand=False)
