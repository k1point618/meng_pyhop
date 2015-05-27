import numpy as np
import matplotlib.pyplot as plt
import problems as ProblemLib
from pprint import pprint
import statistics
import sys
class SimulationParameters(object):
    def __init__(self, planner, model, coc, num_repeat=1):
        self.planner = planner
        self.model = model
        self.coc = coc
        self.num_repeat = num_repeat

    def __repr__(self):
        return str([self.planner.name, self.model.__name__, self.coc, self.num_repeat])

class ProblemParameters(object):
    def __init__(self, BOARD_X, BOARD_Y, NUM_ROCKS, NUM_SOILS, RAND_RANGE, A_PROB):
        self.BOARD_X = BOARD_X
        self.BOARD_Y = BOARD_Y
        self.NUM_ROCKS = NUM_ROCKS
        self.NUM_SOILS = NUM_SOILS
        self.RAND_RANGE = RAND_RANGE
        self.A_PROB = A_PROB

    def get_params(self):
        return [self.BOARD_X, self.BOARD_Y, self.NUM_SOILS, self.NUM_ROCKS, self.RAND_RANGE, self.A_PROB]

    def __repr__(self):
        return str(self.get_params())

class SimResult(object):
	def __init__(self, problem_name, planner, model, CoC, final_cost, num_obs, num_comm, num_void, num_steps):
		self.problem_name = problem_name
		self.planner = planner
		self.model = model
		self.CoC = float(CoC)
		self.final_cost = float(final_cost)
		self.num_obs = int(num_obs)
		self.num_comm = int(num_comm)
		self.num_void = int(num_void)
		self.num_steps = int(num_steps)

	def __repr__(self):

		return str([self.problem_name, self.planner, self.model, self.CoC,\
			self.final_cost, self.num_obs, self.num_comm, self.num_void, self.num_steps])


class SimAvgResult(object):
	def __init__(self, problem_name, planner, model, CoC, avgCost, n):
		self.problem_name = problem_name
		self.planner = planner
		self.model = model
		self.CoC = float(CoC)
		self.avgCost = float(avgCost)
		self.n = int(n)
		
class Line(object):
	def __init__(self, planner, model):
		self.planner = planner
		self.model = model
		self.x = []
		self.y = []

class LineIdentifier(object):
	def __init__(self, planner, model):
		self.planner = planner
		self.model = model

class Key(object):
	def __init__(self):
		pass
def parse_board_simulation(filename):
	f = open(filename, 'r')
	sim_param = {}

	for line in f:
		r = SimResult(*line.split('\t'))
		x, y, p_id, rand_range, a_prob_, t = r.problem_name.split('_')
		sim_param_key = r.planner + '\t' + r.model + '\t' + str(r.CoC) + '\t' + x + '\t' + y
		if sim_param_key in sim_param:
			sim_param[sim_param_key].append(r.final_cost)
		else:
			sim_param[sim_param_key] = [r.final_cost]

	out = open('results/DetPlanner_over_board_averaged.txt', 'a')
	for key, vals in sim_param.items():
		out.write(key + '\t' + str(sum(vals)/len(vals)) + '\t' + str(len(vals)) + '\n')


# Compare two raw file and output a raw-file that contains the intersection of problems
def parse_intersection(subset_file, file_name, out_name, re_write=True):
	s_f = open(subset_file, 'r')
	out_f = open(out_name, 'a')
	keys = set()

	for line in s_f:
		r = SimResult(*line.split('\t')[:9])
		if r.problem_name not in keys:
			keys.add(r.problem_name)
		out_f.write(line)

	n_file = open(file_name, 'r')
	for line in n_file: 
		r = SimResult(*line.split('\t')[:9])
		if r.problem_name in keys:
			out_f.write(line)


def parse_avg_to_lines(filename, out_name):
	f = open(filename, 'r')
	sim_param = {}

	for line in f:
		r = SimResult(*line.split('\t')[:9])
		x, y, p_id, rand_range, a_prob_, t = r.problem_name.split('_')
		sim_param_key = r.planner + '\t' + r.model + '\t' + str(r.CoC) + '\t' + x + '\t' + y
		if sim_param_key in sim_param:
			sim_param[sim_param_key].append(r.final_cost)
		else:
			sim_param[sim_param_key] = [r.final_cost]

	out = open(out_name, 'a')
	for key, vals in sim_param.items():
		out.write(key + '\t' + str(sum(vals)/len(vals)) + '\t' + str(len(vals)) + '\n')


def parse_raw(filename):
	f = open(filename, 'r')
	sim_param = {}
	for line in f:
		r = SimResult(*line.split('\t')[:9])
		x, y, p_id, rand_range, a_prob_, t = r.problem_name.split('_')
		# sim_param_key = ProblemParameters(x, y, 2, 2, rand_range, a_prob_)
		# sim_param_key = Key()
		# sim_param_key.planner = r.planner
		# sim_param_key.model = r.model
		# sim_param_key.CoC = r.CoC
		# sim_param_key.problem_name = r.problem_name
		sim_param_key = r.planner + '\t' + r.model + '\t' + str(r.CoC) + '\t' + r.problem_name
		if sim_param_key in sim_param:
			sim_param[sim_param_key].append(r.final_cost)
		else:
			sim_param[sim_param_key] = [r.final_cost]

	# Compute average over repeated problems
	problem_avg = {}
	problems = {}
	for key, vals in sim_param.items():
		planner, model, CoC, problem_name = key.split('\t')
		# avg = sum(vals)/len(vals)
		avg = statistics.median(vals)
		n = len(vals)
		problem_avg[key] = avg

		problem_key = problem_name + '\t' + CoC
		if problem_key in problems:
			problems[problem_key].append(model + '\t' + str(avg) + '\t' + str(n))
		else:
			problems[problem_key] = [model + '\t' + str(avg) + '\t' + str(n)]
		# print key + '\t' + str(problem_avg[key]) + '\t' + str(len(vals))
	
	BPR_better = 0
	BPRII_better = 0
	M2_better = 0
	Max = 0
	bad_problems = []
	improvements  = []
	for key, vals in problems.items():
		problem_name, CoC = key.split('\t')
		M1 = None
		BPR = None
		BPRII = None
		for v in vals:
			model, cost, n = v.split('\t')
			if model == 'AgentSmartEstimate':
				M1 = float(cost)
			elif model == 'AgentSmartBPR':
				BPR = float(cost)
			elif model == 'AgentSmartBPRII':
				BPRII = float(cost)
		if M1 != None and BPR != None and BPRII != None and float(CoC) < 1:
			Max += 1
			# improvements.append((M1 - BPR) / M1)
			improvements.append(max((M1 - BPR) / M1, (M1 - BPRII)/M1))
			if BPR <= M1: 
				BPR_better += 1
			if BPRII <= M1:
				BPRII_better += 1
			if BPR <= M1 or BPRII <= M1:
				M2_better += 1
			else:
				bad_problems.append(problem_name + '\t' + CoC)
	print "Max: {} BPR_better:{} BPRII_better:{} M2_better:{}".format(Max, BPR_better, BPRII_better, M2_better)

	print "Max: {} BPR_better:{} BPRII_better:{} M2_better:{}"\
		.format(Max/Max, BPR_better/float(Max), BPRII_better/float(Max), M2_better/float(Max))

	improvements.sort(reverse=True)
	n = len(improvements)
	p = 0.1
	print "Improvements: {}".format(improvements)
	print "Top {} percent: {}".format(p*100, improvements[0:int(n * p)])
	print "Top {} percent average: {}".format(p * 100, sum(improvements[0:int(n*p)])/int(n*p))

	for i in range(100):
		start = i * 0.01
		end = (i+1) * 0.01
		print "{}\t{}\t{}".format(int(n*p), i, sum(improvements[int(n * start):int(n * end)])/(int(n*end) - int(n*start)))
	# for i in bad_problems:
	# 	print i

def plot(x, y):
	pass

if __name__ == "__main__":
	filename = sys.argv[1]
	# parse_raw("results_opt/raw_result.txt")
	parse_raw(filename)

# parse_intersection("results/SmartBPRII_over_cost_per_simulation_avg.txt",\
# 	"results/SmartEstimateII_BPR_over_cost_per_simulation_avg.txt",\
# 	"results/AllRand_over_cost_simulation_avg.txt")

# parse_intersection("results/SmartBPRII_over_cost_per_simulation_avg.txt",\
# 	"results/RandPlanner_over_cost_per_simulation_avg.txt",\
# 	"results/AllRand_over_cost_simulation_avg.txt", re_write=False)

# parse_avg_to_lines("results/AllRand_over_cost_simulation_avg.txt",\
# 	"results/AllRand_over_cost_per_line.txt")




