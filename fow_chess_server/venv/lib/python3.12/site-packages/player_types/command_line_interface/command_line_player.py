"""
Noah Rowe 2022/04/06
Started trying to make a CLI for debugging, but time is ticking.
"""
from __future__ import annotations

from typing import List

from game_states import MoveFragmentMap
from game_states.board_packet import BoardPacket
from player_types.abstract.abstract_player import AbstractPlayer
from player_types.command_line_interface.command_line_functions import await_player_move


class CommandlinePlayer(AbstractPlayer):

    def __init__(self):
        super().__init__()
        self.state_stack: List[BoardPacket] = []
        self.fragment_map: MoveFragmentMap

    def _receive_board(self, board: BoardPacket):
        print(board.foggy_board)
        
        self.state_stack.append(board)
        self.fragment_map = MoveFragmentMap(board)

    def _start_making_move(self):  # Set ready_to_send and move_to_send, if appropriate
        if self.latest.current_turn is self.perspective:
            self.move_to_send = await_player_move(self.latest)
        self.ready_to_send = True

    def _receive_color(self, color: bool):
        pass

    def restart(self): pass
