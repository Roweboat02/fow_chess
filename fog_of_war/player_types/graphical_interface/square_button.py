from __future__ import annotations

from typing import Callable, Dict

from basic_data import Piece
import tkinter as tk
from tkinter import Button



class SquareButton:
    piece_to_img: Dict[int, str] = {Piece.K.value: "K",  # "♔",
                           Piece.Q.value: "Q",  # "♕",
                           Piece.R.value: "R",  # "♖",
                           Piece.B.value: "B",  # "♗",
                           Piece.N.value: "N",  # "♘",
                           Piece.P.value: "P",  # "♙",
                           Piece.k.value: "k",  # "♚",
                           Piece.q.value: "q",  # "♛",
                           Piece.r.value: "r",  # "♜",
                           Piece.b.value: "b",  # "♝",
                           Piece.n.value: "n",  # "♞",
                           Piece.p.value: "p",  # "♟",
                           15: "~",
                           0: " "
                           }


    def __init__(self,tkinter_window:tk.Tk, move_callback:Callable[[...], bool], white:bool):
        self.tk_win:tk.Tk = tkinter_window
        self.piece: int
        self._callback: Callable[[...], bool] = move_callback
        self.button: Button|None = None
        self.button_color: str = 'white' if white else 'red'

    def draw(self, row:int, col:int):
        self.button.grid(row=row, column=col)

    def load(self, piece:int):
        self.piece:int = piece
        if self.button is not None:
            self.button.config(text=self.piece_to_img[piece])
        else:
            self._create_button()

    def _create_button(self):
        text:str = self.piece_to_img[self.piece]
        self.button = Button(self.tk_win, command=self._on_tap, text=text, bg=self.button_color)
        self.selected_based_on_piece_value()

    def selected_based_on_piece_value(self):
        self.selection_state(self.piece == 15)

    def selection_state(self, selected:bool):
        if selected:
            self.button['state'] = tk.DISABLED
        else:
            self.button['state'] = tk.NORMAL

    def _on_tap(self):
        print("Pressed!")
        if self.button['state'] == tk.NORMAL:
            self._callback()
        else:
            self.selected_based_on_piece_value()

        self.tk_win.update()
        self.tk_win.update_idletasks()
            #     self.selection_state(False)
            # else:
            #     self.button.flash()
