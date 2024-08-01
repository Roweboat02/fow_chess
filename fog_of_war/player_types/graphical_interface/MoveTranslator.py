from __future__ import annotations

from typing import Callable

from basic_data import Move, Square, Piece
from game_states import MoveFragmentMap, BoardPacket


class MoveTranslator:

    def __init__(self, perspective:bool, send_move:Callable):
        self.perspective:bool = perspective
        self.fragment_map: MoveFragmentMap|None = None
        self.send_move:Callable = send_move
        self.selected_square:Square|None = None

    def receive_board(self, board:BoardPacket):
        self.fragment_map = MoveFragmentMap(board)

    def _callback_maker(self, sqr: Square) -> Callable[[None], bool]:
        def cb() -> bool:
            self._receive_button_calling(sqr=sqr)
            return True
        return cb


    def _receive_button_calling(self, sqr: Square) -> bool:  # this should be handled by someone else
        print("Translator received")
        if self.fragment_map is not None:
            print(sqr)
            if self.selected_square is None:
                if sqr in self.fragment_map.fragment_map.keys():
                    print("Selected: ", sqr)
                    self.selected_square = sqr
                    return True
            elif self.selected_square == sqr:
                print("deselected")
                self.selected_square = None
            else:
                if sqr in self.fragment_map[self.selected_square].keys():
                    move: Move = self.fragment_map[self.selected_square][sqr]
                    print(move)
                    if move == Move(frm=self.selected_square, to=sqr):
                        self.send_move(move)
                        self.fragment_map = None
                        return True
                    elif move.rook_to is not None:
                        self.send_move(move)
                        self.fragment_map = None
                        return True
                    elif move.promotion_to is not None:
                        # Promotions auto to queen for now.
                        self.fragment_map = None
                        self.send_move(
                            Move(frm=self.selected_square,
                                 to=sqr,
                                 promotion_to=Piece.Q if self.perspective else Piece.q))
                        return True

        return False
