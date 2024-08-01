"""
node.py
Class for building a tree of game states to be searched by an MCTS type algorithm

Self citation: Code based off code from my personal repos (close to everything has changed tho)

Author: Noah Rowe
Date: 2022/04/04

added garbage collection 2022/04/05
"""
from __future__ import annotations

import random
from typing import List, Dict, DefaultDict, Set, Callable

from math import sqrt, log

from basic_data import Move, SpecialMoveBitboards, Bitboard
from game_states.board_packet import BoardPacket
from game_states.fow_chess import FOWChess


# This function was modified from my personal repo -Noah
def ucb(node:Node, c_const: float = 1.41, wins_or_led_to:bool=True) -> Node | None:
    """
    Find valid child in children list with the greatest upper confidence bound.
    UCB given by UCB(v,vi) = Q(vi)/N(vi) + c*[ln(N(v))/N(vi)]^1/2
    Where v is current node, vi is a valid child,
    c is an exploitation constant,
    Q() gives score of a node,
    N() gives visits to a node,
    """
    if wins_or_led_to:
        ucb_values = [_child._wins_and_losses / _child._visits +
                      c_const * sqrt(log(node._visits) / _child._visits)
                      for _child in node.children]
    else:
        ucb_values = [_child._led_to_viable_state / _child._visits +
                      c_const * sqrt(log(node._visits) / _child._visits)
                      for _child in node.children]

    return (node.children[ucb_values.index(max(ucb_values))]
            if ucb_values is not None
            else None)


# This function was modified from my personal repo -Noah
def best_child(node:Node, wins_or_led_to:bool=True) -> Node | None:
    """
    Will find the optimal child, if one exists.
    Assumes node has already been populated, and is not considered invalid.

    If no valid children are found, None will be returned (This shouldn't happen)
    In that case, if all children have been visited,
    and the game is not over, the node will be marked invalid
    (This really shouldn't ever happen)
    """
    unvisited: List[Node] = node._unvisited_list
    if unvisited:
        return unvisited.pop(random.randint(0, len(unvisited) - 1))

    best: Node | None = ucb(node, wins_or_led_to)

    if best is None and node.visited and not node.game_state.is_over:
        node._invalid_state = True
    return best

class Node:
    """
    Tree node contains a game state, connected nodes are immediately reachable
    game states.
    """

    def __init__(self,
                 game: FOWChess,
                 move: Move | None,
                 perspective: bool,
                 all_nodes: DefaultDict[int, List[Node]],
                 information_states: Dict[int, BoardPacket]) -> None:

        self.game_state: FOWChess = game  # The game state this node represents

        # What this node's game state would look like if it were foggy
        # (from the perspective of the AI's color)
        self.incomplete_game_state: BoardPacket = self.game_state.create_board_packet(perspective)

        self.move: Move | None = move  # The edge traversed to arrive at this node

        self._perspective = perspective  # The color of the AI

        # The two attibutes below could be static,
        # but that would mean competing AI would interfere with each other.
        # Consider them static to a tree_searcher

        # A key/value pair mapping between
        # a half_move number and all the nodes at that point in time
        self._all_nodes: DefaultDict[int, List[Node]] = all_nodes

        # A key/value pair mapping
        # half move numbers to the information known at that point in time
        self._information_states: Dict[int, BoardPacket] = information_states

        self.visited: bool = False  # has the node been populated?
        self._invalid_state: bool = False  # Has the node contradicted the set of information?

        self.possible_move_set: Set[Move] = self.game_state.possible_moves_set
        self._children: List[Node] = []  # Children nodes (filled at population)
        # self._unvisited_list: List[Node] = []  # Filled at population and popped 1 by 1
        # (to save having to search the children list)

        # Node stats for UCB calculation
        self._visits: int = 0
        self._led_to_viable_state: int = 0
        self._wins_and_losses: int = 0

        # Add itself to the set of nodes at this point in time.
        self._all_nodes[game.half_move].append(self)

    # def prune_children(self, official_move_set:Set[Move]):
    #     if diff:=self.possible_move_set.difference(official_move_set):
    #         self.possible_move_set.difference(diff)

    # def mark_invalid(self):
    #     self._invalid_state = True
    #     if self in self._all_nodes[self.depth]:
    #         self._all_nodes[self.depth].remove(self)

    @property
    def _unvisited_list(self) -> List[Node]:
        return [child for child in self.children if not child.visited]

    @property
    def invalid_state(self) -> bool:
        return self._invalid_state

    @property
    def children(self):
        if self.depth < max(self._information_states.keys()):
            self._children = [_child for _child in self._children]
        return self._children

    @property
    def depth(self):
        """How many half_moves deep the node is from the start"""
        return self.game_state.half_move

    def rollout(self) -> bool:  # This function was modified from my personal repo -Noah
        """
        Make random moves until terminal state is found.
        Returns True if white won, Black if false, None if tie

        Assumes node is not invalid.
        """
        game: FOWChess = self.game_state
        depth: int = self.depth
        while not game.is_over:
            game = game.make_random_move()
            depth += 1
        return game.winner

    @property
    def score(self) -> int:
        """
        Will return the led_to_viable_state metric
        if node's depth is less than the half move of the
        future-most Boardpacket in the information states.
        Else, will return the win/loss metic
        """
        if self.depth < max(self._information_states.keys()):
            return self._led_to_viable_state
        return self._wins_and_losses

    def populate(self) -> None:
        """Create children from possible next moves"""
        self.visited = True
        self._children = [Node(
            game=FOWChess.from_fow(self.game_state, move),
            move=move,
            perspective=self._perspective,
            information_states=self._information_states,
            all_nodes=self._all_nodes) for move in self.game_state.possible_moves_list]

        # self._unvisited_list = self.children.copy()

    def update_score(self, led_to_result: bool, win_result:bool|None) -> None:
        """
        Backpropogate outcome up path.
        If outcome matches the turn, increase. Else decrease.
        """
        self._visits += 1  # Each node is visited if it's on the back propagation trail.

        if self.depth < max(self._information_states.keys()):
            # If info is known about this point in time,
            # a succsess means it led to a possible current game state
            self._led_to_viable_state += 1 if led_to_result else -1

        else:
            if result == self.game_state.current_turn:
                # If player who'e turn it is in the game state, won
                self._wins_and_losses += 1
            elif (not result) is self.game_state.current_turn:
                # If player of the game state lost
                self._wins_and_losses -= 1
            else:
                # If game ended in a tie
                # (tie is better than a loss, and worse than a win, so do nothing)
                pass

    def belongs_to_information_states(self):
        """False if a node contradicts the set of information."""
        try:
            return self._information_states[self.depth] == self.incomplete_game_state
        except KeyError as e:
            print("Node depth: ", self.depth)
            print("Info states ", self._information_states)
            raise e
