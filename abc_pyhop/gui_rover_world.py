import Tkinter
import time
import thread
import models
"""
Top Level Gui: Shows everything
"""
class rover_world_gui(Tkinter.Tk):
    def __init__(self,parent, simulation):
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.running = None
        self.simulation = simulation

        self.real_world = simulation.real_world

        self.CUR_COL = simulation.real_world.prop['num_col']
        self.CUR_ROW = simulation.real_world.prop['num_row']

        # self.agent_worlds = {}
        self.agent_solutions = {}
        self.agent_planTrees = {}
        self.initialize(simulation.real_world)

    def initialize(self, world):
        # Add next-button to board
        self.leftControls = ControlsFrame(self, world)
        self.leftControls.pack(side=Tkinter.LEFT)

        self.boardFrame = BoardFrame(self, world)
        self.boardFrame.pack(side=Tkinter.LEFT)

        self.actionFrame = AgentActionsFrame(self)
        self.actionFrame.pack(side=Tkinter.LEFT)

        self.tomFrame = AgentToMFrame(self)
        self.tomFrame.pack(side=Tkinter.LEFT)

        # For Re-sizing
        for i in range(self.CUR_COL):
            self.grid_columnconfigure(i,weight=1)

        self.resizable(True,False)

    def add_agent(self, agent): # Takes in 1 solution
        self.agent_solutions[agent.get_name()] = agent.get_solution()
        self.agent_planTrees[agent.get_name()] = agent.get_planTree()

        self.actionFrame.initialize_agent_plans(agent, agent.get_planTree())

        # Add Button in control panel if the agent has a ToM Model
        self.leftControls.add_button(agent.get_name())

    def NextStep(self):

        # For each agent, calls step() on simulaiton and then update the world.
        for (agent_name, agent) in self.simulation.agents.items():
            result = self.simulation.step(agent_name=agent_name)

            if result == None:
                self.actionFrame.set_actions(agent_name, None)
                return

            (new_world, step_info) = result
            if agent.is_done():
                self.boardFrame.append_info("{}: agent({}) is done."
                    .format(agent.get_global_step(), agent.get_name()))
            else:
                # Update Board
                ste
                self.boardFrame.update_board(new_world)
                self.boardFrame.append_info("{}: agent({}) performed action({})"
                    .format(agent.get_global_step(), agent.get_name(), step_info['cur_action']))

                # If had to re-plan, then refresh actions list.
                if step_info['replan']:
                    self.actionFrame.set_actions(agent_name, agent.get_solution())
                    self.boardFrame.append_info("{}: agent({}) had to replan."
                        .format(agent.get_global_step(), agent.get_name()))

                # Update Actions
                cur_step = agent.get_cur_step()
                self.actionFrame.set_cur_action(agent_name, cur_step)

    # Returns True if all done for a single step of all-agents
    def NextStepAll(self):
        results = self.simulation.step_all()
        
        if results == True: # All done
            print('All done')
            return True


        (new_world, histories_by_agent) = results        

        # Update Board
        self.boardFrame.update_board(new_world)

        # Append to Activities Log
        for (agent_name, histories) in histories_by_agent.items():
            for hist in histories:
                self.boardFrame.append_info("{}: agent({}) performed action {} cost {}"
                        .format(hist[0], agent_name, hist[1], hist[2]))
            # update actions column
            self.actionFrame.set_actions(agent_name, self.simulation.agents[agent_name].get_solution())
            self.actionFrame.set_cur_action(agent_name, self.simulation.agents[agent_name].cur_step)
            self.actionFrame.set_cur_status(agent_name, self.simulation.agents[agent_name])

        # Update ToM Model
        self.tomFrame.updateContent(self.simulation)

        self.update()
        return False


    # Automatically runs the entire simulation
    def SimulateAll(self):
        def runAll():
            while not self.NextStepAll():
                self.update()
                time.sleep(0.1)
        self.running = thread.start_new_thread(runAll, ())


    # Add-content for showing the ToM Frame for a given agent
    def ShowToM(self, agent_name):
        print "Showing ToM Panel for agent {}".format(agent_name)
        self.tomFrame.setContent(agent_name, self.simulation.agents[agent_name])

    def OnButtonClick(self):
        print "You clicked the button !"
        self.board_var[(0, 0)].set("change")


    def OnPressEnter(self,event):
        print "You pressed enter !"


class ControlsFrame(Tkinter.Frame):
    def __init__(self, parent, world):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.nextButton = Tkinter.Button(self,text=u"Next", command=parent.NextStepAll)
        self.nextButton.pack(side=Tkinter.TOP)

        self.runButton = Tkinter.Button(self,text=u"StepAll", command=parent.SimulateAll)
        self.runButton.pack(side=Tkinter.TOP)

    # Add button for showing the ToM model of an agent
    def add_button(self, agent_name):
        button = Tkinter.Button(self, text=agent_name, command=lambda: self.parent.ShowToM(agent_name))
        button.pack(side=Tkinter.TOP)


# For the main board frame Middle Column: Has Board, Activity Log
class BoardFrame(Tkinter.Frame):
    def __init__(self, parent, world):
        Tkinter.Frame.__init__(self, parent)
        self.grid()
        self.info = Tkinter.StringVar()
        self.initialize_board(world)

    def set_info(self, text):
        print("*** Updating info to {} ****".format(text))
        self.info.set("INFO: " + text)

    def append_info(self, text):
        self.info_list.insert(0, text)

    def initialize_board(self, world):
        num_col = world.prop['num_col']
        num_row = world.prop['num_row']
        self.board_var = {}
        self.board_frames = {}
        self.board_labels = {}
        
        self.label2 = Tkinter.Label(self, text="Real World State", justify=Tkinter.LEFT)
        self.label2.grid(column=0, row=0, columnspan=num_col)

        # Create widgets for the board
        for i in range(num_row):
            for j in range(num_col):
                f = Tkinter.Frame(self, borderwidth=1, relief=Tkinter.SOLID)
                self.board_frames[(i, j)] = f
                self.board_var[(i, j)] = Tkinter.StringVar()
                self.board_var[(i, j)].set("[   ]")
                label = Tkinter.Label(f, textvariable=self.board_var[(i, j)], 
                    fg='black', bg='white', height=2, width=3)
                label.pack(side=Tkinter.LEFT, fill=Tkinter.BOTH, expand=1)
                self.board_labels[(i, j)] = label
                f.grid(column=j, row=i+1, sticky='EWSN')
        self.update_board(world)

        # Add info at the bottom 
        self.label2 = Tkinter.Label(self, text="Activities Log", justify=Tkinter.LEFT)
        self.label2.grid(column=0, row=num_row+1, columnspan=num_col)

        self.info_list = Tkinter.Listbox(self, height=10, width=40, exportselection=0)
        self.info_list.grid(column=0, row=num_row+2, columnspan=num_col)

    def update_board(self, world):

        # Create widgets for the board
        num_col = world.prop['num_col']
        num_row = world.prop['num_row']

        occupied = {}
        for (thing, loc) in world.at.items():
            if loc != None:
                (i, j) = world.loc[loc]
                if((i, j) in occupied):
                    occupied[(i, j)] += "&" + str(thing)
                else:
                    occupied[(i, j)] = str(thing)

        for i in world.cost.keys():
            if world.cost[i] > world.MAX_COST:
                occupied[world.loc[i]] = "X"

        idx = 1
        for i in range(num_row):
            for j in range(num_col):

                # Set text color to black
                self.board_labels[(i, j)].config(fg='black')

                # Put down colors for location
                if (world.cost[idx] < world.MAX_COST):
                    # self.board_var[(i, j)].set("%.2f" % round(world.cost[idx],2))
                    self.board_var[(i, j)].set('')
                    g_scale = hex(int(15 - float(world.cost[idx]) / world.MAX_COST * 15))[2:]
                    self.board_labels[(i, j)].config(bg='#' + 6*'{}'.format(g_scale))
                # else:
                #     self.board_var[(i, j)].set("X")
                
                if (i, j) in occupied:
                    self.board_var[(i, j)].set(occupied[(i, j)])
                    if 'L' in occupied[(i, j)]:
                        self.board_labels[(i, j)].config(bg='#79A7BD')
                    elif 'G' in occupied[(i, j)]:
                        self.board_labels[(i, j)].config(bg='#FF704D')
                    elif 'S' in occupied[(i, j)]:
                        self.board_labels[(i, j)].config(bg='#B88D62')
                    elif 'R' in occupied[(i, j)]:
                        self.board_labels[(i, j)].config(bg='#8FB26B')
                    elif 'X' in occupied[(i, j)]:
                        self.board_labels[(i, j)].config(bg='black')
                    elif 'A' in occupied[(i, j)]:
                        self.board_labels[(i, j)].config(fg='white')                        
                        self.board_labels[(i, j)].config(bg='blue')
                    else: 
                        pass
                        # self.board_labels[(i, j)].config(bg='white')
                idx += 1


# For the actions Frame (right of the board)
class AgentActionsFrame(Tkinter.Frame):
    def __init__(self, parent):
        Tkinter.Frame.__init__(self, parent, background="blue")
        # self.initialize_agent_plans('none', (['test'], ['test'])) # Emmpty one
        # self.listBoxes = {}
        self.agent_columns = {}

    def initialize_agent_plans(self, agent, planTree=None):
        
        # Create a column fro each new agent
        agent_column = AgentColumnFrame(self, agent, planTree, height=40, width=30)
        agent_column.pack(side=Tkinter.LEFT)
        self.agent_columns[agent.name] = agent_column

    def set_actions(self, rover_name, solution):
        self.agent_columns[rover_name].set_actions(solution)

    def set_cur_action(self, rover_name, idx):
        self.agent_columns[rover_name].set_cur_action(idx)

    def set_cur_status(self, rover_name, agent):
        self.agent_columns[rover_name].set_cur_status(agent)


class AgentColumnFrame(Tkinter.Frame):
    def __init__(self, parent, agent, planTree, height, width):
        Tkinter.Frame.__init__(self, parent, height=height, width=width)
        self.name = agent.name
        self.agent = agent

        # Create Description about Agent
        self.about_label = Tkinter.Label(self, text="Name: {}\nGoal: {}\nType: {}"
            .format(self.name, self.agent.goal, self.agent.TYPE), justify=Tkinter.LEFT)
        self.about_label.pack(expand=True)
        # Create List Box Object
        self.listBox = Tkinter.Listbox(self, height=20, width=30, exportselection=0)
        self.listBox.pack(side=Tkinter.TOP, expand=True)
        self.set_actions(agent.get_solution())

        # Create the Plan Tree box, which "explains" an agent's curernt aciton
        # self.explanation = Tkinter.StringVar()
        # self.planTreeBox = Tkinter.Label(self, textvariable=self.explanation, height=10, width=30)
        # self.planTreeBox.pack(side=Tkinter.TOP, expand=True)

        # Show costs
        self.cur_status = Tkinter.StringVar()
        fur_cost = sum(agent.mental_world.cost_func(agent.mental_world, a) for a in agent.actions[agent.cur_step:])
        self.cur_status.set("Incurred Cost: {}\nProjected Cost:{}"
                            .format(0, fur_cost))
        self.costLabel = Tkinter.Label(self, textvariable=self.cur_status, width=30, height=2)
        self.costLabel.pack(side=Tkinter.TOP, expand=True)

    def set_actions(self, solution):
        lb = self.listBox
        # clear items
        lb.delete(0, Tkinter.END)
        lb.insert(Tkinter.END, self.name)
        lb.selection_set(0)

        if solution == None:
            lb.insert(Tkinter.END, "No Solution Found")
            return
        # Show agent's plans
        for action in solution.get_actions():
            # Tkinter.Label(self, text=plan[cur_row-1]).grid(column=self.CUR_COL, row=cur_row)
            lb.insert(Tkinter.END, action)

    def set_cur_action(self, idx):
        lb = self.listBox
        if len(lb.curselection()) != 0:
            lb.selection_clear(lb.curselection())
        lb.selection_set(idx)

        # Update explanation box
        # if idx == 0 or self.agent.planTree == None:
        #     self.explanation.set("")
        # else:
        #     # Explain the current action node
        #     action_node = self.agent.get_planTree().get_action_nodes()[idx-1]
        #     exp = action_node.name
        #     cur_node = action_node
        #     while cur_node.parent != None:
        #         cur_node = cur_node.parent
        #         exp = str(cur_node.name) + "\n" + str(exp)
        #     self.explanation.set(exp)

    def set_cur_status(self, agent):
        # Get Current Cost
        hist_cost = sum(action[2] for action in agent.get_histories())
        fur_cost = sum(agent.mental_world.cost_func(agent.mental_world, a) for a in agent.actions[agent.cur_step:])
        self.cur_status.set("Incurred Cost: {} \nProjected Cost:{}"
                            .format(hist_cost, \
                                fur_cost))


# Shows the ToM Model for 1 agent at a time
class AgentToMFrame(Tkinter.Frame):
    def __init__(self, parent):
        Tkinter.Frame.__init__(self, parent)
        self.cur_agent_name = None
        self.headerLabel = None
        self.plansFrame = None

    # Set the content for a given agent 
    def setContent(self, agent_name, agent_obj):
        # # Check if frame already displays the correct info
        # if self.cur_agent_name == agent_name:
        #     return

        # TODO: Should probably Clear current frame
        if self.plansFrame != None:
            self.plansFrame.pack_forget()
        if self.headerLabel != None:
            self.headerLabel.pack_forget()

        # Check if agent has ToM Mental Model
        if not isinstance(agent_obj, models.AgentToM):
            # Agent doesn't have ToM Model. Nothing to Show. 
            return

        # Show mental model of teammate.
        teammateToM = agent_obj.ToMs.values()[0] # RIght now: showing 1 teammate
        
        # TODO: Solution needs to have a funciton for : Get num_plans
        # TODO: Solution needs to keep track of .selected_plan = (actions, states)
        teammate_plans = teammateToM.get_plans()


        # Header label
        self.headerLabel = Tkinter.Label(self, text="ToM({} --> {})\nNum_Plans:{}"
            .format(agent_name, teammateToM.other_name, teammateToM.get_num_plans()), 
            justify=Tkinter.LEFT)
        self.headerLabel.pack(expand=True, side=Tkinter.TOP)

        # Show plans
        self.plansFrame = PlansFrame(self, agent_name, teammateToM.other_name, teammate_plans)
        self.plansFrame.pack(side=Tkinter.TOP)

        self.cur_agent_name = agent_name
        return

    # Called after each Step to update in case mental model changes
    def updateContent(self, simulation):
        if self.cur_agent_name == None:
            return

        self.setContent(self.cur_agent_name, simulation.agents[self.cur_agent_name])
        # self.plansFrame.updateSelection(simulation)


# Plans Frame are the parallel plans in a ToMFrame
class PlansFrame(Tkinter.Frame):
    def __init__(self, parent, agent_name, teammate_name, teammate_plans):
        Tkinter.Frame.__init__(self, parent)

        self.teammate_name = teammate_name
        self.agent_name = agent_name
        self.num_plans = len(teammate_plans)
        self.listBoxes = []
        for (i, plan) in enumerate(teammate_plans):
            actions = plan.get_actions()

            # Create List Box Object
            lb = Tkinter.Listbox(self, height=20, width=20, exportselection=0)
            lb.pack(side=Tkinter.LEFT, expand=True)
            lb.insert(Tkinter.END, "Likelihood:{}".format(plan.likelihood))
            lb.selection_set(plan.idx)

            self.listBoxes.append(lb)
            # Fill the listBox with actions
            for a in actions:
                lb.insert(Tkinter.END, a)

    # def updateSelection(self, simulation):
    #     teammateMind = simulation.agents[self.agent_name].ToMs[self.teammate_name]
    #     for i in range(self.num_plans):
    #         if len(self.listBoxes[i].curselection()) != 0:
    #             self.listBoxes[i].selection_clear(self.listBoxes[i].curselection())
    #         self.listBoxes[i].selection_set(teammateMind.plans[i].idx)



if __name__ == "__main__":
    app = rover_world_gui(None)
    app.title('my application')
    app.mainloop()