import random
import json
import logging

import torch
import torch.nn as nn
import torch.nn.functional as F

from core.game_core import ChessGameCore
from utils import config


class ResidualBlock(nn.Module):
	def __init__(self, channels):
		super(ResidualBlock, self).__init__()
		self.conv1 = nn.Conv2d(channels, channels, kernel_size=3, padding=1, bias=False)
		self.bn1 = nn.BatchNorm2d(channels)

	def forward(self, x):
		identity = x
		out = self.bn1(self.conv1(x))
		out += identity  
		return F.relu(out)
	
class AlphaZeroModule(torch.nn.Module):
	def __init__(self):
		super(AlphaZeroModule, self).__init__()
		self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
		self.logger = logging.getLogger(__name__)

		# backbone
		self.conv1 = nn.Conv2d(2, 64, kernel_size=3, padding=1)
		self.res1 = ResidualBlock(64)
		self.conv2 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
		self.res2 = ResidualBlock(128)

		# policy head: 输出 [B, H, W]
		self.policy_conv = nn.Conv2d(128, 1, kernel_size=1)

		# value head: 先池化成全局，再MLP
		self.value_fc1  = nn.Linear(128, 128)
		self.value_fc2  = nn.Linear(128, 1)

		self.relu = nn.ReLU()
		self.criterion = torch.nn.MSELoss()
		self.optimizer = torch.optim.Adam(self.parameters(), config.AlphaZero.LearningRate)


		try:
			self.load_state_dict(torch.load('model.pth'))
			print('成功加载模型 model.pth')
		except Exception as e:
			print(f'未加载模型参数: {e}')

		self.buffer = []
		self.buffer_size = config.AlphaZero.BufferSize
		self.buffer_ptr = 0

		self.to(self.device) 

		try:
			for i in range(1, 2):
				path = f'data/d{i}.json'
				with open(path, 'r', encoding='utf-8') as f:
					data = json.load(f)
					self.buffer.extend(data)   

			self.buffer_ptr = len(self.buffer)
			if len(self.buffer) >= self.buffer_size:
				self.buffer = self.buffer[len(self.buffer) - self.buffer_size : self.buffer_size]
				self.buffer_ptr = 0

			print(f'已加载 {len(self.buffer)} 条训练数据到缓冲区')
		except Exception as e:
			print(f'未加载数据: {e}')


	def forward(self, x):
		x = x.to(self.device)
		self.to(self.device)

		# backbone
		x = self.relu(self.conv1(x))
		x = self.res1(x)
		x = self.relu(self.conv2(x))
		x = self.res2(x)

		# policy head
		p = self.policy_conv(x)              
		policy_logits = p.view(p.size(0), -1)  

		# value head
		v = F.adaptive_avg_pool2d(x, (1, 1))   
		v = v.view(v.size(0), -1)              
		v = self.relu(self.value_fc1(v))       
		value = torch.tanh(self.value_fc2(v))  

		return policy_logits, value

	def train_model(self, epochs: int):
		self.to(self.device)   # 确保模型在 self.device
		self.train()

		for epoch in range(1, epochs + 1):
			batch = random.sample(self.buffer, min(config.AlphaZero.BatchSize, len(self.buffer)))
			states,target_policies,target_values = [],[],[]

			n = int(random.random()*3)
			n1 = random.random()
			for data in batch:
				state = torch.tensor(data['state'],dtype=torch.float32).view(2, ChessGameCore.size, ChessGameCore.size) #[2,size,size]
				policy = torch.tensor(data['search_rate'],dtype=torch.float32) #[size,size]

				# 数据增强
				state = torch.rot90(state, k=n, dims=(1, 2))  
				policy = torch.rot90(policy, k=n, dims=(0, 1)) 
				if n1 < 0.5:  
					state = torch.flip(state, dims=[2])  
					policy = torch.flip(policy, dims=[1]) 


				states.append(state)
				target_policies.append(policy.reshape(-1))
				target_values.append(torch.tensor(data['win_rate'],dtype=torch.float32))

			states = torch.stack(states).to(self.device)
			target_policies = torch.stack(target_policies).to(self.device)
			target_values = torch.stack(target_values).unsqueeze(-1).to(self.device)
		

			# forward
			policy_logits, values = self(states)  # forward 已保证输入和模型同设备

			policy_loss = -(target_policies * F.log_softmax(policy_logits, dim=1)).sum(dim=1).mean()

			value_loss = F.mse_loss(values, target_values)

			loss = policy_loss + 0.4*value_loss

			# backward
			self.optimizer.zero_grad()
			loss.backward()
			self.optimizer.step()

			if epoch % 100 == 0: 
				self.logger.info(
					f'Epoch: {epoch}, Loss: {loss.item():.4f}, '
					f'Policy: {policy_loss.item():.4f}, Value: {value_loss.item():.4f}'
				)

		self.to('cpu')
		torch.save(self.state_dict(), 'model.pth')
		self.logger.info('训练结束，最新模型已保存到 model.pth')
		torch.cuda.empty_cache()
		self.eval()


	def add_to_buffer(self,data):
		if len(self.buffer) < self.buffer_size:
			self.buffer.append(data)
		else:
			self.buffer[self.buffer_ptr] = data
			self.buffer_ptr = (self.buffer_ptr+1)%self.buffer_size

a0_model = AlphaZeroModule() 