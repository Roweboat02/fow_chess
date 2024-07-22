"""
Noah Rowe 2022/04/05
Started trying to make a GUI for debugging, but time is ticking.

CURENTYL BROKE
"""
from __future__ import annotations

from typing import Callable, List
import tkinter as tk

from basic_data import Move, Square
from game_states.board_packet import BoardPacket
from player_types.abstract.abstract_player import AbstractPlayer
from player_types.graphical_interface.MoveTranslator import MoveTranslator
from player_types.graphical_interface.button_board import ButtonBoard


class GraphicalPlayer(AbstractPlayer):
    def __init__(self):
        self.tk_win:tk.Tk = tk.Tk()
        self.tk_win.title= "Game"

        self._board:BoardPacket
        self._gui_board:ButtonBoard
        self._translator:MoveTranslator = MoveTranslator()

        self.send_move_callback: Callable
        self.state_stack: List[BoardPacket] = []

        self.ready_to_send: bool = False
        self.move_to_send: Move|None

        self.ready_to_send_square:bool = False
        self.square_to_send:Square|None

        tk.mainloop()
    
    def _receive_board(self, board: BoardPacket):
            
        self.state_stack.append(board)
        self.fragment_map = MoveFragmentMap(board)

    def _receive_move(self, move:Move) -> bool:
        print("received move from translator")
        self.move_to_send = move
        self.ready_to_send = True
        return True

    def receive_move_callback(self, callback: Callable[[Move, int], bool]):
        self.send_move_callback = callback

    def send_move(self, move: Move) -> bool:
        self.ready_to_send = False
        if self.send_move_callback is not None:
            return self.send_move_callback(move, self.latest.half_move)
        else:
            return False

    def receive_board(self, board: BoardPacket):
        self.state_stack.append(board)
        self.move_translator.receive_board(board)
        self.board.load(board)

    def receive_color(self, color:bool):
        self.move_translator =  MoveTranslator(color, self._receive_move)
        self.board = ButtonBoard(self.tk_win, self.receive_square, color)

    def receive_square(self, sqr:Square):
        self.square_to_send = sqr
        self.ready_to_send_square = True
        return True

    def send_square(self):
        self.move_translator._receive_button_calling(sqr=self.square_to_send)
        self.square_to_send = None

    @property
    def latest(self) -> BoardPacket|None:
        return self.state_stack[-1] if self.state_stack else None

    def restart(self): pass
