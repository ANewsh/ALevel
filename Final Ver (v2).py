import tkinter as tk
import sqlite3
import time
import random
import os

class cell():
    #each cell is it's own object
    def __init__(self, curYInd, curXInd, grid, IsEdge, CellNum, window):
        self.Window = window
        self.__alive = False
        self.mygrid = grid
        self.__Edge = IsEdge
        self.__Goal = False
        self.__Revealed = False
        #I made the maze default to being empty with no pathscc
        self.Xind = curXInd
        self.Yind = curYInd
        self.CellNum = CellNum
        #Locations are kept as attributes
        self.State = "Unchecked"
        self.Distance = 0
    def Condition(self):
        if self.__alive:
            return True
        else:
            return False
        #simple method that returns the condition of the cell
    def HardRez(self):#for cases where i do not need to check
        self.__alive = True
    def Rez(self):
        if not self.__Edge:
            self.__alive = True
        #condition exists for literal edge cases
    def Reveal(self):
        self.__Revealed = True
        if self.__alive:
            self.Window.Dict_lbl[self.CellNum].config(bg = "white")
        else:
            self.Window.Dict_lbl[self.CellNum].config(bg = "black")
            #Calls back to container
    def Hide(self):
        self.__Revealed = False
    def IsRevealed(self):
        return self.__Revealed
    def CanSeeThrough(self):
        if self.__Revealed and self.__alive and not self.__Goal:
            #needed so a wrap around error does not occur so the user cannot "see through" the exit and throught to the opposite side
            return  True
        else:
            return False
        
    def Kill(self):
        self.__alive = False

    def CheckNeighbours(self):
        self.NumAround = 0
        #initial value
        if self.Yind != 0:
            if self.mygrid.Grid[self.Yind - 1][self.Xind ].Condition(): self.NumAround += 1
            if self.Xind != 0:
                if self.mygrid.Grid[self.Yind - 1][self.Xind - 1].Condition(): self.NumAround += 1
            if self.Xind != len(self.mygrid.Grid[self.Yind])-1:
                if self.mygrid.Grid[self.Yind - 1][self.Xind+ 1].Condition(): self.NumAround += 1
        #Checks all the cells above, does not trigger if it is on the top row
        if self.Yind != len(self.mygrid.Grid)-1:
            if self.mygrid.Grid[self.Yind + 1][self.Xind].Condition(): self.NumAround += 1
            if self.Xind != 0:
                if self.mygrid.Grid[self.Yind + 1][self.Xind - 1].Condition(): self.NumAround += 1
            if self.Xind != len(self.mygrid.Grid[self.Yind])-1:
                if self.mygrid.Grid[self.Yind + 1][self.Xind + 1].Condition(): self.NumAround += 1
        #checks all the cells below, again does not trigger if it's on the bottom row
        if self.Xind != 0:
            if self.mygrid.Grid[self.Yind][self.Xind - 1].Condition(): self.NumAround += 1
        if self.Xind != len(self.mygrid.Grid[self.Yind])-1:
            if self.mygrid.Grid[self.Yind][self.Xind + 1].Condition(): self.NumAround += 1
        #checks the cells left and right to the cell    
        return self.NumAround
    def CheckAdjecents(self):
        #only checks directly above, below and beside
        self.NumConnect = 0
        self.DirConnect = []
        #Creates two properties, both of which this method updates but only returns  1
        if self.Yind != 0:
            if self.mygrid.Grid[self.Yind - 1][self.Xind ].Condition():
                self.NumConnect += 1
                self.DirConnect.append('N')
        if self.Yind != len(self.mygrid.Grid)-1:
            if self.mygrid.Grid[self.Yind + 1][self.Xind].Condition():
                self.NumConnect += 1
                self.DirConnect.append('S')
        if self.Xind != 0:
            if self.mygrid.Grid[self.Yind][self.Xind - 1].Condition():
                self.NumConnect += 1
                self.DirConnect.append('W')
        if self.Xind != len(self.mygrid.Grid[self.Yind])-1:
            if self.mygrid.Grid[self.Yind][self.Xind + 1].Condition():
                self.NumConnect += 1
                self.DirConnect.append('E')
        # first layer of each if statement is to stop the cell checking non-existant cells such as places outside the maze
        return self.NumConnect
    def CreateMapping(self):
        self.MapsTo = []
        NumAdjacent = self.CheckAdjecents()
        if NumAdjacent == 2:
            self.Pathtype = 'Vertices'

        elif NumAdjacent == 1:
            self.Pathtype = 'Dead End'
        else:
            self.Pathtype = 'Junction'
        if 'N' in self.DirConnect:
           self.MapsTo.append([self.Yind-1, self.Xind])
        if 'E' in self.DirConnect:
            self.MapsTo.append([self.Yind, self.Xind+1])
        if 'S' in self.DirConnect:
            self.MapsTo.append([self.Yind+1, self.Xind])
        if 'W' in self.DirConnect:
            self.MapsTo.append([self.Yind, self.Xind-1])
        #It's more practical to pass in strings which mean relative positions to the cell instead of coordinates
        #Though DirConnect is not defined here it is always created when the CheckAdjecents method is executed
        return self.MapsTo
    def Enqueued(self,From,Distance):
        self.MappedFrom = From
        self.Distance = Distance + 1
        #As it works cell by cell in a breadth first search, the distance will be the shortest possible distance as all nodes are equidistant
        self.State = 'Queued'
    def GetLocation(self):
        return self.Yind, self.Xind
    def GetCoordinates(self):
        return [self.Yind,self.Xind]
    #though these subroutines seem similar, they exist so that I don't have to format the result for each task so I use two different methods
    def MakeExit(self):
        if self.CheckAdjecents() > 0:

            self.__Goal = True
            self.__alive = True
            return True
        else:
            return False
    def HardExit(self):
        self.__Goal = True
        self.__alive = True
    #similar to above, I use two subroutines which have generally the same effect, but instead if handling the result for each case, I made a new subroutine for each case

class Window:
    global Height ,Length
    def __init__(self, parent):
        self.parent = parent
        self.parent.geometry("1000x1000+100+100")
        self.body = tk.Frame(parent)
        self.UDB = UserDatabase('Users.db')
        self.SDB = ScoreDatabase('Maze_Scores.db')
        #Constructs the data bases, i'm using hard coded values for the names of the databases
        self.body = tk.Frame(self.parent)
        self.body.grid()
        #creates a frame to work on
        self.build_login()
        
    def Clear_Body(self):
        for widget in self.body.winfo_children():
            widget.destroy()
    #subroutine exists as an easy way to clear the body
    
    def build_login(self):
         self.Clear_Body()
         self.CurrentUser = None
         #makes it so that whenever this menu is built, there is no user currently signed in
         self.lbl_username = tk.Label(self.body, text = "username",width='10', height='1')
         self.lbl_password = tk.Label(self.body, text = "password",width='10', height='1')
         self.ent_username = tk.Entry(self.body)
         self.ent_password = tk.Entry(self.body, show = '*')
         self.btn_login = tk.Button(self.body, text="Login", width='10',height = '1', command =lambda: self.LogonRequest_Pressed())
         self.btn_SignUp = tk.Button(self.body, text="Sign Up", width='10',height = '1', command = lambda: self.SignupRequest_Pressed())
         self.btn_ViewScores = tk.Button(self.body, text = "View Leaderboard", width = '20', height='1', command= lambda: self.Build_LeaderBoards())
         #instead of directly executing the buttons purpose I made subroutines to handle to button press
         self.lbl_username.grid(row=0, column=0)
         self.lbl_password.grid(row=1, column=0)
         self.ent_username.grid(row=0, column=1)
         self.ent_password.grid(row=1, column=1)
         self.btn_login.grid(row=2, column=1,columnspan = 2)
         self.btn_SignUp.grid(row=4, column=1,columnspan = 2)

    def Build_Signup(self):
        self.Clear_Body()
        self.lbl_Title = tk.Label(self.body, text = "Please enter a username and password",width='30', height='1')
        self.lbl_username = tk.Label(self.body, text = "username",width='10', height='1')
        self.lbl_password = tk.Label(self.body, text = "password",width='10', height='1')
        self.ent_username = tk.Entry(self.body)
        self.ent_password = tk.Entry(self.body, show = '*')
        self.btn_SignUp = tk.Button(self.body, text="Create account", width='10',height = '1', command = self.CreateAccount)
         
        self.lbl_Title.grid(row=0, column=0, columnspan = 4)
        self.lbl_username.grid(row=1, column=1)
        self.lbl_password.grid(row=2, column=1)
        self.ent_username.grid(row=1, column=2,)
        self.ent_password.grid(row=2, column=2,)
        self.btn_SignUp.grid(row=4, column=2,columnspan = 2)

    def Build_LeaderBoards(self):
        self.Clear_Body()
        self.MyArray = self.SDB.GetScores(self.MazeType)
        self.MyArray = sorted(self.MyArray, key=lambda x: x[2])
        #Gets the 2D array of and sorts it by the value in the third item of each array
        self.Dict_lbl_Position = {}
        self.Dict_lbl_Names = {}
        self.Dict_lbl_Times = {}
        self.Position_Lbl = tk.Label(self.body, bg = 'lightgrey',width = '7',height = '1', text = 'Position', relief = "groove" )
        self.Names_Lbl = tk.Label(self.body, bg = 'lightgrey',width = '10',height = '1', text = 'Names', relief = "groove" )
        self.Times_Lbl = tk.Label(self.body, bg = 'lightgrey',width = '7',height = '1', text = 'time', relief = "groove" )

        self.Position_Lbl.grid(row = 0, column = 0)
        self.Names_Lbl.grid(row=0, column = 1)
        self.Times_Lbl.grid(row=0, column =2)

        for item in range(1,len(self.MyArray)+1):
            #The strange +1 to both parameters in this range statment is so that I can use the value of the iteration more efficiently
            self.Dict_lbl_Position[item] = tk.Label(self.body, bg = 'white',width = '7',height = '2', text = item, relief = "groove")
            self.Dict_lbl_Names[item] = tk.Label(self.body, bg = 'white',width = '10',height = '2', text = self.MyArray[item-1][1], relief = "groove")
            self.Dict_lbl_Times[item] = tk.Label(self.body, bg = 'white',width = '7',height = '2', text = self.MyArray[item-1][2], relief = "groove")

            self.Dict_lbl_Position[item].grid(row = item, column = 0)
            self.Dict_lbl_Names[item].grid(row = item, column = 1)
            self.Dict_lbl_Times[item].grid(row = item, column = 2)
        if self.CurrentUser != None:
            self.Contin = tk.Button(self.body, text = 'Back to Menu', command = lambda: self.BuildMenu())
            self.Contin.grid(columnspan = 2)
        else:
            self.Contin = tk.Button(self.body, text = 'Back to Log in', command = lambda: self.build_login())
            self.Contin.grid(columnspan = 2)
        #If the user is signed in and just finnished a maze, the button will send them back to the maze select menu
        #If they checked the leaderboard without signing in, they will get sent back to the sign in menu, so they cannot attempt a maze without being signed in
    def CreateAccount(self):
        result = self.UDB.Process_signup(self.ent_username.get(), self.ent_password.get())
        #Calls the contained database object which handles all database requests
        #The object does not edit the window at all, it just returns whether or not the query was successful
        #This subroutine handles the window changes
        if result:
            self.Clear_Body()
            self.Sucess = tk.Label(self.body, text = 'Account made sucessfully')
            self.Contin = tk.Button(self.body, text = 'Back to login', command = lambda: self.build_login())
            self.Sucess.grid()
            self.Contin.grid()

            
        else:
            self.Clear_Body()
            self.Failure = tk.Label(self.body, text = 'There was an error creating your account')
            self.Contin = tk.Button(self.body, text = 'Back to sign up', command = lambda: self.Build_Signup())
            self.Failure.grid()
            self.Contin.grid()
                                    
            
    def LogonRequest_Pressed(self):
        #Calls the contained database object which handles all database requests
        #The object does not edit the window at all, it just returns whether or not the query was successful
        #This subroutine handles the window changes, like above
        self.CurrentUser = self.UDB.Process_Login(self.ent_username.get(), self.ent_password.get())
        if self.CurrentUser != None:
            self.Clear_Body()
            self.BuildMenu()
        else:
            self.Clear_Body()
            self.Sucess = tk.Label(self.body, text = 'Account not found')
            self.Contin = tk.Button(self.body, text = 'Back to login', command = lambda: self.build_login())
            self.Sucess.grid()
            self.Contin.grid()
        
    def SignupRequest_Pressed(self):
        #makes it so i can add other methods when this button is pressed, though these are the only two and i could easily clear the body within the build sign up method.
        self.Clear_Body()
        self.Build_Signup()
        
    def BuildMenu(self):
        self.Clear_Body()
        self.randMaze = tk.Button(self.body, text = 'Random maze', command = lambda: self.buildMazeCustomMenu())
        UserStr = "you are signed in as "+self.CurrentUser[1]
        self.Name = tk.Label(self.body, text = UserStr)
        self.Name.grid()
        self.Choice_Dict = {}
        Choices = 1
        for item in os.listdir(__file__.replace(os.path.basename(__file__),"/Mazes")):
            self.Choice_Dict[Choices] = tk.Button(self.body, text = 'Maze '+str(Choices), command = lambda c = Choices: self.buildpresetmaze(c))
            self.Choice_Dict[Choices].grid()
            Choices += 1
            #reguardless of file name, the mazes will be labeled in incrementing values following "Maze"
            #The file names are made so that they relate to the database tables and so that the file access in the operating system will always order them in the same way
        self.LogOut = tk.Button(self.body, text = 'Log out', command = lambda: self.build_login())
        self.randMaze.grid()
        self.LogOut.grid()
    def buildMazeCustomMenu(self):
        self.Clear_Body()
        self.mygrid = grid(self)
        self.GenType = tk.IntVar()
        self.lbl_height = tk.Label(self.body, text = "Maze height(10-30)")
        self.ent_height = tk.Entry(self.body,)
        self.lbl_width = tk.Label(self.body, text = "Maze width (10-50)")
        self.ent_width = tk.Entry(self.body,)
        
        self.Type = tk.Label(self.body, text = "Choose maze type")
        self.MazeStyle1 = tk.Radiobutton(self.body, text = "long straights, Lots of paths, no dead ends", variable = self.GenType, value = 2, padx = 100)
        self.MazeStyle2 = tk.Radiobutton(self.body, text = "Winding paths, more dead ends", variable = self.GenType, value = 3, padx = 100)
        #creates radio buttons
        self.Create = tk.Button(self.body,text = "Create maze", command= lambda: self.buildRandomCustard(self.ent_height.get(),self.ent_width.get(),self.GenType.get()))
        #The maze takes 3 parameters: the two entries and the radio button
        self.lbl_height.grid(row=0,column=0)
        self.ent_height.grid(row=0,column=1)
        self.lbl_width.grid(row=1,column=0)
        self.ent_width.grid(row=1,column=1)
        self.Type.grid(row = 2,column = 0)
        self.MazeStyle1.grid(row=3, column = 1)
        self.MazeStyle2.grid(row=4, column = 1)
        self.Create.grid(row =5, column = 0)
    def buildRandomCustard(self, height, width, type):
        try:
            height = int(height)
            width = int(width)
        except:
            pass
        if isinstance(height,int) and isinstance(width, int)  and height in range(10, 31) and width in range(10, 51):
            self.mygrid.GenerateMaze(height,width,type)
            self.Clear_Body()
            self.buildmaze(0)
        #validates the entries input, the radio buttons can only have two possible values so it does not need validations
        else:
            self.Invalid = tk.Label(self.body, text = "Entered values are not valid")
            self.Invalid.grid(column = 1)
    def buildpresetmaze(self, type):
        self.mygrid = grid(self)
        self.mygrid.CreateDefaultMaze(type)
        self.buildmaze(type)
        #creates grid object which stores the information about the maze
    def buildmaze(self, Type):
        self.MazeType = Type
        self.Clear_Body()
        Length, Height = self.mygrid.GetMazeDimensions()
        self.Dict_lbl = {}
        #dictionary allows me to iterate through something and give each new label a new name on each iteration

        CurrentCell = 0
        for Row in range(Length):
            for cell in range(Height):
                if not self.mygrid.Grid[Row][cell].IsRevealed():
                    self.Dict_lbl[self.mygrid.Grid[Row][cell].CellNum] = tk.Label(self.body, width='2', height='1', borderwidth='1', bg='grey',
                                                          highlightbackground='black', relief="groove")
                else:
                    if self.mygrid.Grid[Row][cell].Condition():
                        self.Dict_lbl[self.mygrid.Grid[Row][cell].CellNum] = tk.Label(self.body, width='2', height='1', borderwidth='1', bg='white',
                                                              highlightbackground='black', relief="groove")
                    else:
                        self.Dict_lbl[self.mygrid.Grid[Row][cell].CellNum] = tk.Label(self.body, width='2', height='1', borderwidth='1', bg='black',
                                                              highlightbackground='black', relief="groove")
                self.Dict_lbl[self.mygrid.Grid[Row][cell].CellNum].grid(row=Row, column=cell)
        if self.MazeType ==0:
            co1, co2 = self.mygrid.GetGoalLocation()
            location = self.AddAI(co1, co2)
        else:
            location = self.mygrid.GetStartLocation()
        self.addplayer(location[0], location[1])
        self.start_btn = tk.Button(self.body,text='start', width = 6, height = 1, command = lambda: self.playgame())
        self.Timer = tk.Label(self.body, text = '0', width = 6, height = 1)
        self.start_btn.grid(columnspan=6, column = 0)
        

        
    def MovePlayer(self, Direction):
        if not self.player.atgoal():
            if Direction == 'w':
                if self.mygrid.Grid[self.player.CurRow - 1][self.player.CurColumn].Condition():
                    self.player.MoveRow(-1)
            elif Direction == 'a':
                if self.mygrid.Grid[self.player.CurRow][self.player.CurColumn - 1].Condition():
                    self.player.MoveColumn(-1)
            elif Direction == 's':
                if self.mygrid.Grid[self.player.CurRow + 1][self.player.CurColumn].Condition():
                    self.player.MoveRow(1)
            elif Direction == 'd':
                if self.mygrid.Grid[self.player.CurRow][self.player.CurColumn + 1].Condition():
                    self.player.MoveColumn(1)
            self.Playerspace.grid(row=self.player.CurRow, column=self.player.CurColumn)
            if not self.player.atgoal():
                self.UpdateVision()
            self.parent.update()
        else:
            self.EndGame()
    def AddAI(self, Row, Cell):
        self.AI = Flooder(self, Row, Cell)
        self.Flood()
        Starters = self.CreateStartLocation()
        Start = random.choice(Starters)
        return Start
    def Flood(self):
        t1 = time.time()
        while not self.AI.IsFlooded():
            self.AI.CheckCurCell()
            self.AI.Move()
        self.parent.update()

    def CreateStartLocation(self):
        PossStart = []
        Dim1, Dim2 = self.mygrid.GetMazeDimensions()
        for row in self.mygrid.Grid:
            for cell in row:
                if cell.Distance == (Dim1+Dim2)/2 and cell.Condition():
                    PossStart.append(cell.GetCoordinates())
        if PossStart == []:
            for row in self.mygrid.Grid:
                for cell in row:
                    if cell.Distance == 10:
                        PossStart.append(cell.GetCoordinates())
        return PossStart
    
    def UpdateTime(self):
        CurTime = time.time()
        self.RecTime = CurTime - self.StartTime
        self.RecTime = round(self.RecTime, 3)
        self.Timer = tk.Label(self.body, text = self.RecTime, width = 6, height = 1)
        if not self.player.atgoal():
            self.parent.after(2, self.UpdateTime)
        self.Timer
    def playgame(self):
        self.start_btn.destroy()
        self.StartTime = time.time()
        self.UpdateTime()
        self.parent.bind('<Key>', self.keypress)
        #sets up an event

    def keypress(self, event):
        event.char = event.char.lower()
        self.MovePlayer(event.char)
        #handles the event

    def BuildEndScreen(self):
        self.Congrats = tk.Label(self.body, width='50', height='1', text='You have completed the maze in')
        self.FinalTime = tk.Label(self.body, width='50', height = '1', text =self.EndTime)
        self.Congrats.grid(row=1, column=1)
        self.FinalTime.grid(row=2, column = 1)
        if self.MazeType != 0:
            self.addscore()
            self.btn_ViewScores = tk.Button(self.body, text = "View Leaderboard", width = '20', height='1', command= lambda: self.Build_LeaderBoards())
            self.btn_ViewScores.grid(row=3,column=1, columnspan = 3)
        self.Retry = tk.Button(self.body, text = 'Back to menu', command = lambda: self.BuildMenu())
        self.Retry.grid(row=4,column=1, columnspan = 3)

    def EndGame(self):
        self.parent.bind('<Key>', lambda key: None)
        self.EndTime = self.Timer['text']
        self.Clear_Body()
        self.BuildEndScreen()

    def addplayer(self, Row, Cell):
        self.player = player(Cell, Row, self)
        #player is a child object
        self.Playerspace = tk.Label(self.body, width='2', height='1', borderwidth='1', bg='magenta',
                                    highlightbackground='black', relief="groove")
        self.Playerspace.grid(row=self.player.CurRow, column=self.player.CurColumn)
        self.UpdateVision()
    def addscore(self):
        executed = self.SDB.AddScore(self.CurrentUser,self.EndTime,self.MazeType)
        if executed:
            self.result = tk.Label(self.body, width = '50', height = '1', text = 'New best score')
            self.result.grid(row = 3, column = 1)
    def UpdateVision(self):
        location = self.player.CurLocation

        ###Straight lines
        self.mygrid.Grid[location[0] + 1][location[1]].Reveal()
        if self.mygrid.Grid[location[0] + 1][location[1]].CanSeeThrough():
            self.mygrid.Grid[location[0] + 2][location[1]].Reveal()
            if self.mygrid.Grid[location[0] + 2][location[1]].CanSeeThrough():
                self.mygrid.Grid[location[0] + 3][location[1]].Reveal()
        self.mygrid.Grid[location[0] - 1][location[1]].Reveal()
        if self.mygrid.Grid[location[0] - 1][location[1]].CanSeeThrough():
            self.mygrid.Grid[location[0] - 2][location[1]].Reveal()
            if self.mygrid.Grid[location[0] - 2][location[1]].CanSeeThrough():
                self.mygrid.Grid[location[0] - 3][location[1]].Reveal()
        self.mygrid.Grid[location[0]][location[1] + 1].Reveal()
        if self.mygrid.Grid[location[0]][location[1] + 1].CanSeeThrough():
            self.mygrid.Grid[location[0]][location[1]+2].Reveal()
            if self.mygrid.Grid[location[0]][location[1]+2].CanSeeThrough():
                self.mygrid.Grid[location[0]][location[1]+3].Reveal()
        self.mygrid.Grid[location[0]][location[1] - 1].Reveal()
        if self.mygrid.Grid[location[0]][location[1] - 1].CanSeeThrough():
            self.mygrid.Grid[location[0]][location[1]-2].Reveal()
        if self.mygrid.Grid[location[0]][location[1]-2].CanSeeThrough():
            self.mygrid.Grid[location[0]][location[1]-3].Reveal()

        ###Adjacent but diagonally
        if self.mygrid.Grid[location[0] - 1][location[1]].CanSeeThrough() or self.mygrid.Grid[location[0]][location[1] - 1].CanSeeThrough():
            self.mygrid.Grid[location[0] - 1][location[1]- 1].Reveal()
        if self.mygrid.Grid[location[0] + 1][location[1]].CanSeeThrough() or self.mygrid.Grid[location[0]][location[1] - 1].CanSeeThrough():
            self.mygrid.Grid[location[0] + 1][location[1]- 1].Reveal()
        if self.mygrid.Grid[location[0] - 1][location[1]].CanSeeThrough() or self.mygrid.Grid[location[0]][location[1] + 1].CanSeeThrough():
            self.mygrid.Grid[location[0] - 1][location[1]+ 1].Reveal()
        if self.mygrid.Grid[location[0] + 1][location[1]].CanSeeThrough() or  self.mygrid.Grid[location[0]][location[1] + 1].CanSeeThrough():
            self.mygrid.Grid[location[0] + 1][location[1] + 1].Reveal()


        ### next to the locations above
        if self.mygrid.Grid[location[0] - 1][location[1] - 1].CanSeeThrough():
            if self.mygrid.Grid[location[0] - 2][location[1]].CanSeeThrough():
                self.mygrid.Grid[location[0] - 2][location[1] - 1].Reveal()
            if self.mygrid.Grid[location[0]][location[1] - 2].CanSeeThrough():
                self.mygrid.Grid[location[0] - 1][location[1] - 2].Reveal()
        if self.mygrid.Grid[location[0] - 1][location[1] + 1].CanSeeThrough():
            if self.mygrid.Grid[location[0]- 2][location[1]].CanSeeThrough():
                self.mygrid.Grid[location[0]- 2][location[1] + 1].Reveal()
            if self.mygrid.Grid[location[0]][location[1] + 2].CanSeeThrough():
                self.mygrid.Grid[location[0] - 1][location[1] + 2].Reveal()
        if self.mygrid.Grid[location[0] + 1][location[1] - 1].CanSeeThrough():
            if self.mygrid.Grid[location[0] + 2][location[1]].CanSeeThrough():
                self.mygrid.Grid[location[0] + 2][location[1] - 1].Reveal()
            if self.mygrid.Grid[location[0]][location[1] - 2].CanSeeThrough():
                self.mygrid.Grid[location[0] + 1][location[1] - 2].Reveal()
        if self.mygrid.Grid[location[0] + 1][location[1] + 1].CanSeeThrough():
            if self.mygrid.Grid[location[0] + 2][location[1]].CanSeeThrough():
                self.mygrid.Grid[location[0] + 2][location[1] + 1].Reveal()
            if self.mygrid.Grid[location[0]][location[1] + 2].CanSeeThrough():
                self.mygrid.Grid[location[0] + 1][location[1] + 2].Reveal()
class grid():
    def __init__(self, window):
        self.Grid = []
        self.window = window
        #Initialized the grid and the callback to the container
    def CreateDefaultMaze(self, MazeNo):
        self.path = os.getcwd()+"\\Mazes"
        os.chdir(self.path)
        #Changes directory relative to the current working dirtector
        #It's changed to a subdirectory of the current one called Mazes
        MazeNo = str(MazeNo)
        MazeName = "MAZE_"+MazeNo+".txt"
        #Creates a name for the file being searched for
        MazeFile = open(MazeName,'r')
        #opens the text file and reads it
        Lines = MazeFile.readlines()
        #Reads the file and adds them line by line to an array
        self.start = Lines[0].split(",")
        #splits the first item in the array into an array of two strings
        self.start = [int(self.start[0]), int(self.start[1])]
        #Takes the integer values of the first item (now an array) and uses them as coordinates
        #These coordinates are the starting position of the player
        Dimensions = Lines[1].split(",")
        self.__height = int(Dimensions[0])
        self.__width = int(Dimensions[1])
        #Similarly to the starting position, a similar method is used to get the maze dimensions
        #However they are both assigned as different values instead of both of them into one coordinate
        Goal = Lines[2].split(",")
        self.__GoalCord=[int(Goal[0]), int(Goal[1])]
        #Same method to finding the start but with the goal coordinate instead
        CurrentCell = 0
        #initialized a value
        for num in range(self.__height):
            self.Grid.append([])
            for number in range(self.__width):
                if num in [0,self.__height-1] or number in [0,self.__width-1]:
                    item = cell(num, number, self, True, CurrentCell,self.window)
                else:
                    item = cell(num, number, self, False, CurrentCell,self.window)
                CurrentCell += 1
                self.Grid[num].append(item)
        self.Grid[self.__GoalCord[0]][self.__GoalCord[1]].HardExit()
        #Iterates through the dimensions to create an empty maze of correct dimensions, cell by cell
        #This is where whether or not the cell is an edge and the cell number is created
        for Location in range(3, len(Lines)):
            line = Lines[Location]
            line = line.split(",")
            item = [int(line[0]),int(line[1])]
            self.Grid[item[0]][item[1]].HardRez()
        #It then iterates through each other line in the text file and splits it into coordinates
        #It then creates a path where the coordinates are
        #As the maze is hard coded it does not check for any conditions of the coded locations
    def GenerateMaze(self, height, width, type):
        self.__height = height
        self.__width = width
        #These are parameters taken from the user
        #These are validated in the window object
        CurrentCell = 0
        for num in range(self.__height):
            self.Grid.append([])
            for number in range(self.__width):
                if num in [0, self.__height - 1] or number in [0, self.__width - 1]:
                    item = cell(num, number, self, True, CurrentCell, self.window)
                else:
                    item = cell(num, number, self, False, CurrentCell,self.window)
                CurrentCell += 1
                self.Grid[num].append(item)
        #Initializes a blank maze
        self.PlantSeeds()
        self.Generation(type)
    def PlantSeeds(self):
        NumOfCells = self.__height * self.__width
        NumOfSeeds = (NumOfCells / 5)
        NumOfSeeds= round(NumOfSeeds)
        Seeds = 0
        while Seeds < NumOfSeeds:
            randY = random.randint(0,self.__height-1)
            randX = random.randint(0,self.__width-1)
            if not self.Grid[randY][randX].Condition():
                self.Grid[randY][randX].Rez()
                Seeds += 1
            else:
                Seeds -= 1
        #Creates a base for the generation to start from
    def Generation(self, type):
        self.laststate = self.OutputGrid()
        self.UpdateGrid(type)
        count = 0
        while self.OutputGrid() != self.laststate and count != 100 :
            self.UpdateGrid(type)
            count += 1
        #updates the cell states until they either don't update anymore ot it reaches 100 generations
        self.Finalize()
    def UpdateGrid(self, type):
        for num in range(self.__height):
            for number in range(self.__width):
                if self.Grid[num][number].CheckNeighbours() in range(type,6):
                    self.Grid[num][number].Rez()
                else:
                   self.Grid[num][number].Kill()
        #One iteration of a generation
    def Finalize(self):
        resolved = False
        while not resolved:
            #exit condition
            side = random.randint(1,4)
            #Randomly selects a side
            if side % 2 == 0:
                length = random.randint(0,self.__height-1)
                if side == 2:
                    resolved = self.Grid[length][self.__width-1].MakeExit()
                    if resolved:self.__GoalCord = [length, self.__width-1]
                else:
                    resolved = self.Grid[length][0].MakeExit()
                    if resolved:self.__GoalCord = [length, 0]
                #selecting a cell on the left or right wall
            else:
                length = random.randint(0,self.__width-1)
                if side == 2:
                    resolved = self.Grid[self.__height-1][length].MakeExit()
                    if resolved:self.__GoalCord = [self.__height-1, length]
                else:
                    resolved = self.Grid[0][length].MakeExit()
                    if resolved:self.__GoalCord = [0, length]
                #selecting a cell on the top and bottom wall
            #randomly selects a ecll
    def GetGoalLocation(self):
        return self.__GoalCord
    def GetStartLocation(self):
        return self.start
    def GetMazeDimensions(self):
        return self.__height, self.__width
    #Getters
    def OutputGrid(self):
        image = []
        index = 0
        for row in self.Grid:
            image.append([])
            for item in row:
                image[index].append(item.Condition())
            index += 1
        #returns as an array of Booleans so that the window class can intepret the maze as an array of variables instead of objects
        #The window object now uses the Grid array itself so this is now only used for the generation step to check if there is a new state
        return image

class player:
    def __init__(self, StartXind, StartYind, window):
        self.window = window
        self.CurRow = StartYind
        self.CurColumn = StartXind
        self.CurLocation = [self.CurRow, self.CurColumn]
        #location is defined as an attribute, these are updated as the player moves
        #The coordinate and each individual value is stored
    def MoveRow(self, magnitude):
        self.CurRow = self.CurRow + magnitude
        self.CurLocation = [self.CurRow, self.CurColumn]
        #updates the values
    def MoveColumn(self,magnitude):
        self.CurColumn = self.CurColumn + magnitude
        self.CurLocation = [self.CurRow, self.CurColumn]
        #updates the values
    def atgoal(self):
        GoalCoord1, GoalCoord2 = self.window.mygrid.GetGoalLocation()
        if [self.CurRow, self.CurColumn] == [GoalCoord1, GoalCoord2]:
            return True
        else:
            return False
        #Compares the player location to the goal location

class UserDatabase:
    def __init__(self, path):
        self.path = path
        #Initializes the path to the database
    def Process_signup(self, Username,Password):
        os.chdir(__file__.replace(os.path.basename(__file__),''))
        #Makes sure the working directory is in the same as the program
        if Username != "" and Password != "":
            conn = sqlite3.connect(self.path)
            cur = conn.cursor()
            query = "SELECT * FROM UsersInfo " \
                    "WHERE Username = '{0}' " \
                    "OR Password = '{1}'".format(Username, Password)
            cur.execute(query)
            row = cur.fetchone()
            #checks if the username or password is already in use
            if row is None:
                query = "INSERT INTO UsersInfo (Username,Password,Rank)" \
                        " VALUES ('{0}','{1}',1000)".format(Username, Password)
                cur.execute(query)
                conn.commit()
                #Creates a new account in the database
                return True
                #returns whether or not the attempt was sucessful
            else:
                return False
            cur.close()
            
        else:
            return False
    def Process_Login(self, Username, Password):
        os.chdir(__file__.replace(os.path.basename(__file__),''))
        # Makes sure the working directory is in the same as the program
        conn = sqlite3.connect(self.path)
        cur = conn.cursor()

        query = "SELECT * FROM UsersInfo " \
                "WHERE Username = '{0}' AND Password = '{1}'".format(Username, Password)
        #Query validates the database values
        cur.execute(query)
        row = cur.fetchone()
        if row != None:
            User = [row[0],row[1]]
        else:
            User = row
        #returns the user or none
        conn.close()
        return User

class ScoreDatabase:
    def __init__(self, path):
        self.path = path
        #initialises the database path
    def AddScore(self, User,Time, MazeNo):
        if MazeNo != 0:
            MazeName = "MAZE_"+str(MazeNo)
            #constructs a string for the filename
            os.chdir(__file__.replace(os.path.basename(__file__),''))
            # Makes sure the working directory is in the same as the program
            UserID = User[0]
            Username = User[1]
            conn = sqlite3.connect(self.path)
            cur = conn.cursor()
            query = "SELECT * FROM '{0}' " \
                    "WHERE Username = '{1}'" \
                    " and UserID = '{2}'".format(MazeName,Username, UserID)
            #Checking if the user already has a score in the database
            cur.execute(query)
            row = cur.fetchone()
            if row == None:
                query = "INSERT INTO '{0}'(UserID,Username,Time) " \
                        "VALUES ('{1}','{2}','{3}')".format(MazeName,UserID, Username,Time)
                #If there isn't a score, it creates one
                cur.execute(query)
                conn.commit()
                return True
                #returns result of the query
            elif row[2] >= Time:
                #compares the recorded time to the new time
                cur = conn.cursor()
                query = "DELETE FROM '{0}' " \
                        "WHERE Username = '{1}' " \
                        "and UserID = '{2}'".format(MazeName,Username, UserID)
                #As SQLite doesn't have an update feature
                #It deletes the old score record
                cur.execute(query)
                query = "INSERT INTO '{0}'(UserID,Username,Time) " \
                        "VALUES ('{1}','{2}','{3}')".format(MazeName,UserID, Username,Time)
                #Creates a new score record
                cur.execute(query)
                conn.commit()
                return True
            else:
                return False
            cur.close()
    def GetScores(self, MazeNo):
        os.chdir(__file__.replace(os.path.basename(__file__),''))
        # Makes sure the working directory is in the same as the program
        conn = sqlite3.connect(self.path)
        MazeName = "MAZE_"+str(MazeNo)
        #Constructs a string to be used as the file name
        cur = conn.cursor()
        query = "SELECT * FROM '{0}'".format(MazeName)
        cur.execute(query)
        row = cur.fetchall()
        #returns all values of the table
        return row
            
        

class Flooder:
    def __init__(self, window, StartXind, StartYind):
        self.window = window
        #A call back to the container
        self.CurRow = StartXind
        self.CurColumn = StartYind
        self.CurLocation = [self.CurRow, self.CurColumn]
        #initialises the coordinates
        #The inidividual coordinates and the coordinate as a array are both stored
        self.NavQueue = SearchQueue(self.window)
        #Creates a queue object within itself
        self.__Flooded = False
        #The exit condition
        self.CurCell = self.window.mygrid.Grid[self.CurRow][self.CurColumn]
        #Also assigns the cell it is on to a property

    def CheckCurCell(self):
        self.CellMaps = []
        self.CellMaps = self.CurCell.CreateMapping()
        #Gets the current cells surrounding cells
        for item in self.CellMaps:
            #Iterates throught the surrounding cells
            if self.window.mygrid.Grid[item[0]][item[1]].State == 'Unchecked':
                #checks if the cells have been visited or queued
                self.NavQueue.Add(item)
                #Adds the cells to queue
                self.window.mygrid.Grid[item[0]][item[1]].Enqueued(self.CurLocation, self.window.mygrid.Grid[self.CurRow][self.CurColumn].Distance)
                #Updates the cell so it knows its been queued
                #Also adds it's distance to the goal to the cell
        self.CurCell.State = "Checked"
        #Updates the current cell state

    def Move(self):
        self.Newlocation = self.NavQueue.Remove()
        #Removes the item from the front of the queue
        if self.Newlocation != None:
            #if the queue wasn't empty
            self.CurRow = self.Newlocation[0]
            self.CurColumn = self.Newlocation[1]
            self.CurLocation = [self.CurRow, self.CurColumn]
            self.CurCell = self.window.mygrid.Grid[self.CurRow][self.CurColumn]
            #Updates the location properties
        else:
            self.__Flooded = True
            #Meets the exit condition for the flooder
    def IsFlooded(self):
        return self.__Flooded
        #returns whether or not the exit condition has been met



class SearchQueue():
    def __init__(self, window):
        self.window = window
        #A call back to its container's container
        self.Queue = []
        #Using an array to simulate a queue
        self.Front = -1
        self.Rear = -1
        #Pointers initialized
    def Add(self, NewCell):
        self.Queue.append(NewCell)
        #Adds the new cell
        self.Rear += 1
        self.Front = 0
        #sets pointers
    def Remove(self):
        if not self.IsEmpty():
            #Checks if it is empty
            Cell = self.Queue[self.Front]
            #Takes the item at the front of the queue (where the front pointer is)
            self.Rear -= 1
            #Moves Rear pointer forward 1
            if len(self.Queue) == 1:
                self.front = -1
                #For when the queue becomes empty
            for item in range(len(self.Queue) - 1):
                self.Queue[item] = self.Queue[item + 1]
                #Moves all items in the queue 1 down in index
            del self.Queue[-1]
            #Removes the last item in the list (which should be None)
            return Cell
            #Returns the item at the front of the queue
        else:
            return None

    def IsEmpty(self):
        if self.Rear == -1:
            Empty = True
        else:
            Empty = False
        #checks headers to see if the queue is empty and returns the result
        return Empty

    def GiveCells(self):
        cells = []
        for location in self.Queue:
            if location != None:
                cells.append(self.window.mygrid.Grid[location[0]][location[1]])
        #Gives all the cells that are currently queued
        #not the coordinates but the cell objects as an array
        return cells
    
if __name__ == "__main__":
    game = tk.Tk()
    Maze = Window(game)
    #Runs the program
    game.mainloop()


