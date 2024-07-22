import 'package:fow_chess/bloc/turn_bloc.dart';
import 'package:fow_chess/board_message.dart';
import 'package:fow_chess/move.dart';
import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

class ServerProxy {
  late final Function emit;
  final WebSocketChannel socket;

  ServerProxy(this.socket);

  _mapToMove(Map<String, dynamic> map) {
    Move(map["frm"]!, map["to"]!,
        rookTo: map["rook_frm"],
        rookFrm: map["rook_to"],
        promotion: map["promotion_to"],
        resignation: map["resignation"]!,
        enPassent: map["en_passent"]);
  }

  void listenForBoard() {
    socket.stream.listen((data) {
      Map<String, dynamic> dict = json.decode(utf8.decode(data));
      List<List<String>> board = dict["board"];
      bool turn = dict["turn"];
      List<Move> moves =
          dict["possible_moves"].map(json.decode).map(_mapToMove).toList();
      int halfMove = dict["half_move"];
      bool isOver = dict["is_over"];
      bool perspective = dict["perspective"];
      bool? winner = dict["winner"];

      emit(NewTurnStart(BoardMessage(
          board, perspective, turn, moves, halfMove, isOver, winner)));
    });
  }

  void turn(Move move) {
    // send move
    socket.sink.add({
      "to": move.toSqr,
      "frm": move.frmSqr,
      "rook_frm": move.rookFrm,
      "rook_to": move.rookTo,
      "promotion_to": move.promotion,
      "resignation": move.resignation,
      "en_passent": move.enPassent
    });
  }
}
