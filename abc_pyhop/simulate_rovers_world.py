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
        self.time = 0
        self.communications = {}
        self.comm_buff = {}

        self.real_world = copy.deepcopy(world) # Real world has possible uncertainties.
        self.solutions = {}
        self.planTrees = {}
        self.agent_worlds = {}
        self.cur_steps = {}
        self.global_steps = {}
        self.histories = {} # Keeps a history of steps actually taken by each agent

        # Samples 1 solution for this problem
        for agent_name in world.goals.keys():

            # Create Agent
            agent = AgentNoComm(agent_name, copy.deepcopy(world))
            # agent = AgentFullComm(agent_name, copy.deepcopy(world))
            self.agents[agent_name] = agent
            self.communications[agent_name] = []

            # Get Plan
            results = pyhop(world, agent_name, plantree=use_tree)
            if self.PARAMS['verbose']: print ('num solutions: ', len(results))
            agent.set_solution(random.choice(results))

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
            self.step_all()

            # for (agent_name, agent) in self.agents.items():
            #     if agent.is_done():
            #         continue

            #     result = self.step(agent_name=agent_name)
            #     if result == None:
            #         print("No solution found for agent {}".format(agent_name))
            #     else:
            #         (cur_world, step_info) = result

            if all(agent.is_done() for agent in self.agents.values()):
                return

            print_board(cur_world)
            # raw_input("......")

    """
    New implementation of step that takes into account communication and generates
    uncertainties only once per time-step.
    """
    def step_all(self):
        """
        1. Generate uncertainties
        2. Each agent 
            - Observes the world in two ways
                1. Surrounding env
                2. Incoming communication
            - Given observations, determine two things
                1. Communicate?
                2. Replan?
            - Make moves
        """

        if all(agent.is_done() for agent in self.agents.values()):
            return True # All done

        if hasattr(self.real_world, 'uncertainties'):
            # If a world comes with it's own uncertainty-funciton, then apply that
            self.real_world.uncertainties(self.real_world, self.time)
        elif self.PARAMS['uncertainty']:
            generate_uncertainty(self.real_world, a_prob=self.PARAMS['uncertainty'], verbose=True)

        actions_took = {}

        for (agent_name, agent) in self.agents.items():
            # info and base-case
            if not agent.is_done():

                (actions, states) = agent.get_solution()
                cur_action = actions[agent.get_cur_step()]
                next_state = states[agent.get_cur_step()]     

            # ??
            # step_info[(agent_name, 'cur_action')] = cur_action

            
            # Diffs contains the new observations
            diffs = agent.incoming_comm(self.communications) # Process Communication by updating agent's mental_world
            diffs += agent.make_observations(self.real_world) # TODO: Implement
            self.communications = {}
            

            # Given observations (diffs), determine communications
            # Returns the set of communications to make.
            # Messages is a dictionary that maps agent-names to messages
            messages = agent.communicate(diffs)
            self.append_communications(messages)

            if agent.is_done(): continue

            # Given observations (diffs), determine replan
            replan = agent.replan_q(diffs) # Given the new observations, should the agent re-plan?
            if replan:
                # When re-plan need to reset "visited" from the Real-world
                self.real_world.visited[agent_name] = set()
                results = pyhop(copy.deepcopy(agent.mental_world), agent_name, plantree=self.PARAMS['use_tree'])
                result = random.choice(results)

                if result == None or result == False:
                    print('*** no solution found for agent:{}, goal:{}'.format(agent_name, self.real_world.goals[agent_name]))
                    agent.add_history(('None', sys.maxint))
                    agent.done = True
                    actions_took[agent_name] = ('failed')


                agent.set_solution(result)
                agent.cur_step = 0
                agent.global_step += 1
                agent.add_history(('replan', 1))

                actions_took[agent_name] = ('replan')

            else:
                # 4: (if not replan) Agent takes action
                print('cur_action: ', cur_action)
                self.real_world = act(self.real_world, cur_action)
                agent.mental_world = act(agent.mental_world, cur_action)

                assert(self.real_world != False)
                assert(agent.mental_world != False) 

                agent.add_history((cur_action, 1))
                agent.cur_step += 1
                agent.global_step += 1

                if agent.cur_step >= len(agent.actions):
                    agent.done = True
                    agent.success = True

                # end: Info
                print('next state')
                print_board(next_state)
                print('real world')
                print_board(self.real_world)

                actions_took[agent_name] = cur_action


        self.flush_communications()
        self.time += 1
        return (self.real_world, actions_took) # TODO


    def append_communications(self, messages):
        Simulation.append_dict(self.comm_buff, messages)

    def flush_communications(self):
        Simulation.append_dict(self.communications, self.comm_buff)
        self.comm_buff = {}

    @staticmethod
    def append_dict(d, delta):
        for (new_k, new_v) in delta.items():
            if new_k in d.keys():
                d[new_k] += new_v
            else:
                d[new_k] = new_v

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
        step_info = {}
        step_info['replan'] = False
        
        replan = False
        agent = self.agents[agent_name]
        solution = agent.get_solution()
        cur_step = agent.get_cur_step()

        # Get actions and states
        # If agent is Done and successful
        (actions, states) = solution
        if cur_step == len(actions):
            print("Done")
            agent.done = True
            agent.add_history(('done', 0))
            return (self.real_world, step_info)
        cur_action = actions[cur_step]
        next_state = states[cur_step]     

        step_info['cur_action'] = cur_action

        # 1: Generate possible Uncertainty to the real-world
        if hasattr(self.real_world, 'uncertainties'):
            # If a world comes with it's own uncertainty-funciton, then apply that
            self.real_world.uncertainties(self.real_world, cur_step)
        elif self.PARAMS['uncertainty']:
            # Else, generate randomly
            new_uncertainties = generate_uncertainty(self.real_world, a_prob=self.PARAMS['uncertainty'], verbose=True)

        # 2: This agent get observation about surrounding world and decides to replan if not already
        if self.PARAMS['re_plan']:
            replan = get_observation(agent_name, None, cur_action, self.real_world)

        # 3: Agent MIGHT need to re-plan.
        if replan:
            step_info['replan'] = True

            print('agent {} is replanning; world is: '.format(agent_name))
            print_board(self.real_world)

            # When re-plan need to reset "visited" from the Real-world
            self.real_world.visited[agent_name] = set()
            results = pyhop(copy.deepcopy(self.real_world), agent_name, plantree=self.PARAMS['use_tree'])
            result = random.choice(results)

            if result == None or result == False:
                print('*** no solution found for agent:{}, goal:{}'.format(agent_name, self.real_world.goals[agent_name]))
                agent.add_history(('None', sys.maxint))
                agent.done = True
                return None

            agent.set_solution(result)
            agent.cur_step = 0
            agent.global_step += 1
            agent.add_history(('replan', 1))
            return (self.real_world, step_info)

        else:
            # 4: (if not replan) Agent takes action
            print('cur_action: ', cur_action)
            self.real_world = act(self.real_world, cur_action)
            agent.mental_world = act(agent.mental_world, cur_action)

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
# 
# simulation = Simulation(num_agent=2, gui=True, re_plan=True, uncertainty=1, use_tree=True)

# simulation = Simulation(num_agent=1, gui=False, re_plan=True, uncertainty=0, problem=problem_bank.maze_5())

simulation = Simulation(num_agent=1, gui=True, re_plan=True, uncertainty=0, problem=problem_bank.navigate_replan_team())

simulation.run(delay=100)
print('simulaiton total cost {}'.format(sum(simulation.cost_p_agent())))
print('simulation cost breakdown: ', simulation.cost_p_agent())
for (agent_name, agent) in simulation.agents.items():
    print(agent_name, agent.get_histories())





