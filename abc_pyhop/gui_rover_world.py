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
        self.agent_worlds = {}
        self.agent_solutions = {}

        self.initialize(simulation.real_world)

    def add_rover(self, rover_name, rover_world, solution): # Takes in 1 solution
        self.rovers.append(rover_name)
        self.agent_worlds[rover_name] = rover_world
        self.agent_solutions[rover_name] = solution

        self.actionFrame.initialize_agent_plans(rover_name, solution)


    def initialize(self, world):
        self.boardFrame = BoardFrame(self, world)
        self.boardFrame.pack(side=Tkinter.LEFT)

        self.actionFrame = AgentActionsFrame(self)
        self.actionFrame.pack(side=Tkinter.LEFT)

        # Add next-button to board
        self.nextButton = Tkinter.Button(self,text=u"Next", command=self.NextStep)
        self.nextButton.pack(side=Tkinter.BOTTOM)

        
        # For Re-sizing
        for i in range(self.CUR_COL):
            self.grid_columnconfigure(i,weight=1)

        self.resizable(True,False)

    def NextStep(self):
        for agent in self.simulation.real_world.goals.keys():
            (new_world, new_solution) = self.simulation.step(agent=agent)

            # Update Board
            self.boardFrame.update_board(new_world)
            
            # If had to re-plan, then refresh actions list.
            if new_solution:
                self.actionFrame.set_actions(agent, self.simulation.solutions[agent])

            # Update Actions
            cur_step = self.simulation.cur_steps[agent]
            self.actionFrame.set_cur_action(agent, cur_step)

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
        Tkinter.Frame.__init__(self, parent, background="blue", height=100)
        # self.initialize_agent_plans('none', (['test'], ['test'])) # Emmpty one
        self.listBoxes = {}


    def initialize_agent_plans(self, rover_name, solution):
        
        # Create List Box Object
        listBox = Tkinter.Listbox(self, height=40, exportselection=0)
        listBox.pack(side=Tkinter.LEFT, fill="both", expand=True)
        self.listBoxes[rover_name] = listBox

        self.set_actions(rover_name, solution)


    def set_actions(self, rover_name, solution):
        lb = self.listBoxes[rover_name]
        # clear items
        lb.delete(0, Tkinter.END)
        lb.insert(Tkinter.END, rover_name)

        # Show agent's plans
        (plan, states) = solution
        for action in plan:
            # Tkinter.Label(self, text=plan[cur_row-1]).grid(column=self.CUR_COL, row=cur_row)
            lb.insert(Tkinter.END, action)


    def set_cur_action(self, rover_name, idx):
        lb = self.listBoxes[rover_name]
        print("cur selection: ", lb.curselection())
        if len(lb.curselection()) != 0:
            lb.selection_clear(lb.curselection())
        print("*** Clearning Selections... ***")
        print("*** Setting new selection by index: ", idx)
        lb.selection_set(idx)


# For the main board frame (Top left)
class BoardFrame(Tkinter.Frame):
    def __init__(self, parent, world):
        Tkinter.Frame.__init__(self, parent, background="black")
        self.grid()
        self.initialize_board(world)


    def initialize_board(self, world):
        # Create widgets for the board
        num_col = world.prop['num_col']
        num_row = world.prop['num_row']
        self.board_var = {}
        for i in range(num_row):
            for j in range(num_col):
                self.board_var[(i, j)] = Tkinter.StringVar()
                self.board_var[(i, j)].set("[\t]")
                label = Tkinter.Label(self, textvariable=self.board_var[(i, j)], 
                    text="empty", fg='black', bg='gray',anchor=Tkinter.CENTER, height=4)
                label.grid(column=j, row=i, sticky='EWSN')

        # Add objects onto the board
        for (obj, loc) in world.at.items():
            cur_x, cur_y = world.loc[loc]
            self.board_var[(cur_x, cur_y)].set([obj])

    def update_board(self, world):

        # Create widgets for the board
        num_col = world.prop['num_col']
        num_row = world.prop['num_row']

        occupied = {}
        for (thing, loc) in world.at.items():
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
                        self.board_var[(i, j)].set("[\t]")
                    else:
                        self.board_var[(i, j)].set("[X]\t")
                idx += 1
                
        # # Add objects onto the board
        # for (obj, loc) in world.at.items():
        #     cur_x, cur_y = world.loc[loc]
        #     self.board_var[(cur_x, cur_y)].set(obj)



if __name__ == "__main__":
    app = rover_world_gui(None)
    app.title('my application')
    app.mainloop()