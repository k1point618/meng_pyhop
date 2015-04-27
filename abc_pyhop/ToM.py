import models
import copy
import solution

class Plan(object):

    def __init__(self, self_name, actions, states):
        self.name = self_name
        self.actions = actions
        self.states = states
        self.idx = 0
        self.done = False
        self.likelihood = None

    def get_actions(self):
        return self.actions

    def get_likelihood(self):
        return self.get_likelihood

    def set_likelihood(self, prob):
        self.likelihood = prob

    def step_back(self):
        self.idx -= 1
        if self.idx < 0:
            self.idx = 0
        self.done = False
        return

    def step(self):
        if self.done:
            return

        self.idx += 1

        if self.idx == len(self.actions):
            self.done = True
        
    def get_projected_cost(self, world):
        return sum([world.cost_func(world, a) for a in self.actions[self.idx:]])

    # Return the probability of observing loc at idx
    def get_obs_prob(self, loc, idx):
        if idx <= 0:
            return 0.5
        if idx > len(self.states):
            idx = len(self.states)
        print("Get_obs_prob for loc:{} and idx:{}".format(loc, idx))
        print(self.states[idx-1].at)
        return int(self.states[idx-1].at[self.name] == loc)


# A distribution of minds
class ToM(object):

    def __init__(self, self_name, other_name, other_solution, world):
        self.name = self_name, 
        self.other_name = other_name
        self.agent_minds = {}
        self.add_solutions(other_solution) # World is the starting

    def add_solutions(self, other_solution, p_factor=1):
        num_plans = other_solution.get_num_opt_plans()
        world = other_solution.problem
        for (actions, states) in other_solution.get_all_plans():
            p = Plan(other_solution.agent, actions, states)
            p.set_likelihood(1.0/num_plans * p_factor)
            self.agent_minds[p] = self.make_agent_model(p, world)

    # Make AgentMind Model for a given plan
    def make_agent_model(self, p, world):   
        teammate = models.AgentMind(self.other_name, copy.deepcopy(world))
        sol = solution.Solution(world, self.name, p.actions, p.states)
        teammate.set_solution(sol)
        return teammate

    def get_num_plans(self):
        return len(self.agent_minds.keys())

    def get_plans(self):
        return self.agent_minds.keys()

    def step(self):
        for plan, teammate in self.agent_minds.items():
            plan.step()
            if not teammate.is_done():
                teammate.mental_world = teammate.states[teammate.cur_step]
                teammate.cur_step += 1
                if teammate.cur_step >= len(teammate.actions):
                    teammate.done = True

    def step_back(self):
        for plan, teammate in self.agent_minds.items():
            plan.step_back()
            teammate.cur_step -= 1
            if teammate.cur_step <= 0:
                teammate.mental_world = teammate.solution.problem
            else:
                teammate.mental_world = teammate.states[teammate.cur_step]
            teammate.done = False
            
    def update_plan_dist(self, old_plan, replacement_sol):
        del self.agent_minds[old_plan]
        self.add_solutions(replacement_sol, p_factor=old_plan.likelihood)

    def get_agent_minds(self):
        return self.agent_minds



