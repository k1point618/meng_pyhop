import Tkinter

class rover_world_gui(Tkinter.Tk):
    def __init__(self,parent, simulation):
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent

        self.simulation = simulation

        self.real_world = simulation.real_world

        self.CUR_COL = real_world.prop['num_col']
        self.CUR_ROW = real_world.prop['num_row']

        self.solutions = None
        self.rovers = []
        self.agent_worlds = {}
        self.agent_solutions = {}

        self.initialize(real_world)

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
        new_world = self.simulation.step()
        self.boardFrame.update_board(new_world)

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

    def initialize_agent_plans(self, rover_name, solution):
        
        scrollbar = Tkinter.Scrollbar(self)
        scrollbar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)

        listBox = Tkinter.Listbox(self)
        listBox.pack(side=Tkinter.LEFT, fill=Tkinter.Y)
        
        # Header Label for agent's name
        # Tkinter.Label(self, text=rover_name).grid(column=self.CUR_COL, row=0)
        listBox.insert(Tkinter.END, rover_name)

        # Show agent's plans
        (plan, states) = solution
        for action in plan:
            # Tkinter.Label(self, text=plan[cur_row-1]).grid(column=self.CUR_COL, row=cur_row)
            listBox.insert(Tkinter.END, action)

        scrollbar.config(command=listBox.yview)

        # self.next_action = Tkinter.StringVar()
        # self.next_action.set(self.cur_actions[0])
        # label_next_action = Tkinter.Label(self, textvariable=self.next_action)
        # label_next_action.grid(column=CUR_COL, row=0)


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
                self.board_var[(i, j)].set("|\t|")
                label = Tkinter.Label(self, textvariable=self.board_var[(i, j)], 
                    text="empty", fg='black', bg='gray',anchor=Tkinter.CENTER, height=4)
                label.grid(column=j, row=i, sticky='EWSN')

        # Add objects onto the board
        for (obj, loc) in world.at.items():
            cur_x, cur_y = world.loc[loc]
            self.board_var[(cur_x, cur_y)].set(obj)

    def update_board(self, world):

        # Create widgets for the board
        num_col = world.prop['num_col']
        num_row = world.prop['num_row']
        for i in range(num_row):
            for j in range(num_col):
                self.board_var[(i, j)].set("|\t|")
                
        # Add objects onto the board
        for (obj, loc) in world.at.items():
            cur_x, cur_y = world.loc[loc]
            self.board_var[(cur_x, cur_y)].set(obj)

if __name__ == "__main__":
    app = rover_world_gui(None)
    app.title('my application')
    app.mainloop()