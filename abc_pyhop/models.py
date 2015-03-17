"""
Mental Models for agents
"""
import copy, sys
from random_rovers_world import *
from plantree import *

class AgentMind(object):
    """
    All agent should have
        - a name
        - A view of the world
        - An Idea of its solution, which should include both plan (linear or a planTree)
            and sequence of states
        - It's current position in the plan
        - A history of past steps
    """
    def __init__(self, name, world):
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

    def set_solution(self, solution):
        print("set solution", solution)
        if solution == False or solution == None:
            # no solution found
            self.add_history(('done', sys.maxint))
            self.done = True
            self.success = False
            return
        if isinstance(solution, PlanNode):
            print("solution is a planNode")
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
        cur_world = copy.deepcopy(self.mental_world)
        # The agent re-plans when the pre-conditions for any of the future actions is violated
        for step_idx in range(self.cur_step, len(self.actions)):
            cur_action = self.actions[step_idx]
            cur_world = act(cur_world, cur_action)
            if cur_world == False:
                print('Agent Type: {}; must replan!!!!'.format(type(self)))
                return True
        return False


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

        print_board(self.mental_world)
        return loc_diff#, #at_diff # TODO: also include other differences inthe observation.

    @staticmethod
    def visible(A, B, world, range=2):
        a_x, a_y = world.loc[A]
        b_x, b_y = world.loc[B]
        return((abs(a_x - b_x)**2 + abs(a_y - b_y)**2) <= range)
    
    # Process communication by updating agent's mental_world
    # Return the set of differences
    # Reminder: Also update agent's mental_world
    def incoming_comm(self, communication):
        print("Agent {} is handling incomming communications".format(self.name))

        if (self.name not in communication.keys()) or len(communication[self.name]) == 0:
            print("\tNothing was communicated to agent {}".format(self.name))
            return []

        # TODO: given communication, return a set of differences that are new
        # NOTE: assume only location-availability information is given
        loc_diff = []
        inc_diff = communication[self.name]
        print("\t incomming messages: {}".format(inc_diff))

        for (loc, avail) in inc_diff:
            if self.mental_world.loc_available[loc] != avail:
                loc_diff.append((loc, avail))
                self.mental_world.loc_available[loc] = avail

        return loc_diff



class AgentFullComm(AgentMind):
    def __init__(self, name, world, args=[]):
        super(AgentFullComm, self).__init__(name, world)
        self.TYPE = 'FullComm'

    # Given the set of differences observed from environment and communication, 
    # Determine what and to-whom to communicate to.
    # In this Agent Type, we communicate every difference to all other agents
    def communicate(self, diffs):
        print("Agent {} communicates ... {}".format(self.name, diffs))
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
        print("Agent {} communicates ... None".format(self.name))
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
        msg = {}
        for diff in diffs:
            for (teammate_name, teammate) in self.teammates.items():
                print("Agent {} decides to communicate <{}> to teammate: {}"
                    .format(self.name, diff, teammate_name))
                # Assuming that the teammate has already completed the current step
                # because the message doesn't get delivered until the next timestep.

                # If we communicate
                cost_comm = self.comm_cost(teammate, diff)

                # If we don't communicate
                cost_no_comm = self.no_comm_cost(teammate, diff)

                if cost_comm <= cost_no_comm:
                    # Send message
                    if teammate.name in msg:
                        msg[teammate.name] += diff
                    else:
                        msg[teammate.name] = [diff]
                else:
                    # Do not send
                    pass

        return msg
    """
    other: a teammate's mental model
    """
    def comm_cost(self, other, diff):
        print("Evaluating the cost IF we were to communicate")
        to_return = 1 # Cost of comm
        teammate = copy.deepcopy(other)
        teammate.cur_step = self.cur_step + 1

        # Pretend to send message and update teammate's world
        msg = {}
        msg[teammate.name] = [diff]
        teammate.incoming_comm(msg)

        # Pretend to re-plan with new info # no need to check for re-plan
        new_cost_to_finish = self.ex_cost(teammate.mental_world, teammate)

        to_return += new_cost_to_finish
        print("The cost of communicating is {} + {} = {}".format(1, new_cost_to_finish, to_return))
        return to_return


    """
    other: a teammate's mental model
    """
    def no_comm_cost(self, other, diffs):
        # TODO Implement what would happen if we do not communicate.
        return 100000


    def ex_cost(self, world, agent):
        print("Evaluating the remainingcost for agent {}",format(agent.name))
        solutions = pyhop(world, agent.name, plantree=True)
        print("found solutions: {}".format(solutions))
        return solutions[0].cost

            
    # Process communication by updating agent's mental_world
    # Return the set of differences
    # In this agent type, we also perform plan recognition and update our belief of 
    # our teammate's world.
    def incoming_comm(self, communication):
        diffs = super(AgentSmartComm, self).incoming_comm(communication)
        # Update belief about Teammate's world
        # TODO: This means that communication should also include "FROM" in addition to "TO"



