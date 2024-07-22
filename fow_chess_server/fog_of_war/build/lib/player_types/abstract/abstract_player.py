"""
Noah Rowe: The man who almost didn't have to make any abstract classes ;(



2022/02/30
"""
from __future__ import annotations

from typing import Callable

from abc import ABC, abstractmethod

from basic_data import Move
from game_states import BoardPacket


class AbstractView(ABC):
    """Protocol for how a model talks to a view"""

    @abstractmethod
    def receive_color(self, color: bool):
        """
        Before the start of a game, receive what color you are playing as
        """

    @abstractmethod
    def receive_board(self, board: BoardPacket):
        """How model will send a BoardPacket"""


class AbstractController(ABC):
    """Protocol for how a controller and model talk"""

    # def __init__(self, perspective:bool): pass
    # Perspective being the color of a player
    @abstractmethod
    def receive_move_callback(self, callback: Callable[[Move, int], bool]):
        """How the move callback is handed out by the model"""

    @abstractmethod
    def send_move(self):
        """Controllers need a method which uses the above callback"""

    @abstractmethod
    def restart(self):
        """Given on creation, see main.py"""


class AbstractPlayer(AbstractController, AbstractView, ABC):
    """
    The protocol of how a model expects to talk to a player entity
    Inherits from both AbstractController and AbstractView
    because they total like 4 methods.
    Use either both of those, this one, or neither. I'm not your mother.
    """

    def __init__(self):
        self.perspective: bool
        self.ready_to_start: bool = False
        self.ready_to_send: bool = False
        self.move_to_send: Move | None = None
        self.__latest__: BoardPacket | None = None
        self.move_callback: Callable[[Move, int], bool] = lambda x, y: False

    @property
    def half_move(self):
        return self.__latest__.half_move

    @property
    def latest(self):
        return self.__latest__

    def receive_color(self, color: bool):
        self.perspective = color
        self._receive_color(color)

    def send_move(self):
        self.ready_to_send = False
        if self.latest.current_turn is self.perspective:
            self.move_callback(self.move_to_send, self.latest.half_move)
        self.move_to_send = None
        self.move_callback = None
        self.ready_to_start = False

    def receive_move_callback(self, callback: Callable[[Move, int], bool]):
        self.move_callback = callback

    def receive_board(self, board: BoardPacket):
        # print("board received: ")
        # print(board.foggy_board)
        # print("\n")
        self.__latest__ = board
        self._receive_board(board)
        self.ready_to_start = True

    def start_making_move(self):  # Set ready_to_send and move_to_send, if appropriate
        self.ready_to_start = False
        self._start_making_move()

    def __call__(self): pass

    @abstractmethod
    def _start_making_move(self): pass

    @abstractmethod
    def _receive_color(self, color: bool): pass

    @abstractmethod
    def _receive_board(self, board: BoardPacket): pass
