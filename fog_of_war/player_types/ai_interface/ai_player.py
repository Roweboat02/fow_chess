"""
ai_player.py
Class for communicating between TreeSearch (or some other FOW chess algorithm) and the model.

Author: Noah Rowe
Date: 2022/04/04
"""
from __future__ import annotations

from game_states.board_packet import BoardPacket
from player_types.abstract.abstract_player import AbstractPlayer
from .tree_seach import TreeSearch


class AIPlayer(AbstractPlayer):
    """Interface between MCTS algorithm and model"""

    def restart(self): pass

    def __init__(self):
        """Perspective:bool is white(True) or black(False)"""
        super().__init__()
        self.tree_search = None
        self.tree_search: TreeSearch  # TreeSearch algorithm

    def _receive_color(self, color: bool):
        self.tree_search = TreeSearch(color)

    def _receive_board(self, board: BoardPacket):
        """Receive a new BoardPacket from model (FOWReferee)"""
        self.tree_search.add_to_information_state(self.latest)
        if board.winner is None:
            self.ready_to_start = True

    def _start_making_move(self):  # Set ready_to_send and move_to_send, if appropriate
        self.ready_to_start = False

        if self.latest.current_turn is self.perspective:
            self.move_to_send = self.tree_search.start_search(self.latest, 150)
            self.ready_to_send = True
        else:
            self.tree_search.start_search(self.latest, 50)
            self.ready_to_send = False
            self.move_to_send = None
