import 'package:flutter/material.dart';

Color backgroundChess(List<int> cords,
    {List<Color> colors = const [Color(0xFFFFF9C4), Color(0xFF795548)]}) {
  int k = 0;
  for (int i in cords) {
    k += i;
  }
  k = k % 2;
  return colors[k];
}

Color foregroundChess(List<int> cords,
    {List<Color> colors = const [Color(0xFFFFF9C4), Color(0xFF795548)]}) {
  int k = 0;
  for (int i in cords) {
    k += i;
  }
  k = k % 2;
  return colors.reversed.toList(growable: false)[k];
}

Color white = Color.fromARGB(255, 247, 234, 208);
Color black = Color.fromARGB(255, 82, 62, 15);
Color grey = Color.fromARGB(255, 102, 102, 102);

class TileValues {
  static Map<String, List> stingToPiece = {
    "": [" ", const Color.fromARGB(0, 255, 255, 255)],
    " ": [" ", const Color.fromARGB(0, 255, 255, 255)],
    "P": ["\u265F", white],
    "B": ["\u265D", white],
    "N": ["\u265E", white],
    "R": ["\u265C", white],
    "Q": ["\u2655", white],
    "K": ["\u265A", white],
    "p": ["\u265F", black],
    "b": ["\u265D", black],
    "n": ["\u265E", black],
    "r": ["\u265C", black],
    "q": ["\u2655", black],
    "k": ["\u265A", black],
    "F": ["X", grey]
  };

  static Map<String, Map> getPieceMap(List<List<String>> pieces) {
    Map<String, Map> out = {};
    for (var i = 0; i < pieces.length; i++) {
      for (var j = 0; j < pieces[i].length; j++) {
        List x = stingToPiece[pieces[i][j]]!;
        out[[i, j].toString()] = {
          "text": x[0],
          "foreground": x[1],
          "background": backgroundChess([i, j])
        };
      }
    }
    return out;
  }
}
