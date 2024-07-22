"""
Noah Rowe
2022/04/05
moved some stupid big functions here for neatness
also the visible squares and possible move functions were once based on functions from
https://github.com/niklasf/python-chess/blob/master/chess/__init__.py
the python chess library.

They seem to work differently now, but the ordering is still similar.
Relatedly, those are also based on functions from before this semester, and also function differently.
"""
from typing import Iterable

from basic_data import Move, Bitboard, reverse_scan_for_square, Square, Piece \
    , reduce_with_bitwise_or
from basic_data import attk


# 'Best practice' calls for these to be made into a billion little functions
# But honestly I think making a bunch of little functions just to use them in FOWChess
# is less readable and takes more time than these huge massive ones.
# And they're all pretty specialized,
# so it's not like they'll be reused anywhere else.


def _anyone_attacking(self, square_mask: Bitboard) -> bool:
    """
    Using the principal of
    "Is one of their pieces attacking square" being logically the same as
    "If a piece of our color was on square, could it attack the same piece type of their color"
    determine if anyone is attacking square.
    """
    square: Square = Square(square_mask.bit_length())

    occupied = self.bitboards.black | self.bitboards.white
    their_pieces = self.occupied_by_color(not self.current_turn)

    r_and_f_attackers = (self.bitboards.queens | self.bitboards.rooks) & their_pieces
    diag_attackers = (self.bitboards.queens | self.bitboards.bishops) & their_pieces
    king_attackers = (self.bitboards.kings | self.bitboards.queens) & their_pieces
    knight_attackers = self.bitboards.knights & their_pieces

    return any((
            (self.bitboards.pawns
             & their_pieces
             & attk.pawn_attack_mask(square, self.current_turn)),
            ((attk.rank_moves(square, occupied) | attk.file_moves(square, occupied))
             & r_and_f_attackers),
            attk.diagonal_moves(square, occupied) & diag_attackers,
            attk.king_moves(square) & king_attackers,
            attk.knight_moves(square) & knight_attackers))


def _possible_move_generator(self) -> Iterable[Move]:
    """List of possible moves the current player can legally make."""

    our_pieces: Bitboard = self.occupied_by_color(self.current_turn)
    their_pieces: Bitboard = self.occupied_by_color(not self.current_turn)
    everyones_pieces: Bitboard = our_pieces | their_pieces

    # Generate non-pawn moves.
    for frm_sqr in reverse_scan_for_square(our_pieces & ~self.bitboards.pawns):
        for to_sqr in reverse_scan_for_square(
                ~our_pieces &
                attk.non_pawn_move_mask(frm_sqr, self.bitboards.piece_at(frm_sqr), everyones_pieces)
        ):
            yield Move(to=to_sqr, frm=frm_sqr)

    # check for castling
    if (self.special_moves.castling_kings & our_pieces
            and self.special_moves.castling_rooks & our_pieces):

        backrank: Bitboard = (Bitboard.from_rank(1)
                              if self.current_turn else Bitboard.from_rank(8))

        a_mask: Bitboard = backrank & Bitboard.from_file(1)
        b_mask: Bitboard = backrank & Bitboard.from_file(2)
        c_mask: Bitboard = backrank & Bitboard.from_file(3)
        d_mask: Bitboard = backrank & Bitboard.from_file(4)

        f_mask: Bitboard = backrank & Bitboard.from_file(6)
        g_mask: Bitboard = backrank & Bitboard.from_file(7)
        h_mask: Bitboard = backrank & Bitboard.from_file(8)

        our_king_mask: Bitboard = self.bitboards.kings & our_pieces

        # Try for king side castle
        if (self.special_moves.castling_kings & our_pieces
                and self.special_moves.king_side_castling & our_pieces
                and not (everyones_pieces & (f_mask | g_mask))
                and not any(_anyone_attacking(self, square_mask)
                            for square_mask in (our_king_mask, f_mask, g_mask))):
            yield Move(to=Square(g_mask.bit_length()),
                       frm=Square(our_king_mask.bit_length()),
                       rook_to=Square(f_mask.bit_length()),
                       rook_frm=Square(h_mask.bit_length()))

        # Try for queen side
        if (self.special_moves.castling_kings & our_pieces
                and self.special_moves.queen_side_castling & our_pieces
                and not (everyones_pieces & (b_mask | c_mask | d_mask))
                and not any(_anyone_attacking(self, square)
                            for square in (our_king_mask, c_mask, d_mask))):
            yield Move(to=Square(c_mask.bit_length()),
                       frm=Square(our_king_mask.bit_length()),
                       rook_frm=Square(a_mask.bit_length()),
                       rook_to=Square(d_mask.bit_length()))

    # If there are pawns, generate their moves
    if pawns := self.bitboards.pawns & our_pieces:
        # First if they can attack anyone
        for frm_sqr in reverse_scan_for_square(pawns):
            for to_sqr in reverse_scan_for_square(
                    attk.pawn_attack_mask(frm_sqr, self.current_turn)
                    & their_pieces):
                yield Move(to_sqr, frm_sqr)

        forward_or_back: int

        # Then find their single and double moves
        backranks = (Bitboard.from_rank(8), Bitboard.from_rank(1))
        if self.current_turn:
            single_moves = (pawns << 8) & ~everyones_pieces
            single_moves = single_moves & ~backranks[0]
            double_moves = (single_moves << 8
                            & Bitboard.from_rank(4)
                            & ~everyones_pieces)
            forward_or_back = -1
        else:
            single_moves = pawns >> 8 & ~everyones_pieces
            single_moves = single_moves & ~backranks[1]
            double_moves = (
                    single_moves >> 8
                    & Bitboard.from_rank(5)
                    & ~everyones_pieces)
            forward_or_back = 1

        # The &MAX is definitely a bandaid for *something*.
        # But I was getting a ValueError of 65+
        # Which I have no idea how that's possible since
        # I'm negating single moves with the backrank?
        # That's also why thats on different lines above ^^^
        for to_sqr in reverse_scan_for_square(single_moves & Bitboard.MAX()):
            yield Move(to_sqr, Square(to_sqr.value + (8 * forward_or_back)))

        for to_sqr in reverse_scan_for_square(double_moves & Bitboard.MAX()):
            yield Move(to_sqr, Square(to_sqr.value + (16 * forward_or_back)))

        # Promotions
        if backranks[self.current_turn] & single_moves:
            for pawn in reverse_scan_for_square(single_moves & backranks[self.current_turn]):
                for promote in (2, 3, 4):
                    yield Move(to=pawn,
                               frm=Square(pawn.value + (8*forward_or_back)),
                               promotion_to=Piece(
                                       promote * (-1 if not self.current_turn else 1)
                               ))

        # Check for en passent
        if (self.special_moves.ep_bitboard
                and not self.special_moves.ep_bitboard & everyones_pieces):
            # "Is there one of our pawns attacking the ep square?"
            # is logically the same question as
            # "If there was one of their pawns on the ep square,
            #   would it be attacking one of our pawns?"
            ep_square: Square = Square(self.special_moves.ep_bitboard.bit_length())
            for frm_sqr in reverse_scan_for_square(
                    attk.pawn_attack_mask(ep_square, not self.current_turn) & pawns):
                yield Move(ep_square, frm_sqr, en_passent=True)


def _visible_squares(self, perspective: bool) -> Bitboard:
    """
    Generate a bitboard of squares which should not be visible to the @param perspective
    (where True is white and black is False)
    """

    visible: Bitboard = Bitboard(0)

    our_pieces: Bitboard = Bitboard(self.occupied_by_color(perspective))
    their_pieces: Bitboard = Bitboard(self.occupied_by_color(not perspective))
    everyones_pieces: Bitboard = our_pieces | their_pieces

    visible |= our_pieces

    # Generate non-pawn moves.
    piece_moves = reduce_with_bitwise_or(
            *(attk.non_pawn_move_mask(frm,
                                      self.bitboards.piece_at(frm),
                                      everyones_pieces
                                      ) & ~our_pieces
              for frm in (reverse_scan_for_square(our_pieces & ~self.bitboards.pawns)))
    )
    visible |= piece_moves

    # If there are pawns, generate their moves
    if pawns := self.bitboards.pawns & our_pieces:
        # First if they can attack anyone
        pawn_attacks = reduce_with_bitwise_or(
                *(attk.pawn_attack_mask(frm, perspective) & their_pieces
                  for frm in reverse_scan_for_square(pawns))
        )
        visible |= pawn_attacks

        # Then find their single and double moves
        if perspective:
            single_moves = pawns << 8 & ~everyones_pieces
            double_moves = single_moves << 8 & Bitboard.from_rank(4) & ~everyones_pieces

        else:
            single_moves = pawns >> 8 & ~everyones_pieces
            double_moves = single_moves >> 8 & Bitboard.from_rank(5) & ~everyones_pieces
        visible |= single_moves | double_moves

        # Finally, check if an en passant is available
        if (self.special_moves.ep_bitboard
                and not (everyones_pieces
                         & self.special_moves.ep_bitboard)):
            ep_square: Square = Square(self.special_moves.ep_bitboard.bit_length())
            visible |= reduce_with_bitwise_or(
                    *(Bitboard.from_square(frm_sqr) for frm_sqr in reverse_scan_for_square(
                            attk.pawn_attack_mask(ep_square, not self.current_turn) & pawns)))

    return Bitboard(visible)
