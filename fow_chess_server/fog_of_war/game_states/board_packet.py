"""
Noah Rowe
(made a while ago, but has kept changing as the project changes,
 I think around beginning of march. CHECK IN GIT (I'll prob forget))

Last updated: 2022/04/05 - Added documentation and fixed is_over

A class for holding data describing a game state.
"""
from __future__ import annotations

from typing import List


from basic_data import Bitboard
from basic_data import ChessBitboards
from basic_data import Move
from basic_data import Square


# def apply_fog(board: np.ndarray, visible: np.ndarray) -> np.ndarray:
#     """
#     Given a numpy array representing a board and the visible squares on it,
#     fog up the board.
#     """
#     foggy_board: np.ndarray = board.copy()
#     foggy_board[np.logical_not(visible)] = 15
#     return foggy_board


class BoardPacket:
    """
    Data class for model->player
    The hope was to keep this JSON-able for transfering it around.
    """

    def __init__(self,
                 bitboards: ChessBitboards,
                 perspective:bool,
                 current_turn: bool,
                 visible: Bitboard,
                 possible_moves: List[Move],
                 half_move: int,
                 is_over: bool,
                 winner: bool | None):
        board = bitboards.to_board()
        vis = visible.to_list()
        # Immutable
        self.__board = [[j if vis[i_ind][j_ind] else "F" for j_ind,j in enumerate(i)] for i_ind, i in enumerate(board)]
        self.__perspective = perspective
        # I made it a numpy arrays because neural networks like them,
        # but other repersentations are possible
        # For is the number 15, other numbers follow encoding in Piece enum

        # What "half_move" number the game was on at the time of creation.
        self.__half_move: int = half_move

        self.__turn: bool = current_turn  # whos turn it is

        self.__possible_moves: List[Move] = possible_moves  # A list of potential legal moves

        self.__winner: None | bool = winner  # if anyone has won, that will be distributed here
        self.__is_over: bool = is_over  # winner could be None if draw.
        # There's a billion places where black and white
        # (or black and white and one of many third states)
        # need to be differentiated between.
        # I don't want to make a billion enums,
        # or one bad general purpose one.
        # Let me have this or fix it yourself
        # (That goes for anyone grading to! FIGHT ME).
    @property
    def flipped_board(self):
        return [[j for j in i[::-1]] for i in self.__board[::-1]]
    def __dict__(self):
        return {
            "board":self.__board if self.__perspective else self.flipped_board,
            "half_move":self.__half_move,
            "perspective":self.__perspective,
            "turn":self.__turn,
            "possible_moves":[i.__dict__() for i in self.__possible_moves],
            "winner":self.__winner,
            "is_over":self.__is_over
            }

    def __hash__(self):
        """Quick and dirty hash"""
        return hash(str(self.__board) + str(self.__half_move))

    # Casting to strings above and below as a dumb shortcut

    def __eq__(self, other: BoardPacket):
        """Quick and dirty equality"""
        return (
            # str(self.__foggy_board) + str(self.__half_move) + str(self.__possible_moves) ==
            # str(other.foggy_board) + str(other.half_move) + str(other.possible_moves_list))
                str(self.__board) + str(self.__half_move) ==
                str(other.__board) + str(other.half_move))

    def __getitem__(self, key: Square) -> int:
        """
        Index array with Squares
        (if you want.
        I mean, just use the board's getter if you don't)
        """
        return self.__board[8 - key.rank, key.file - 1]
