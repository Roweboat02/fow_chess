"""
move.py
Dataclass for representing moves in a chess game

Author: Noah Rowe
Date: 2022/02/21
Last Modified: 2022/02/23
    Added docstrings
"""
import dataclasses
from dataclasses import dataclass
from typing import Optional

from basic_data.square import Square
from basic_data.piece import Piece


@dataclass(frozen=True)
class Move:
    """
    Use to and frm to specify a chess move.

    If move is a promotion,
     make to and frm equal,
     and specify the Piece promotion_to (None by default)
     assumes is promoted from pawn as that's the only legal promotion in chess

    If move is castling,
     make to and frm the squares the king moves to /from
     specify where the rook moves to and from using rook_to and rook_frm
     (both rook_to and rook_frm are None by default)
    """

    to: Square
    frm: Square
    rook_to: Optional[Square] = None
    rook_frm: Optional[Square] = None
    promotion_to: Optional[Piece] = None
    resignation: Optional[bool] = None
    en_passent: Optional[bool] = None

    def __dict__(self):
        return {
            "to":[self.to.rank,self.to.file],
            "frm":[self.frm.rank,self.frm.file],
            "rook_to": [self.rook_to.rank,self.rook_to.file] if self.rook_to else None,
            "rook_frm": [self.rook_frm.rank,self.rook_frm.file] if self.rook_frm else None,
            "promotion_to": self.promotion_to.name,
            "resignation": self.resignation,
            "en_passent": self.en_passent
            }

    @classmethod
    def from_json(json:dict):
        to: list[int] = json["to"]
        to = to[0]*8 + to[1]
        frm: list[int] = json["frm"]
        frm = frm[0]*8 + frm[1]
        to = Square(to)
        frm= Square(frm)

        try:
            rook_to = Square(json["rook_to"])
            rook_frm = Square(json["rook_frm"])
        except KeyError as e:
            rook_to = None
            rook_frm = None

        try:
            promotion_to = Piece(json["promotion_to"])
        except KeyError as e:
            promotion_to = None

        try:
            resignation: Optional[bool] = json["resignation"]
        except KeyError as e:
            resignation = None

        try:
            en_passent: Optional[bool] = json["en_passent"]
        except KeyError as e:
            en_passent = None

        return Move(
            to=to,
            frm=frm,
            rook_to=rook_to,
            rook_frm=rook_frm,
            promotion_to=promotion_to,
            resignation=resignation,
            en_passent=en_passent
            )
