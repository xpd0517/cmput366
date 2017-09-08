EMPTY = 0
BLACK = 1
WHITE = 2
BORDER = 3
FLOODFILL = 4
import numpy as np
from pattern import pat3set

import sys
import random

class GoBoardUtil(object):
    
    @staticmethod       
    def playGame(board, color, **kwargs):
        komi = kwargs.pop('komi', 0)
        limit = kwargs.pop('limit', 1000)
        check_selfatari = kwargs.pop('selfatari', True)
        pattern = kwargs.pop('pattern', True)
        if kwargs:
            raise TypeError('Unexpected **kwargs: %r' % kwargs)
        numPass = 0
        for _ in range(limit):
            move = GoBoardUtil.generate_move_with_filter(board,pattern,check_selfatari)
            if move != None:
                isLegalMove = board.move(move,color)
                if not isLegalMove:
                    print("color {} move {} and board\n {} not legal,,,,".format(color ,move,board.get_twoD_board()))
                assert isLegalMove
                numPass = 0
            else:
                board.move(move,color)
                numPass += 1
                if numPass == 2:
                    break
            color = GoBoardUtil.opponent(color)
        winner = board.get_winner(komi)
        return winner
    
    @staticmethod
    def generate_legal_moves(board, color):
        """
        generate a list of legal moves

        Arguments
        ---------
        board : np.array
            a SIZExSIZE array representing the board
        color : {'b','w'}
            the color to generate the move for.
        """
        empty = board.get_empty_points()
        legal_moves = []
        for move in empty:
            if board.check_legal(move, color):
                legal_moves.append(move)
        return legal_moves

    @staticmethod
    def sorted_point_string(points, ns):
        result = []
        for point in points:
            x, y = GoBoardUtil.point_to_coord(point, ns)
            result.append(GoBoardUtil.format_point((x, y)))
        return ' '.join(sorted(result))

    @staticmethod
    def generate_pattern_moves(board):
        pattern_checking_set = board.last_moves_empty_neighbors()
        moves = []
        for p in pattern_checking_set:
            if (board.neighborhood_33(p) in pat3set):
                assert p not in moves
                assert board.board[p] == EMPTY
                moves.append(p)
        return moves
        
    @staticmethod
    def generate_atari_moves(board):
        color = board.current_player
        opp_color = GoBoardUtil.opponent(color)
        if not board.last_move:
            return [],"None"
        last_lib_point = board._single_liberty(board.last_move, opp_color)
        if last_lib_point: #When num of liberty is 1 for last point we will get this point
            if board.check_legal(last_lib_point,color):
                return [last_lib_point],"AtariCapture"
        moves = GoBoardUtil.atari_defence(board, board.last_move, color)
        return moves,"AtariDefense"

    @staticmethod
    def prob_moves(board):
        from feature import Feature
        from feature import Features_weight
        num_features= Feature.find_all_features(board)
                #print(num_features)
                #print(Features_weight)
        dict1={}
        problist=[]
        for item in num_features:
            #print(item)
            if item =="PASS":
                #gamma=Feature.compute_move_gamma(Features_weight, num_features[item])
                #dict1[item]=gamma
                continue
            else:
                move = GoBoardUtil.format_point(GoBoardUtil.point_to_coord(item,board.NS))
                    #print(move)
                gamma=Feature.compute_move_gamma(Features_weight, num_features[item])
                dict1[move]=gamma
                problist.append(gamma)
                    #print(gamma)
        norm = [float(i)/sum(problist) for i in problist]
        norm.sort(reverse=True)
        dict2={}
        for item in dict1:
            dict2[item]=float(dict1[item])/sum(dict1.values())
        sorted(dict2.values(),reverse=True)
        #print(dict2)
        return dict2
        
    @staticmethod
    def generate_all_policy_moves(board,pattern,check_selfatari):
        """
            generate a list of policy moves on board for board.current_player.
            Use in UI only. For playing, use generate_move_with_filter
            which is more efficient
        """
        #from feature import Feature
        #from feature import Features_weight
        #num_features= Feature.find_all_features(board)
        #print(num_features)
        #print(Features_weight)
        #dict1={}
        #problist=[]
        #for item in num_features:
            #print(item)
            #move = GoBoardUtil.format_point(GoBoardUtil.point_to_coord(item,board.NS))
            #print(move)
            #gamma=Feature.compute_move_gamma(Features_weight, num_features[item])
            #dict1[move]=gamma
            #problist.append(gamma)
            #print(gamma)
        #norm = [float(i)/sum(problist) for i in problist]
        #norm.sort(reverse=True)
        #dict2={}
        #for item in dict1:
            #dict2[item]=float(dict1[item])/sum(dict1.values())
        #sorted(dict2.values(),reverse=True)
        #print(dict2)
        #for item in dict1:
            #print(dict1[item])
        #for i in norm:
            #print("{:.5f}".format(i))
        #print(norm)
        #print(Features_weight)
        atari_moves,msg = GoBoardUtil.generate_atari_moves(board)
        atari_moves = GoBoardUtil.filter_moves(board, atari_moves, check_selfatari)
        if len(atari_moves) > 0:
            return atari_moves, msg
        pattern_moves = GoBoardUtil.generate_pattern_moves(board)
        pattern_moves = GoBoardUtil.filter_moves(board, pattern_moves, check_selfatari)
        if len(pattern_moves) > 0:
            return pattern_moves, "Pattern"
        return GoBoardUtil.generate_random_moves(board), "Random"

    @staticmethod
    def generate_random_moves(board):
        empty_points = board.get_empty_points()
        color = board.current_player
        moves = []
        for move in empty_points:
            if board.check_legal(move, color) and not board.is_eye(move, color):
                moves.append(move)
        return moves

    @staticmethod
    def generate_random_move(board):
        color = board.current_player
        moves = board.get_empty_points()
        while len(moves) > 0:
            index = random.randint(0,len(moves) - 1)
            move = moves[index]
            if board.check_legal(move, color) and not board.is_eye(move, color):
                return move
            else:
                # delete moves[index] by overwriting with last in list
                lastIndex = len(moves) - 1
                if index < lastIndex:
                    moves[index] = moves[lastIndex]
                moves.pop()
        return None

    @staticmethod
    def filter_moves(board, moves, check_selfatari):
        color = board.current_player
        good_moves = []
        for move in moves:
            if not GoBoardUtil.filter(board,move,color,check_selfatari):
                good_moves.append(move)
        return good_moves

    # return True if move should be filtered
    @staticmethod
    def filleye_filter(board, move, color):
        assert move != None
        return not board.check_legal(move, color) or board.is_eye(move, color)
    
    # return True if move should be filtered
    @staticmethod
    def selfatari_filter(board, move, color):
        return (  GoBoardUtil.filleye_filter(board, move, color)
               or GoBoardUtil.selfatari(board, move, color)
               )

    # return True if move should be filtered
    @staticmethod
    def filter(board, move, color, check_selfatari):
        if check_selfatari:
            return GoBoardUtil.selfatari_filter(board, move, color)
        else:
            return GoBoardUtil.filleye_filter(board, move, color)

    @staticmethod 
    def filter_moves_and_generate(board, moves, check_selfatari):
        color = board.current_player
        while len(moves) > 0:
            candidate = random.choice(moves)
            if GoBoardUtil.filter(board, candidate, color, check_selfatari):
                moves.remove(candidate)
            else:
                return candidate
        return None

    @staticmethod
    def atari_defence(board, point, color):
        moves = []
        for n in board._neighbors(point):
            if board.board[n] == color:
                last_lib_point = board._single_liberty(n, color)
                if last_lib_point:
                    defend_move = GoBoardUtil.runaway(board, last_lib_point, color)
                    if defend_move:
                        moves.append(defend_move)
                    attack_moves = GoBoardUtil.counterattack(board, n)
                    if attack_moves:
                        moves = moves + attack_moves
        return moves
    
    @staticmethod
    def runaway(board, point, color):
        cboard = board.copy()
        if cboard.move(point, color):
            if cboard._liberty(point,color) > 1:
                return point
            else:
                return None
            
    @staticmethod
    def counterattack(board, point):
        color = board.board[point]
        opp_color = GoBoardUtil.opponent(color)
        moves = []
        for n in board._neighbors(point):
            if board.board[n] == opp_color:
                opp_single_lib = board._single_liberty(n, opp_color)
                if opp_single_lib:
                    cboard = board.copy()
                    if cboard.move(opp_single_lib, color):
                        if cboard._liberty(point, color) > 1:
                            moves.append(opp_single_lib)
        return moves
    
    @staticmethod
    def generate_move_with_filter(board, use_pattern, check_selfatari):
        """
            Arguments
            ---------
            check_selfatari: filter selfatari moves?
                Note that even if True, this filter only applies to pattern moves
            use_pattern: Use pattern policy?
        """
        move = None
        #TODO make dictionary for options so argument passing becomes cleaner and add atari defence to it
        moves,_ = GoBoardUtil.generate_atari_moves(board)
        move = GoBoardUtil.filter_moves_and_generate(board, moves, 
                                                  check_selfatari)
        if move:
            return move
        if use_pattern:
            moves = GoBoardUtil.generate_pattern_moves(board)
            move = GoBoardUtil.filter_moves_and_generate(board, moves, 
                                                         check_selfatari)
        if move == None:
            move = GoBoardUtil.generate_random_move(board)
        return move 
    
    @staticmethod
    def selfatari(board, move, color):
        max_old_liberty = GoBoardUtil.blocks_max_liberty(board, move, color, 2)
        if max_old_liberty > 2:
            return False
        cboard = board.copy()
        # swap out true board for simulation board, and try to play the move
        isLegal = cboard.move(move, color) 
        if isLegal:               
            new_liberty = cboard._liberty(move,color)
            if new_liberty==1:
                return True 
        return False

    @staticmethod
    def blocks_max_liberty(board, point, color, limit):
        assert board.board[point] == EMPTY
        max_lib = -1 # will return this value if this point is a new block
        neighbors = board._neighbors(point)
        for n in neighbors:
            if board.board[n] == color:
                num_lib = board._liberty(n,color) 
                if num_lib > limit:
                    return num_lib
                if num_lib > max_lib:
                    max_lib = num_lib
        return max_lib
        
    @staticmethod
    def format_point(move):
        """
        Return coordinates as a string like 'a1', or 'pass'.

        Arguments
        ---------
        move : (row, col), or None for pass

        Returns
        -------
        The move converted from a tuple to a Go position (e.g. d4)
        """
        column_letters = "abcdefghjklmnopqrstuvwxyz"
        if move is None:
            return "pass"
        row, col = move
        if not 0 <= row < 25 or not 0 <= col < 25:
            raise ValueError
        return    column_letters[col - 1] + str(row) 
        
    @staticmethod
    def move_to_coord(point, board_size):
        """
        Interpret a string representing a point, as specified by GTP.

        Arguments
        ---------
        point : str
            the point to convert to a tuple
        board_size : int
            size of the board

        Returns
        -------
        a pair of coordinates (row, col) in range(1, board_size+1)

        Raises
        ------
        ValueError : 'point' isn't a valid GTP point specification for a board of size 'board_size'.
        """
        if not 0 < board_size <= 25:
            raise ValueError("board_size out of range")
        try:
            s = point.lower()
        except Exception:
            raise ValueError("invalid point")
        if s == "pass":
            return None
        try:
            col_c = s[0]
            if (not "a" <= col_c <= "z") or col_c == "i":
                raise ValueError
            if col_c > "i":
                col = ord(col_c) - ord("a")
            else:
                col = ord(col_c) - ord("a") + 1
            row = int(s[1:])
            if row < 1:
                raise ValueError
        except (IndexError, ValueError):
            raise ValueError("wrong coordinate")
        if not (col <= board_size and row <= board_size):
            raise ValueError("wrong coordinate")
        return row, col
    
    @staticmethod
    def opponent(color):
        assert color == BLACK or color == WHITE
        return BLACK + WHITE - color
            
    @staticmethod
    def color_to_int(c):
        """convert character representing player color to the appropriate number"""
        color_to_int = {"b": BLACK , "w": WHITE, "e":EMPTY, "BORDER":BORDER, "FLOODFILL":FLOODFILL}
        try:
           return color_to_int[c] 
        except:
            raise ValueError("wrong color")
    
    @staticmethod
    def int_to_color(i):
        """convert number representing player color to the appropriate character """
        int_to_color = {BLACK:"BLACK", WHITE:"WHITE", EMPTY:"EMPTY", BORDER:"BORDER", FLOODFILL:"FLOODFILL"}
        try:
           return int_to_color[i] 
        except:
            raise ValueError("Provided integer value for color is invalid")
        
    @staticmethod
    def point_to_coord(point, ns):
        """
        Transform one dimensional point presentation to two dimensional.

        Arguments
        ---------
        point

        Returns
        -------
        x , y : int
                coordinates of the point  1 <= x, y <= size
        """
        if point is None:
            return 'pass'
        row, col = divmod(point, ns)
        return row,col
    @staticmethod
    def verify_weights(distribution):
            epsilon = 0.000000001 # allow small numerical error
            sum1 = 0.0
            for item in distribution:
                sum1 += float((item[1]))
            assert abs(sum1 - 1.0) < epsilon
            print(sum1)        
    @staticmethod
    def random_select(distribution):
        r = random.random();
        sum = 0.0
        for item in distribution:
            sum += item[1]
            if sum > r:
                return item
        return distribution[-1]    

