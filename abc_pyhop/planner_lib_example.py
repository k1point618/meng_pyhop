from planners import * 
import problem_bank as PROBLEMS

problem = PROBLEMS.maze_1()
planner = Planner.get_HPlanner_v13()
for agent in problem.goals.keys():
	solutions =  planner.plan(problem, agent)
	for (actions, states) in solutions:
		print actions
	print "found a total of {} plans".format(len(solutions))