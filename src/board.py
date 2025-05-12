from const import *
from square import Square
from piece import *
from move import Move
from sound import Sound
import os

class Board:

    def __init__(self):
        self.squares = [[0, 0, 0, 0, 0, 0, 0, 0] for col in range(COLS)]
        self.last_move = None
        self.next_player = 'white'  # Track whose turn it is
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')

    def move(self, piece, move, testing=False):
        initial = move.initial
        final = move.final

        # Store undo information
        captured_piece = self.squares[final.row][final.col].piece
        was_en_passant = False
        if isinstance(piece, Pawn) and abs(initial.col - final.col) == 1 and captured_piece is None:
            was_en_passant = True
            captured_piece = self.squares[initial.row][final.col].piece

        # Perform the move
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece

        if was_en_passant:
            self.squares[initial.row][final.col].piece = None

        if isinstance(piece, Pawn):
            self.check_promotion(piece, final)

        if isinstance(piece, King):
            if self.castling(initial, final):
                diff = final.col - initial.col
                rook_col = 0 if diff < 0 else 7
                rook_final_col = 3 if diff < 0 else 5
                rook = self.squares[initial.row][rook_col].piece
                self.squares[initial.row][rook_col].piece = None
                self.squares[initial.row][rook_final_col].piece = rook
                rook.moved = True

        piece.moved = True
        piece.clear_moves()
        self.last_move = move

        # Switch player
        self.next_player = 'black' if self.next_player == 'white' else 'white'

        return {
            'piece': piece,
            'move': move,
            'captured_piece': captured_piece,
            'was_en_passant': was_en_passant,
            'promoted_to': None if not isinstance(piece, Pawn) or final.row not in [0, 7] else self.squares[final.row][final.col].piece
        }

    def undo_move(self, undo_info):
        piece = undo_info['piece']
        move = undo_info['move']
        captured_piece = undo_info['captured_piece']
        was_en_passant = undo_info['was_en_passant']
        promoted_to = undo_info['promoted_to']

        # Revert the move
        self.squares[move.final.row][move.final.col].piece = captured_piece
        self.squares[move.initial.row][move.initial.col].piece = piece

        if was_en_passant:
            self.squares[move.initial.row][move.final.col].piece = captured_piece

        if promoted_to:
            self.squares[move.initial.row][move.initial.col].piece = Pawn(piece.color)

        if isinstance(piece, King) and self.castling(move.initial, move.final):
            diff = move.final.col - move.initial.col
            rook_col = 0 if diff < 0 else 7
            rook_final_col = 3 if diff < 0 else 5
            rook = self.squares[move.initial.row][rook_final_col].piece
            self.squares[move.initial.row][rook_final_col].piece = None
            self.squares[move.initial.row][rook_col].piece = rook
            rook.moved = False

        piece.moved = False
        self.last_move = None

        # Switch player back
        self.next_player = 'white' if self.next_player == 'black' else 'black'

    def evaluate(self):
        if len(self.get_all_possible_moves(self.next_player)) == 0:
            if self.in_check(self.next_player):
                return -100000 if self.next_player == 'white' else 100000  # Checkmate
            else:
                return 0  # Stalemate

        score = 0
        for row in range(ROWS):
            for col in range(COLS):
                if self.squares[row][col].has_piece():
                    piece = self.squares[row][col].piece
                    score += piece.value
                    # Bonus for developed pieces
                    if piece.moved and piece.name in ['knight', 'bishop', 'rook']:
                        score += 0.1 if piece.color == 'white' else -0.1
                    # Bonus for central pawns
                    if piece.name == 'pawn' and col in [3, 4] and row in [3, 4]:
                        score += 0.2 if piece.color == 'white' else -0.2
        return score

    def get_all_possible_moves(self, color):
        moves = []
        for row in range(ROWS):
            for col in range(COLS):
                if self.squares[row][col].has_team_piece(color):
                    piece = self.squares[row][col].piece
                    self.calc_moves(piece, row, col, bool=True)
                    for move in piece.moves:
                        if self.squares[move.final.row][move.final.col].has_piece():
                            move.value = self.squares[move.final.row][move.final.col].piece.value
                        else:
                            move.value = 0
                        moves.append(move)
        moves.sort(key=lambda m: m.value, reverse=True if color == 'white' else False)
        return moves

    def alphabeta(self, depth, alpha, beta, maximizing_player):
        if depth == 0 or self.is_game_over():
            return self.evaluate(), None

        moves = self.get_all_possible_moves('white' if maximizing_player else 'black')

        if maximizing_player:
            max_eval = float('-inf')
            best_move = None
            for move in moves:
                piece = self.squares[move.initial.row][move.initial.col].piece
                undo_info = self.move(piece, move)
                eval, _ = self.alphabeta(depth - 1, alpha, beta, False)
                self.undo_move(undo_info)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            for move in moves:
                piece = self.squares[move.initial.row][move.initial.col].piece
                undo_info = self.move(piece, move)
                eval, _ = self.alphabeta(depth - 1, alpha, beta, True)
                self.undo_move(undo_info)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def is_game_over(self):
        return len(self.get_all_possible_moves(self.next_player)) == 0

    def calc_moves(self, piece, row, col, bool=True):
        # (Existing move calculation logic remains unchanged)
        pass

    def valid_move(self, piece, move):
        return move in piece.moves

    def check_promotion(self, piece, final):
        if final.row == 0 or final.row == 7:
            self.squares[final.row][final.col].piece = Queen(piece.color)

    def castling(self, initial, final):
        return abs(initial.col - final.col) == 2

    def set_true_en_passant(self, piece):
        # (Existing en passant logic remains unchanged)
        pass

    def in_check(self, color):
        # (Existing check detection logic remains unchanged)
        pass

    def _create(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)

    def _add_pieces(self, color):
        row_pawn, row_other = (6, 7) if color == 'white' else (1, 0)
        for col in range(COLS):
            self.squares[row_pawn][col].piece = Pawn(color)
        self.squares[row_other][0].piece = Rook(color)
        self.squares[row_other][1].piece = Knight(color)
        self.squares[row_other][2].piece = Bishop(color)
        self.squares[row_other][3].piece = Queen(color)
        self.squares[row_other][4].piece = King(color)
        self.squares[row_other][5].piece = Bishop(color)
        self.squares[row_other][6].piece = Knight(color)
        self.squares[row_other][7].piece = Rook(color)