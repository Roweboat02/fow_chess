"""
Noah Rowe
Whenever I made this (End of March? CHECK GIT)

2022/02/05 - Added documentation

A way to oragnize moves for parsing/verifying moves
"""
from __future__ import annotations

from typing import List, Dict

from basic_data import Move, Square, Piece
from game_states import BoardPacket


class MoveFragmentMap:
    """
    A way of organizing moves,
    such that it's easier to parse if a given part of a move
    is part of a move in this map
    """

    def __init__(self, board: BoardPacket):
        # Immutable
        fragment_map: Dict[Square, Dict[Square, Move]] = {
            move.frm: {} for move in board.possible_moves_list}

        for move in board.possible_moves_list:
            fragment_map[move.frm][move.to] = move

        self.__fragment_map: Dict[Square, Dict[Square, Move]] = fragment_map

        self.__frm_square: Square | None = None
        self.__to_square: Square | None = None
        self.__promotion_to: Piece | None = None
        self.__promotion_square: Square | None
        self.__move: Move | None = None

    def clear(self):
        self.__to_square = None
        self.__frm_square = None
        self.__move = None
        self.__promotion_to = None

    def attempt_add_square(self, sq: Square) -> bool:
        if self.__frm_square is None:
            if sq in self.fragment_map:
                self.__frm_square = sq
                return True
            return False
        elif self.__to_square is None:
            if sq in self.fragment_map[self.__frm_square]:
                self.__to_square = sq
                move = self.fragment_map[self.__frm_square][self.__to_square]
                if (move == Move(frm=self.__frm_square, to=self.__to_square)
                        or (move.rook_to is not None and move.rook_frm is not None)):
                    self.__move = Move
                    return True
        return False

    def attempt_add_promotable_square(self, sqr: Square) -> bool:
        if sqr in self.fragment_map:
            if sqr in self.fragment_map[sqr]:
                self.__promotion_square = sqr
                return True
        return False

    def attempt_add_promotion_to(self, piece: Piece) -> bool:
        # Assumes piece is a valid promotion to type!
        if self.__frm_square is not None:
            if self.__frm_square in self.fragment_map[self.__frm_square]:
                self.__move = Move(frm=self.__frm_square, to=self.__to_square, promotion_to=piece)
                return True
        return False

    @property
    def move(self) -> Move:
        return self.__move

    @property
    def frm_square(self) -> Square:
        return self.__frm_square

    @property
    def to_square(self) -> Square:
        return self.__to_square

    @property
    def fragment_map(self) -> Dict[Square, Dict[Square, Move]]:
        """Fragment map getter"""
        return self.__fragment_map

    @property
    def promotion_square(self) -> Square:
        return self.__promotion_square

    @property
    def promotion_to(self) -> Piece:
        return self.__promotion_to

    def __getitem__(self, key0: Square) -> Dict[Square, Move]:
        """Index using two Squares (from and to respectively)"""
        return self.__fragment_map[key0]
