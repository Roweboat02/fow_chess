"""
Noah Rowe 2022/04/06
Started trying to make a CLI for debugging, but time is ticking.
"""
from __future__ import annotations

from basic_data import Square, Move, Piece
from game_states import BoardPacket, MoveFragmentMap


def await_player_move(board: BoardPacket):
    fragment_map: MoveFragmentMap = MoveFragmentMap(board)

    move: Move | None = None
    # print(board.foggy_board)
    while move is None:

        from_square: Square | None = None
        to_square: Square | None = None
        promotion_to: Piece | None = None

        while from_square is None:
            square_attempt: str = input("From square: ")
            try:
                sqr = Square[square_attempt]
                if sqr in fragment_map.fragment_map.keys():
                    from_square = sqr
                else:
                    print("Not a valid from square")
            except KeyError:
                print("Square not understood")

        while to_square is None:
            print("Type clear to re-enter from square")
            square_attempt: str = input("To square: ")
            if square_attempt == "clear":
                from_square = None
                break
            try:
                sqr = Square[square_attempt]
                if sqr in fragment_map.fragment_map[from_square].keys():
                    to_square = sqr
                else:
                    print("Not a valid to square")
            except KeyError:
                print("Square not understood")

        while move is None and (to_square is not None and from_square is not None):
            move = fragment_map.fragment_map[from_square][to_square]
            if move == Move(frm=from_square, to=to_square) or move.rook_to is not None:
                return move
            elif move.promotion_to is not None:
                while promotion_to is None:
                    print("Type clear to re-enter from square")
                    promote_attempt: str = input("Promote to (B, N, R, Q): ")
                    if promote_attempt == "clear":
                        break
                    elif promote_attempt in ('B', 'N', 'R', 'Q'):
                        try:
                            promotion_to = Piece[promote_attempt]
                            move = Move(frm=from_square, to=to_square, promotion_to=promotion_to)
                        except KeyError:
                            print("Piece not understood")
            else:
                print("Uh Oh! Dunno what that means, so I'm clearing\n")
                move = None
                break

        if move is None:
            print("\n")
            print(board.foggy_board)
        else:
            move = None
