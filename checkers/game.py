import pygame
from copy import deepcopy
from .constants import RED, WHITE, BLUE, SQUARE_SIZE
from checkers.board import Board


class Game:
    def __init__(self, win):
        self._init()
        self.win = win


    def update(self):
        self.board.draw(self.win)
        self.draw_valid_moves(self.valid_moves)
        pygame.display.update()

    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = RED
        self.valid_moves = {}

    def winner(self):
        return self.board.winner()

    def reset(self):
        self._init()

    def select(self, row, col):
        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.select(row, col)

        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_checked_valid_moves(piece)
            return True

        return False

    def _move(self, row, col):
        piece = self.board.get_piece(row, col)
        if self.selected and piece == 0 and (row, col) in self.valid_moves:
            self.board.move(self.selected, row, col)
            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board.remove(skipped)
            self.change_turn()
        else:
            return False

        return True

    #no need yet, maybe later
    def min_amount_of_pieces(self):

        all_possible_boards = self.get_all_moves(self.board, self.turn, self)
        #checking the amount of possible pieces
        min_white_left = self.board.white_left
        min_red_left = self.board.red_left

        # finding the least amount of pieces of the opposite side after our move to have the rule of necessity of taking the most pieces
        if self.turn == RED:
            for board in all_possible_boards:
                if board.white_left < min_white_left:
                    min_white_left = board.white_left
            return min_white_left
        else:
            for board in all_possible_boards:
                if board.red_left < min_white_left:
                    min_white_left = board.red_left
            return min_red_left

    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            pygame.draw.circle(self.win, BLUE,
                               (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), 15)


    def change_turn(self):
        self.valid_moves = {}
        if self.turn == RED:
            self.turn = WHITE
        else:
            self.turn = RED

    def get_board(self):
        return self.board

    def ai_move(self, board):
        self.board = board
        self.change_turn()



        # pygame.time.delay(100)