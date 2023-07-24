import pygame
from .constants import BLACK, ROWS, RED, SQUARE_SIZE, COLS, WHITE
from .piece import Piece


class Board:
    def __init__(self):
        self.board = []
        self.red_left = self.white_left = ((ROWS-2) // 2) * COLS // 2
        self.red_kings = self.white_kings = 0
        self.create_board()

    def draw_squares(self, win):
        win.fill(BLACK)
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                pygame.draw.rect(win, RED, (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def evaluate(self):
        return self.white_left - self.red_left + (self.white_kings * 0.5 - self.red_kings * 0.5)

    def get_all_pieces(self, color):
        pieces = []
        for row in self.board:
            for piece in row:
                if piece != 0 and piece.color == color:
                    pieces.append(piece)
        return pieces

    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)

        if row == ROWS - 1 or row == 0:
            piece.make_king()
            if piece.color == WHITE:
                self.white_kings += 1
            else:
                self.red_kings += 1

    def get_piece(self, row, col):
        return self.board[row][col]

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if col % 2 == ((row + 1) % 2):
                    if row < ROWS // 2 - 1 :
                        self.board[row].append(Piece(row, col, WHITE))
                    elif row > ROWS // 2:
                        self.board[row].append(Piece(row, col, RED))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)

    def draw(self, win):
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win)

    def remove(self, pieces):
        for piece in pieces:
            self.board[piece.row][piece.col] = 0
            if piece != 0:
                if piece.color == RED:
                    self.red_left -= 1
                else:
                    self.white_left -= 1

    def winner(self):
        if self.red_left <= 0:
            return WHITE
        elif self.white_left <= 0:
            return RED

        return None

    def get_valid_moves(self, piece):
        moves = {}
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row

        if piece.color == RED and not piece.king:
            moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left))
            moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right))
            moves.update(self._traverse_left(row + 1, min(row + 3, ROWS), 1, piece.color, left))
            moves.update(self._traverse_right(row + 1, min(row + 3, ROWS), 1, piece.color, right))
            list_of_keys_to_delete = []

            for key, value in moves.items():
                if key[0] == piece.row + 1:
                    list_of_keys_to_delete.append(key)

            for key in list_of_keys_to_delete:
                del moves[key]
        elif piece.color == WHITE and not piece.king:
            moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left))
            moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right))
            moves.update(self._traverse_left(row + 1, min(row + 3, ROWS), 1, piece.color, left))
            moves.update(self._traverse_right(row + 1, min(row + 3, ROWS), 1, piece.color, right))
            list_of_keys_to_delete = []

            for key, value in moves.items():
                if key[0] == piece.row - 1:
                    list_of_keys_to_delete.append(key)

            for key in list_of_keys_to_delete:
                del moves[key]
        else:
            pass

        #Include the rule of necessary take
        for key, value in moves.items():
            print(key, value)
        new_moves = {key: value for key, value in moves.items() if value != [] }

        #check if there are possibility to take
        if len(new_moves) == 0:

            #if there is nothing to take - return previous dictionary
            return moves

        else:

            #if there is something to take - return new changed dictionary only with moves which take something
            return new_moves

    def get_valid_moves1(self, piece):
        valid_moves = []
        row = piece.row
        col = piece.col

        # Check for possible moves in all directions
        if not piece.king:
            moves = [
                (row - 1, col - 1),  # Top-left
                (row - 1, col + 1),  # Top-right
                (row + 1, col + 1),
                (row + 1, col - 1),
                ]

        for move in moves:
            new_row, new_col = move
        # Check if the move is within the board boundaries
            if 0 <= new_row < ROWS and 0 <= new_col < COLS:
                # Check if the target position is empty
                if piece.color == RED and new_row == row - 1 and self.board[new_row][new_col] == 0:
                    if self.board[new_row][new_col] == 0:
                        valid_moves.append((new_row, new_col))

                elif piece.color == WHITE and new_row == row + 1 and self.board[new_row][new_col] == 0:
                    if self.board[new_row][new_col] == 0:
                        valid_moves.append((new_row, new_col))



                # Check if there is an opponent's piece that can be captured
                elif self.board[new_row][new_col] != piece.color and self.board[new_row][new_col] != 0:
                    capture_row = new_row + (new_row - row)
                    capture_col = new_col + (new_col - col)

                    # Check if the capture position is within the board boundaries
                    if 0 <= capture_row < ROWS and 0 <= capture_col < COLS:
                        # Check the capture position is empty
                        if self.board[capture_row][capture_col] == 0:
                            valid_moves.append((capture_row, capture_col))




        print(valid_moves)
        return valid_moves

    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
        moves = {}

        #last - the last piece we skipped to move to this point
        last = []

        for r in range(start, stop, step):

            #The situation we are now looking outside of the board
            if left < 0:
                break

            current = self.board[r][left]

            #check if the cell we are in is empty
            if current == 0:

                #The case when we skipped a piece and have not seen a piece yet
                if skipped and not last:
                    break

                #double+ jump
                elif skipped:
                    #combine the last checker we jumped and the checker on this move
                    moves[(r, left)] = last + skipped

                #if it is 0 and last existed - we can jump over it
                else:
                    moves[(r, left)] = last

                #we found an empty square and last has a value in it - we had something we skipped over
                if last:
                    if step == -1:

                        #created row and opposite_row to have the ability to move upwards and downwards by any piece (row - maximum in the direction we moved in before, opposite_row - the opposite direction)
                        row = max(r - 3, -1)
                        opposite_row = min(r + 3, ROWS)
                    else:
                        row = min(r + 3, ROWS)
                        opposite_row = max(r - 3, -1)
                    #record the current length of dict moves
                    length = [len(moves)]
                    moves.update(self._traverse_left(r + step, row, step, color, left - 1, skipped=last + skipped))
                    moves.update(self._traverse_right(r + step, row, step, color, left + 1, skipped=last + skipped))
                    moves.update(self._traverse_left(r-step, opposite_row, -step, color, left-1, skipped=last + skipped))

                    # if len(moves) > length[0]:
                    #     delete_pair_by_value(moves, last)

                break
            #if there is our piece in this square - we cant move here, so break
            elif current.color == color:
                break

            #if there is a piece in the square and it is not of our color - then we can move further (last piece will be the piece we are jumping through now)
            else:
                last = [current]

            left -= 1

        return moves

    def _traverse_right(self, start, stop, step, color, right, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= COLS:
                break

            current = self.board[r][right]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, right)] = last + skipped
                else:
                    moves[(r, right)] = last

                if last:
                    if step == -1:

                        #description in traverse_left
                        row = max(r - 3, -1)
                        opposite_row = min(r + 3, ROWS)
                    else:
                        row = min(r + 3, ROWS)
                        opposite_row = max(r - 3, -1)
                    # record the current length of dict moves
                    length = [len(moves)]
                    moves.update(self._traverse_left(r + step, row, step, color, right - 1, skipped=last + skipped))
                    moves.update(self._traverse_right(r + step, row, step, color, right + 1, skipped=last + skipped))
                    moves.update(self._traverse_right(r - step, opposite_row, -step, color, right + 1, skipped=last + skipped))
                    #if len(moves) > length[0]:
                        #delete_pair_by_value(moves, last)

                    #delete_pair_by_value(moves, last)
                break
            elif current.color == color:
                break
            else:
                last = [current]

            right += 1

        return moves

#Delete the pair key-value from dictionary by value
def delete_pair_by_value(dictionary, value):
    keys_to_delete = []
    for key, val in dictionary.items():
        if val == value:
            keys_to_delete.append(key)

    for key in keys_to_delete:
        del dictionary[key]