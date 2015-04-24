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
import problem_bank

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
    solutions_b = pyhop(world, 'agent1', verbose, all_solutions=True, amortize=True) # only one solution
    end = time.time()
    print ('after:', end-start)
    print ('num_recurse calls', get_num_recurse_calls())
    
    print('solution_a size: ', len(solutions_a))
    print('solution_b size: ', len(solutions_b))

def benchmark_compare_a_star(verbose=0):
    world = get_random_world(6, 5)

    print_board(world)

    # Get all solutions using Hierarchical Decompositions for navigating (Baseline3)
    world.settings['a-star'] = False
    start = time.time()
    solutions_a = pyhop(world, 'agent1', verbose, all_solutions=True, amortize=False) # only one solution
    end = time.time()

    print ('before:', end-start)
    print('num solutions found:', len(solutions_a))
    print ('num_recurse calls', get_num_recurse_calls())
    
    # Get all solutions using A-star for navigating
    world.settings['a-star'] = True
    start = time.time()
    solutions_b = pyhop(world, 'agent1', 0, all_solutions=True, amortize=False) # only one solution
    end = time.time()
    print ('after:', end-start)
    print('num solutions found:', len(solutions_b))
    print ('num_recurse calls', get_num_recurse_calls())
    
# Benchmark for how long navigaton takes for random navigation problems
def benchmark_a_star(verbose=0):
    
    num_worlds = 1
    num_problems = 1
    num_repeat = 5
    problem_bank = {}
    
    planner = Planner.get_HPlanner_v14()

    for i in range(num_worlds):
        # world = get_random_world(10, 10) # Defaut to 10 x 10
        # world.uncertainties = get_uncertainty_fun(world, num_step=100, a_prob=0.5)
        # world.uncertainties(world, 0)

        world = make_rand_nav_problem(10, 10)
        world.uncertainties(world, 0)

        # Get all solutions using A-star for navigating
        print_board(world)
        if verbose: 
            print_board(world)
            print_state(world)
        
        world.a_star = True

        for j in range(num_problems):
            # Make a navigation problem
            random_loc = random.choice(world.loc_available.keys())
            world.goals['A1'] = [('navigate', 'A1', random_loc)]
            world.settings['verbose'] = 0
            
            print("Goal: {}".format(world.goals['A1']))

            for k in range(num_repeat):
                start = time.time()
                sol = planner.plan(world, 'A1')[0]
                end = time.time()
                
                print ('time:', end-start)
                print ('problem: ', world.goals)
                print ('solutiON; ', sol)
                
                print ('solution length', len(sol.get_actions()))
                problem_bank[world.goals['A1'][0]] = end-start

                if (end-start) > 1:
                    print_board(world)
                    print ('solution', solutions_b)
                    print ('*** Re-run problem with verbose=3')
                    world.settings['verbose'] = 2
                    pyhop(world, 'agent1', 3, all_solutions=True, amortize=False) # only one solution
                    raw_input("Above problem took too long... {} seconds".format(end-start))


# Generic Bencharmking method
def benchmark(planner1, planner2):

    # Set the number of problems
    NUM_RUNS = 1
    planner1_time = []
    planner2_time = []
    for i in range(NUM_RUNS):

        # First generate a problem
        PROBLEM = get_random_world(BOARD_X=5, BOARD_Y=5, num_agent=2, a_star=True) # with default width and height (10 x 10)
        # PROBLEM = problem_bank.navigate_replan_team_4p()
        # PROBLEM = problem_bank.maze_5()
        # PROBLEM = problem_bank.navigate_replan_team_4()
        # PROBLEM = problem_bank.navigate_replan_team_6()
        # PROBLEM = problem_bank.maze_0()
        # PROBLEM = problem_bank.navigate_replan_team_2()

        # Plan with each planner
        start = time.time()
        solutions1 = planner1.plan(PROBLEM, PROBLEM.goals.keys()[0])
        planner1_time.append(time.time() - start)

        start = time.time()
        solutions2 = planner2.plan(PROBLEM, PROBLEM.goals.keys()[0])
        planner2_time.append(time.time() - start)

        print("\nplanner1 solution: ", solutions1[0])
        print("\nplanner2 solution: ", solutions2[0])
    print("planner1_time: {}".format(planner1_time))
    print("planner2_time: {}".format(planner2_time))
    print("avg planner1_time: {}".format(sum(planner1_time)/len(planner1_time)))
    print("avg planner2_time: {}".format(sum(planner2_time)/len(planner2_time)))


# Generic Bencharmking method
def test_planner(planner1):

    # Set the number of problems
    NUM_RUNS = 1
    planner1_time = []
    for i in range(NUM_RUNS):

        # First generate a problem
        PROBLEM = get_random_world(BOARD_X=7, BOARD_Y=7, num_agent=2, a_star=True) # with default width and height (10 x 10)
        # PROBLEM = problem_bank.navigate_replan_team_4p()
        # PROBLEM = problem_bank.navigate_replan_team_5()
        # PROBLEM = problem_bank.maze_0()
        # PROBLEM = problem_bank.maze_1()
        # PROBLEMS.append(problem_bank.maze_2())
        # PROBLEMS.append(problem_bank.maze_4())
        # PROBLEMS.append(problem_bank.maze_5())

        # Plan with each planner
        start = time.time()
        solutions1 = planner1.plan(PROBLEM, PROBLEM.goals.keys()[0])
        planner1_time.append(time.time() - start)
        print (solutions1)
    print("planner1_time: {}".format(planner1_time))
    print("avg planner1_time: {}".format(sum(planner1_time)/len(planner1_time)))


from planners import *
# These two are practically the same
# benchmark(Planner.get_HPlanner_v10(), Planner.get_HPlanner_v13())

# Comparing the simply-modified original and the seek-plan-all
# benchmark(Planner.get_HPlanner_v12(), Planner.get_HPlanner_v13())

# Comparing using A* vs not using A* for each of the sampling planner
# benchmark(Planner.get_HPlanner_v10(), Planner.get_HPlanner_v11())

# Comparing using A* vs not for the simply-modified of the original
# benchmark(Planner.get_HPlanner_v13(), Planner.get_HPlanner_v14())

# benchmark(Planner.get_HPlanner_bb(), Planner.get_HPlanner_bb_prob())


# test_planner(Planner.get_HPlanner_v13())
# test_planner(Planner.get_HPlanner_v14())
# test_planner(Planner.get_HPlanner_bb_prob())
# test_planner(Planner.get_HPlanner_v13())

# benchmark_amortized(verbose=0)

# single_agent_benchmark()

# benchmark_compare_a_star()

benchmark_a_star(verbose=0)














