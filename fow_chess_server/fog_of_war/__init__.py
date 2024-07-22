"""
The fog of war package contains:

chess data representations:
bitboards,
moves,
board squares,
chess pieces

Collections of bitboards for:
Pieces and colors,
special moves

The above classes are used to make a fog of war class, which holds a fog of war game state.
"""
import fog_of_war.basic_data as bd
from fog_of_war.game_states import BoardPacket, FOWChess
import fog_of_war.game as game
