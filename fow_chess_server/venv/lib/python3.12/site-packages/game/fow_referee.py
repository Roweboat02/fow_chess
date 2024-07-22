"""
fow_referee.py
A class representing the model in a FOW game
Could theoretically be ran on a server,
it would just need some class pretending to be a player,
but is actually sending and receiving json'd BoardPackets and Moves.

CHECK GIT FOR CREATION TIME (sometime end of march)
last edited 2022/04/04 - added documentation

"""
from __future__ import annotations

import time

from collections import deque
from typing import Deque, List, Callable, Tuple

from basic_data import Move, Piece
from game_states import FOWChess, BoardPacket
from player_types.abstract.abstract_player import AbstractPlayer


class FOWReferee:
    """
    Model class for a fow game
    """

    WHITE = True
    BLACK = False

    def __init__(self):
        self._creation_time:str = str(time.time())

        self._state_stack: Deque[FOWChess] = deque()
        self._captured_list: List[Piece] = []

        # Using a list here would be totally fine, even on a browser 1v1 game.
        # BoardPacket would just need two static methods that json/un-jsons it.

        self._players: Tuple[AbstractPlayer, AbstractPlayer]  # Ordered black, white

        self.ready_to_distribute: bool = False

        self.ready_to_receive: bool = False

    def distribute(self):
        """
        Create and distribute BoardPackets to both players,
        and assign a move callback to whoever's turn it is.
        """
        # print("\nOfficial Game State: ")
        # print(self.current_state.bitboards.to_numpy())
        # print("\nOfficial possible moves: ")
        # print(self.current_state.possible_moves_list)
        # print("\n")

        self._players[self.current_turn].receive_move_callback(
            self._make_move_callback(self.half_move)
        )
        black: BoardPacket = self.current_state.create_board_packet(False)
        white: BoardPacket = self.current_state.create_board_packet(True)
        # with open("recorded_games."+self._creation_time, "a") as file:
        #     file.write(f"Half_move: {self.current_state.half_move}\n")
        #     file.write(f"Offical:\n {self.current_state.bitboards.to_numpy()}\n")
        #     file.write(f"Offical:\n {self.current_state.possible_moves_list}\n")
        #
        #     file.write(f"White:\n {white.foggy_board}")
        #     file.write(f"Black:\n {black.foggy_board}")

        self._players[True].receive_board(white),
        self._players[False].receive_board(black)
        self.ready_to_distribute = False
        self.ready_to_receive = True
        return

    def start_game(self, players: Tuple[AbstractPlayer, AbstractPlayer]) -> None:
        """Players should be ordered black, white"""
        self._state_stack: Deque[FOWChess] = deque([FOWChess.new_game()])

        self._players = players
        # self._distribute()
        self.ready_to_distribute = True

    def _make_move_callback(self, callback_valid_on: int) -> Callable[[Move, int], bool]:
        """
        Make a callback players can send moves on.
        For "added" security,
        players also have to input the half_move number they're on.
        Like, I don't think that should ever be an issue, but just in case I guess.
        """

        def _move_callback(move: Move, half_move: int) -> bool:
            if half_move == callback_valid_on:
                print("Validating move....")
                if not self._validate_move(move):
                    print("unable to validate")
                    return False
                self._enact_move(move=move)

                return True
            print("Callback invalid")
            return False

        return _move_callback

    def restart(self):
        """
        Start a new game
        """
        # Given to FOWReferee at server creation time

    @property
    def half_move(self) -> int:
        """The half move count of the most recent game state"""
        return self.current_state.half_move

    @property
    def current_state(self) -> FOWChess:
        """The most recent FOWChess game state"""
        return self._state_stack[-1]

    @property
    def current_turn(self) -> bool:
        """True if white, False if black"""
        return self.current_state.current_turn

    def _enact_move(self, move: Move) -> None:
        """
        Assumes inputed move is valid, and from the correct player.
        Create a new FOWChess node using the received move, then distribute BoardPackets.
        """
        self.ready_to_receive = False

        print("Enacting....")
        self._state_stack.append(self.current_state.from_fow(move))

        self.ready_to_distribute = True

    def _validate_move(self, move: Move) -> bool:
        """Test if a given move is in the set of possible next moves"""
        return move in self.current_state.possible_moves_set
