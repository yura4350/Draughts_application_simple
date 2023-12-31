import pygame
from .constants import BLACK, ROWS, RED, SQUARE_SIZE, COLS, WHITE
from .piece import Piece


class Board:
    def __init__(self):
        self.board = []
        self.red_left = ((ROWS-2) // 2) * COLS // 2
        self.white_left = ((ROWS-2) // 2) * COLS // 2
        self.red_kings = self.white_kings = 0
        self.create_board()

    def draw_squares(self, win):
        win.fill(BLACK)
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                pygame.draw.rect(win, RED, (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def evaluate(self):
        evaluation = self.white_left - self.red_left + (self.white_kings * 2 - self.red_kings * 2)
        #print(self.white_left - self.red_left + (self.white_kings * 0.5 - self.red_kings * 0.5))
        pieces_white = self.get_all_pieces(WHITE)
        pieces_black = self.get_all_pieces(BLACK)
        for piece in pieces_white:
            #evaluation += piece.row/100
            evaluation -= abs(3.5 - piece.col)/50
        for piece in pieces_black:
            #evaluation -= (7 - piece.row) / 100
            evaluation += abs(3.5 - piece.col)/50
        return evaluation

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

        #this piece of code checks the condition where a king should be made
        if piece.color == WHITE:
            if row == ROWS - 1:
                piece.make_king()
                self.white_kings += 1
        else:
            if row == 0:
                piece.make_king()
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
            moves.update(self._traverse_left_king(row - 1, -1, -1, piece.color, left))
            moves.update(self._traverse_right_king(row - 1, -1, -1, piece.color, right))
            moves.update(self._traverse_left_king(row + 1, ROWS, 1, piece.color, left))
            moves.update(self._traverse_right_king(row + 1, ROWS, 1, piece.color, right))

            max_length = 0

            for key, value in moves.items():
                if len(value) > max_length:
                    max_length = len(value)

            new_moves = {key: value for key, value in moves.items() if len(value) == max_length}

            values = []

            if max_length > 0:
                for key, value in new_moves.items():
                    if value not in values:
                        values.append(value)

            #list of keys to be deleted
            list_of_keys_to_delete = []
            #list of keys which should not be deleted when going through other values
            list_of_undeletable_keys = []
            #problem is here
            if max_length > 0:
                #looping through all values
                for value_first in values:
                    print(value_first)
                    print(values)
                    #we get diagonal so we can understand what to look for: sum or difference of rows and columns
                    updown_diagonal= True
                    sum = -1
                    difference = -1
                    #checking value
                    for key, value in new_moves.items():
                        if value == value_first:
                            if abs(key[0] - value[0].row) == 1 and abs(key[1] - value[0].col) == 1:
                                if key[0] + key[1] == value[0].row + value[0].col:
                                    updown_diagonal = False
                                else:
                                    updown_diagonal = True

                    if updown_diagonal == True:
                        for key, value in new_moves.items():
                            if key[0] - key[1] != value[0].row - value[0].col and value_first == value:
                                list_of_keys_to_delete.append(key)
                            else:
                                list_of_undeletable_keys.append(key)

                    else:
                        for key, value in new_moves.items():
                            if key[0] + key[1] != value[0].row + value[0].col and value_first == value:
                                list_of_keys_to_delete.append(key)
                            else:
                                list_of_undeletable_keys.append(key)


            print(new_moves, 1)
            print(list_of_undeletable_keys, 5)
            print(list_of_keys_to_delete, 6)

            for key in list_of_keys_to_delete:
                if key not in list_of_undeletable_keys:
                    del new_moves[key]

            print(new_moves, 2)

            moves = new_moves




        #Include the rule of the necessary take of the most pieces possible

        max_length = 0

        #find maximum length of the take (max_length)
        for key, value in moves.items():
            if len(value) > max_length:
                max_length = len(value)

        #create new list of moves, which will only include moves, in which you can take the most pieces
        new_moves = {key: value for key, value in moves.items() if len(value) == max_length}

        return new_moves

    def get_checked_valid_moves(self, piece):
        moves = self.get_valid_moves(piece)
        max_to_take = self.get_max_to_take(piece.color)
        new_moves = {}

        for move, skip in moves.items():
            if len(skip) == max_to_take:
                new_moves[move] = skip

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
                if current in skipped:
                    print(1)
                    break
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
                if current in skipped:
                    print(1)
                    break
                last = [current]

            right += 1

        return moves

    def _traverse_left_king(self, start, stop, step, color, left, skipped=[], prev=False, change_of_direction=False, passed=[]):
        moves = {}

        # last - the last piece we skipped to move to this point
        last = []

        for r in range(start, stop, step):

            # The situation we are now looking outside of the board
            if left < 0:
                break

            current = self.board[r][left]

            if current != 0 and current.color != color:
                if prev:
                    break
                else:
                    prev = current.color


            # check if the cell we are in is empty
            if current == 0:

                prev = False

                # The case when we skipped a piece and have not seen a piece yet

                # double+ jump
                if skipped:
                    # combine the last checker we jumped and the checker on this move
                    moves[(r, left)] = last + skipped

                # if it is 0 and last existed - we can jump over it
                else:
                    moves[(r, left)] = last + skipped
                    #print(last, 3)

                # we found an empty square and last has a value in it - we had something we skipped over


                if step == -1:

                    # created row and opposite_row to have the ability to move upwards and downwards by any piece (row - maximum in the direction we moved in before, opposite_row - the opposite direction)
                    row = -1
                    opposite_row = ROWS
                else:
                    row = ROWS
                    opposite_row = -1
                # record the current length of dict moves
                length = [len(moves)]
                if change_of_direction == True:
                    moves.update(self._traverse_left_king(r + step, row, step, color, left - 1, skipped=last + skipped, prev = prev, change_of_direction=True, passed=passed))
                    moves.update(self._traverse_right_king(r + step, row, step, color, left + 1, skipped=last + skipped, prev = prev, change_of_direction=False, passed=passed))
                    moves.update(self._traverse_left_king(r - step, opposite_row, -step, color, left - 1, skipped=last + skipped, prev = prev, change_of_direction=False, passed=passed))
                else:
                    moves.update(self._traverse_left_king(r + step, row, step, color, left - 1, skipped=last + skipped,prev=prev, change_of_direction=False, passed=passed))

                    # if len(moves) > length[0]:
                    #     delete_pair_by_value(moves, last)


                break
            # if there is our piece in this square - we cant move here, so break
            elif current.color == color:
                break

            # if there is a piece in the square and it is not of our color - then we can move further (last piece will be the piece we are jumping through now)
            else:

                if current in passed:
                    print(1)
                    break
                last = [current]
                passed = passed + last
                change_of_direction=True
            last = [current]

            #print(last, 4)

            left -= 1

        return moves

    def _traverse_right_king(self, start, stop, step, color, right, skipped=[], prev=False, change_of_direction=False, passed=[]):
        moves = {}
        last = []


        for r in range(start, stop, step):
            if right >= COLS:
                break

            current = self.board[r][right]

            if current != 0 and current.color != color:
                if prev:
                    break
                else:
                    prev = current.color

            if current == 0:
                prev = False
                if skipped:
                    moves[(r, right)] = last + skipped
                else:
                    #print(last, 1)
                    moves[(r, right)] = last+skipped



                if step == -1:

                    # description in traverse_left
                    row = -1
                    opposite_row = ROWS
                else:
                    row = ROWS
                    opposite_row = -1
                # record the current length of dict moves
                length = [len(moves)]


                if change_of_direction == True:
                    moves.update(self._traverse_right_king(r + step, row, step, color, right + 1, skipped=last + skipped,prev=prev, change_of_direction=True, passed=passed))
                    moves.update(self._traverse_left_king(r + step, row, step, color, right - 1, skipped=last + skipped, prev=prev, change_of_direction=False, passed=passed))
                    moves.update(self._traverse_right_king(r - step, opposite_row, -step, color, right + 1, skipped=last + skipped, prev = prev, change_of_direction=False, passed=passed))
                else:
                    moves.update(self._traverse_right_king(r + step, row, step, color, right + 1, skipped=last + skipped,prev=prev, change_of_direction=False, passed=passed))
                # if len(moves) > length[0]:
                    # delete_pair_by_value(moves, last)

                    # delete_pair_by_value(moves, last)
                break

            elif current.color == color:
                break

            else:
                if current in passed:
                    print(1)
                    break
                last = [current]
                passed = passed + last
                change_of_direction = True

            last = [current]

            #print(last, 2)


            right += 1

        return moves

    #the function identifies the maximum amount of pieces we can take
    def get_max_to_take(self, color):
        moves = {}
        max_skipped = 0

        for piece in self.get_all_pieces(color):
            valid_moves = self.get_valid_moves(piece)
            for move, skip in valid_moves.items():
                if len(skip) > max_skipped:
                    max_skipped = len(skip)

        return max_skipped

#Delete the pair key-value from dictionary by value
def delete_pair_by_value(dictionary, value):
    keys_to_delete = []
    for key, val in dictionary.items():
        if val == value:
            keys_to_delete.append(key)

    for key in keys_to_delete:
        del dictionary[key]