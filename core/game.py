import pygame

from alg.a0_node import AlphaZeroNode
from core.game_core import ChessGameCore
from core.ui import ChessGameUI
from utils import config
from utils.enums import ChessGameState, ChessType, flip_chess


class ChessGame:
	def __init__(self):
		self.core = ChessGameCore()
		self.ui = None

		self.player_chess: ChessType = None
		self.current_chess: ChessType = ChessType.Black

		self.x: int = 0
		self.y: int = 0
		self.game_state: ChessGameState = ChessGameState.NoWinnerYet
		self.search_tree = AlphaZeroNode(self.current_chess, self.core)

	def redraw_ui(self):
		self.ui.draw_all(
			game = self.core,
			node = self.search_tree
		)
		pygame.display.flip()
	
	def update_node(self):
		self.search_tree.expand_children_nodes()
		for i in range(config.Train.InCombatUpdateTimes):
			if not i % 10:
				self.redraw_ui()
			self.search_tree.update()
		self.redraw_ui()
	
	def run_ai_turn(self):
		action = self.search_tree.get_best_action(0)
		self.x, self.y = action.x, action.y
		_, self.game_state = self.core.place_chess(self.x, self.y, self.current_chess)
		
	def run_player_turn(self):
		while True:
			pos_x, pos_y = self.ui.wait_for_click()
			self.x = int((pos_x - config.UI.Margin) / config.UI.CellSize)
			self.y = int((pos_y - config.UI.Margin) / config.UI.CellSize)

			succeeded, self.game_state = self.core.place_chess(self.x, self.y, self.current_chess)
			if succeeded:
				return
	
	def update_search_tree(self):
		flag = True
		for child in self.search_tree.children:
			if child.x == self.x and child.y == self.y:
				self.search_tree = child
				flag = False
		
		if flag:
			self.search_tree = AlphaZeroNode(self.current_chess, self.core)
		
	def change_player(self):
		self.current_chess = flip_chess(self.current_chess)
	
	def handle_ending(self):
		self.redraw_ui()
		self.ui.wait_for_click()

	def loop(self):
		self.update_node()
		if self.current_chess == self.player_chess:
			self.run_player_turn()
		else:
			self.run_ai_turn()
		self.redraw_ui()

		self.change_player()
		self.update_search_tree()

		if self.game_state != ChessGameState.NoWinnerYet:
			self.handle_ending()
			return False

		return True
		
	def request_for_player_chess(self):
		self.ui = ChessGameUI()
		self.player_chess = self.ui.request_initial_choice()
		self.ui.player_chess = self.player_chess

	def run(self):
		self.request_for_player_chess()

		while self.loop():
			pass
