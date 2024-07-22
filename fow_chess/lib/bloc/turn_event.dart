part of 'turn_bloc.dart';

abstract class TurnEvent {}

class PiecePickedUp implements TurnEvent {
  String piece;
  List<int> frmSqr;
  PiecePickedUp(this.piece, this.frmSqr);
}

class PieceLaidDown implements TurnEvent {
  String piece;
  List<int> frmSqr;
  List<int> toSqr;
  PieceLaidDown(this.piece, this.frmSqr, this.toSqr);
}

class NewTurnStart implements TurnEvent {
  BoardMessage board;
  NewTurnStart(this.board);
}
