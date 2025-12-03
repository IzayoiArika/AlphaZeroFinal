from enum import Enum


class RGBTuple:
	Black = (0, 0, 0)
	White = (255, 255, 255)
	Brown = (222, 184, 135)
	LightBlue = (238, 238, 255)

class ChessGameState(int, Enum):
	NoWinnerYet = 0
	SomeoneWins = 1
	Draw = 2
	NoSuccession = 3

class ChessType(int, Enum):
	NoChess = 0
	Black = 1
	White = 2

def flip_chess(chess: int | ChessType) -> ChessType:
	if chess == ChessType.Black:
		return ChessType.White
	elif chess == ChessType.White:
		return ChessType.Black

class Subwindow(str, Enum):
	Chessboard = 'chessboard'
	SearchNum = 'search_num'

subwindow_index = {
	Subwindow.Chessboard: 0,
	Subwindow.SearchNum: 1,
}