import pygame

from const import *
from board import Board
from dragger import Dragger
from config import Config
from square import Square

class Game:

    def __init__(self):
        self.next_player = 'white'
        self.hovered_sqr = None
        self.board = Board()
        self.dragger = Dragger()
        self.config = Config()

    def show_bg(self, surface):
        # (Existing background rendering logic)
        pass

    def show_pieces(self, surface):
        # (Existing piece rendering logic)
        pass

    def show_moves(self, surface):
        # (Existing move highlighting logic)
        pass

    def show_last_move(self, surface):
        # (Existing last move highlighting logic)
        pass

    def show_hover(self, surface):
        # (Existing hover effect logic)
        pass

    def next_turn(self):
        self.next_player = 'white' if self.next_player == 'black' else 'black'

    def set_hover(self, row, col):
        self.hovered_sqr = self.board.squares[row][col]

    def change_theme(self):
        self.config.change_theme()

    def play_sound(self, captured=False):
        # (Existing sound logic)
        pass

    def reset(self):
        self.__init__()