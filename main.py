#TODO: find if a position, a player is in check, and if the king is checkmated
#TODO: fix the board representation - it's currently reversed

from copy import copy

init_pos_pre = [['R' ,'N' ,'B' ,'Q' ,'K' ,'B' ,'N' ,'R'],
                ['P' ,'P' ,'P' ,'P' ,'P' ,'P' ,'P' ,'P'],
                [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
                ['r' ,'n' ,'b' ,'q' ,'k' ,'b' ,'n' ,'r']]

init_pos = reduce(lambda x,y: x+y,map(lambda x: [' '] + x + [' '],init_pos_pre))


directions = {'r':[1,-1,10,-10],'b':[11,9,-11,-9],'n':[21,19,12,8,-8,-12,-21,-19],'q':[1,-1,10,-10,11,9,-11,-9],'k':[1,-1,10,-10,11,9,-11,-9],'p':[1]}


class Move:

    def __init__(self,fr,to,en_passant=False,castle=False):
        self.fr = fr
        self.to = to
        self.en_passant = en_passant
        self.castle = castle

        
class Position:

    def __init__(self, board=init_pos, rights_to_castle={'w': True, 'b': True}):
        self.board = board
        self.last_move = None
        self.captured_piece = ' '
        self.rights_to_castle = rights_to_castle
        
    def __getitem__(self, square):
        return self.board[square]

    def __setitem__(self, square, value):
        self.board[square] = value
    
    def make_move(self, move,color):
        fr, to = move.fr, move.to
        new_position = Position(copy(self.board), copy(self.rights_to_castle))
        new_position.last_move = self.last_move
        new_position.captured_piece = self.captured_piece
        
        moving_piece = new_position.board[fr]
        new_position.board[fr] = ' '
        new_position.captured_piece = position[to]
        new_position.board[to] = moving_piece
        new_position.last_move = move
        if move.en_passant:
            # removing the captured pawn here
            new_position.board[move.en_passant] = ' '
        if moving_piece.lower() == 'k':
            if new_position.rights_to_castle[color]['big']:
                new_position.rights_to_castle[color]['big'] = False
            if new_position.rights_to_castle[color]['small']:
                new_position.rights_to_castle[color]['small'] = False
        if moving_piece.lower() == 'r':
            if color == 'w':
                if fr == 71 and new_position.rights_to_castle[color]['big']:
                    new_position.rights_to_castle[color]['big'] = False
                if fr == 79 and new_position.rights_to_castle[color]['small']:
                    new_position.rights_to_castle[color]['small'] = False
            elif color == 'b':
                if fr == 1 and new_position.rights_to_castle[color]['big']:
                    new_position.rights_to_castle[color]['big'] = False
                if fr == 9 and new_position.rights_to_castle[color]['small']:
                    new_position.rights_to_castle[color]['small'] = False
        if move.castle:
            print(move.castle)
            # moving the rook of the castle
            new_rook_square = (move.castle + 3) if (move.castle % 10) == 1 else (move.castle - 2)
            rook =  new_position.board[move.castle]
            print(rook,new_position.board[8])
            new_position.board[new_rook_square] = rook
            new_position.board[move.castle] = ' '
        return new_position

    def __str__(self):
        res = ""
        for y in range(7, -1, -1):
            tmp = ""
            for x in range(1, 9):
                square = 10*y+x
                tmp += self.board[square]
            tmp += "\n"
            res += tmp
        return res


squares = range(80)


def sign(x):
    if x == 0:
        return 0
    return -1 if x < 0 else 1


def all_p(pred, lst):
    for elt in lst:
        if not pred(elt):
            return False
    return True


def any_p(pred, lst):
    for elt in lst:
        if pred(elt):
            return True
    return False

def in_board(square):
    x, y = square%10, square/10
    return x > 0 and x < 9 and y > 0 and y < 9

def get_color(piece):
    if piece == ' ':
        return ' '
    return 'w' if piece.isupper() else 'b'

def extend_direction(position, color, direction, square, continuous):
    if not continuous:
        tmp_square = square + direction
        return [] if get_color(position[tmp_square]) == color or not in_board(tmp_square) else [tmp_square]
    res = []
    tmp_square = square + direction
    while in_board(square) and position[tmp_square] != ' ':
        res.append(tmp_square)
        tmp_square = tmp_square + direction
    if in_board(square) and position[tmp_square] != color:
        res.append(tmp_square)
    return res

def go_to_end_of_direction(position,direction,square):
    """from a given square, goes to the end of a direction, that is: either the last square on board, or the first piece that is reached."""
    tmp_square = square + direction
    while in_board(tmp_square) and position[tmp_square] == ' ':
        tmp_square = tmp_square + direction
    return position[tmp_square]

def get_pawn_moves(position, color, square):
    """special function to find out the moves a pawn can make."""
    direction_move = -10 if color == 'b' else 10
    second_row = 1 if color == 'w' else '6'
    res = []
    if square % 10 == second_row:
        extra_direction = 20 if color == 'w' else -20
        tmp_square = square + extra_direction
        if position[tmp_square] != color:
            res.append(tmp_square)
    tmp_square = square + direction_move
    if in_board(tmp_square) and position[tmp_square] != color:
        res.append(tmp_square)
    #now handling captures
    capture_directions = [9,11] if color == 'w' else [-11,-9]
    for direction in capture_directions:
        tmp_square = square + direction_move
        if not in_board(tmp_square):
            continue
        tmp = position[tmp_square]
        if tmp != ' ' and tmp != color:
            res.append(tmp_square)
    #TODO: handle promotions
    return res


def convert_square(square):
    """converts a square in standard notation ("e2") into a number used internally to denote a square (15)."""
    x, y = ord(square[0])-96,int(square[1])-1
    return 10*y+x


def convert_move(move, color):
    """move is a string like "e2-e4". The function converts it into a move like (15,35). 
    For now only the notation "<from>-<to>" is supported (not the algebraic notation.
    `color` is required for castle and en passant moves"""
    if move == "00":
        king_square = 5 if color == 'w' else 75
        rook_square = 8 if color == 'w' else 78
        return Move(king_square, king_square+2,castle=rook_square)
    if move == '000':
        king_square = 5 if color == 'w' else 75
        rook_square = 1 if color == 'w' else 71
        return Move(king_square,king_square-3,castle=rook_square)
    if "e.p" in move:
        #en passant captures need to be handled separately
        tmp_move = move.split(" ")[0]
        fr_square, to_square = move.split("-")
        fr, to = convert_square(fr_square), convert_square(to_square)
        capture_square = fr + ((to - fr) % 10)
        return Move(fr, to, en_passant=capture_square)
    fr, to = move.split("-")
    return Move(convert_square(fr), convert_square(to))


def get_moves_pieces(position, square, piece):
    lower = piece.lower()
    res = []
    color = get_color(piece)
    if lower != 'p':
        dirs = directions[lower]
    else:
        return get_pawn_moves(position, color,square)
    continuous = lower not in ['p','n']
    for direction in dirs:
        res += extend_direction(position, color, direction, square, continuous)
    return res


def coordinates_to_square(x, y):
    return x+1+10*y


def get_moves(position, color):
    res = []
    # TODO: change this function:
    # 1. make sure the resulting position is not a check
    # before adding a move to `res`
    # 2. check for castle and en-passant
    for x in range(8):
        for y in range(8):
            square = coordinates_to_square(x, y)
            piece = position[square]
            if piece == ' ' or get_color(piece) != color:
                continue
            res.append({square: get_moves_pieces(position, square, piece)})
    return res


def is_controlled(position, square, color):
    """return True if a piece of `color` can go to `square`, False otherwise."""
    for square in range(0, 80):
        piece = position[square]
        if get_color(piece) != color:
            continue
        possible_squares = get_moves_pieces(position, square, piece)
        if square in possible_squares:
            return True
    return False

def check_if_check(position, color):
    """return True if *color* is in check, False otherwise."""
    king = 'K' if color == 'w' else 'k'
    #get king's position
    for x,y in [(x,y) for x in range(8) for y in range(8)]:
        square = coordinates_to_square(x,y)
        piece = position[square]
        if piece == king:
            king_square = square
            break
    #checking one step directions
    sense = 1 if color == 'w' else -1
    #colorize sets a piece to uppercase if the color is black (because
    #it's the opposite color)
    colorize = (lambda x: x.upper()) if color == 'b' else (lambda x: x)
    dirs = [(10,['k']),(-10,['k']),(10*sense+1,['k','p']),(10*sense-1,['k','p']),(-10*sense+1,['k']),(-10*sense-1,['k']),(1,['k']),(-1,['k']),
            (19,['n']),(21,['n']),(12,['n']),(8,['n']),(-12,['n']),(-8,['n']),(-19,['n']),(-21,['n'])]
    for d in dirs:
        move, compatible_pieces = d[0], map(colorize, d[1])
        square = king_square + move
        if position[square] in compatible_pieces:
            return True
    #now checking multi steps directions
    dirs = [(10,['r','q']),(-10,['r','q']),(1,['r','q']),(-1,['r','q']),(11,['b','q']),(9,['b','q']),(-9,['b','q']),(-11,['b','q'])]
    for d in dirs:
        move, compatible_pieces = d[0], map(colorize, d[1])
        square = go_to_end_of_direction(position, move, king_square)
        if position[square] in compatible_pieces:
            return True
    return False


def second_row(square, color):
    if color == 'w':
        return square >= 10 and square <= 19
    return square >= 60 and square <= 69


def is_castle_legal(move, position, color):
    castle_type = "small" if move.castle == 8 % 10 else "big"
    if not position.rights_to_castle[color][castle_type]:
        return False
    if check_if_check(position,color):
        return False
    # now, checking that all the squares between the king
    # and the rooks are empty
    castle_dir = sign(move.fr - move.to)
    start_square, end_square = move.fr + castle_dir, move.castle - castle_dir
    for square in range(start_square, move.castle, castle_dir):
        if position[square] != ' ':
            return False
    # now, checking if the squares between the king_square
    # and the arrival square of the king are not controled
    opposite_color = 'b' if color == 'w' else 'w'
    for square in range(start_square, move.to, castle_dir):
        if is_controlled(square, position, opposite_color):
            return False
    return True


def is_legal(move, position, color):
    """returns True if a move is legal, False otherwise."""
    if move.castle:
        if not is_castle_legal(move, position, color):
            return False
    moving_piece = position[move.fr]
    if get_color(moving_piece) != color:
        return False
    # checking that the move are following a legal direction
    diff = move.to - move.fr
    piece = moving_piece.lower()
    if piece in ['b', 'q', 'r']:
        possible_directions = directions[piece]
        compatible_directions = filter(lambda d: sign(d) == sign(diff) and diff % d != 0, possible_directions)
        if len(compatible_directions) == 0:
            return False
        # check if there is a piece in between move.fr and move.to
        direction = compatible_directions[0]
        tmp_square = move.fr + direction
        while tmp_square != move.to:
            if position[tmp_square] != ' ':
                return False
    elif piece in ['k', 'n']:
        possible_directions = directions[piece]
        compatible_directions = filter(lambda d: sign(d) == sign(diff) and diff % d != 0, possible_directions)
        if len(compatible_directions) == 0:
            return False
        return True
    else:
        #in this case, piece == 'p'
        sense = 1 if color == 'w' else -1
        if diff not in [10 * sense, 10 * sense + 1, 10 * sense - 1, 20 * sense]:
            return False
        if diff == 10 * sense:
            if position[move.to] != ' ':
                return False
        if diff == 10 * sense:
            if position[move.to] != ' ' or position[move.fr + 10 * sense] != ' ' or not second_rank(move.fr, color) :
                return False
    return True


#TODO: remove from the board the captured pawn
def list_en_passant(position, color):
    """check if *color* can do an en passant capture."""
    last_move = position.last_move
    pawn = 'p' if color == 'w' else 'P'
    if position[last_move[1]] != pawn:
        return []
    sense = -1 if color == 'w' else 1
    if last_move[1] - last_move[0] != 20*sense:
        return []
    left, right = last_move[1] - 1, last_move[1] + 1
    capturing_pawn = 'P' if color == 'w' else 'p'
    res = []
    capture_square = last_move + 10*sense
    if position[left] == capturing_pawn:
        res.append((left,capture_square))
    if position[right] == capturing_pawn:
        res.append((right,capture_square))
    return res


def list_castle(position, color):
    """gives the castle moves *color* can execute."""
    res = []
    return res


def switch_color(color):
    return 'b' if color == 'w' else 'w'

if __name__ == '__main__':
    position = Position()
    color = 'w'
    moves = ["e2-e4","e7-e5","g1-f3","b8-c6","f1-c4","f8-c5","00"]
    print(position)
    # for move in moves:
    #     position.make_move(convert_move(move,color))
    #     color = switch_color(color)
    #     print(position)
    while True:
        user_move = raw_input(">")
        position = position.make_move(convert_move(user_move,color),color)
        color = switch_color(color)
        print(position)
