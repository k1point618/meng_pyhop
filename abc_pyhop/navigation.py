""" 
We implement A* for navigation in order to circumvent using hierarchical 
planning for finding the path of least cost. 

The navigation function replaces the navigation-method in the rovers-world defintion. 
It returns a sequence of primitive actions. 
"""
from __future__ import print_function
import pprint, pyhop, random, math, heapq
import random_rovers_world

def a_star(state, agent, sink):
	source = state.at[agent] # Navigates to sink from wherever the agent currently is.
	if VERBOSE: print('*** A* from {} to {} ***'.format(source, sink))

	closed_set = set() # Set of nodes that have already been evaluated
	openset = [] # Set of tentative nodes to be evaluated. Initially containing the start node
	heapq.heappush(openset, (0, source))
	came_from = {} # Keep track of parents for path-reconstruction

	g_score = {} # Cost from start along best known path
	g_score[source] = 0
	# Estimated total cost from start to goal through y
	f_score = {}
	f_score[source] = g_score[source] + heuristic(state, source, sink)

	while len(openset) != 0:
		# TODO: Make opeset a min-priority-queue
		(cur_f_score, current) = heapq.heappop(openset) # Want the node in openset with lowest f-score
		if current == sink:
			if VERBOSE: print('path found')
			return to_actions(reconstruct_path(came_from, sink), agent)

		closed_set.add(current)
		for neighbor in get_neighbors(state, current):
			if neighbor in closed_set:
				continue
			tentative_g_score = g_score[current] + dist_between(current, neighbor)

			if (not (neighbor in openset)) or tentative_g_score < g_score[neighbor]:
				came_from[neighbor] = current
				g_score[neighbor] = tentative_g_score
				f_score[neighbor] = g_score[neighbor] + heuristic(state, neighbor, sink)
				if (not(neighbor in openset)):
					heapq.heappush(openset, (f_score[neighbor], neighbor))

	if VERBOSE: print('no path found')
	return False

def to_actions(path, agent):
	to_return = []
	for i in range(len(path)-1):
		to_return.append(('navigate_op', agent, path[i], path[i+1]))
	return to_return

def get_neighbors(state, current):
	neighbors = []
	(cur_x, cur_y) = state.loc[current]
	if cur_x != 0 and state.loc_available[current-state.prop['num_col']]:
		neighbors.append(current-state.prop['num_col'])
	if cur_x != state.prop['num_row'] - 1 and state.loc_available[current+state.prop['num_col']]:
		neighbors.append(current + state.prop['num_col'])
	if cur_y != 0 and state.loc_available[current-1]:
		neighbors.append(current-1)
	if cur_y != state.prop['num_col']-1 and state.loc_available[current+1]:
		neighbors.append(current+1)
	return neighbors

def heuristic(state, source, sink):
	(source_x, source_y) = state.loc[source]
	(sink_x, sink_y) = state.loc[sink]

	return math.sqrt((source_x - sink_x)**2 + (source_y - sink_y)**2)

def reconstruct_path(came_from, current):
	to_return = [current]
	while current in came_from:
		current = came_from[current]
		to_return.append(current)
	to_return.reverse()
	return to_return

def dist_between(current, neighbor):
	return 1

VERBOSE = True
if __name__ == '__main__':
	print("Testing a_star")
	world = random_rovers_world.get_random_world(5, 5)
	print("Random world: ")
	random_rovers_world.print_board(world)

	pyhop.print_state(world)
	sink = random.choice(world.loc.keys())
	path = a_star(world, 'agent1', sink)
	print(path)
