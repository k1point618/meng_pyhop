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
import problem_bank
from models import *

class Simulation():

    def __init__(self, uncertainty=0, 
                verbose=False, 
                a_star=True, 
                gui=True, 
                re_plan=True,
                num_agent=1,
                use_tree=False, problem=None, agent=None):
        
        # Simulation parameters: 
        self.PARAMS = {}
        self.PARAMS['uncertainty'] = uncertainty
        self.PARAMS['verbose'] = verbose # Simulaton verbosity
        self.PARAMS['gui'] = gui
        self.PARAMS['num_agent'] = num_agent
        self.PARAMS['re_plan'] = re_plan
        self.PARAMS['use_tree'] = use_tree

        # Generate a random world if none is provided
        if problem == None:
            world = get_random_world(num_agent=num_agent, a_star=a_star) # with default width and height (10 x 10)
        else:
            world = problem
    
    
        if self.PARAMS['verbose']:
            print('start state')
            print_state(world)
            print_board(world)

        self.agents = {} # Agents and their mental Models

        self.real_world = copy.deepcopy(world) # Real world has possible uncertainties.
        self.solutions = {}
        self.planTrees = {}
        self.agent_worlds = {}
        self.cur_steps = {}
        self.global_steps = {}
        self.done = {}
        self.histories = {} # Keeps a history of steps actually taken by each agent

        # Samples 1 solution for this problem
        for agent_name in world.goals.keys():

            # Create Agent
            agent = AgentMind(agent_name, world)
            self.agents[agent_name] = agent

            # Get Plan
            results = pyhop(world, agent_name, plantree=use_tree)
            if self.PARAMS['verbose']: print ('num solutions: ', len(results))
            agent.set_solution(random.choice(results))

            # if results[0] == False:
            #     solution = None
            #     self.planTrees[agent_name] = None
            # else:    
            #     result = random.choice(results)

            #     if use_tree:
            #         solution = (result.get_actions(), result.get_states())
            #         self.planTrees[agent_name] = result
            #     else:
            #         solution = result
            #         self.planTrees[agent_name] = None

            # self.solutions[agent_name] = solution # TODO: Just 1 solution for now
            # self.cur_steps[agent_name] = 0 # Keeps track of where in the solution we are
            # self.global_steps[agent_name] = 0
            # self.agent_worlds[agent_name] = copy.deepcopy(world)
            # self.done[agent_name] = False
            # self.histories[agent_name] = []

        # Initialize Gui
        if gui:
            app = rover_world_gui(None, self)
            app.title('Rovers World GUI')
            for (agent_name, agent) in self.agents.items():
                print("agent: {}".format(agent))
                app.add_agent(agent)
            app.mainloop()
            self.gui = app


   
    """ temporary hack for testing """
    def remove_traps(world):
        for key in world.loc_available:
            world.loc_available[key] = True
        return world

    @staticmethod # Outdated
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

                solutions = pyhop(real_world, 'agent1', verbose=3, all_solutions=False)
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

    @staticmethod # Outdated
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

                solutions = pyhop(real_world, 'agent1', verbose=0, all_solutions=False)
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

    def run(self, delay=100):
        # current_world = self.real_world
        step = 0
        cur_world = None
        while True:
            step += 1
            print("========= step {} ========".format(step))
            for agent in self.real_world.goals.keys():
                result = self.step(agent_name=agent)
                if result == None:
                    print("No solution found for agent {}".format(agent))
                else:
                    (cur_world, step_info) = result

            if all(agent.is_done() for agent in self.agents.values()):
                return

            print_board(cur_world)
            # raw_input("......")

    """
    Takes 1 step for a given agent. It gets the next step from self.solutions and self.cur_steps
    Then it generates uncertainties in the world. 
    Checks whether the agent's next step is possible. If not, replans. And returns the step as action:replan
    Returns a new world and a set of info regarding on the step, such as
    - whether it involved replanning
    - whehter the agent has no more steps to take
    - the cost of the step for the given agent
    """
    def step(self, agent_name):
        # 0: Info
        replan = False
        step_info = {}
        step_info['replan'] = False
        step_info['done'] = False
        
        agent = self.agents[agent_name]
        solution = agent.get_solution()

        if not solution or solution == None: 
            replan = True
        else:
            (actions, states) = solution
            cur_step = agent.get_cur_step()

            # If agent is Done.
            if cur_step == len(actions):
                print("Done")
                step_info['done'] = True
                self.done[agent] = True
                agent.add_history(('done', 0))
                return (self.real_world, step_info)

            print("*** Next Step ***")
            print('length of remaining plan: {}; \nlength of remaining states: {}'
                .format(len(actions[cur_step:]), len(states[cur_step:])))
            print('\ttimestep: {}; \n\tactions: {};'.format(cur_step, actions[cur_step:]))

            cur_action = actions[cur_step]
            next_state = states[cur_step]     
            step_info['cur_action'] = cur_action

        # 1: Generate possible Uncertainty to the real-world
        if hasattr(self.real_world, 'uncertainties'):
            # If a world comes with it's own uncertainty-funciton, then apply that
            self.real_world.uncertainties(self.real_world, cur_step)
        elif self.PARAMS['uncertainty']:
            new_uncertainties = generate_uncertainty(self.real_world, a_prob=self.PARAMS['uncertainty'], verbose=True)
            step_info['new_uncertainty'] = new_uncertainties
            print("new_uncertainties", new_uncertainties)

        # 2: This agent get observation about surrounding world and decides to replan if not already
        if not replan:
            if self.PARAMS['re_plan']:
                replan = get_observation(agent_name, None, cur_action, self.real_world)

        # 3: Agent MIGHT need to re-plan.
        if replan:
            step_info['replan'] = True

            print('replanning')
            print_board(self.real_world)

            # When re-plan need to reset "visited" from the Real-world
            self.real_world.visited[agent_name] = set()
            results = pyhop(copy.deepcopy(self.real_world), agent_name, verbose=3, plantree=self.PARAMS['use_tree'])
            result = random.choice(results)

            if result == None or result == False:
                print('*** no solution found for agent:{}, goal:{}'.format(agent_name, self.real_world.goals[agent_name]))
                # self.histories[agent].append(('None', sys.maxint))
                agent.add_history(('None', sys.maxint))
                return

            agent.set_solution(result)
            agent.cur_step = 0
            agent.global_step += 1
            agent.add_history(('replan', 1))
            return (self.real_world, step_info)

        else:
            # 4: (if not replan) Agent takes action
            # next_state = act(cur_world, cur_action) # This is the same as states[i]
            print('cur_action: ', cur_action)
            self.real_world = act(self.real_world, cur_action)
            agent.add_history((cur_action, 1))

            # end: Info
            print('next state')
            print_board(next_state)
            print('real world')
            print_board(self.real_world)


        agent.cur_step += 1
        agent.global_step += 1
        return (self.real_world, step_info)

    def cost_p_agent(self):

        to_return = []
        for (agent_name, agent) in self.agents.items():
            to_return.append(sum(action[1] for action in agent.get_histories()))
        return to_return

# simulation = Simulation(num_agent=2, gui=False, re_plan=True, uncertainty=0.4, use_tree=True)
# simulation.run()

# simulation = Simulation(num_agent=1, re_plan=True, uncertainty=0, problem=problem_bank.maze_2())

simulation = Simulation(num_agent=1, gui=True, re_plan=True, uncertainty=0, problem=problem_bank.decompose_replan())

simulation.run(delay=100)
print('simulaiton total cost {}'.format(sum(simulation.cost_p_agent())))
print('simulation cost breakdown: ', simulation.cost_p_agent())





