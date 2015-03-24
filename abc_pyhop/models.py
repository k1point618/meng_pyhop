"""
Mental Models for agents
"""
import copy, sys, logging
from random_rovers_world import *
from plantree import *

END_EXPERIMENT = False
class AgentMind(object):

    def make_logger(self):
        self.log = logging.getLogger('{}.{}'.format(type(self).__name__, self.name))
        self.log.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler('logs/AgentMind_{}.log'.format(self.name))
        formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s(%(lineno)d):%(message)s')
        file_handler.setFormatter(formatter)
        self.log.addHandler(file_handler)

    """
    All agent should have
        - a name
        - A view of the world
        - An Idea of its solution, which should include both plan (linear or a planTree)
            and sequence of states
        - It's current position in the plan
        - A history of past steps
    """
    def __init__(self, name, world, makeLog=True):
        self.name = name
        self.mental_world = copy.deepcopy(world)
        self.goal = world.goals[name]
        self.solution = None
        self.planTree = None
        self.actions = None
        self.states = None
        self.cur_step = 0
        self.global_step = 0
        self.histories = []
        self.done = False
        self.success = False
        if makeLog:
            self.make_logger()

    def set_solution(self, solution):
        self.log.info(("set solution", solution))
        if solution == False or solution == None:
            # no solution found
            self.add_history(('done', sys.maxint))
            self.done = True
            self.success = False
            return
        if isinstance(solution, PlanNode):
            self.log.info("solution is a planNode")
            self.planTree = solution
            self.solution = (solution.get_actions(), solution.get_states())
        else:
            self.solution = solution
        (self.actions, self.states) = self.solution

        if len(self.actions) == 0: # Do nothing
            self.done = True
            self.success = True

    def get_solution(self): 
        if self.solution == None or self.solution[0] == False:
            return None
        return self.solution

    def get_planTree(self): return self.planTree

    def get_cur_step(self): return self.cur_step

    def add_history(self, new_action):
        self.histories.append(new_action)

    def is_done(self): return self.done

    def get_histories(self): return self.histories

    def get_name(self): return self.name

    def get_global_step(self): return self.global_step

    def is_success(self): return self.success

    # Given the set of differences observed from environment and communications, 
    # Determine whether or not to re-plan
    def replan_q(self):
        self.log.info("Agent: {} replan?".format(self.name))
        cur_world = copy.deepcopy(self.mental_world)
        (simulated, end_world, accum_cost) = self.simulate(cur_world, self.actions[self.cur_step:])
        if simulated:
            self.log.info("Simulation success, no need for re-plan. Accum_cost:{}".format(accum_cost))
            return False
        else:
            self.log.info ("Agent: {}; Type: {}; must replan !!!".format(self.name, type(self)))
            return True

    def simulate(self, cur_world, step_actions):
        self.log.info("Simulating Agent {}'s world with actions: {}; world:\n".format(self.name, step_actions, print_board_str(cur_world)))
        accum_cost = 0
        num_steps = 0
        for action in step_actions:
            next_world = act(cur_world, action)
            if next_world == False:
                self.log.info('Simulation failed at step: {} after cost: {}'.format(num_steps, accum_cost))
                return (False, cur_world, accum_cost)
            else:
                cur_world = next_world
                accum_cost += 1 #cost(action)
                num_steps += 1
        return (True, cur_world, accum_cost)


    # Returns the set of observations that is relevatnt to the agent
    # depending on the location of the agent
    # Reminder: Also update agent's mental_world
    # Note: Only looking at location-availability differences and .at[] differences
    def make_observations(self, real_world):

        loc_diff = [] # NOTE TODO: For now it is only location diff
        # at_diff = [] # Note TODO: For now also include object locaitons

        my_l = self.mental_world.at[self.name]
        for l in self.mental_world.loc.keys():
            if AgentMind.visible(my_l, l, real_world, range=2) and self.mental_world.loc_available[l] != real_world.loc_available[l]:
                self.mental_world.loc_available[l] = real_world.loc_available[l]
                loc_diff.append((l, real_world.loc_available[l]))
            
        for (obj, loc) in real_world.at.items():
            if loc != None and AgentMind.visible(my_l, loc, real_world, range=2) and self.mental_world.at[obj] != real_world.at[obj]:
                self.mental_world.at[obj] = real_world.at[obj]
        for (obj, loc) in self.mental_world.at.items():
            if loc != None and AgentMind.visible(my_l, loc, self.mental_world, range=2) and self.mental_world.at[obj] != real_world.at[obj]:
                self.mental_world.at[obj] = real_world.at[obj]

        self.log.info(print_board_str(self.mental_world))
        return loc_diff#, #at_diff # TODO: also include other differences inthe observation.

    @staticmethod
    def visible(A, B, world, range=2):
        a_x, a_y = world.loc[A]
        b_x, b_y = world.loc[B]
        return((abs(a_x - b_x)**2 + abs(a_y - b_y)**2) <= range)
    
    # Returns a simple copy of current agent
    def simple_copy(self):
        other = AgentMind(self.name, copy.deepcopy(self.mental_world), makeLog=False)
        other.goal = self.goal
        other.solution = self.solution
        other.planTree = self.planTree
        other.actions = self.actions
        other.states = self.states
        other.cur_step = self.cur_step
        other.histories = self.histories
        other.done = self.done
        other.success = self.success
        other.log = self.log
        return other
    
    # Process communication by updating agent's mental_world
    # Return the set of differences
    # Reminder: Also update agent's mental_world
    def incoming_comm(self, communication):
        self.log.info("Agent {} is handling incoming communications:\n\t{}".format(self.name, communication))

        if (self.name not in communication.keys()) or len(communication[self.name]) == 0:
            self.log.info("\tNothing was communicated to agent {}".format(self.name))
            return []

        # TODO: given communication, return a set of differences that are new
        # NOTE: assume only location-availability information is given
        loc_diff = []
        inc_diff = communication[self.name]
        self.log.info("\t incomming messages: {}".format(inc_diff))

        for (loc, avail) in inc_diff:
            if self.mental_world.loc_available[loc] != avail:
                loc_diff.append((loc, avail))
                self.mental_world.loc_available[loc] = avail

        self.log.info("Agent {} finished handling incomming communication. New world:\n{}"
            .format(self.name, print_board_str(self.mental_world)))
        self.log.info("returning loc_diff that were realized: {}".format(loc_diff))
        return loc_diff



class AgentFullComm(AgentMind):
    def __init__(self, name, world, args=[]):
        super(AgentFullComm, self).__init__(name, world)
        self.TYPE = 'FullComm'

    # Given the set of differences observed from environment and communication, 
    # Determine what and to-whom to communicate to.
    # In this Agent Type, we communicate every difference to all other agents
    def communicate(self, diffs):
        if len(diffs) == 0 or diffs == None:
            return {}

        self.log.info("Agent {} communicates ... {}".format(self.name, diffs))
        msg = {}
        for agent_name in self.mental_world.goals.keys():
            if agent_name != self.name:
                msg[agent_name] = diffs
        return msg # Communicate All



class AgentNoComm(AgentMind):
    def __init__(self, name, world, args=[]):
        super(AgentNoComm, self).__init__(name, world)
        self.TYPE = 'NoComm'

    # Given the set of differences observed from environment and communication, 
    # Determine what and to-whom to communicate to.
    # In this Agent Type, we do not communicate.
    def communicate(self, diffs):
        self.log.info("Agent {} communicates ... None".format(self.name))
        return {} # No comm



class AgentSmartComm(AgentMind):
    def __init__(self, name, world, args=[]):
        super(AgentSmartComm, self).__init__(name, world)
        self.TYPE = 'SmartComm'
        solutions = args[0] # Assuming that the only input is solutions
        self.teammates = {}
        for a in world.goals.keys():
            if a != self.name:
                teammate = AgentMind(a, copy.deepcopy(world))
                teammate.set_solution(solutions[a]) # <-- The type of solution is the same as the agent's solution type (PlanTree or Linear)
                self.teammates[a] = teammate
                # We want to keep track of each teammate's plan and the relative cost of each plan. 
                # (Later, we might want to add a distribution of solutions?)

    # Given the set of differences observed from environment and communication
    # Determine what and to-whome to communicate to.
    def communicate(self, diffs):
        # For each teammte, compare the expected cost of communicating with not-communicating
        if len(diffs) == 0:
            self.log.info("Agent {} observed no diff, so have nothing to communicate".format(self.name))
            return {}

        msg = {}
        for (teammate_name, teammate) in self.teammates.items():
            
            for diff in diffs:
                self.log.info("AgentSmartComm.communicate ... Should Agent {} communicate <{}> to teammate: {}?"
                    .format(self.name, diff, teammate_name))
                # Assuming that the teammate has already completed the current step
                # because the message doesn't get delivered until the next timestep.

                self.log.info("teammate world:\n{}".format(print_board_str(teammate.mental_world)))
                # If we communicate
                copyA = teammate.simple_copy()
                self.log.info("copyA:\n{}".format(print_board_str(copyA.mental_world)))

                cost_comm = self.comm_cost(copyA, diff)
                self.log.info("copyA after comm_cost:\n{}".format(print_board_str(copyA.mental_world)))

                # If we don't communicate
                copyB = teammate.simple_copy()
                self.log.info("copyB:\n{}".format(print_board_str(copyB.mental_world)))
                cost_no_comm = self.no_comm_cost(copyB, diff)
                self.log.info("copyB after no_comm_cost:\n{}".format(print_board_str(copyB.mental_world)))

                if cost_comm <= cost_no_comm:
                    # Send message
                    self.log.info("Agent {}: decided to COMMUNICATE".format(self.name))
                    raw_input("...")
                    if teammate.name in msg:
                        msg[teammate.name] += diff
                    else:
                        msg[teammate.name] = [diff]
                else:
                    self.log.info("Agent {}: decide to NOT COMM".format(self.name))
                    # Do not send
                    pass

        return msg

    """
    other: a teammate's mental model
    """
    def comm_cost(self, other, diff):
        self.log.info("Evaluating the cost IF we were to communicate")
        to_return = 1 # Cost of comm
        other.cur_step = self.cur_step + 1

        # Pretend to send message and update teammate's world
        msg = {}
        msg[other.name] = [diff]
        other.incoming_comm(msg)

        # Pretend to re-plan with new info # no need to check for re-plan
        self.log.info("Computing expected cost for agent {} to accomplish {}".format(other.name, other.goal))
        new_cost_to_finish = AgentSmartComm.EX_COST(other.mental_world, other)
        self.log.info("The expected cost if we were to communicate is: {}".format(new_cost_to_finish))

        to_return += new_cost_to_finish
        self.log.info("Agent {}: The cost of communicating is {} + {} = {}".format(self.name, 1, new_cost_to_finish, to_return))
        return to_return


    """
    other: a teammate's mental model
    """
    def no_comm_cost(self, other, diff):

        # Then check for point of failure
        self.log.info("Agent {} is simulating agent {}'s world \n{}\n\
            ...for no-comm,\n\
            ...regarding on diffs: {}"
            .format(self.name, other.name, print_board_str(other.mental_world), diff))

        if self.cur_step >= len(other.actions):
            self.log.info("... the other agent should be done. no need for simulation")
            return 0

        other.cur_step = self.cur_step
        other.mental_world = other.states[self.cur_step]
        msg = {}
        msg[other.name] = [diff]
        other.incoming_comm(msg)

        (simulated, world, cost) = other.simulate(copy.deepcopy(other.mental_world), other.actions[self.cur_step:])
        self.log.info("... result -- Simulated: {}; Cost: {}".format(simulated, cost))

        if simulated:
            # if simulated is True, then the cost of the cost for the rest of the plan
            return cost
        else:
            # If simulated is False, then the cost is up to the point of failure 
            # Must re-plan
            replan_cost = AgentSmartComm.EX_COST(world, other)
            self.log.info("... lost-cost: {}".format(cost))
            self.log.info("... replan cost: {}".format(replan_cost))
            raw_input("Simulation failed in simulating no-communication ... ")
            END_EXPERIMENT=True
            return cost + replan_cost

    # Process communication by updating agent's mental_world
    # Return the set of differences
    # In this agent type, we also perform plan recognition and update our belief of 
    # our teammate's world.
    def incoming_comm(self, communication):
        diffs = super(AgentSmartComm, self).incoming_comm(communication)
        # Update belief about Teammate's world
        # TODO: This means that communication should also include "FROM" in addition to "TO"

    @staticmethod
    def EX_COST(world, agent):
        print("AgentSmartComm.EX_COST: computing expected cost of agent {} with goal {} in world \n{}".format(agent.name, agent.goal, print_board_str(world)))
        solutions = pyhop(world, agent.name, plantree=True)
        print("Solutions: {}".format([s.get_actions() for s in solutions]))
        return solutions[0].cost




