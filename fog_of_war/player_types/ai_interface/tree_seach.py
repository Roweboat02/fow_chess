"""
tree_search.py
Class searching the game state tree and estimating best moves.

Author: Noah Rowe
Date: 2022/04/04

added garbage collection 2022/04/05
"""
from __future__ import annotations

import random
from collections import defaultdict
from statistics import mean
from typing import List, DefaultDict, Dict, Tuple

from basic_data import Move
from game_states.board_packet import BoardPacket
from game_states.fow_chess import FOWChess
from .node import Node, best_child, ucb


class TreeSearch:
    """Modified MCTS algorithm"""

    def __init__(self, perspective: bool):
        self.information_states: Dict[int, BoardPacket] = {}
        self.all_nodes: DefaultDict[int, List[Node]] = defaultdict(list)

        # Always assume the opponent (and consequently, yourself) can en_passent.
        # If they couldn't
        self.root: Node = Node(
            game=FOWChess.new_game(),
            move=None,
            perspective=perspective,
            all_nodes=self.all_nodes,
            information_states=self.information_states,
            # special=self.our_special_move_bitboards,
        )

        self.latest: BoardPacket | None = None

    def create_root(self, perspective):
        self.root: Node = Node(
            game=FOWChess.new_game(),
            move=None,
            perspective=perspective,
            all_nodes=self.all_nodes,
            information_states=self.information_states)
        # special=self.our_special_move_bitboards & (Bitboard.from_rank(1) if perspective else Bitboard.from_rank(8))

    def add_to_information_state(self, board: BoardPacket) -> None:
        """
        Add a new piece of information (a BoardPacket) to the information_states,
        and mark any nodes that may already exist at the same half_move_number,
        which don't jibe with the new board, as "invalid"
        """
        self.information_states[board.half_move] = board
        # print("Pruning....")
        # print(f"Before: {len(self.all_nodes[board.half_move])}")
        # node_list:List[Node] = self.all_nodes[board.half_move]
        # for node in node_list:
        #     for
        # self.all_nodes[board.half_move] = [node for node in self.all_nodes[board.half_move] if
        #                                    node.incomplete_game_state == board]
        # print(f"After: {len(self.all_nodes[board.half_move])}")
        self.latest = board

    def start_search(self, board: BoardPacket, simulations: int = 20) -> Move:
        """
        Start a modified MCTS to find a move to make.

        A simulation that didn't succsessfully find
        a state the "unfogged" game could be in
        doesn't count toward the parameter simulations.

        PRE: board is a new piece of info about the other players previous move
            (So it's this players move now)
        """
        # self.add_to_information_state(board)  # New info gained
        print("MCTS search started....")
        this_should_never_ever_happen: int = 100_000

        while simulations > 0:
            if self._state_estimator_mcts(self.root):
                this_should_never_ever_happen = 100_000
                simulations -= 1
                if simulations % 10 == 0:
                    print(f"simulations remaining: {simulations}")
            else:
                this_should_never_ever_happen -= 1
                if this_should_never_ever_happen < 0:
                    break

        else:  # n simulations have been run
            move_scores: DefaultDict[Move, List[int]] = defaultdict(list)
            for _node in self.all_nodes[board.half_move]:
                if _node.visited and not _node.invalid_state:
                    for _child in _node.children:
                        move_scores[_child.move].append(_child._visits)
            averaged_move_scores: Dict = {move: mean(visits) for move, visits in move_scores.items()}
            try:
                move: Move = max(averaged_move_scores, key=lambda x: averaged_move_scores[x])
            except ValueError as e:
                print("Ruh Roh")
                print("")
                raise e
            return move

        # 100_000 times in a row,
        # a possible state the board could currently be in, was unable to be found
        # I'm never expecting this to occur, but random moves are better than no moves?
        return random.choice(board.possible_moves_list)  # Just in case....

    # This function was modified from my personal repo -Noah
    def _best_move_estimator_mcts(self, node: Node) -> bool | None:
        """
        Standard MCTS used to estimate the best move leaving param node.
        Returns true if white won, false if black one, none if tie
        None==Draw because I'm tired of enums. Let me have this.

        PRE: Node is still considered to be valid, and so are all nodes traversed to arrive here
        Assumes no info is known about what the next state the board could be
        (i.e. any children would be in the future, with respect to the game being analyzed)
            Not *actually* important, it's just pretty inefficient to use this if you know that info
        """
        result: bool | None

        if node.invalid_state:
            return

        if node.game_state.is_over:
            # Found an end to the game.
            result = node.game_state.winner

        elif not node.visited:
            # Found a potential future game state, that has not been considered yet
            node.populate()  # Add its children to the tree, mark it as visited.
            # (no info is known on if children are valid or not)

            result = node.rollout()  # make random moves until the game is over

        else:
            # Node is a potential future node. Continue search with its most promising child
            result = self._best_move_estimator_mcts(node.best_child)

        # Search ended, a result was determined.
        # Backpropogate result up call stack
        node.update_score(result)

        return result

    def _state_estimator_mcts(self, node: Node) -> Tuple[bool,bool]:
        """
        A kinda-MCTS used to estimate the current game state, unaffected by fog.
         @param node is the node currently being operated on (if calling make it the start node).
        Returns true if the simulation found a possible valid current state, false if it failed.
        """
        # PRE: The node is closer to the start then the end of the information states
        # This implies the node could (not definite) be determined to be invalid
        # (but has not already has been determined to be so)
        # As we have information on the state the board at this point in time.
        # PRE: No nodes traversed to get to this node are invalid.

        # POST: Either an invalid node will be found (mark it as invalid)
        # Or a valid node which could be the un-fogged position that the board is in
        # is found (start normal mcts)
        # In either case, the path of possible past states traversed on this run will be updated

        result: bool

        # NOTE: node can't be a winning state, as if a winning state is part of the info set,
        # the search wouldn't have been called
        current_half_move = max(self.information_states.keys())

        if node.depth <= current_half_move:
            if not node.visited:
                node.populate()
                rollout = node.rollout()
                node.update_score(True, rollout)
                return True, rollout

            if node.depth==current_half_move:
                return True, self._best_move_estimator_mcts(best_child(node, wins_or_led_to=True))
            return self._state_estimator_mcts(best_child(node, wins_or_led_to=False))



        node.update_score(result)
        return result
