#TODO: find if a position, a player is in check, and if the king is checkmated

init_pos = [' ','R','N','B','Q','K','B','N','R',' ',' ','P','P','P','P','P','P','P','P',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','p','p','p','p','p','p','p','p',' ',' ','r','n','b','q','k','b','n','r',' ']

directions = {'r':[1,-1,10,-10],'b':[11,9,-11,-9],'n':[21,19,12,8,-8,-12,-21,-19],'q':[1,-1,10,-10,11,9,-11,-9],'k':[1,-1,10,-10,11,9,-11,-9],'p':[1]}

class Position:
    def __init__(self,board=init_pos,can_castle=True):
        self.board = board
        self.can_castle = can_castle
    def __getitem__(self,square):
        return self.board[square]

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


if __name__ == '__main__':
    position = Position()
    print(get_moves(position,"w"))
