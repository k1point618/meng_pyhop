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
import logging, shutil
import rovers_world_operators
import rovers_world_methods
from random_rovers_world import *
from gui_rover_world import *
import problem_bank
from models import *

class Simulation():

    def make_logger(self, problem, AgentType):
        self.log = logging.getLogger('{}.{}'.format(AgentType.__name__, problem.name))
        self.log.setLevel(logging.CRITICAL)
        # file_handler = logging.FileHandler('logs/sim_{}.log'.format(AgentType.__name__))
        # formatter = logging.Formatter('%(asctime)s-%(name)s-(%(lineno)d):%(message)s')
        # file_handler.setFormatter(formatter)
        # self.log.addHandler(file_handler)


    def __init__(self, world, AgentType, planner,
                uncertainty=0, 
                verbose=0, 
                a_star=True, 
                gui=False, 
                re_plan=True,
                use_tree=False):
        
        self.make_logger(world, AgentType)
        self.log.info('Simulation Logger Created')
        self.AgentType = AgentType.__name__
        self.name = "{}_{}".format(world.name, self.AgentType)
        self.planner_name = planner.name

        # Simulation parameters: 
        self.PARAMS = {}
        self.PARAMS['uncertainty'] = uncertainty
        self.PARAMS['verbose'] = verbose # Simulaton verbosity
        self.PARAMS['gui'] = gui
        self.PARAMS['re_plan'] = re_plan
        self.PARAMS['use_tree'] = use_tree

        if self.PARAMS['verbose']:
            print('start state')
            print_state(world)
            print_board(world)

        self.agents = {}            # Agents and their mental Models
        self.time = 0               # Global time of the simulation
        self.communications = []    # A set of CommMessage objects
        self.comm_buff = []         # Keeps temporary communication during the current step

        self.real_world = copy.deepcopy(world) # Real world has possible uncertainties.
        self.solutions = {}
        self.planTrees = {}
        self.agent_worlds = {}
        self.cur_steps = {}
        self.global_steps = {}
        self.histories = {} # Keeps a history of steps actually taken by each agent

        # Samples 1 solution for each agent in the problem
        for agent_name in world.goals.keys():
            # Get Plan
            # results = pyhop(world, agent_name, plantree=use_tree, verbose=verbose)
            results = planner.plan(world, agent_name)
            self.solutions[agent_name] = random.choice(results)
            
        # Create Agent and set solutions
        for agent_name in self.solutions.keys():
            agent = AgentType(agent_name, copy.deepcopy(world), args=[self.solutions])
            agent.planner = planner
            self.agents[agent_name] = agent
            agent.set_solution(self.solutions[agent_name])

        # Initialize Gui
        if gui:
            app = rover_world_gui(None, self)
            app.title('Rovers World GUI')
            for (agent_name, agent) in self.agents.items():
                # print("agent: {}".format(agent))
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
        self.log.info(self.real_world)
        if hasattr(self.real_world, 'uncertainties'):
            self.log.info("Using predefined uncertainties.")
            self.real_world.uncertainties(self.real_world, self.time)
        elif self.PARAMS['uncertainty']:
            generate_uncertainty(self.real_world, a_prob=self.PARAMS['uncertainty'], verbose=True)

        actions_took = {} # Maps agent names to the set of actions

        self.log.info('REAL WORLD: ' + str(self.real_world.at))
        self.log.info('REAL WORLD: ' + str(self.real_world.cost))
        self.log.info(('rock analysis: ', self.real_world.rock_analysis))
        self.log.info(('soil analysis: ', self.real_world.soil_analysis))
        self.log.info(('has rock sample: ', self.real_world.has_rock_sample))
        self.log.info(('has soil sample: ', self.real_world.has_soil_sample))
        self.log.info("\n" + print_board_str(self.real_world))

        for (agent_name, agent) in self.agents.items():
            self.log.info("\n\nAgent Name: {}\n".format(agent_name))
            # info and base-case
            if not agent.is_done():
                cur_action = agent.get_cur_action()
                next_state = agent.get_next_state()
                self.log.info("agent {} current action is {}".format(agent_name, cur_action))

            # initailize
            actions_took[agent_name] = []
            
            # First process the incomming communications
            world_changed = agent.incoming_comm(self.communications) 

            # 1. Update agent's world model
            # TODO: 2. update agent's model of the sender (plan recognition)

            # Diffs contains the new observations
            diffs = agent.make_observations(self.real_world)  # 1. Update agent's world model 
            self.log.info("Agent {} made the following observations: {}\n".format(agent.name, diffs))


            # 2. Decide to Communicate ~~~~~~~~~~~~
            # Given observations (diffs), determine communications
            # Returns the set of communications to make.
            # Messages is a dictionary that maps agent-names to messages
            out_commMsgs = []
            void_msgs = []
            if len(diffs) > 0:
                self.log.info("****** Agent {} Reasons about Communicaiton ******".format(agent.name))
                (out_commMsgs, void_msgs) = agent.communicate(diffs) # Out_messages is a set of CommMessage
                self.comm_buff += out_commMsgs # append to comm-buffer
                

                self.log.info("Agent {} decided to communicate:\n\t{}".format(agent.name, out_commMsgs))
                self.log.info("Agent {} decide NOT to communicate:\n\t{}".format(agent.name, void_msgs))

                # Add communication to actions taken (including all messages NOT sent)
                for commMsg in out_commMsgs:
                    hist = agent.add_history('comm {} to {}'.format(commMsg.msg, commMsg.receiver), self.real_world.COST_OF_COMM)
                    actions_took[commMsg.sender].append(hist)
                for commMsg in void_msgs:
                    hist = agent.add_history('no-comm from {} to {}'.format(commMsg.msg, commMsg.receiver), 0)
                    actions_took[commMsg.sender].append(hist)            


            # 3.0: If agent is done, no need to replan or act
            if agent.is_done(): continue

            # 3. REPLAN if needed
            replan = agent.replan_q()
            if  replan or world_changed or len(diffs) > 0: # If we do not include world_changed, then does not seek for "better" plan
                verbose = 0

                # Used for debugging re-planning
                # if world_changed and not replan:
                #     self.log.info("Replanning Agent {} due to incoming message!!".format(agent.name))
                #     verbose = 10

                if agent.replan(stuck=replan, verbose=verbose):
                    hist = agent.add_history('replan', self.real_world.COST_REPLAN)
                    actions_took[agent_name].append(hist)
                    agent.cur_step = 0
                    agent.times_replanned += 1
                # If replan returns false, then plan was not updated
            
            # 4: Agent takes action
            try:
                self.log.info(('cur_action: ', agent.get_cur_action()))
            except IndexError: 
                print("Agent: {}", agent)
                raw_input("...")

            new_world = act(self.real_world, agent.get_cur_action())
            assert(new_world != None), "Real world:\n{}\nAgent {}'s world:\n{}".format(print_board_str(self.real_world), agent.name, print_board_str(agent.mental_world))
            assert(new_world != False), "Real world:\n{}\nAgent {}'s world:\n{}".format(print_board_str(self.real_world), agent.name, print_board_str(agent.mental_world))
            self.real_world = new_world

            # Step Agent                
            hist = agent.step(self.real_world, out_commMsgs)
            actions_took[agent_name].append(hist)
            

            
        self.communications = {}
        self.flush_communications()
        self.time += 1
        self.log.info("Timestep: {}")
        self.log.info("Communications: {}")

        return (self.real_world, actions_took)


    # def append_communications(self, messages):
    #     Simulation.append_dict(self.comm_buff, messages)

    def flush_communications(self):
        self.communications = []
        self.communications += self.comm_buff
        self.comm_buff = []

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
        actions = solution.get_actions()
        states = solution.get_states()
        if cur_step == len(actions):
            print("Done")
            agent.done = True
            agent.add_history('done', 0)
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
                agent.add_history('None', sys.maxint)
                agent.done = True
                return None

            agent.set_solution(result)
            agent.cur_step = 0
            agent.global_step += 1
            agent.add_history('replan', 1)
            return (self.real_world, step_info)

        else:
            # 4: (if not replan) Agent takes action
            print('cur_action: ', cur_action)
            self.real_world = act(self.real_world, cur_action)
            agent.mental_world = act(agent.mental_world, cur_action)

            agent.add_history(cur_action, self.real_world.cost_func(self.real_world, cur_action))

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
            if not agent.success:
                to_return.append(sys.maxint)
            else:
                to_return.append(sum(action[2] for action in agent.get_histories()))
        return to_return

    def get_total_cost(self):
        return sum(self.cost_p_agent())

    def total_observations(self):
        return sum([len(agent.observations) for agent in self.agents.values()])

    def total_messages_sent(self):
        return sum([len(agent.sent_msgs) for agent in self.agents.values()])

    def total_messages_voided(self):
        return sum([len(agent.voided_msgs) for agent in self.agents.values()])

    def total_replans(self):
        return sum([agent.times_replanned for agent in self.agents.values()])
    
    def total_steps(self):
        return sum([len(agent.get_histories()) for agent in self.agents.values()])

    def get_summary(self, cost=True, cost_bd=False, obs=False, comm=False, void=False, planner=False):
        to_return = "\nSimulation Summary for Problem:{} with AgentType:{}\n".format(
            self.real_world.name, self.AgentType)
        if planner:
            to_return += "Planner: {}\n".format(self.planner_name)
        if cost:
            to_return += "\tTotal Cost: {}\n".format(self.get_total_cost())
        if cost_bd:
            to_return += "\tCost Breakdown: {}\n".format(self.cost_p_agent())
        if obs:
            to_return += "\tTotal Observations: {}\n".format(self.total_observations())
        if comm:
            to_return += "\tMessages Communicated: {}\n".format(self.total_messages_sent())
        if void:
            to_return += "\tMessages Voided: {}".format(self.total_messages_voided())

        return to_return

    def write_to_file(self):
        # Output a file of name: simulation.name.actions
        # The number of columns = the number of agents
        hist_file = "logs/HIST_{}_.actions".format(self.AgentType)
        cur_file = "logs/CUR_{}_.actions".format(self.AgentType)
        f = open(cur_file, 'w')
        hf = open(hist_file, 'a')

        to_write = ""
        for agent_name in self.agents.keys():
            to_write += agent_name + "\t"
        to_write += '\n'

        idx = 0
        while any([idx < len(a.get_histories())for (an, a) in self.agents.items()]):
            for (an, a) in self.agents.items():
                l = str(a.get_histories()[idx]) if idx < len(a.get_histories()) else "None"
                to_write += l + "\t"
            idx += 1
            to_write += '\n'

        f.write(to_write)
        hf.write("Problem Summary for {}\n".format(self.real_world.name))
        hf.write(to_write)

    @staticmethod
    def write_to_file(PROBLEM, simulations):
        file_name = "logs/PROBLEM_{}.sims".format(PROBLEM.name)
        f = open(file_name, 'w')

        for sim in simulations:
            f.write("{}\t\t".format(sim.AgentType))

        f.write('\n')
        
        for agent_name in PROBLEM.goals.keys():
            f.write(agent_name + '\n')
            idx = 0
            while any([idx < len(sim.agents[agent_name].get_histories()) for sim in simulations]):
                for sim in simulations:
                    h = sim.agents[agent_name].get_histories()
                    if idx < len(h):
                        f.write("{}\t{}\t{}".format(*h[idx]))
                    else:
                        f.write("None\tNone\tNone")
                    f.write("\t")
                f.write("\n")
                idx += 1


