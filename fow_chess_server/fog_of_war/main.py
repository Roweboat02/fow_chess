"""
main.py
Starts the game.

Noah Rowe
2022/04/04
"""
from __future__ import annotations

from functools import partial
from random import random
from typing import Tuple, Callable

from player_types.abstract.abstract_player import AbstractPlayer
from game.fow_referee import FOWReferee
from player_types.ai_interface import AIPlayer
# from player_types.command_line_interface.command_line_player import CommandlinePlayer
from player_types.command_line_interface.command_line_player import CommandlinePlayer
from player_types.graphical_interface.graphical_player import GraphicalPlayer


def game_init(player_a: AbstractPlayer, player_b: AbstractPlayer, ref: FOWReferee):
    """
    Start a game between player_a and player_b, with ref as the referee
    """
    # rand_turn: bool = random() < 0.5
    rand_turn = True  # Committee voted true to be most random
    player_a.receive_color(rand_turn)
    player_b.receive_color(not rand_turn)

    players: Tuple[AbstractPlayer, AbstractPlayer] = (
        (player_b, player_a)
        if rand_turn else
        (player_a, player_b)
    )

    ref.start_game(players)


if __name__ == "__main__":
    referee: FOWReferee = FOWReferee()
    # user: AbstractPlayer = AIPlayer()
    # mcts_bot: AbstractPlayer = AIPlayer()

    user_a: AbstractPlayer = CommandlinePlayer()
    user_b: AbstractPlayer = CommandlinePlayer()

    start: Callable = partial(game_init, ref=referee, player_a=user_a, player_b=user_b)

    FOWReferee.restart = start
    user_a.restart = start
    user_b.restart = start

    start()
    while True:
        if referee.ready_to_distribute and (not user_a.ready_to_start and not user_b.ready_to_start):
            referee.distribute()

        if user_b.ready_to_start is True:
            user_b.start_making_move()

        if user_a.ready_to_start is True:
            user_a.start_making_move()

        if user_b.ready_to_send is True:
            user_b.send_move()

        if user_a.ready_to_send is True:
            user_a.send_move()
