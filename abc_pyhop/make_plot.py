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

def parse_simulation_raw(filename):
	f = open(filename, 'r')
	sim_results = []
	for line in f:
		sim_results.append(SimResult(*line.split('\t')))

def parse_simulation_avg(filename):
	f = open(filename, 'r')
	plot_lines = {}

	for line in f:



def plot(x, y):
	pass

parse_simulation_raw("results/DetPlanner_over_cost_per_simulation.txt")