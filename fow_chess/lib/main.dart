import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:fow_chess/bloc/turn_bloc.dart';
import 'package:fow_chess/board.dart';
import 'package:fow_chess/server_proxy.dart';
import 'package:fow_chess/tile_values.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

Future<void> main() async {
  try {
    final channel = WebSocketChannel.connect(Uri.parse('ws://127.0.0.1:5555'));
    await channel.ready;
    final ServerProxy sp = ServerProxy(channel);
    runApp(MyApp(sp));
  } catch (e) {
    print(e);
  }
}

class MyApp extends StatelessWidget {
  final ServerProxy sp;
  MyApp(this.sp, {super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Demo',
      theme: ThemeData(
        primarySwatch: Colors.blueGrey,
      ),
      home: MyHomePage(sp),
    );
  }
}

class MyHomePage extends StatefulWidget {
  final ServerProxy sp;
  const MyHomePage(this.sp, {super.key});

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  Widget drawBoard(BuildContext context) {
    // return Center(
    //     child: Board(const [8, 8], TileValues.getPieceMap(startBoard)));
    return Center(
      child: BlocBuilder<TurnBloc, TurnState>(
        builder: (BuildContext context, TurnState state) {
          return Center(
              child: Board(
                  const [8, 8], TileValues.getPieceMap(state.board.board)));
        },
        buildWhen: (previousState, state) {
          return state is NewTurn;
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    // This method is rerun every time setState is called, for instance as done
    // by the _incrementCounter method above.
    //
    // The Flutter framework has been optimized to make rerunning build methods
    // fast, so that you can just rebuild anything that needs updating rather
    // than having to individually change instances of widgets.
    return BlocProvider(
        create: (context) => TurnBloc(widget.sp),
        child: Scaffold(
            body: Center(
          child: drawBoard(context),
        )));
  }
}
