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
from player_types.command_line_interface.command_line_player import CommandlinePlayer
from threading import Thread

def game_init(player_a: AbstractPlayer, player_b: AbstractPlayer, ref: FOWReferee):
    """
    Start a game between player_a and player_b, with ref as the referee
    """
    rand_turn: bool = random() < 0.5
    # rand_turn = True  # Comittee voted true to be most random
    player_a.receive_color(rand_turn)
    player_b.receive_color(not rand_turn)

    players: Tuple[AbstractPlayer, AbstractPlayer] = (
        (player_b, player_a)
        if rand_turn else
        (player_a, player_b)
    )

    ref.start_game(players)
    return player_a, player_b, ref


def restart_init(player_a: AbstractPlayer, player_b: AbstractPlayer, ref: FOWReferee):
    start: Callable = partial(game_init, ref=ref, player_a=player_a, player_b=player_b)

    FOWReferee.restart = start
    player_a.restart = start
    player_b.restart = start

    return start

def thread_init(player_a, player_b):
    # user: CommandlinePlayer = CommandlinePlayer()
    thread_a:Thread = Thread(target=player_a)
    thread_b:Thread = Thread(target=player_b)

    return thread_a, thread_b

def main(player_a: AbstractPlayer, player_b: AbstractPlayer, referee: FOWReferee):
    while True:
        if referee.ready_to_distribute:
            referee.distribute()

        if referee.ready_to_receive:
            pass

        if player_a.ready_to_start:
            player_a.start_making_move()

        if player_b.ready_to_start:
            player_b.start_making_move()

        if player_a.ready_to_send_move:
            player_a.send_move()

        if player_b.ready_to_send_move:
            player_b.send_move()

if __name__ == "__main__":
    player_a, player_b, ref = restart_init(*game_init(AIPlayer(), AIPlayer(), FOWReferee()))
    thread_a, thread_b = thread_init(player_a, player_b)

    main_thread = Thread(target=partial(main, player_a=player_a, player_b=player_b, referee=ref))
