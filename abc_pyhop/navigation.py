""" 
We implement A* for navigation in order to circumvent using hierarchical 
planning for finding the path of least cost. 

The navigation function replaces the navigation-method in the rovers-world defintion. 
It returns a sequence of primitive actions. 
"""
from __future__ import print_function
import pprint, pyhop, random, math, heapq, time
import random_rovers_world

def a_star(state, agent, sink):
	VERBOSE = False
	SAMPLE = state.rand
	
	source = state.at[agent] # Navigates to sink from wherever the agent currently is.
	if VERBOSE > 1: 
		print('*** A* from {} to {} ***'.format(source, sink))
		start = time.time()

	closed_set = set() # Set of nodes that have already been evaluated
	openset = [] # Set of tentative nodes to be evaluated. Initially containing the start node
	came_from = {} # Keep track of parents for path-reconstruction

	g_score = {} # Cost from start along best known path
	g_score[source] = 0
	# Estimated total cost from start to goal through y
	f_score = {}
	new_f_score = g_score[source] + heuristic(state, source, sink)
	f_score[source] = new_f_score
	heapq.heappush(openset, (new_f_score, source))
	
	# Inverse mapping: maps f_score to an array of locations (Should always contain the same items as openset)
	inverse_f_scores = {}
	inverse_f_scores[new_f_score] = [source]


	NUM_ITER = 0
	while len(openset) != 0:
		NUM_ITER += 1
		
		# Instead of popping the first one, we first pop to get the min f-score
		# Then we find all nodes with min f-score
		# Then we remove a random one
		(cur_f_score, current) = heapq.heappop(openset) # Want the node in openset with lowest f-score
		if VERBOSE:
			print ('iteration', NUM_ITER)
			print ('\tcurrently picked: ', (cur_f_score, current))
			print ('\topenset: ', openset)
			print ('\tinverse_f_scores:', inverse_f_scores) 

		if SAMPLE and len(inverse_f_scores[cur_f_score]) > 1 :
			if VERBOSE:
				print ('*** Has multiple locations with the same f-score')
			# If there are multiple values in the openset with the same min score
			heapq.heappush(openset, (cur_f_score, current)) # First put it back
			if VERBOSE: print ('put back... openset', openset)

			to_pop_loc = random.choice(inverse_f_scores[cur_f_score]) # pick a random location
			if VERBOSE: print ('randomly picked location... ', to_pop_loc)

			inverse_f_scores[cur_f_score].remove(to_pop_loc) # remove from inverse_f_socre
			openset.remove((cur_f_score, to_pop_loc)) # Remove from heap
			heapq.heapify(openset)
			
			current = to_pop_loc
		else:
			inverse_f_scores[cur_f_score].remove(current)

		

		if current == sink:
			return to_actions(reconstruct_path(came_from, sink), agent)

		closed_set.add(current)
		for neighbor in get_neighbors(state, current):
			if neighbor in closed_set:
				continue
			task = ('navigate_op', agent, current, neighbor)
			tentative_g_score = g_score[current] + state.cost_func(state, task)

			if (not (neighbor in openset)) or tentative_g_score < g_score[neighbor]:
				came_from[neighbor] = current
				g_score[neighbor] = tentative_g_score
				new_f_score = g_score[neighbor] + heuristic(state, neighbor, sink)
				f_score[neighbor] = new_f_score

				# Add to inverse_f_scores
				if new_f_score in inverse_f_scores.keys():
					if neighbor not in inverse_f_scores[new_f_score]:
						inverse_f_scores[new_f_score].append(neighbor)
				else: 
					inverse_f_scores[new_f_score] = [neighbor]

				if (not((f_score[neighbor], neighbor) in openset)):
					heapq.heappush(openset, (f_score[neighbor], neighbor))

	if VERBOSE: 
		print('no path found')

	return False

def to_actions(path, agent):
	to_return = []
	for i in range(len(path)-1):
		to_return.append(('navigate_op', agent, path[i], path[i+1]))
	return to_return

def get_neighbors(state, current):
	neighbors = []
	(cur_x, cur_y) = state.loc[current]
	# Neighbor above
	# if cur_x != 0 and state.loc_available[current-state.prop['num_col']]:
	if cur_x != 0:
		neighbors.append(current-state.prop['num_col'])
	# Neighbor below
	# if cur_x != state.prop['num_row'] - 1 and state.loc_available[current+state.prop['num_col']]:
	if cur_x != state.prop['num_row'] - 1:
		neighbors.append(current + state.prop['num_col'])
	# Neighbor Left
	# if cur_y != 0 and state.loc_available[current-1]:
	if cur_y != 0:
		neighbors.append(current-1)
	# Neighbor Right
	# if cur_y != state.prop['num_col']-1 and state.loc_available[current+1]:
	if cur_y != state.prop['num_col']-1:
		neighbors.append(current+1)
	return neighbors

def heuristic(state, source, sink):
	(source_x, source_y) = state.loc[source]
	(sink_x, sink_y) = state.loc[sink]

	return abs((source_x - sink_x)) + abs((source_y - sink_y))


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
	world = random_rovers_world.get_random_world(10, 10)
	world.rand = False
	print("Random world: ")
	random_rovers_world.print_board(world)

	# pyhop.print_state(world)
	sink = random.choice(world.loc.keys())
	print("*** Navigating from {} to {} ***".format(world.at['A1'], sink))
	path = a_star(world, 'A1', sink)
	print(path)
	for action in path:
		print("{}\t{}".format(action, world.cost_func(world, action)))
