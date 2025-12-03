import os

from utils.enums import RGBTuple


WorkingPath = os.path.dirname(os.path.dirname(__file__))

class Train:
	"""训练相关配置项。"""

	MinReward: float = 0.2
	"""最小奖励值。"""

	RewardAttenuationFactor: float = 0.6
	"""奖励衰减系数。"""

	Times: int = 3600
	"""训练次数。"""

	Epochs: int = 1000
	"""模型训练周期数。"""

	SnapshotGap: int = 300
	"""模型快照保存间隔。每训练这么多次，保存一次模型快照。"""

	SelfPlayingUpdateTimes: int = 300
	"""训练时 MCTS 搜索次数。"""

	InCombatUpdateTimes: int = 500
	"""游玩时 MCTS 搜索次数。"""

	UseRandomFlip: bool = False
	"""是否启用随机翻转。"""

	RandomFlipThreshold: float = 0.5
	"""随机翻转临界值。随机值小于该值时，尝试启用随机翻转。"""

	ValueLossWeight: float = 0.4
	"""Value loss 权重。"""

	MCTSExplorationRate: float = 0.3
	"""MCTS 探索率。"""

	BufferSize: int = 50000
	"""缓冲区大小。"""

	LearningRate: float = 0.001
	"""学习率。"""

	BatchSize: int = 128
	"""训练批次大小。"""

class GameCore:
	"""
	N子棋游戏规则设置。**!!! 修改后请删除旧模型与数据以避免维度不一致或模型失效 !!!** :: 
	
		rm -rf model.pth data
	
	"""

	ChessboardSize: int = 7
	"""游戏方形棋盘的边长。对于传统五子棋，这个值为15；对于井字棋，这个值为3。以此类推。"""

	WinCount: int = 4
	"""判定游戏胜利的最小连子数。对于传统五子棋，这个值为5；对于井字棋，这个值为3。以此类推。"""

	CheckDirections: tuple[int, int] = [
		(1, 0), (0, 1), (1, 1), (1, -1)
	]
	"""
	将在哪些方向上检查连子数。例如::

		CheckDirections = [(1, 0), (0, 1)]   # 只检查行列，不检查对角线
		CheckDirections = [(1, 1), (1, -1)]  # 只检查对角线，不检查行列
		CheckDirections = [(2, 0)]           # 只检查行，且要求相邻的两个子中间隔开一个空位
		# ...更多玩法

	"""

class UI:
	"""
	**!!! 不推荐修改 !!!**

	UI 相关配置项。本项目对 UI 的适配并非完美，不恰当的配置值可能导致各种现实问题，因此如非必要请勿修改。
	"""

	CellSize: int = 35
	"""棋盘格单格边长。"""

	Margin: int = 20
	"""棋盘外边距。"""

	BackgroundColor: tuple[int, int, int] = RGBTuple.LightBlue

	BorderWidth: int = 2

	ChessSize: int = 10

	MoveOrderUISizeX: int = 700
	MoveOrderUISizeY: int = 400