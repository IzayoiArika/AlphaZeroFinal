import sys
if sys.version_info >= (3, 11):
	from typing import Self
else:
	from typing_extensions import Self

import torch
import numpy as np

from utils import config
from utils.enums import ChessGameState, ChessType, flip_chess
from utils.clsprop import classproperty


class ChessGameCore:
	@classproperty
	def size(self) -> int:
		return config.GameCore.ChessboardSize
	
	@classproperty
	def win_num(self) -> int:
		return config.GameCore.WinCount

	def __init__(
			self,
			chessboard: np.ndarray | None = None
		):
		self.chessboard = np.zeros((self.size,self.size)) if chessboard is None else chessboard

	def __getitem__(
			self,
			coordinate: tuple[int, int]
		):
		x, y = coordinate
		return self.chessboard[x][y]

	def __setitem__(
			self,
			coordinate: tuple[int, int],
			value: int | ChessType
		) -> None:
		x, y = coordinate
		self.chessboard[x][y] = value
	
	@property
	def placed_count(self) -> int:
		return np.count_nonzero(self.chessboard)
	
	@property
	def is_full(self) -> bool:
		return self.placed_count == self.size ** 2

	@classmethod
	def is_valid_position(
			cls,
			x: int,
			y: int
		) -> bool:

		return x >= 0 and x < cls.size and y >= 0 and y < cls.size
	
	def place_chess(
			self,
			x: int,
			y: int,
			chess: ChessType
		) -> tuple[bool, ChessGameState]:

		if not self.is_valid_position(x, y) or not self[x, y] == ChessType.NoChess:
			return False, ChessGameState.NoWinnerYet
		self[x, y] = chess

		for dir in config.GameCore.CheckDirections:
			count = 1
			dir_x, dir_y = dir
			
			curr_x, curr_y = x + dir_x, y + dir_y
			while self.is_valid_position(curr_x, curr_y) and self[curr_x, curr_y] == chess:
				count += 1
				curr_x += dir_x
				curr_y += dir_y

			curr_x, curr_y = x - dir_x, y - dir_y
			while self.is_valid_position(curr_x, curr_y) and self[curr_x, curr_y] == chess:
				count += 1
				curr_x -= dir_x
				curr_y -= dir_y
			
			if count >= self.win_num:
				return True, ChessGameState.SomeoneWins
		
		if self.is_full:
			return True, ChessGameState.Draw
		return True, ChessGameState.NoWinnerYet

	def copy(self) -> Self:
		return type(self)(
			chessboard = self.chessboard.copy()
		)

	def to_tensor(
			self,
			chess: int | ChessType,
			should_unsqueeze: bool = True
		) -> torch.Tensor:

		chessboard = torch.from_numpy(self.chessboard)
		this_layer = (chessboard == chess).float()
		opponent_layer = (chessboard == flip_chess(chess)).float()
		result = torch.stack([this_layer, opponent_layer])

		return result.unsqueeze(0) if should_unsqueeze else result

	def __str__(self) -> Self:
		return '\n'.join(' '.join(row.astype(str)) for row in self.chessboard)