import Tkinter

class rover_world_gui(Tkinter.Tk):
    def __init__(self,parent, simulation):
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent

        self.simulation = simulation

        self.real_world = simulation.real_world

        self.CUR_COL = simulation.real_world.prop['num_col']
        self.CUR_ROW = simulation.real_world.prop['num_row']

        self.solutions = None
        self.rovers = []
        # self.agent_worlds = {}
        self.agent_solutions = {}
        self.agent_planTrees = {}
        self.initialize(simulation.real_world)

    def add_agent(self, agent): # Takes in 1 solution
        self.rovers.append(agent.get_name())
        # self.agent_worlds[rover_name] = rover_world
        self.agent_solutions[agent.get_name()] = agent.get_solution()
        self.agent_planTrees[agent.get_name()] = agent.get_planTree()

        self.actionFrame.initialize_agent_plans(agent, agent.get_planTree())


    def initialize(self, world):
        # Add next-button to board
        self.nextButton = Tkinter.Button(self,text=u"Next", command=self.NextStepAll)
        self.nextButton.pack(side=Tkinter.LEFT)

        self.boardFrame = BoardFrame(self, world)
        self.boardFrame.pack(side=Tkinter.LEFT)

        self.actionFrame = AgentActionsFrame(self)
        self.actionFrame.pack(side=Tkinter.LEFT)

        # For Re-sizing
        for i in range(self.CUR_COL):
            self.grid_columnconfigure(i,weight=1)

        self.resizable(True,False)

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

    def NextStepAll(self):
        results = self.simulation.step_all()
        
        if results == True: # All done
            print('All done')
            return 

        (new_world, actions) = results
        
        # Update Board
        self.boardFrame.update_board(new_world)

        for (agent_name, actions) in actions.items():
            for a in actions:
                self.boardFrame.append_info("{}: agent({}) performed action({})"
                        .format(self.simulation.time, agent_name, a))
            # update actions column
            self.actionFrame.set_actions(agent_name, self.simulation.agents[agent_name].get_solution())
            self.actionFrame.set_cur_action(agent_name, self.simulation.agents[agent_name].cur_step)
            self.actionFrame.set_cur_status(agent_name, self.simulation.agents[agent_name])

    def OnButtonClick(self):
        print "You clicked the button !"
        self.board_var[(0, 0)].set("change")


    def OnPressEnter(self,event):
        print "You pressed enter !"

    def set_solutions(self, solutions):
        this.solutions = solutions


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
        Tkinter.Frame.__init__(self, parent, background='yellow', height=height, width=width)
        self.name = agent.name

        # Create List Box Object
        self.listBox = Tkinter.Listbox(self, height=20, width=30, exportselection=0)
        self.listBox.pack(side=Tkinter.TOP, expand=True)
        self.set_actions(agent.get_solution())

        # Create the Plan Tree box
        self.planTreeBox = Tkinter.Label(self, text=str(planTree), height=10, width=30)
        self.planTreeBox.pack(side=Tkinter.TOP, expand=True)

        # Show costs
        self.cur_status = Tkinter.StringVar()
        self.cur_status.set("Cost: {}".format(sum(action[1] for action in agent.get_histories())))
        self.costLabel = Tkinter.Label(self, textvariable=self.cur_status, width=30, height=2)
        self.costLabel.pack(side=Tkinter.TOP, expand=True)

    def set_actions(self, solution):
        lb = self.listBox
        # clear items
        lb.delete(0, Tkinter.END)
        lb.insert(Tkinter.END, self.name)

        if solution == None:
            lb.insert(Tkinter.END, "No Solution Found")
            return
        # Show agent's plans
        (plan, states) = solution
        for action in plan:
            # Tkinter.Label(self, text=plan[cur_row-1]).grid(column=self.CUR_COL, row=cur_row)
            lb.insert(Tkinter.END, action)

    def set_cur_action(self, idx):
        lb = self.listBox
        print("cur selection: ", lb.curselection())
        if len(lb.curselection()) != 0:
            lb.selection_clear(lb.curselection())
        print("*** Clearning Selections... ***")
        print("*** Setting new selection by index: ", idx)
        lb.selection_set(idx)

    def set_cur_status(self, agent):
        # Get Current Cost
        cost = sum(action[1] for action in agent.get_histories())
        self.cur_status.set("Cost: {}".format(cost))


# For the main board frame (Top left)
class BoardFrame(Tkinter.Frame):
    def __init__(self, parent, world):
        Tkinter.Frame.__init__(self, parent, background="black")
        self.grid()
        self.info = Tkinter.StringVar()
        self.initialize_board(world)

    def set_info(self, text):
        print("*** Updating info to {} ****".format(text))
        self.info.set("INFO: " + text)

    def append_info(self, text):
        self.info_list.insert(0, text)

        # prev = self.info.get()
        # self.info.set(prev + "\n" + text)

    def initialize_board(self, world):
        # Create widgets for the board
        num_col = world.prop['num_col']
        num_row = world.prop['num_row']
        self.board_var = {}
        for i in range(num_row):
            for j in range(num_col):
                self.board_var[(i, j)] = Tkinter.StringVar()
                self.board_var[(i, j)].set("[   ]")
                label = Tkinter.Label(self, textvariable=self.board_var[(i, j)], 
                    text="empty", fg='black', bg='gray', height=2)
                label.grid(column=j, row=i, sticky='EWSN')

        self.update_board(world)
        # # Add objects onto the board
        # for (obj, loc) in world.at.items():
        #     cur_x, cur_y = world.loc[loc]
        #     self.board_var[(cur_x, cur_y)].set([obj])

        # Add info at the bottom # TODO: Make this scrollable
        self.info_list = Tkinter.Listbox(self, height=10, width=50, exportselection=0)
        self.info_list.grid(column=0, row=num_row, columnspan=num_col)

        # label=Tkinter.Label(self, textvariable=self.info, justify=Tkinter.LEFT)
        # label.grid(column=0, row=num_row, columnspan=num_col)

    def update_board(self, world):

        # Create widgets for the board
        num_col = world.prop['num_col']
        num_row = world.prop['num_row']

        occupied = {}
        for (thing, loc) in world.at.items():
            if loc != None:
                (i, j) = world.loc[loc]
                if((i, j) in occupied):
                    occupied[(i, j)].append(thing)
                else:
                    occupied[(i, j)] = [thing]

        idx = 1
        for i in range(num_row):
            for j in range(num_col):
                if (i, j) in occupied:
                    self.board_var[(i, j)].set(occupied[(i, j)])
                else:
                    if (world.loc_available[idx]):
                        self.board_var[(i, j)].set("[   ]")
                    else:
                        self.board_var[(i, j)].set("[ X ]")
                idx += 1
                
        # # Add objects onto the board
        # for (obj, loc) in world.at.items():
        #     cur_x, cur_y = world.loc[loc]
        #     self.board_var[(cur_x, cur_y)].set(obj)



if __name__ == "__main__":
    app = rover_world_gui(None)
    app.title('my application')
    app.mainloop()