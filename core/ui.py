import pygame
from pygame.draw import rect as draw_rect, line as draw_line, circle as draw_circle

from alg.a0_node import AlphaZeroNode
from core.game_core import ChessGameCore
from utils import config
from utils.enums import ChessType, RGBTuple, Subwindow, subwindow_index


class ChessGameUI:
	def __init__(self):
		pygame.init()
		screen_size = config.UI.CellSize * ChessGameCore.size * 2 + 3 * config.UI.Margin
		self.font = pygame.font.Font(None, 20)
		self.screen = pygame.display.set_mode((1.5 * screen_size, screen_size))
		
		self._n_cells_size = config.UI.CellSize * ChessGameCore.size
		_margin_1 = config.UI.Margin
		_margin_2 = config.UI.Margin * 2 + self._n_cells_size

		self.subwindow_offsets = [
			(_margin_1, _margin_1),
			(_margin_2, _margin_1),
			(_margin_1, _margin_2),
			(_margin_2, _margin_2),
		]


		self.player_chess: ChessType = None

	def get_subwindow_offset(self, subwindow: Subwindow) -> tuple[int, int]:
		return self.subwindow_offsets[subwindow_index.get(subwindow)]

	def draw_subwindow(
			self,
			subwindow: Subwindow,
			game: ChessGameCore,
			node: AlphaZeroNode,
		) -> None:

		offset_x, offset_y = self.get_subwindow_offset(subwindow)

		draw_rect(
			surface = self.screen,
			color = RGBTuple.Brown,
			rect = (
				offset_x, offset_y,
				self._n_cells_size, self._n_cells_size
			)
		)

		for i in range(ChessGameCore.size + 1):
			draw_line(
				surface = self.screen,
				color = RGBTuple.Black,
				start_pos = (
					0 + offset_x,
					i * config.UI.CellSize + offset_y
				),
				end_pos = (
					self._n_cells_size + offset_x,
					i *config.UI.CellSize + offset_y
				),
				width = 3
			)

			draw_line(
				surface = self.screen,
				color = RGBTuple.Black,
				start_pos = (
					i * config.UI.CellSize + offset_x,
					0 + offset_y
				),
				end_pos = (
					i * config.UI.CellSize + offset_x,
					self._n_cells_size + offset_y
				),
				width = 3
			)

		label = self.font.render(subwindow.value, True, RGBTuple.Black)
		self.screen.blit(
			source = label,
			dest = (
				offset_x + 0.2 * self._n_cells_size,
				offset_y - config.UI.Margin + 4
			)
		)

		for i in range(ChessGameCore.size):
			for j in range(ChessGameCore.size):
				chess = game.chessboard[i, j]
				if chess == ChessType.NoChess:
					continue

				else:
					if chess == self.player_chess:
						# 这是玩家的棋子
						color = RGBTuple.Black if self.player_chess == ChessType.Black else RGBTuple.White
					else:
						# 这是AI的棋子
						color = RGBTuple.White if self.player_chess == ChessType.Black else RGBTuple.Black
					
					draw_circle(
						surface = self.screen,
						color = color,
						center = (
							offset_x + (i + 0.5) * config.UI.CellSize,
							offset_y + (j + 0.5) * config.UI.CellSize
						),
						radius = 13
					)
		
		if subwindow == Subwindow.Chessboard:
			return
		
		for child in node.children:
			value = 0
			x, y = child.x, child.y
			if subwindow == Subwindow.ValueOut:
				value = round(-child.value_out, 2)
			elif subwindow ==  Subwindow.SearchNum:
				value = child.visits
			elif subwindow == Subwindow.PolicyOut:
				value = round(node.policy_out[x * ChessGameCore.size + y], 2)
			
			label = self.font.render(str(value), True, RGBTuple.Black)
			self.screen.blit(
				source = label,
				dest = (
					offset_x + (x + 0.1) * config.UI.CellSize,
					offset_y + (y + 0.2) * config.UI.CellSize,
				)
			)

	def draw_all(
			self,
			game: ChessGameCore,
			node: AlphaZeroNode,
		) -> None:
		self.screen.fill(RGBTuple.White)
		for subwindow in Subwindow:
			self.draw_subwindow(
				subwindow = subwindow,
				game = game,
				node = node
			)

	@staticmethod
	def wait_for_click() -> None | tuple[float, float]:
		while True:
			for event in pygame.event.get():
				if event.type ==  pygame.QUIT:
					pygame.quit()
					return None
				elif event.type == pygame.MOUSEBUTTONDOWN:
					return event.pos
	
	def request_initial_choice(self) -> None | ChessType:
		self.screen.fill(RGBTuple.White)

		title_font = pygame.font.Font(None, 40)
		title_text = title_font.render('Choose Your Color', True, RGBTuple.Black)
		self.screen.blit(title_text, (config.UI.CellSize*ChessGameCore.size - 100, 50))
		
		# Black
		black_rect = pygame.Rect(100, 150, 200, 100)
		draw_rect(self.screen, (200, 200, 200), black_rect)
		draw_rect(self.screen, RGBTuple.Black, black_rect, 3)
		draw_circle(self.screen, RGBTuple.Black, (200, 200), 30)
		
		black_text = self.font.render('Black (First Move)', True, RGBTuple.Black)
		self.screen.blit(black_text, (130, 270))
		
		# White
		white_rect = pygame.Rect(350, 150, 200, 100)
		draw_rect(self.screen, (200, 200, 200), white_rect)
		draw_rect(self.screen, RGBTuple.Black, white_rect, 3)
		draw_circle(self.screen, RGBTuple.White, (450, 200), 30)
		draw_circle(self.screen, RGBTuple.Black, (450, 200), 30, 2)
		
		white_text = self.font.render('White (Second Move)', True, RGBTuple.Black)
		self.screen.blit(white_text, (370, 270))
		
		pygame.display.flip()
		
		while True:
			pos = self.wait_for_click()
			if pos is None:
				pygame.quit()
				return None
			
			if black_rect.collidepoint(pos):
				return ChessType.Black
			elif white_rect.collidepoint(pos):
				return ChessType.White