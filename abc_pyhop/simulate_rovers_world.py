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

    def __init__(self, uncertainty=0, 
                verbose=True, 
                show_run=True, 
                a_star=True, 
                gui=True, 
                re_plan=True,
                num_agent=1):
        # Simulation parameters: 
        self.PARAMS = {}
        self.PARAMS['uncertainty'] = uncertainty
        self.PARAMS['verbose'] = verbose # Simulaton verbosity
        self.PARAMS['a-star'] = a_star
        self.PARAMS['show_run'] = show_run
        self.PARAMS['gui'] = gui
        self.PARAMS['num_agent'] = num_agent
        self.PARAMS['re_plan'] = re_plan

        # Generate a random world
        world = get_random_world(num_agent=num_agent) # with default width and height (10 x 10)
        world.settings['a-star'] = self.PARAMS['a-star']
        world.settings['verbose'] = 0 # Pyhop planning verbosity
        world.settings['sample'] = False # If sample=false, then each agent's plan is deterministic

        if self.PARAMS['verbose']:
            print('start state')
            print_state(world)
            print_board(world)

        # Real world has possible uncertainties.
        self.real_world = copy.deepcopy(world)
        self.solutions = {}
        self.agent_worlds = {}
        self.cur_steps = {}
        self.global_steps = {}

        # Samples 1 solution for this problem
        for agent in world.goals.keys():
            solutions = pyhop(world, agent, world.settings['verbose'], all_solutions=(not world.settings['sample']), amortize=False)
            if self.PARAMS['verbose']:
                print ('num solutions: ', len(solutions))
            self.solutions[agent] = random.choice(solutions) # TODO: Just 1 solution for now
            self.cur_steps[agent] = 0 # Keeps track of where in the solution we are
            self.global_steps[agent] = 0
            self.agent_worlds[agent] = copy.deepcopy(world)

        # Initialize Gui
        if gui:
            app = rover_world_gui(None, self)
            app.title('Rovers World GUI')
            for agent in world.goals.keys():
                app.add_rover(agent, self.agent_worlds[agent], self.solutions[agent])
            app.mainloop()
            self.gui = app

        # elif show_run:
        #     for (i, solution) in enumerate(a1_solutions):
        #         print('*** Showing plan #{} of {}'.format(i+1, len(a1_solutions)))
        #         Simulation.show_single_agent(agent_init_world, real_world, solution, 'agent1')

   
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

    def step(self, agent):
        # To be displayed on GUI regarding the details of Step
        step_info = {}
        step_info['replan'] = False
        step_info['done'] = False

        # 0: Info
        solution = self.solutions[agent] # Maps to 1 solution
        (actions, states) = solution
        cur_step = self.cur_steps[agent]

        # If agent is Done.
        if cur_step == len(actions):
            print("Done")
            step_info['done'] = True
            return (self.real_world, step_info)

        print("*** Next Step ***")
        print('length of remaining plan: {}; \nlength of remaining states: {}'
            .format(len(actions[cur_step:]), len(states[cur_step:])))
        print('\ttimestep: {}; \n\tactions: {};'.format(cur_step, actions[cur_step:]))


        cur_action = actions[cur_step]
        next_state = states[cur_step]     
        step_info['cur_action'] = cur_action

        # 1: Generate possible Uncertainty to the real-world
        if self.PARAMS['uncertainty']:
            new_uncertainties = generate_uncertainty(self.real_world, a_prob=self.PARAMS['uncertainty'], verbose=True)
            step_info['new_uncertainty'] = new_uncertainties

        # 2: This agent get observation about surrounding world and decides to replan
        if self.PARAMS['re_plan']:
            replan = get_observation(agent, None, cur_action, self.real_world)
        else: replan = False

        # 3: Agent MIGHT need to re-plan.
        if replan:
            step_info['replan'] = True

            print('replanning')
            print_board(self.real_world)

            solutions = pyhop(self.real_world, agent, verbose=3, all_solutions=False, amortize=False)
            solution = solutions[0]
            
            self.solutions[agent] = solution
            self.cur_steps[agent] = 0

            print('new plan', solution[0])

            if solution != False: 
                (actions, states) = solution
                self.global_steps[agent] += 1
                return (self.real_world, step_info)

            else:
                print('*** no solution found for agent:{}, goal:{}'.format(agent, self.real_world.goals[agent]))
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


        self.cur_steps[agent] += 1
        self.global_steps[agent] += 1
        return (self.real_world, step_info)

simulation = Simulation(num_agent=2, re_plan=True, uncertainty=1)

