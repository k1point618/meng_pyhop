import Tkinter

class rover_world_gui(Tkinter.Tk):
    def __init__(self,parent,agent_init_world, real_world, solutions):
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.agent_init_world = agent_init_world
        self.real_world = real_world
        self.solutions = solutions
        self.cur_solution_idx = 0
        self.cur_actions, self.cur_states = self.solutions[self.cur_solution_idx]
        self.initialize(real_world)

    def initialize(self, world):
        self.grid()

        # Create widgets for the board
        num_col = world.prop['num_col']
        num_row = world.prop['num_row']
        self.board_var = {}
        for i in range(num_row):
            for j in range(num_col):
                self.board_var[(i, j)] = Tkinter.StringVar()
                self.board_var[(i, j)].set("|\t|")
                label = Tkinter.Label(self, textvariable=self.board_var[(i, j)], 
                    text="empty", fg='black', bg='gray',anchor=Tkinter.CENTER, height=3)
                label.grid(column=j, row=i, sticky='EWSN')

        CUR_ROW=num_row
        # Add objects onto the board
        for (obj, loc) in world.at.items():
            cur_x, cur_y = world.loc[loc]
            self.board_var[(cur_x, cur_y)].set(obj)

        # Add next-button to board
        button_nextstep = Tkinter.Button(self,text=u"Next Step", command=self.NextStep)
        button_nextstep.grid(column=0,row=CUR_ROW,columnspan=3)
        CUR_ROW += 1

        # Labels for showing progress
        self.next_action = Tkinter.StringVar()
        self.next_action.set(self.cur_actions[0])
        label_next_action = Tkinter.Label(self, textvariable=self.next_action)
        label_next_action.grid(column=0, row=CUR_ROW)


        # For Re-sizing
        for i in range(num_col):
            self.grid_columnconfigure(i,weight=1)

        self.resizable(True,False)

    def NextStep(self):
        pass

    def OnButtonClick(self):
        print "You clicked the button !"
        self.board_var[(0, 0)].set("change")

    def OnPressEnter(self,event):
        print "You pressed enter !"

    def set_solutions(self, solutions):
        this.solutions = solutions

if __name__ == "__main__":
    app = rover_world_gui(None)
    app.title('my application')
    app.mainloop()