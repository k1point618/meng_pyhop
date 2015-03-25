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
import logging
import rovers_world_operators
import rovers_world_methods
from random_rovers_world import *
from gui_rover_world import *
import problem_bank
from models import *

class Simulation():

    def make_logger(self, problem, AgentType):
        self.log = logging.getLogger('{}.{}'.format(AgentType.__name__, problem.ID))
        self.log.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler('logs/sim_{}.log'.format(AgentType.__name__))
        formatter = logging.Formatter('%(name)s-%(levelname)s:%(message)s')
        file_handler.setFormatter(formatter)
        self.log.addHandler(file_handler)


    def __init__(self, problem, AgentType,
                uncertainty=0, 
                verbose=0, 
                a_star=True, 
                gui=True, 
                re_plan=True,
                use_tree=True):
        
        self.make_logger(problem, AgentType)
        self.log.info('Simulation Logger Created')

        # Simulation parameters: 
        self.PARAMS = {}
        self.PARAMS['uncertainty'] = uncertainty
        self.PARAMS['verbose'] = verbose # Simulaton verbosity
        self.PARAMS['gui'] = gui
        self.PARAMS['re_plan'] = re_plan
        self.PARAMS['use_tree'] = use_tree

        world = problem

        if self.PARAMS['verbose']:
            print('start state')
            print_state(world)
            print_board(world)

        self.agents = {}            # Agents and their mental Models
        self.time = 0               # Global time of the simulation
        self.communications = {}    # 
        self.comm_buff = {}         # 

        self.real_world = copy.deepcopy(world) # Real world has possible uncertainties.
        self.solutions = {}
        self.planTrees = {}
        self.agent_worlds = {}
        self.cur_steps = {}
        self.global_steps = {}
        self.histories = {} # Keeps a history of steps actually taken by each agent

        # Samples 1 solution for each agent in the problem
        for agent_name in world.goals.keys():
            self.communications[agent_name] = []
            # Get Plan
            results = pyhop(world, agent_name, plantree=use_tree, verbose=verbose)
            if self.PARAMS['verbose']: 
                print ('num solutions: ', len(results))
            self.solutions[agent_name] = random.choice(results)

        # Create Agent
        for agent_name in self.solutions.keys():
            agent = AgentType(agent_name, copy.deepcopy(world), args=[self.solutions])
            self.agents[agent_name] = agent
            agent.set_solution(self.solutions[agent_name])

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
            logging.info('length of plan: {}; length of states: {}'.format(len(plan), len(states)))
            logging.info('\ttimestep: {}; \n\tactions: {};'.format(i, plan[i:]))

            # 1: Generate possible Uncertainty to the real-world
            generate_uncertainty(real_world, a_prob=1, verbose=True)

            # 2: This agent get observation about surrounding world and decides to replan
            replan = get_observation(agent, states[i], cur_action, real_world)

            # 3: Agent MIGHT need to re-plan.
            if replan:
                raw_input("Need to re-plan...")
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

    def run(self):
        step = 0
        while True:
            step += 1
            self.log.info("========= step {} ========".format(step))
            self.step_all()
            if all(agent.is_done() for agent in self.agents.values()):
                return


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
            self.log.info("Using predefined uncertainties.")
            # If a world comes with it's own uncertainty-funciton, then apply that
            self.real_world.uncertainties(self.real_world, self.time)
        elif self.PARAMS['uncertainty']:
            generate_uncertainty(self.real_world, a_prob=self.PARAMS['uncertainty'], verbose=True)

        actions_took = {} # Maps agent names to the set of actions

        self.log.info('REAL WORLD: ' + str(self.real_world.at))
        self.log.info(('rock analysis: ', self.real_world.rock_analysis))
        self.log.info(('soil analysis: ', self.real_world.soil_analysis))
        self.log.info(print_board_str(self.real_world))

        for (agent_name, agent) in self.agents.items():
            self.log.info("\n\nAgent Name: {}\n".format(agent_name))
            # info and base-case
            if not agent.is_done():
                (actions, states) = agent.get_solution()
                cur_action = actions[agent.get_cur_step()]
                next_state = states[agent.get_cur_step()]     
                self.log.info("agent {} current action is {}".format(agent_name, cur_action))

            # initailize
            actions_took[agent_name] = []
            
            # First process the incomming communications
            agent.incoming_comm(self.communications) # 1. Update agent's world model
            # TODO: 2. update agent's model of the sender (plan recognition)

            # Diffs contains the new observations
            self.log.info("****** Make Observations ******")
            self.log.info("Agent {} is about to make observations".format(agent.name))
            diffs = agent.make_observations(self.real_world)  # 1. Update agent's world model 
            self.log.info("Agent {} made the following observations: {}\n".format(agent.name, diffs))

            # 2. Decide to Communicate
            # Given observations (diffs), determine communications
            # Returns the set of communications to make.
            # Messages is a dictionary that maps agent-names to messages
            self.log.info("****** Reason about Communicaiton ******")
            if len(diffs) > 0:
                out_messages = agent.communicate(diffs)
                self.append_communications(out_messages)

                # Add communication to actions taken
                for (tm_n, tm) in self.agents.items():
                    self.log.info(">>> out_messages = {}".format(out_messages))
                    self.log.info(">>> (tm_n, tm) = {}, {}".format(tm_n, tm))
                    if tm_n == agent_name:
                        continue
                    if tm_n in out_messages.keys():
                        m = out_messages[tm_n]
                        actions_took[agent_name].append(('comm {} to {}'.format(m, tm_n), 0)) # cost of comm is 0
                        agent.add_history(('comm {} to {}'.format(m, tm_n), 0)) # cost of comm is
                    else: 
                        actions_took[agent_name].append(('no-comm from {} to {}'.format(agent_name, tm_n), 0))
                        agent.add_history(('no-comm from {} to {}'.format(agent_name, tm_n), 0))
            

            # 3.0: If agent is done, no need to replan or act
            if agent.is_done(): continue

            # 3. Continue ACTING or REPLAN on real-world (aka: replana or not)
            replan = agent.replan_q()
            if replan:
                # When re-plan need to reset "visited" from the Real-world
                self.real_world.visited[agent_name] = set()
                results = pyhop(copy.deepcopy(agent.mental_world), agent_name, plantree=self.PARAMS['use_tree'])
                result = random.choice(results)

                if result == None or result == False:
                    self.log.info('*** no solution found for agent:{}, goal:{}'.format(agent_name, self.real_world.goals[agent_name]))
                    agent.add_history(('None', sys.maxint))
                    agent.done = True
                    actions_took[agent_name].append(('failed', sys.maxint))


                agent.set_solution(result)
                agent.cur_step = 0
                agent.global_step += 1
                agent.add_history(('replan', 1))

                actions_took[agent_name].append(('replan', 1))

            else:
                # 4: (if not replan) Agent takes action
                self.log.info(('cur_action: ', cur_action))
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
                
                actions_took[agent_name].append((cur_action, 1))


        self.communications = {}
        self.flush_communications()
        self.time += 1
        return (self.real_world, actions_took)


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


    




