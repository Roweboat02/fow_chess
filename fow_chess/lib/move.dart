class Move {
  List<int> frmSqr;
  List<int> toSqr;
  List<int>? rookTo;
  List<int>? rookFrm;
  String? promotion;
  bool? resignation;
  bool? enPassent;

  Move(
    this.frmSqr,
    this.toSqr, {
    this.rookTo,
    this.rookFrm,
    this.promotion,
    this.resignation = false,
    this.enPassent = false,
  });
}
