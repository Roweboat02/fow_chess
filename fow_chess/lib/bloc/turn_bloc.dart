import 'package:bloc/bloc.dart';
import 'package:fow_chess/board_message.dart';
import 'package:fow_chess/move.dart';
import 'package:fow_chess/server_proxy.dart';
part 'turn_event.dart';
part 'turn_state.dart';

class TurnBloc extends Bloc<TurnEvent, TurnState> {
  ServerProxy sp;

  TurnBloc(this.sp) : super(AwaitPlayers()) {
    on<PiecePickedUp>(_piecePickedUp);
    on<PieceLaidDown>(_pieceLaidDown);
    on<NewTurnStart>(_newMove);
    sp.emit = add;
    sp.listenForBoard();
  }

  void _pieceLaidDown(PieceLaidDown event, Emitter<TurnState> emit) {
    Set<List<int>> toSqrs =
        (state.board.moves.map((Move e) => e.toSqr)).toSet();
    if (toSqrs.contains(event.toSqr)) {
      emit(PieceLaid(state.board, event.piece, event.frmSqr, event.toSqr));
      sp.turn(Move(event.frmSqr, event.toSqr));
    } else {
      emit(NewTurn(state.board));
    }
  }

  void _piecePickedUp(PiecePickedUp event, Emitter<TurnState> emit) {
    Set<List<int>> frmSqrs =
        (state.board.moves.map((Move e) => e.frmSqr)).toSet();
    if (frmSqrs.contains(event.frmSqr) &&
        state.board.turn == state.board.perspective) {
      emit(PieceHeld(state.board, event.piece, event.frmSqr));
    } else if (state.board.turn == state.board.perspective) {
      emit(NewTurn(state.board));
    }
  }

  void _newMove(NewTurnStart event, Emitter<TurnState> emit) {
    emit(NewTurn(event.board));
  }
}
