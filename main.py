#TODO: find if a position, a player is in check, and if the king is checkmated
#also: handle en passant

init_pos = [' ','R','N','B','Q','K','B','N','R',' ',' ','P','P','P','P','P','P','P','P',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','p','p','p','p','p','p','p','p',' ',' ','r','n','b','q','k','b','n','r',' ']

directions = {'r':[1,-1,10,-10],'b':[11,9,-11,-9],'n':[21,19,12,8,-8,-12,-21,-19],'q':[1,-1,10,-10,11,9,-11,-9],'k':[1,-1,10,-10,11,9,-11,-9],'p':[1]}

class Position:

    def __init__(self,board=init_pos,can_castle=True):
        self.board = board
        self.can_castle = can_castle
        self.last_move = None
        self.captured_piece = ' '
        
    def __getitem__(self,square):
        return self.board[square]

    def make_move(self,move):
        fr, to = move
        moving_piece = position[fr]
        position[fr] = ' '
        self.captured_piece = position[to]
        position[to] = moving_piece
        self.last_move = move

squares = range(80)

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

def convert_move(move):
    """move is a string like "e2-e4". The function converts it into a move like (15,35). For now only the notation "<from>-<to>" is supported (not the algebraic notation."""
    fr, to = move.split("-")
    return (convert_square(fr), convert_square(to))

def get_moves_pieces(position,square, piece):
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

def coordinates_to_square(x,y):
    return x+1+10*y

def get_moves(position,color):
    res = []
    for x in range(8):
        for y in range(8):
            square = coordinates_to_square(x,y)
            piece = position[square]
            if piece == ' ' or get_color(piece) != color:
                continue
            res.append({square:get_moves_pieces(position,square,piece)})
    return res

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

def check_en_passant(position, color):
    """check if *color* can do an en passant capture."""
    last_move = position.last_move
    pawn = 'p' if color == 'w' else 'P'
    if position[last_move[1]] != pawn:
        return False
    sense = -1 if color == 'w' else 1
    if last_move[1] - last_move[0] != 20*sense:
        return False
    left, right = last_move[1] - 1, last_move[1] + 1
    capturing_pawn = 'P' if color == 'w' else 'p'
    if position[left] == capturing_pawn or position[right] == capturing_pawn:
        return True
    return False

if __name__ == '__main__':
    position = Position()
    print(get_moves(position,"w"))
