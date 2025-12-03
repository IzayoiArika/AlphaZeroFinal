import datetime
import json
import logging
import os
import time

import numpy as np
import torch

from alg.a0 import a0_model
from alg.a0_node import AlphaZeroNode
from core.game_core import ChessGameCore
from utils import config
from utils.enums import ChessGameState, ChessType, flip_chess
from utils.timestr import timestr




class SelfPlayChessGame:
	def __init__(self):
		self.reset()
	
	def reset(self):
		self.core = ChessGameCore()
		center = self.core.size // 2
		self.core.place_chess(center, center, ChessType.White)

		self.buffer = {
			ChessType.Black: [],
			ChessType.White: [],
		}

		self.current_player = ChessType.Black
		self.game_state = ChessGameState.NoWinnerYet
		self.step_count = 0
	
	def update_node(self):
		self.search_tree = AlphaZeroNode(self.current_player, self.core)
		self.search_tree.expand_children_nodes()
		for i in range(config.Train.SelfPlayingUpdateTimes):
			self.search_tree.update()
	
	def new_trial(self):
		self.reset()
		while self.game_state == ChessGameState.NoWinnerYet:
			self.step_count += 1
			self.update_node()

			search_rate = np.zeros((ChessGameCore.size, ChessGameCore.size))
			for child in self.search_tree.children:
				search_rate[child.x][child.y] = child.visits / self.search_tree.visits
			
			self.buffer[self.current_player].append({
				'state': self.core.to_tensor(self.search_tree.chess).tolist(),
				'search_rate': search_rate.tolist(),
				'win_rate': self.search_tree.win_rate,
			})

			tau = 1 if self.step_count <= 5 else 0
			action = self.search_tree.get_best_action(tau)
			x, y = action.x, action.y

			_, self.game_state = self.core.place_chess(x, y, self.search_tree.chess)
			self.current_player = flip_chess(self.current_player)
		
		someone_wins = self.game_state == ChessGameState.SomeoneWins

		self.buffer[self.current_player].append({
			'state': self.core.to_tensor(self.current_player).tolist(),
			'search_rate': np.zeros((ChessGameCore.size, ChessGameCore.size)).tolist(),
			'win_rate': -1 if someone_wins else 0,
		})

		if someone_wins:
			loser = self.current_player
			winner = flip_chess(loser)

			logging.info(f'{winner} 赢了')

			reward = 1
			for info in reversed(self.buffer[winner]):
				info['win_rate'] = min(1, info['win_rate'] + reward)
				reward = max(config.Train.MinReward, reward * config.Train.RewardAttenuationFactor)

			reward = 1
			for info in reversed(self.buffer[loser]):
				info['win_rate'] = max(-1, info['win_rate'] - reward)
				reward = max(config.Train.MinReward, reward * config.Train.RewardAttenuationFactor)
		else:
			logging.info('平局')
		
		for info_list in self.buffer.values():
			for info in info_list:
				a0_model.add_to_buffer(info)

class SelfTrainer:
	logger_initialized = False

	@classmethod
	def init_logger(cls):
		if cls.logger_initialized:
			return
		
		log_dir = os.path.join(config.WorkingPath, 'log')
		os.makedirs(log_dir, exist_ok=True)
		log_path = os.path.join(log_dir, f'training_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log')

		cls.models_dir = os.path.join(config.WorkingPath, 'models')
		os.makedirs(cls.models_dir, exist_ok=True)

		logging.basicConfig(
			level=logging.INFO,
			format='%(asctime)s - %(levelname)s - %(message)s',
			handlers=[
				logging.FileHandler(log_path),
				logging.StreamHandler()  # print to terminal at the same time
			]
		)
		cls.logger_initialized = True
	
	@classmethod
	def train(cls):
		cls.init_logger()
		sp = SelfPlayChessGame()

		begin_t = time.time()
		prev_snapshot_t = begin_t

		for i in range(1, config.Train.Times + 1):
			logging.info(f'第 {i} 局')
			sp.new_trial()
			if i >= 10 and i % 10 == 0:
				a0_model.train_model(config.Train.Epochs)
			
			if not i % config.Train.SnapshotGap:
				snapshot_path = os.path.join(cls.models_dir, f'model_game_{i}.pth')
				torch.save(a0_model.state_dict(), snapshot_path)
				logging.info(f'保存模型快照: {snapshot_path}')

				logging.info(f'缓存区数据量: {len(a0_model.buffer)}')

				data_folder = os.path.join(config.WorkingPath, 'data')
				os.makedirs(data_folder, exist_ok=True)
				
				idx = i // config.Train.SnapshotGap - 1
				snapshot_data_path = os.path.join(data_folder, f'snapshot_{idx}.json')
				with open(snapshot_data_path, 'w', encoding='utf-8') as f:
					json.dump(a0_model.buffer, f, ensure_ascii=False, indent=4)
				
				current_t = time.time()
				round_duration = current_t - prev_snapshot_t

				duration = current_t - begin_t
				
				logging.info(f'本轮耗时 {timestr(round_duration)}；累计用时 {timestr(duration)}')
				
				avg_time = duration / i
				rest_time = avg_time * (config.Train.Times - i)
				logging.info(f'平均每局用时 {timestr(avg_time)}；预计剩余时间 {timestr(rest_time)}')

				prev_snapshot_t = current_t