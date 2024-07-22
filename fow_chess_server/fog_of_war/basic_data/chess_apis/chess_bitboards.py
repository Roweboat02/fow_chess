# Can't have a low pylint score if you disable all checks. *Taps forehead*
# Disabled because pylint doesn't like the Square class
# Or using "self" as a namedtuple
# pylint: disable=E1136, E1133
"""
chess_bitboards.py
ChessBitboards hold piece and color bitboards for a chess game.

Author: Noah Rowe
Date: 2022/02/22
    Was part of bitboards.py
Modified
    2022/02/23 - Added docstrings
    2022/02/24 - moved special move bitboards into its own file
            and renamed this one from chess_apis chess_bitboards
"""
from __future__ import annotations

from typing import NamedTuple, List

from functools import reduce

from basic_data import Bitboard
from basic_data import Move
from basic_data import Piece
from basic_data import Square


class ChessBitboards(NamedTuple):
    """
    ChessBitboards is a NamedTuple subclass.
    Holds bitboards recording piece location for both colors and all chess pieces.
    """
    black: Bitboard
    white: Bitboard
    pawns: Bitboard
    knights: Bitboard
    bishops: Bitboard
    rooks: Bitboard
    queens: Bitboard
    kings: Bitboard

    def to_board(self) -> list:
        """
        A numpy representation of the chess board, using integers.
        See Piece enum for encoding
        """
        kings = [["K" if j else ""  for j in i] for i in Bitboard(self.kings).to_list()]
        queens = [["Q" if j else "" for j in i] for i in Bitboard(self.queens).to_list()]
        pawns = [["P" if j else "" for j in i] for i in Bitboard(self.pawns).to_list()]
        rooks = [["R" if j else "" for j in i] for i in Bitboard(self.rooks).to_list()]
        bishops = [["B" if j else "" for j in i] for i in Bitboard(self.bishops).to_list()]
        knights = [["N" if j else "" for j in i] for i in Bitboard(self.knights).to_list()]
        all = (kings,queens, pawns,rooks, bishops,knights)
        b=[[reduce(lambda a,b: a+b, [board[i][j] for board in all]) for j in range(8)] for i in range(8)]
        return [[b[i_ind][j_ind].lower() if j else b[i_ind][j_ind] for j_ind,j in enumerate(i)] for i_ind,i in enumerate(Bitboard(self.black).to_list())]
        # return (
        #                Bitboard(self.kings).to_numpy() * Piece['K'].value
        #                + Bitboard(self.queens).to_numpy() * Piece['Q'].value
        #                + Bitboard(self.pawns).to_numpy() * Piece['P'].value
        #                + Bitboard(self.rooks).to_numpy() * Piece['R'].value
        #                + Bitboard(self.bishops).to_numpy() * Piece['B'].value
        #                + Bitboard(self.knights).to_numpy() * Piece['N'].value
        #        ) * (
        #                Bitboard(self.black).to_numpy() * -1
        #                + Bitboard(self.white).to_numpy()
        #        )

    def piece_at(self, square: Square) -> Piece | None:
        """If a piece is at square, return its value, else return None"""
        piece_bbs: List[int] = [i * bool(bb & Bitboard.from_square(square))
                                for bb, i in zip(self, [-1, 1, 1, 2, 3, 4, 5, 6])]
        if any(piece_bbs):
            possible_piece: int = sum(piece_bbs[0:2]) * sum(piece_bbs[2:])
            if possible_piece:
                return Piece(possible_piece)
        return None

    @classmethod
    def new_game(cls) -> ChessBitboards:
        """Create a new Bitboards representing a new chess game"""
        return cls(
            white=Bitboard.from_rank(1) | Bitboard.from_rank(2),

            black=Bitboard.from_rank(7) | Bitboard.from_rank(8),

            pawns=Bitboard.from_rank(7) | Bitboard.from_rank(2),

            knights=(Bitboard.from_square(Square.b1)
                     | Bitboard.from_square(Square.g1)
                     | Bitboard.from_square(Square.b8)
                     | Bitboard.from_square(Square.g8)),

            bishops=(Bitboard.from_square(Square.c1)
                     | Bitboard.from_square(Square.f1)
                     | Bitboard.from_square(Square.c8)
                     | Bitboard.from_square(Square.f8)),

            rooks=(Bitboard.from_square(Square.a8)
                   | Bitboard.from_square(Square.h8)
                   | Bitboard.from_square(Square.a1)
                   | Bitboard.from_square(Square.h1)),

            queens=(Bitboard.from_square(Square.d1)
                    | Bitboard.from_square(Square.d8)),

            kings=(Bitboard.from_square(Square.e8)
                   | Bitboard.from_square(Square.e1))
        )

    def make_move(self, move: Move) -> ChessBitboards:
        """Clear move.frm and set move.to in the same bitboard. Clear move.to"""

        if move.promotion_to is None or not move.en_passent:
            def search(current_bb: Bitboard,
                       frm_mask: Bitboard,
                       to_mask: Bitboard):
                if current_bb & to_mask:
                    # If the to square is already set in a BB, we're capturing it, Therefore clear it
                    current_bb ^= to_mask

                if move.rook_to is not None and current_bb & Bitboard.from_square(move.rook_frm):
                    # If there's a rook move, we're castling. Clear frm and set to in rooks.
                    current_bb = ((current_bb
                                   ^ Bitboard.from_square(move.rook_frm))
                                  | Bitboard.from_square(move.rook_to))

                if current_bb & frm_mask:
                    # If frm is set, this is the piece we're moving. Clear it and set to in the same bb
                    current_bb = (current_bb ^ frm_mask) | to_mask

                return current_bb

            return ChessBitboards(
                *(search(current_bb,
                         frm_mask=Bitboard.from_square(move.frm),
                         to_mask=Bitboard.from_square(move.to))
                  for current_bb in self))

        # If we're here, we're either en passenting, or promoting.
        cpy: List[Bitboard] = list(self)
        cpy[2] = self.pawns ^ Bitboard.from_square(move.frm) # In either case we don't need the pawn on the from square
        if move.promotion_to is not None:
            # if we're promoting, set the to square in the pieces bb high
            cpy[abs(move.promotion_to.value) + 1] = (
                    cpy[abs(move.promotion_to.value) + 1] ^ move.to.value
            )
        elif move.en_passent:
            # Remove the pawn that was en_passent'd
            # (must be same rank as origin and file as destination)
            cpy[2] = cpy[2] ^ Bitboard.from_square(Square(8*move.frm.rank + move.to.file))

            # Set the to square high for the pawn that did the enpassenting
            cpy[2] = cpy[2] ^ Bitboard.from_square(move.to)

        return ChessBitboards(*cpy)
