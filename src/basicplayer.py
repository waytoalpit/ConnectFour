global nodes_exapnded
from util import memoize, run_search_function
import sys
from _sqlite3 import Row

'''
Basic evaluate function to calculate score of the called player
'''
def basic_evaluate(board):
    """
    The original focused-evaluate function from the lab.
    The original is kept because the lab expects the code in the lab to be modified. 
    """
    if board.is_game_over():
        # If the game has been won, we know that it must have been
        # won or ended by the previous move.
        # The previous move was made by our opponent.
        # Therefore, we can't have won, so return -1000.
        # (note that this causes a tie to be treated like a loss)
        score = -1000
    else:
        score = board.longest_chain(board.get_current_player_id()) * 10
        # Prefer having your pieces in the center of the board.
        for row in range(6):
            for col in range(7):
                if board.get_cell(row, col) == board.get_current_player_id():
                    score -= abs(3-col)
                elif board.get_cell(row, col) == board.get_other_player_id():
                    score += abs(3-col)

    return score

'''
return all the successors of the given state
'''
def get_all_next_moves(board):
    """ Return a generator of all moves that the current player could take from this position """
    from connectfour import InvalidMoveException

    for i in xrange(board.board_width):
        try:
            yield (i, board.do_move(i))
        except InvalidMoveException:
            pass


'''
check if it is a terminal/leaf node
'''
def is_terminal(depth, board):
    """
    Generic terminal state check, true when maximum depth is reached or
    the game has ended.
    """
    return depth <= 0 or board.is_game_over()

'''
Implementation of Minimax algorithm
'''
def minimax(board, depth, eval_fn,
            get_next_moves_fn = get_all_next_moves,
            is_terminal_fn = is_terminal,
            verbose = True):
    """
    Do a minimax search to the specified depth on the specified board.

    board -- the ConnectFourBoard instance to evaluate
    depth -- the depth of the search tree (measured in maximum distance from a leaf to the root)
    eval_fn -- (optional) the evaluation function to use to give a value to a leaf of the tree; see "focused_evaluate" in the lab for an example

    Returns an integer, the column number of the column that the search determines you should add a token to
    """
    global nodes_exapnded
    nodes_exapnded=0
    
    bestVal, bestCol = doMinimax(board, depth, eval_fn,get_next_moves_fn,is_terminal_fn,True)
    
    return (bestCol, nodes_exapnded)
        

'''
Minimax recursive processing
'''
def doMinimax(board, depth, eval_fn,
            get_next_moves_fn,
            is_terminal_fn,
            isMaxTurn):
    """
    Do a minimax search to the specified depth on the specified board.

    board -- the ConnectFourBoard instance to evaluate
    depth -- the depth of the search tree (measured in maximum distance from a leaf to the root)
    eval_fn -- (optional) the evaluation function to use to give a value to a leaf of the tree; see "focused_evaluate" in the lab for an example

    Returns an integer, the column number of the column that the search determines you should add a token to
    """
    global nodes_exapnded
            
    if depth is 0 or is_terminal_fn(depth, board):
        return (eval_fn(board),0)
    
    
    if isMaxTurn:
        bestMove=0
        bestValue=-sys.maxint
        maxChild= get_next_moves_fn(board)
        for child in maxChild:
            (val,col)=doMinimax(child[1],depth-1,eval_fn,get_next_moves_fn,is_terminal_fn,False)
            nodes_exapnded=nodes_exapnded+1            
            if(val>bestValue):
                bestValue=val
                bestMove=child[0]
    
        return (bestValue,bestMove)
    
    else:
        bestMove=0
        bestValue=sys.maxint
        minChild= get_next_moves_fn(board)
        for child in minChild:
            (val,col)=doMinimax(child[1],depth-1,eval_fn,get_next_moves_fn,is_terminal_fn,True)
            nodes_exapnded=nodes_exapnded+1
            if(val<bestValue):
                bestValue=val
                bestMove=child[0]
    
        return (bestValue,bestMove)

def rand_select(board):
    """
    Pick a column by random
    """
    import random
    moves = [move for move, new_board in get_all_next_moves(board)]
    return (moves[random.randint(0, len(moves) - 1)],0)

'''
new evaluate function to provide better heuristic for next move
'''
def new_evaluate(board):
    if board.is_game_over():        
        if board.is_win() == board.get_current_player_id():
            score = 100000
        else:
            score = -100000
    else:
                
#        print "Board kVal" + str(board._kVal)
        cons_2_curr = findConsecPos(board, board.get_current_player_id(), board._kVal-1) 
        cons_1_curr = findConsecPos(board, board.get_current_player_id(), board._kVal-2)
        
        opp_2_curr = findConsecPos(board, board.get_current_player_id(), board._kVal-1)
        opp_1_curr = findConsecPos(board, board.get_current_player_id(), board._kVal-2)
        
        if board.get_current_player_id() == 1:
            score = cons_2_curr * 10000 + cons_2_curr * 100 - opp_2_curr * 100000 - opp_1_curr * 100
        else:
            score = -1 * (cons_2_curr * 10000 + cons_1_curr * 100 - - opp_2_curr * 100000 - opp_1_curr * 100) 
        
    return score

def findConsecPos(board, player, nCount):
    count = 0
    
    for row in range(6):
        for col in range(7):
            if board.get_cell(row,col) == player :
                count += findHorizontalCount(board, row, col, player, nCount)
                count += findVerticalCount(board, row, col, player, nCount)
                count += findDiagonalCount(board, row, col, player, nCount)                

    return count

def findHorizontalCount(board, row, col, player, nCount):
    count = 0
    
    for j in xrange(col, 7):
        if board.get_cell(row, j) == player:
            count = count + 1
            if (count == nCount):
                return 1            
        else:
            break        
    
    return 0

def findVerticalCount(board, row, col, player, nCount):
    count = 0
    
    for i in xrange(row, 6):
        if board.get_cell(i, col) == player:
            count = count +1
            if (count == nCount):
                return 1
        else:
            break
            
    return 0       
 
def findDiagonalCount(board, row, col, player, nCount):
    tCount = 0
    count = 0
    
    pCol = col
    for i in xrange(row, -1, -1):
        if board.get_cell(i, pCol) == player:
            count = count + 1
        else:
            break
        
        pCol = pCol + 1
        if pCol > 6:
            break     
                   
    if(count >= nCount):
        tCount = tCount + 1
              
    count = 0
    
    
    pCol = col
    for i in xrange(row, 6):        
        if board.get_cell(i, pCol) == player:
            count = count + 1            
        else:
            break
        
        pCol = pCol + 1
        if pCol > 6:
            break
    
    if(count >= nCount):
        tCount = tCount + 1
        
    return tCount

random_player = lambda board: rand_select(board)
basic_player = lambda board: minimax(board, depth=4, eval_fn=basic_evaluate)
new_player = lambda board: minimax(board, depth=4, eval_fn=new_evaluate)
progressive_deepening_player = lambda board: run_search_function(board, search_fn=minimax, eval_fn=basic_evaluate)
