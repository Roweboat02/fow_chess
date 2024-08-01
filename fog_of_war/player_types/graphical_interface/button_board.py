"""
Noah Rowe 2022/04/05
Started trying to make a GUI for debugging, but time is ticking.
"""
from __future__ import annotations

from functools import partial
from typing import Dict, Callable, List

import tkinter as tk

from basic_data import Square, Move, Piece
from game_states import BoardPacket, MoveFragmentMap
from player_types.graphical_interface.square_button import SquareButton


class ButtonBoard:
    def __init__(self, tkinter_window:tk.Tk, button_callback:Callable, perspective:bool):
        self.tkinter_window:tk.Tk = tkinter_window
        self._button_map: Dict[Square, SquareButton] = {
                sqr:SquareButton(tkinter_window=tkinter_window,
                                 move_callback=partial(button_callback, sqr=sqr),
                                 white=sqr.color) for sqr in Square
        }
        self.perspective:bool = perspective

    def draw_board(self):
        for sqr in Square:
            if self.perspective:
                self._button_map[sqr].draw(8 - sqr.rank, sqr.file - 1)

            else:
                self._button_map[sqr].draw(sqr.rank - 1, sqr.file - 1)

        self.tkinter_window.update()
        self.tkinter_window.update_idletasks()

    def load(self, board:BoardPacket):
        self.fragment_map = MoveFragmentMap(board)
        self.perspective = board.perspective
        for sqr in Square:
            self._button_map[sqr].load(board[sqr])

        self.draw_board()

    def load_buttons(self, board:BoardPacket):
        for sqr in Square:
            self._button_map[sqr].load(board[sqr])
