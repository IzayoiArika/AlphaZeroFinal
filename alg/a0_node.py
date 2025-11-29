from genericpath import isfile
import math

import numpy as np
import torch
import torch.nn.functional as F

from alg.a0 import a0_model
from alg.mcts_node import MCTSNode
from core.game_core import ChessGameCore
from utils.enums import ChessGameState, ChessType, flip_chess


class AlphaZeroNode(MCTSNode):
	def __init__(
			self,
			chess: ChessType,
			core: ChessGameCore,
			x: int | None = None,
			y: int | None = None,
		):
		
		super().__init__()
		self.x = x
		self.y = y
		self.chess = chess
		self.core = core.copy()
		self.game_state = ChessGameState.NoWinnerYet
		self.model = a0_model
		
		# 如果不是根节点，先把落子执行到棋盘
		if self.x is not None:
			_, self.game_state = self.core.place_chess(self.x, self.y, flip_chess(chess))
		
		if self.parent == None: #祖宗节点只能单独计算
			with torch.no_grad():
				state = self.core.to_tensor(self.chess).to(self.model.device)
				self.policy_out, self.value_out = self.model(state)
				self.policy_out = self.policy_out[0]
				self.value_out = self.value_out.item() 
				
				for x in range(self.core.size):
					for y in range(self.core.size):
						if self.core[x, y] != ChessType.NoChess:
							self.policy_out[x * self.core.size + y] = float('-inf')
				self.policy_out = F.softmax(self.policy_out, dim=-1).cpu().numpy()

	def expand_children_nodes(self) -> int:
		if self.game_state != ChessGameState.NoWinnerYet:
			return 0

		if self.children:
			return len(self.children)
		
		states = []
		for x in range(self.core.size):
			for y in range(self.core.size):
				if self.core[x, y] == ChessType.NoChess:
					child = AlphaZeroNode(flip_chess(self.chess), self.core, x=x, y=y)
					child.parent = self
					self.children.append(child)
					self.unvisited_children.append(child)

					if child.game_state == ChessGameState.SomeoneWins: #如果子节点赢了，证明这步棋赢了，没必要再探索
						child.value_out = -1
						self.game_state = ChessGameState.NoSuccession
						self.value_out = 1
						return 0

					states.append(child.core.to_tensor(child.chess, False))
		
		with torch.no_grad():
			states = torch.stack(states).float().to(self.model.device)
			policy, value = self.model.forward(states)

			masks = []
			for child in self.children:
				mask = torch.from_numpy(child.core.chessboard.flatten() != 0)
				masks.append(mask)
			
			masks = torch.stack(masks).to(dtype=torch.bool, device=a0_model.device) 


			policy[masks] = float('-inf')
			policy = F.softmax(policy, dim=-1)
			policy = policy.cpu().numpy()
			value = value.cpu().squeeze(-1).numpy()

		for x in range(len(self.children)):
			self.children[x].policy_out = policy[x]
			self.children[x].value_out = float(value[x])
			self.children[x].cal_model_out()

		return len(self.children)

	def cal_model_out(self):                   
		if self.game_state == ChessGameState.SomeoneWins: #如果赢了肯定是上一次落子，也就是对于这个节点来说对方的颜色赢了，所以反馈为-1
			self.value_out = -1
		elif self.game_state == ChessGameState.Draw:
			self.value_out = 0
		
	def random_simulate(self) -> float: # 对于父节点
		return self.value_out

	def select_child(self):
		win_rates = np.array([-n.win_rate for n in self.children], dtype=np.float32)
		nums = np.array([n.visits for n in self.children], dtype=np.float32)
		idxs = np.array([n.x * self.core.size + n.y for n in self.children], dtype=np.int32)
		priors = self.policy_out[idxs] 

		uct = win_rates + self.exploration_rate * priors * math.sqrt(self.visits) / (1.0 + nums)
		best_idx = np.argmax(uct)
		return self.children[best_idx]
	
	def get_best_action(self, tau: float = 1):
		counts = np.array([node.visits for node in self.children], dtype=np.float32)

		if tau == 0:
			# 贪心：选择访问次数最多的
			idx = np.argmax(counts)
		else:
			# 温度采样
			probs = counts ** (1.0 / tau)
			probs /= probs.sum()
			idx = np.random.choice(len(self.children), p=probs)

		return self.children[idx]
	
	def __str__(self):
		"""统计信息"""

		# 初始化结果数组
		size = self.core.size
		model_win_rates = [[0.00 for _ in range(size)] for _ in range(size)]
		search_win_rates = [[0.00 for _ in range(size)] for _ in range(size)]
		visit_counts = [[0 for _ in range(size)] for _ in range(size)]
		
		for node in self.children:
			model_win_rates[node.x][node.y] = -node.value_out
			search_win_rates[node.x][node.y] = -node.win_rate
			visit_counts[node.x][node.y] = node.visits
		
		def fmtmtx(matrix, value_format):
			return '\n'.join(
				'  '.join(value_format.format(value) for value in row)
				for row in matrix
			)
		
		sections = [
			('子节点模型胜率:', model_win_rates, '{:.2f}'),
			('子节点探索胜率:', search_win_rates, '{:.2f}'), 
			('子节点探索次数:', visit_counts, '{}')
		]
		
		lines = []
		for title, matrix, fmt in sections:
			lines.extend([title, fmtmtx(matrix, fmt), ''])
		
		return '\n'.join(lines)