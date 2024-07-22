"""
Noah Rowe: The man who almost didn't have to make any abstract classes ;(
2022/02/30
"""
from typing import Callable

from abc import ABC, abstractmethod

from basic_data import Move
from game_states import BoardPacket

from threading import Thread

from player_types.abstract.abstract_player import AbstractView
from player_types.command_line_interface.command_line_player import CommandlinePlayer

"""Protocol for how a model talks to a view"""

class ThreadingAbstractView(Thread, AbstractView):
    def __init__(self, target=None, name=None, args=(), kwargs={}, daemon=None, player_class=CommandlinePlayer):
        Thread.__init__(self, target=None, name=None, args=(), kwargs={}, daemon=None)
        self.player_class: Callable = CommandlinePlayer

    def start(self) -> None:
        """
        Starting the thread
        """
        self.player
    @abstractmethod
    def receive_color(self, color:bool):
        """
        Before the start of a game, receive what color you are playing as
        """

    @abstractmethod
    def receive_board(self, board:BoardPacket):
        """How model will send a BoardPacket"""

class AbstractController(ABC):
    """Protocol for how a controller and model talk"""

    # def __init__(self, perspective:bool): pass
    # Perspective being the color of a player
    @abstractmethod
    def receive_move_callback(self, callback:Callable[[Move, int], bool]):
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
