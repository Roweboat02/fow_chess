part of 'turn_bloc.dart';

abstract class TurnState {
  BoardMessage _board;
  TurnState(this._board);
  BoardMessage get board {
    return _board;
  }
}

class PieceHeld extends TurnState {
  PieceHeld(super._board, this.piece, this.frmSqr);
  String piece;
  List<int> frmSqr;
  get board {
    return super._board;
  }
}

class PieceLaid extends TurnState {
  PieceLaid(super._board, this.piece, this.frmSqr, this.toSqr);
  String piece;
  List<int> frmSqr;
  List<int> toSqr;
  get board {
    return super._board;
  }
}

class NewTurn extends TurnState {
  NewTurn(super._board);

  get board {
    return super._board;
  }
}

class AwaitPlayers extends TurnState {
  static BoardMessage bm = BoardMessage(
      [
        ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
        ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
        ['', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', ''],
        ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
        ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
      ],
      true,
      true,
      [],
      0,
      false,
      null);
  AwaitPlayers() : super(bm);
}
