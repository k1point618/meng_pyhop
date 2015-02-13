""" 
This file is used to benchmar the performance of the different versions of pyhop.
"""

from __future__ import print_function
from pyhop import *
import random
import time
import collections
import matplotlib.pyplot as plt

import rovers_world_operators
import rovers_world_methods
from random_rovers_world import *

def single_agent_benchmark():

	num_repeat = 7
	board_X = range(4, 6)
	board_Y = range(3, 5)
	world_gen_times = {}
	board_size_times = {}
	num_solutions_times = {}
	num_recurse_calls = {}

	for x in board_X:
		for y in board_Y:
			board_size = x*y
			print ('board size: ', x, y)
			world_gen_sum = 0
			board_size_sum = 0


			for i in range(num_repeat):
				start = time.time()
				world = get_random_world(x, y)
				end = time.time()
				world_gen_sum += (end-start)

				print_board(world)

				start = time.time()
				solutions = pyhop(world, 'agent1', verbose=0, all_solutions=True)
				end = time.time()
				board_size_sum += (end-start)
				num_recurse_calls[len(solutions)] = get_num_recurse_calls()
				num_solutions_times[len(solutions)] = end-start
				print('find {} solutions for board of size {}'.format(len(solutions), board_size))
				print('num_recurse_calls', num_recurse_calls)
				print('num_solutions_times', num_solutions_times)			
	
	# plot time with respect to the number of solutions found.
	od_num_solutions_times = collections.OrderedDict(sorted(num_solutions_times.items()))
	print('Ordered od_num_solutions_time', od_num_solutions_times)
	od_num_recurse_calls = collections.OrderedDict(sorted(num_recurse_calls.items()))
	print('Ordered od_num_recurse_calls', od_num_recurse_calls)
	
	plt.plot(od_num_solutions_times.keys(), od_num_solutions_times.values())
	plt.plot(od_num_recurse_calls.keys(), od_num_recurse_calls.values())
	plt.show()

def benchmark_amortized(verbose=0):
	world = get_random_world(6, 5)

	print_board(world)

	start = time.time()
	solutions_a = pyhop(world, 'agent1', verbose, all_solutions=True, amortize=False) # only one solution
	end = time.time()
	print ('before:', end-start)
	print ('num_recurse calls', get_num_recurse_calls())
	start = time.time()
	solutions_b = pyhop(world, 'agent1'], verbose, all_solutions=True, amortize=True) # only one solution
	end = time.time()
	print ('after:', end-start)
	print ('num_recurse calls', get_num_recurse_calls())
	
	print('solution_a size: ', len(solutions_a))
	print('solution_b size: ', len(solutions_b))


benchmark_amortized(verbose=0)


