from abc import ABC, abstractmethod
import math
import sys
if sys.version_info >= (3, 11):
	from typing import Self
else:
	from typing_extensions import Self

class MonteCarloTreeSearchNode(ABC):
	def __init__(self):
		self.visits : int = 0
		"""访问次数"""
		
		self.parent: Self = None
		"""父节点"""

		self.children : list[Self] = []
		"""全部子节点"""

		self.unvisited_children : list[Self] = []
		"""尚未访问的子节点"""
		
		self.total_reward = 0
		"""总收益"""

		self.exploration_rate = 0.3
		"""探索率"""

	@abstractmethod
	def expand_children_nodes(self) -> int:
		"""扩展子节点，返回子节点数量"""
		return 0

	@abstractmethod
	def random_simulate(self) -> float:
		"""随机模拟，返回当前节点的收益"""
		return 1    

	def update(self) -> None:
		"""更新节点状态"""
		if self.unvisited_children:
			node = self.unvisited_children.pop()  
			reward = node.random_simulate()
			node.backpropagate(reward)

		else:
			node:Self = self.select_child()
			if(node.expand_children_nodes() == 0):
				reward = node.random_simulate()
				node.backpropagate(reward)
			else:
				node.update()
	
	@property
	def win_rate(self) -> float:
		"""胜率"""
		return self.total_reward / self.visits if self.visits else 0
	
	def select_child(self) -> Self:
		"""选择一个待探索的子节点"""
		best_value = float('-inf')
		best_child = None

		for child in self.children:
			if child.visits == 0:
				return child
			
			win_rate = -child.win_rate
			value = win_rate + self.exploration_rate * math.sqrt(math.log(self.visits + 1) / (child.visits + 1))
			if value > best_value:
				best_value = value
				best_child = child
		
		return best_child
	
	def backpropagate(self, reward: float) -> None:
		"""反向传播更新节点统计"""
		current = self
		while current is not None:
			current.visits += 1
			current.total_reward += reward
			reward *= -1
			current = current.parent

	def get_best_action(self) -> Self:
		"""获取最佳子节点（探索次数最多的子节点）"""
		if not self.children:
			return None
		
		return max(self.children, key=lambda node: node.visits)

MCTSNode = MonteCarloTreeSearchNode