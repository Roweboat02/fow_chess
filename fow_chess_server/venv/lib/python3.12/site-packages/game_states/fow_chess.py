# pylint: disable=C0415
"""
fow_chess.py
Game state representation

self citation: part of the fog generation algorithm,
 and some bitboard to numpy functionality was taken from Noah's personal code repo

Author: Noah Rowe
Date: 2022/02/21
Last Modified: 2022/02/23
    Added docstrings
"""
from __future__ import annotations

import random
from functools import cached_property
from math import log
from typing import List, Set

from basic_data import Bitboard
from basic_data import Move
from basic_data import reverse_scan_for_square
from basic_data import ChessBitboards
from basic_data import SpecialMoveBitboards
from game_states._functions_for_fow_chess import _possible_move_generator, _visible_squares
from game_states.board_packet import BoardPacket


class FOWChess:
    """
    Represents a state of a fog of war chess game.
    """
    WHITE = True
    BLACK = False

    def __init__(self,
                 bitboards: ChessBitboards,
                 turn: bool,
                 special_moves: SpecialMoveBitboards,
                 half_move: int
                 ) -> None:
        # immutable

        self.__current_turn: bool = turn  # color of the current player

        # Integer bitboards of both colors and all pieces
        self.__bitboards: ChessBitboards = bitboards

        # Bitboards for castling/ep bitboards
        self.__special: SpecialMoveBitboards = special_moves

        self.__half_move: int = half_move

    def __repr__(self):
        s=""
        for i in self.bitboards.to_board():
            s += str(i)+"\n"
        return s

    def __hash__(self) -> int:
        """Quick and dirty hash"""
        return hash(
            tuple([*self.__bitboards, *self.__special, self.__current_turn])
        )

    def __eq__(self, other: FOWChess) -> bool:
        """Quick and dirty equality"""
        return (self.bitboards == other.bitboards
                and self.special_moves == other.special_moves
                and self.current_turn == other.current_turn)

    @classmethod
    def new_game(cls) -> FOWChess:
        """
        Alternate constructor for a FOWChess game.
        Creates game in the standard chess board starting position.
        """
        return cls(
            bitboards=ChessBitboards.new_game(),
            turn=cls.WHITE,
            special_moves=SpecialMoveBitboards.new_game(),
            half_move=0)

    def from_fow(self: FOWChess, move: Move) -> FOWChess:
        """
        Create a new fow game state,
        by applying a move to an existing fow game state
        """
        new_bitboards: ChessBitboards = self.bitboards.make_move(move)
        return self(
            bitboards=new_bitboards,
            turn=not self.current_turn,
            special_moves=self.special_moves.update(self.bitboards, move),
            half_move=self.half_move+1)

    @property
    def current_turn(self) -> bool:
        """Color of the current player. True if white, False if black"""
        return self.__current_turn

    @property
    def bitboards(self) -> ChessBitboards:
        """Bitboards representing pieces and colors"""
        return self.__bitboards

    @property
    def special_moves(self) -> SpecialMoveBitboards:
        """Bitboards representing ep and castling bitboards"""
        return self.__special

    @cached_property
    def possible_moves_list(self) -> List[Move]:
        """List of possible legal moves"""
        return list(_possible_move_generator(self))

    @cached_property
    def possible_moves_set(self) -> Set[Move]:
        """List of possible legal moves"""
        return set(self.possible_moves_list)

    @property
    def winner(self) -> bool | None:  # maybe make this a class
        """Return True if white, False if Black, None if not over."""
        white: int = self.bitboards.white & self.bitboards.kings
        black: int = self.bitboards.black & self.bitboards.kings
        if white == black:
            return None
        elif not white:
            return self.BLACK
        elif not black:
            return self.WHITE
        return None

    @property
    def is_over(self) -> bool:  # TODO: better termination checks
        """True if 1 king left on board"""
        kings = self.bitboards.kings
        kings ^= 1 << (kings.bit_length()-1)
        return (kings==0)

    @property
    def half_move(self) -> int:
        """The half_move number of the current state"""
        return self.__half_move

    def create_board_packet(self, perspective: bool) -> BoardPacket:
        """
        Create a BoardPacket from this state,
        from perspective of a player
        """
        bitboards: ChessBitboards = self.bitboards
        moves: List[Move] = (self.possible_moves_list.copy()
                             if perspective == self.current_turn else [])

        return BoardPacket(
            bitboards=bitboards,
            perspective=perspective,
            current_turn=self.current_turn,
            possible_moves=moves,
            half_move=self.half_move,
            winner=self.winner,
            is_over=self.is_over,
            visible=self.visible(perspective=perspective)
        )

    def make_random_move(self) -> FOWChess:
        """
        Make and return a FOWChess instance,
        by making a random move from the given states possible moves
        """
        return self.from_fow(self, random.choice(self.possible_moves_list))

    def visible(self, perspective: bool) -> Bitboard:
        """A bitboard representing squares outside the fog (as 1's)"""
        return _visible_squares(self, perspective)

    def occupied_by_color(self, color: bool) -> Bitboard:
        """White's bitboard if True, black's if False"""
        return self.bitboards.white if color else self.bitboards.black
