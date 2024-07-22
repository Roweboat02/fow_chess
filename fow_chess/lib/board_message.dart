import 'package:fow_chess/move.dart';

class BoardMessage {
  List<List<String>> board;
  bool perspective;
  bool turn;
  List<Move> moves;
  int halfMove;
  bool isOver;
  bool? winner;
  BoardMessage(this.board, this.perspective, this.turn, this.moves,
      this.halfMove, this.isOver, this.winner);
}
