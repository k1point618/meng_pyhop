"""
Write a set of problems to file;
Given a problem id or set of attributes, fetch problem from file. 
"""
import time, math
import random_rovers_world as rrw

def write_problems_to_file(problems, file_name=None, file_obj=None):
	if file_name == None and file_obj == None:
		assert False, "Must specify file_name OR file_obj"
		return

	if file_obj == None:
		file_obj = open(file_name, 'a')

	for p in problems:
		write_problem_to_file(p, file_obj=file_obj)
		print("wrote problem {} to file {}".format(p.name, file_obj.name))

# Write ONE problem to file
def write_problem_to_file(problem, file_name=None, file_obj=None):

	if file_obj == None and file_name == None:
		assert False, "Must specify file_name OR file_obj"
		return

	if file_obj == None:
		file_obj = open(file_name, 'a')

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

	for i in range(len(problem.sequence)):
		if i == None:
			to_write += '\tNone\tNone'
		else:
			to_write += '\t{}\t{}'.format(problem.sequence[i], problem.randoms[i])

	file_obj.write(to_write + '\n')


def read_problems_from_file(file_name, problem_name=None, \
	BOARD_X=None, BOARD_Y=None, NUM_ROCKS=None, NUM_SOILS=None):

	to_return = []
	problem_file = open(file_name)
	for line in problem_file:
		problem_array = line.split('\t')

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

# output files are organized by Board-size / dimensions (per file)
# Within a file (board-dimension), problems vary by rand_rang, and a-prob (uncertainty params)
def write_problems(x, y, rand_range, max_cost, a_prob, num_repeat, file_name=None, file_obj=None):
	if file_obj == None:
		file_obj = open("problems/problem_X{}_Y{}.txt".format(x, y), 'a')

	problems = []
	for i in range(num_repeat):
		p_name = "{}_{}_{}_{}_{}".format(x, y, i, rand_range, a_prob) + "_%.0f" % (time.time()*100000%1000)
		problems.append(rrw.make_random_problem(x, y, rand_range=rand_range, max_cost=max_cost, a_prob=a_prob, name=p_name))

	write_problems_to_file(problems, file_obj=file_obj)


# Make and write-problems by bulk
def bulk_write():
	RAND_RANGE = [10]
	MAX_COST = 30
	A_PROBS = [0.3, 0,5, 0.7]
	num_repeat = 100
	BOARD_SIDES = [0.5 * x for x in range(8, 27)]

	for SIDE in BOARD_SIDES:
		x = int(math.floor(SIDE))
		y = int(math.ceil(SIDE))
		file_obj = open("problems/problem_X{}_Y{}.txt".format(x, y), 'a')
		for rand_range in RAND_RANGE:
			for a_prob in A_PROBS:
				write_problems(x, y, rand_range, rand_range*3, a_prob, num_repeat, file_obj=file_obj)

bulk_write()
# write_problems(5, 5, rand_range=10, a_prob=0.5, num_repeat=10)

# # Test read and write
# p = rrw.make_random_problem(5, 5, rand_range=10, name=str(time.time()))
# # write_problem_to_file(p, file_name="problems/problems_test.txt")
# write_problems_to_file([p], file_name="problems/problems_test.txt")

# new_p = read_problems_from_file(file_name="problems/problems_test.txt", problem_name=p.name)[0]










