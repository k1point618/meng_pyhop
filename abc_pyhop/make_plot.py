import numpy as np
import matplotlib.pyplot as plt
import problems as ProblemLib
from pprint import pprint

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
	def __init__(self, planner, model, CoC, avgCost):
		pass
		
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




def plot(x, y):
	pass

parse_intersection("results/SmartBPRII_over_cost_per_simulation_avg.txt",\
	"results/SmartEstimateII_BPR_over_cost_per_simulation_avg.txt",\
	"results/AllRand_over_cost_simulation_avg.txt")

parse_intersection("results/SmartBPRII_over_cost_per_simulation_avg.txt",\
	"results/RandPlanner_over_cost_per_simulation_avg.txt",\
	"results/AllRand_over_cost_simulation_avg.txt", re_write=False)

parse_avg_to_lines("results/AllRand_over_cost_simulation_avg.txt",\
	"results/AllRand_over_cost_per_line.txt")




