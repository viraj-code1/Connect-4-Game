
import numpy as np
import math
import pickle
import random

rows = 6
cols = 5
C =1.4

# computing USB value of each child state. This value will be used to pick a child 
def UCB(state):
    return state.wins/state.games + C* math.sqrt(math.log(state.parent.games)/state.games)

# Traversing to the Leaf state
def select(state):
    next= state

    while(state.remainPossibleChild==0 ):   

        # If a child state hasn't been picked yet (games=0) then pick it    
        for i in range(0,len(state.children)):
            if(state.children[i].games==0 ):
                next =state.children[i]
                return next
                
        
        # Selecting the child state with maximum UCB value
        max_ucb_val =-1
        for i in range(0,len(state.children)):
            cur_child_ucb =UCB(state.children[i])
            if(max_ucb_val<=cur_child_ucb ):
                next =state.children[i]
                max_ucb_val = cur_child_ucb
        
        state = next

        if( checkTerminal(next.board)):
            return next    
        
    return next

# Creating a child state from a Leaf Node
def expand(state):
    ct=0
    player=1
    
    # If the state is already a terminal state, then we return the current state as child couldn't be created 
    if(checkTerminal(state.board)):
        return state

    if(state.player==1):
        player=2

    # Checking if a child corresponding to a move can be created or not, if possible create the child and return it 
    for i in range(state.lastChildCheck+1,5):        
        if(validMove(state.board, i)):
            childState = GameNode(state,player,i)
            state.addChild(childState)
            state.lastChildCheck=i
            state.remainPossibleChild-=1
            return childState

# randomly selecting moves (for both players) from current state to terminal state and return the result of terminal state
def simulate(state):
    board = state.board
    player = state.player
    res = getResult(board)
    
    while( res==0):
        if(checkTerminal(state.board)):
            return res
    
        possibleMoves=[]
        for i in range(0,cols):
            if(validMove(board,i)):
                possibleMoves.append(i)
        

        if(len(possibleMoves)==0):
            return res
        
        move = random.choice(possibleMoves)
        possibleMoves.clear()
        if(player==1):
            player=2
        else:
            player=1
        
        board=doMove(board,player,move)
        res = getResult(board)
    
    return res

# From the result compute updating all the values (number of games played, number of wins) from leaf to root state
def backPropogate(res,state):
    if(state==None):
        return 

    state.games+=1
    if(res==state.player):
        state.wins+=1
    
    backPropogate(res,state.parent)


# Gives the best child state
def MCTS(state, iterations):  
    
    while(iterations>0):
        
        leaf = select(state)
        # print(leaf.board)
        # print(leaf.player)
        # print()
        
        child = expand(leaf)        
        # print(child.board)
        # print(child.player)
        # print()

        res =simulate(child)
        # print(res)
        # print()

        backPropogate(res, child)
        # print(iterations)
        # print(leaf.remainPossibleChild)
        # print(leaf.lastChildCheck)
        # print("________________________")
        iterations-=1
    
    #state's child to be selected using max games
    max_games=0
    bestAction =None
    for child in state.children:
        if(child.games>max_games):
            bestAction = child
            max_games = child.games
    return bestAction


# Checks if a winning seq is present on the board for either players
def getResult(board):       

    #horizontal row
    for player in range(1,3):
        for c in range(0,cols-3):
            for r in range(0,rows):
                if board[r][c]==player and board[r][c+1]==player and board[r][c+2]==player and board[r][c+3]==player:                    
                    return player
                    
    #vertical cols
    for player in range(1,3):
        for r in range(0,rows-3):
            for c in range(0,cols):
                if board[r][c]==player and board[r+1][c]==player and board[r+2][c]==player and board[r+3][c]==player:
                    return player
                    
    #diagonals /
    for player in range(1,3):
        for r in range(0,rows-3):
            for c in range(0,cols-3):
                if board[r][c]==player and board[r+1][c+1]==player and board[r+2][c+2]==player and board[r+3][c+3]==player:
                    return player
    #diagonals \
    for player in range(1,3):
        for r in range(3,rows):
            for c in range(0,cols-3):
                if board[r][c]==player and board[r-1][c+1]==player and board[r-2][c+2]==player and board[r-3][c+3]==player:
                    return player
    return 0


# Checks if the given move is valid or not
def validMove(board, move):

    if move<0 or move>cols-1:
        return False
    if(board[0][move]==0):
        return True
    return False


# Performs the given move on the given board and returns new board
def doMove(board,player,move):
    childBoard = np.copy(board)
    top =rows-1 
    
    while(childBoard[top][move]!=0):       
        top-=1

    childBoard[top][move]=player
    return childBoard



# check if the given board is terminal (no more moves possible or a player wins)
def checkTerminal(board):
    if(getResult(board)!=0):
        return True
    
    for i in range(0,cols):
        if(validMove(board,i)):
            return False
    
    return True



class GameNode:
    
    def __init__(self, n1,player:int,move:int ):
        self.parent = n1
        self.children = []
        self.games =0   # number of visit
        self.wins=0     # number of wins 
        self.player=player  # player at the node
        self.lastChildCheck=-1  # the last child created was from which move
        self.remainPossibleChild=0  # number of more childs that can be created 
        if(n1==None):
            self.board = np.zeros((rows,cols),dtype='i')
        else:
            self.board = doMove(n1.board,player,move)  # create child's board from parent's board and the move selected
        
        for i in range(0,cols):
            if(validMove(self.board,i)):
                self.remainPossibleChild+=1
            
    
    def addChild(self,n1):
        self.children = np.append(self.children,n1)       



#Game Play
def MCTS_Play():
    games_to_be_played=1
    p1_wins=0
    p2_wins=0

    for i in range(0,games_to_be_played):
        
        cur = GameNode(None,None,None)
        next= None
        ct=0
        while(checkTerminal(cur.board)==0):
            
            if(ct%2==1):
                next = MCTS(cur,40)
            else:
                next = MCTS(cur,200)
            if(next.player==1):
                print("Player 1 MCTS(200) played:  ")
            else:
                print("Player 2 MCTS(40) played:  ")
            print(next.board)
            print()
            if(checkTerminal(next.board)):
                res = getResult(next.board)
                # print()
                # print(next.board)
                print("Number of Moves = ", ct+1)
                if(res==0):
                    print("Draw")
                elif res==1:
                    print("Player 1 MCTS(200) wins")
                elif res==2:
                    print("Player 2 MCTS(40) wins")
                
                if(res==1):
                    p1_wins+=1
                elif(res==2):
                    p2_wins+=1

                break;
            cur= next
            ct+=1
    # print("_____________________________")
    # print("Player1 wins ",p1_wins)
    # print("Player2 wins ",p2_wins)
    # print("Draw ",games_to_be_played-p1_wins-p2_wins)
    # print("_____________________________")







# QLearning Training

state_Action_Map={}
alpha =0.2
gamma =0.5


# function to encode given (board,move) pair to string
def convertToString(board,move):
    s=""
    for r in board:
        for val in r:
            s+=str(val)
    s+=str(move)
    return s

# function to decode given string into (board,move) pair 
def convertToBoard(s):
       
    board =np.zeros((rows,cols),dtype='i')
    move= int(s[len(s)-1])
    for i in range(0,len(s)-1):
        board[int(i/cols)][i%cols]= int(s[i])
    
    return board,move


# using epsilon greedy method to select a action from a given set of action
# epsilon =0.1
def chooseAction(actionArr):
    
    r1 = random.randint(1, 10)
    if(r1==1):
        return random.choice(actionArr)

    maxValue =-100000
    bestAction =None
    for s in actionArr:
        if(s not in state_Action_Map.keys()):
            state_Action_Map[s]=0
        if(maxValue<state_Action_Map[s]):
            bestAction = s
            maxValue = state_Action_Map[s]
    return bestAction
    


# computing max{q(s,a)} value of child states
def maxQSAchild(state_action):
    board,move = convertToBoard(state_action)
    if(checkTerminal(board)):
        return 0
    board= doMove(board,2,move)


    possibleActions=[]
    for i in range(0,cols):
        if(validMove(board,i)):
            child_state_action=convertToString(board,i)
            possibleActions.append(child_state_action)

    max_QSA=-100000
    for s in possibleActions:
        if(s not in state_Action_Map.keys()):
            state_Action_Map[s]=0
        max_QSA = max(max_QSA,state_Action_Map[s])

    if(max_QSA==-100000):
        return 0
    
    return max_QSA
    

# rewarding based on result
# win = +5, loss = -5 , draw = +2, not a terminal state =-1
def reward(state_action):
    board,move = convertToBoard(state_action)
    if(checkTerminal(board)):
        
        res = getResult(board)
        if(res==2):
            return 5
        elif(res==0):
            return 2
        elif(res==1):
            return -5
    else:
        
        return -1


# updating the dictionary which stores q{s,a} values
def updateMap(state_action):
    if(state_action not in state_Action_Map.keys()):
        state_Action_Map[state_action]=0
    newQSA = state_Action_Map[state_action] + alpha*( reward(state_action)+ gamma*( maxQSAchild(state_action)) - state_Action_Map[state_action])
    state_Action_Map[state_action]=newQSA


def TrainQLearning(iterations):

    for i in range(iterations):
        if(i%100==0):
            print("iterations done : ",i)
        cur = GameNode(None,None,None)
        next= None
        ct=0
        while(checkTerminal(cur.board)==0):
            # print(cur.board)
            next = MCTS(cur,25)
            
            if(checkTerminal(next.board)==0):
                possibleActions=[]
                for i in range(0,cols):
                    if(validMove(next.board, i)):
                        s= convertToString(next.board,i)
                        updateMap(s)
                        possibleActions.append(s)
                
                state_action = chooseAction(possibleActions)
                if(state_action==None):
                    break

                updateMap(state_action)
               
                player = 2

                child = GameNode(next,player, int(state_action[len(state_action)-1]))
                next.addChild(child)
                
                cur = child
            else:
                for j in range(0,5):
                    if(validMove(cur.board,j)):
                        s1= convertToString(cur.board,j)
                        updateMap(s1)
                s2= convertToString(next.board,0)
                updateMap(s2)

                # print(cur.board)
                break

                

def MCTSvQLearn():
    games_to_be_played=1
    p1_wins=0
    p2_wins=0

    for i in range(0,games_to_be_played):
        
        cur = GameNode(None,None,None)
        next= None
        ct=0
        while(checkTerminal(cur.board)==0):
            
            if(ct%2==0):
                next = MCTS(cur,25)
            else:
                
                possible_states = []
                for i in range(0,5):
                    if(validMove(cur.board,i)):                        
                        s = convertToString(cur.board,i)
                        possible_states.append(s)
               
                maxQSA=-10000
                state = None
                for s in possible_states:
                    if(s not in state_Action_Map.keys()):
                        state_Action_Map[s]=0
                    if(maxQSA<state_Action_Map[s]):
                        state= s 
                        maxQSA = state_Action_Map[s]
                if(maxQSA==-10000):
                    break
                board, move = convertToBoard(state)
                player =1
                if(cur.player==1):
                    player=2
                next = GameNode(cur,player,move)
                cur.addChild(next)               

            if(ct%2==0):
                print("Player 1 MCTS(25) played ")
            else:
                print("Player 2 Q-Learning played ")
            print(next.board)
            print()
            if(checkTerminal(next.board)):
                res = getResult(next.board)
                print("Number of Moves = ", ct+1)
                if(res==0):
                    print("Draw")
                elif res==1:
                    print("Player 1 MCTS(25) wins")
                elif res==2:
                    print("Player 2 Q-Learning wins")
                # print(next.board)
                # print()
                if(res==1):
                    p1_wins+=1
                elif(res==2):
                    p2_wins+=1
                
                break;
            cur= next
            ct+=1
    # print("_____________________________")
    # print("Player1 wins ",p1_wins)
    # print("Player2 wins ",p2_wins)
    # print("Draw ",games_to_be_played-p1_wins-p2_wins)
    # print("_____________________________")



def PrintGrid(positions):
    print('\n'.join(' '.join(str(x) for x in row) for row in positions))
    print()

def main():
    selectGame  = int(input(" 1 -> MCTS(200) vs MCTS(40) \n 2 -> MCTS(25) vs Q-Learning \n Enter your value: "))
    if(selectGame==1):
        MCTS_Play()
            
        
    elif selectGame==2:
        global rows
        rows=4
        # Training Q-Learning 
        # TrainQLearning(50000)
        # for k,v in state_Action_Map.items():
        #     print(k,v)
        # filehandler = open('2018B3A70741G_VIRAJ_data', 'wb')        
        # pickle.dump(state_Action_Map, filehandler)

        # Playing MCTS(25) vs QLearning
        global state_Action_Map
        filehandler = open("2018B3A70741G_VIRAJ_data", "rb")
        state_Action_Map = pickle.load(filehandler)
        # for k,v in tp.items():
        #     print(k,v)
        
        MCTSvQLearn()
    else:
        print("Invalid number selected")


    

    # print("************ Sample output of your program *******")

    # game1 = [[0,0,0,0,0],
    #       [0,0,0,0,0],
    #       [0,0,1,0,0],
    #       [0,2,2,0,0],
    #       [1,1,2,2,0],
    #       [2,1,1,1,2],
    #     ]


    # game2 = [[0,0,0,0,0],
    #       [0,0,0,0,0],
    #       [0,0,1,0,0],
    #       [1,2,2,0,0],
    #       [1,1,2,2,0],
    #       [2,1,1,1,2],
    #     ]

    
    # game3 = [ [0,0,0,0,0],
    #           [0,0,0,0,0],
    #           [0,2,1,0,0],
    #           [1,2,2,0,0],
    #           [1,1,2,2,0],
    #           [2,1,1,1,2],
    #         ]

    # print('Player 2 (Q-learning)')
    # print('Action selected : 2')
    # print('Value of next state according to Q-learning : .7312')
    # PrintGrid(game1)


    # print('Player 1 (MCTS with 25 playouts')
    # print('Action selected : 1')
    # print('Total playouts for next state: 5')
    # print('Value of next state according to MCTS : .1231')
    # PrintGrid(game2)

    # print('Player 2 (Q-learning)')
    # print('Action selected : 2')
    # print('Value of next state : 1')
    # PrintGrid(game3)
    
    # print('Player 2 has WON. Total moves = 14.')
    
if __name__=='__main__':
    main()
