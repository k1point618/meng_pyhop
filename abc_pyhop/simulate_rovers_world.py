""" 
In this file, we simulate various problems in the rovers domain.
- Single-agent solving a problem with no uncertainty
- Single-agent solving a problem with uncertainty
- Multi-agent solving a problem with no uncertainty
- Multi-agent solving a problem with uncertainty but no communication
- Multi-agent solving a problem with uncertainty and hand-crafted communication protocol
- Multi-agent solving a problem with uncertainty and anticipatory mental model for Communication
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
from gui_rover_world import *


class Simulation():

    def __init__(self, uncertainty=False, verbose=0, show_run=True, a_star=True, gui=True):
        # Simulation parameters: 
        
        self.step_counter = 0
        world = get_random_world()
        world.settings['a-star'] = a_star
        
        print('start state')
        print_state(world)
        print_board(world)

        # Samples 1 solution for this problem
        a1_solutions = pyhop(world, 'agent1', 0, all_solutions=False, amortize=False)
        
        # Real world has possible uncertainties.
        real_world = copy.deepcopy(world)
        agent_init_world = copy.deepcopy(world)
        
        self.real_world = world
        self.agent_init_world = agent_init_world
        self.agent_solution = a1_solutions[0] # TODO: Just 1 solution for now
        self.actions, self.states = a1_solutions[0]

        # Initialize Gui
        if gui:
            app = rover_world_gui(None, self)
            app.title('Rovers World GUI')
            app.add_rover('agent1', agent_init_world, a1_solutions[0]) #Just 1 solution for now
            app.add_rover('agent2', copy.deepcopy(agent_init_world), a1_solutions[0])
            app.mainloop()
            self.gui = app

        elif show_run:
            for (i, solution) in enumerate(a1_solutions):
                print('*** Showing plan #{} of {}'.format(i+1, len(a1_solutions)))
                Simulation.show_single_agent(agent_init_world, real_world, solution, 'agent1')

   
    """ temporary hack for testing """
    def remove_traps(world):
        for key in world.loc_available:
            world.loc_available[key] = True
        return world

    @staticmethod
    def show_single_agent_recurse(cur_world, real_world, solution, agent, uncertainty=False):
        (plan, states) = solution

        # Take 1 step at a time
        for (i, cur_action) in enumerate(plan):

            # 0: Info
            print('length of plan: {}; length of states: {}'.format(len(plan), len(states)))
            print('\ttimestep: {}; \n\tactions: {};'.format(i, plan[i:]))

            # 1: Generate possible Uncertainty to the real-world
            generate_uncertainty(real_world, a_prob=1, verbose=True)

            # 2: This agent get observation about surrounding world and decides to replan
            replan = get_observation(agent, states[i], cur_action, real_world)

            # 3: Agent MIGHT need to re-plan.
            if replan:
                raw_input("Need to re-plan...")
                # Do replanning Stuff
                # TODO: Include the problem/goal in State/World definition
                print('replanning')
                # TODO: Update domain definition (preconditions) so that if task is done, 
                # no need to re-do
                real_world = remove_traps(copy.deepcopy(real_world))
                print('remove_traps...')
                print_board(real_world)

                solutions = pyhop(real_world, 'agent1', verbose=3, all_solutions=False, amortize=False)
                solution = solutions[0]
                print('new solution', solution)

                if solution != False: 
                    show_single_agent(real_world, real_world, solution, agent)
                    return
                else:
                    print('no solution found for agent:{}, goal:{}'.format(agent, real_world.goals[agent]))
                    return
            # 4: (if not replan) Agent takes action
            next_state = act(cur_world, cur_action) # This is the same as states[i]
            real_world = act(real_world, cur_action)

            # Infity: Info
            print('next state')
            print_board(states[i])
            print('real world')
            print_board(real_world)

            raw_input("Press Enter to continue...")

    @staticmethod
    def show_single_agent(cur_world, real_world, solution, agent, uncertainty=False):
        (actions, states) = solution

        # Take 1 step at a time
        step_counter = 0
        while len(actions) != 0:
            
            print("*** Old stuff ***")
            # 0: Info
            print('length of remaining plan: {}; \nlength of remaining states: {}'
                .format(len(actions), len(states)))
            print('\ttimestep: {}; \n\tactions: {};'.format(step_counter, actions))

            cur_action = actions.pop(0)
            next_state = states.pop(0)

            # 1: Generate possible Uncertainty to the real-world
            generate_uncertainty(real_world, a_prob=1, verbose=True)

            # 2: This agent get observation about surrounding world and decides to replan
            replan = get_observation(agent, next_state, cur_action, real_world)

            # 3: Agent MIGHT need to re-plan.
            if replan:
                raw_input("Need to re-plan...")
                print('replanning')

                print_board(real_world)

                solutions = pyhop(real_world, 'agent1', verbose=0, all_solutions=False, amortize=False)
                solution = solutions[0]
                
                # print('new solution', solution)

                if solution != False: 
                    (actions, states) = solution

                else:
                    print('no solution found for agent:{}, goal:{}'.format(agent, real_world.goals[agent]))
                    return

            else:
                # 4: (if not replan) Agent takes action
                # next_state = act(cur_world, cur_action) # This is the same as states[i]
                real_world = act(real_world, cur_action)

                # end: Info
                print('next state')
                print_board(next_state)
                print('real world')
                print_board(real_world)

                raw_input("Press Enter to continue...")

            step_counter += 0

    def step(self, agent='agent1'):
        # 0: Info
        print("*** Next Step ***")
        print('length of remaining plan: {}; \nlength of remaining states: {}'
            .format(len(self.actions), len(self.states)))
        print('\ttimestep: {}; \n\tactions: {};'.format(self.step_counter, self.actions))


        cur_action = self.actions.pop(0)
        next_state = self.states.pop(0)

        # 1: Generate possible Uncertainty to the real-world
        # generate_uncertainty(real_world, a_prob=1, verbose=True)

        # 2: This agent get observation about surrounding world and decides to replan
        # replan = get_observation(agent, next_state, cur_action, real_world)
        replan=False
        # 3: Agent MIGHT need to re-plan.
        if replan:
            raw_input("Need to re-plan...")
            print('replanning')

            print_board(self.real_world)

            solutions = pyhop(self.real_world, 'agent1', verbose=0, all_solutions=False, amortize=False)
            solution = solutions[0]
            
            # print('new solution', solution)

            if solution != False: 
                (actions, states) = solution

            else:
                print('no solution found for agent:{}, goal:{}'.format(agent, self.real_world.goals[agent]))
                return

        else:
            # 4: (if not replan) Agent takes action
            # next_state = act(cur_world, cur_action) # This is the same as states[i]
            print('cur_action: ', cur_action)
            self.real_world = act(self.real_world, cur_action)

            # end: Info
            print('next state')
            print_board(next_state)
            print('real world')
            print_board(self.real_world)

            # raw_input("Press Enter to continue...")

        self.step_counter += 1
        return self.real_world

simulation = Simulation()

