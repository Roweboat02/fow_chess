import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:fow_chess/bloc/turn_bloc.dart';
// import 'color_rule_JSON.dart';

class Tile extends StatelessWidget {
  final List<int> locationCord;

  final String text;

  final Color foreground;

  final Color background;

  const Tile(
    this.locationCord, // acts a
    this.text,
    this.foreground,
    this.background, {
    super.key,
  });

  void onPressed(context) {
    TurnBloc bloc = BlocProvider.of<TurnBloc>(context);
    if (bloc.state is PieceHeld) {
      bloc.add(PieceLaidDown((bloc.state as PieceHeld).piece,
          (bloc.state as PieceHeld).frmSqr, locationCord));
    } else if (bloc.state.board.perspective == bloc.state.board.turn) {
      bloc.add(PiecePickedUp(text, locationCord));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 75,
      height: 75,
      padding: const EdgeInsets.all(1.0),
      child: TextButton(
          onPressed: () => onPressed(context),
          style: ButtonStyle(
              padding: MaterialStateProperty.all(const EdgeInsets.all(0)),
              // minimumSize: MaterialStateProperty.all(const Size(100, 100)),
              shape: MaterialStateProperty.all(const BeveledRectangleBorder()),
              backgroundColor: MaterialStateProperty.all(background),
              foregroundColor: MaterialStateProperty.all(foreground)),
          child: Align(
              // alignment: Alignment.center, child: Icon(Icons.access_alarm))),
              alignment: Alignment.center,
              child: Text(text,
                  style: const TextStyle(
                      fontSize: 30,
                      fontWeight: FontWeight.bold,
                      shadows: [
                        Shadow(
                            // bottomLeft
                            offset: Offset(-2, -2),
                            color: Colors.black),
                        Shadow(
                            // bottomRight
                            offset: Offset(2, -2),
                            color: Colors.black),
                        Shadow(
                            // topRight
                            offset: Offset(2, 2),
                            color: Colors.black),
                        Shadow(
                            // topLeft
                            offset: Offset(-2, 2),
                            color: Colors.black),
                      ])))),
    );
  }
}
