"""
Write a set of problems to file;
Given a problem id or set of attributes, fetch problem from file. 
"""
import time
import random_rovers_world as rrw

def write_problem_to_file(problem, file_name="problems.txt"):

	problem_file = open(file_name, 'a')

	# Problem name
	to_write = problem.name

	# Problem Size
	to_write += '\t{}\t{}'.format(problem.BOARD_X, problem.BOARD_Y)

	# Proble num soil and num_rocks
	to_write += '\t{}\t{}'.format(problem.NUM_SOILS, problem.NUM_ROCKS)

	# Problem Uncertainty-settings: Rand-range, max-rand, rand-prob
	to_write += '\t' + str(problem.MAX_COST)
	to_write += '\t' + str(problem.RAND_RANGE)
	to_write += '\t' + str(problem.RAND_PROB)

	# Problem Lander + Lab + Rovers + soil + rocks locations (.at)
	num_objects = len(problem.at.keys())
	to_write += '\t' + str(num_objects)
	for obj_name, loc in problem.at.items():
		to_write += '\t{}\t{}'.format(obj_name, loc)

	# Problem Goal
	num_goals = len(problem.goals.keys())
	to_write += '\t' + str(num_goals)
	for agent_name, goal in problem.goals.items():
		to_write += '\t{}\t{}'.format(agent_name, goal)

	# Problem Uncertainties
	num_sequence = len(problem.sequence)
	to_write += '\t' + str(num_sequence)

	print("sequence: ", problem.sequence)
	print("randoms: ", problem.randoms)
	for i in range(len(problem.sequence)):
		if i == None:
			to_write += '\tNone\tNone'
		else:
			to_write += '\t{}\t{}'.format(problem.sequence[i], problem.randoms[i])

	print("to_write: {}".format(to_write))
	problem_file.write(to_write + '\n')


def read_problems_from_file(file_name='problems.txt', problem_name=None, \
	BOARD_X=None, BOARD_Y=None, NUM_ROCKS=None, NUM_SOILS=None):

	to_return = []
	problem_file = open(file_name)
	for line in problem_file:
		problem_array = line.split('\t')
		print("problem_array: {}".format(problem_array))

		# pase basic parameters
		p_name = problem_array[0]
		board_x, board_y, num_soils, num_rocks = [int(s) for s in problem_array[1:5]]
		max_cost, rand_range, rand_prob = [float(s) for s in problem_array[5:8]]
		problem_array = problem_array[8:]

		# parse AT
		AT = {}
		num_at = int(problem_array.pop(0))
		for i in range(num_at):
			obj, loc = problem_array[2*i:2*i+2]
			AT[obj] = int(loc)
		problem_array = problem_array[2*num_at:]

		# parse GOALS
		GOALS = {}
		num_goals = int(problem_array.pop(0))
		for i in range(num_goals):
			agent, goal = problem_array[2*i:2*i+2]
			GOALS[agent] = goal
		problem_array = problem_array[2*num_goals:]

		# parse UNCERT
		SEQ = []
		RANDs = []
		num_rand = int(problem_array.pop(0))
		for i in range(num_rand):
			s, r = problem_array[2*i:2*i+2]
			if s != 'None':
				SEQ.append(int(s))
			else:
				SEQ.append(None)
			RANDs.append(float(r))

		to_return.append(rrw.make_world(p_name, board_x, board_y, num_soils, num_rocks, max_cost, rand_range, rand_prob, AT, GOALS, SEQ, RANDs))

	return to_return

# Test read and write
p = rrw.make_random_problem(5, 5, rand_range=10, name=str(time.time()))
write_problem_to_file(p, file_name="problems/problems_test.txt")


new_p = read_problems_from_file(file_name="problems/problems_test.txt", problem_name=p.name)[0]
write_problem_to_file(new_p, file_name="problems/problems_test.txt")

new_p = read_problems_from_file(file_name="problems/problems_test.txt", problem_name=p.name)[0]
write_problem_to_file(new_p, file_name="problems/problems_test.txt")


