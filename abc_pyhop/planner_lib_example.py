from planners import * 
import problem_bank as PROBLEMS

problem = PROBLEMS.maze_1()
planner = Planner.get_HPlanner_v10()
for agent in problem.goals.keys():
	print planner.plan(problem, agent)
