import 'package:flutter/material.dart';
import 'tile.dart';

class Board extends StatelessWidget {
  final List<int> shape;
  late final List<List<Tile>> tiles;
  late final Map<String, Map> tileValues;

  List<List<Tile>> makeTileGrid(List<int> shape) {
    List<List<Tile>> eventualTile = [];
    for (var i = 0; i < shape[0]; i++) {
      eventualTile.add([]);
      for (var j = 0; j < shape[1]; j++) {
        eventualTile[i].add(makeTile([i, j]));
      }
    }
    return eventualTile.reversed.toList();
  }

  Board(this.shape, this.tileValues, {super.key}) {
    this.tiles = makeTileGrid(shape);
  }
  set tileStates(Map<String, Map> tileVals) => tileValues = tileVals;

  Tile makeTile(List<int> location) {
    dynamic mapOut = tileValues[location.toString()];
    return Tile(
        location, mapOut["text"], mapOut["foreground"], mapOut["background"]);
  }

  void change(List<int> location) {
    tiles[location[0]][location[1]] = makeTile(location);
  }

  Widget drawTiles() {
    List<Widget> col = [];
    for (var i = 0; i < tiles.length; i++) {
      col.add(Row(
        children: tiles[i],
      ));
    }
    return Column(
      children: col,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Center(child: SizedBox(width: 800, height: 800, child: drawTiles()));
  }
}
