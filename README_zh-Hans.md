# AlphaZero Five (Gomoku)

一个轻量级的 AlphaZero 五子棋项目：自对弈生成数据，MCTS 引导策略，卷积神经网络训练，带可视化对战与“先手/后手”选择。

- 语言: Python 3.12+
- 框架: PyTorch, NumPy, Pygame
- 棋盘: 默认 9×9（可切换 6×6, 11×11, 15×15 等）

---

## 目录结构

```
AlphaZero_Five/
│
├─ main.py          # 游戏启动入口
├─ train.py         # 模型训练入口
├─ model.pth        # 训练好的模型（运行后产生/更新）
│
├─ alg/             # 算法核心，策略-价值网络，训练逻辑
│  ├─ a0.py         # AlphaZero 前置
│  ├─ a0_node.py    # AlphaZero 节点实现 `AlphaZeroNode`
│  └─ mcts_node.py  # 蒙特卡洛树搜索（MCTS）节点抽象基类 `MCTSNode`
│
├─ core/            # 程序主功能
│  ├─ game.py       # 可视化人机对战 `ChessGame`
│  ├─ game_core.py  # 棋盘与规则定义 `ChessGameCore`
│  ├─ trainer.py    # 自对弈 + 训练主循环（生成数据并优化模型）
│  └─ ui.py         # 游戏 UI
│
├─ data/            # 数据缓存
│  └─ d1.json       # 自对弈数据缓存（运行后产生/更新）
│
└─ utils/           # 技术性杂项
   ├─ clsprop.py    # `classproperty`装饰器（仅用于简化程序）
   ├─ enums.py      # 枚举（优化程序可读性）
   └─ config.py     # 可供修改的程序参数和配置项
```

---

## 环境准备

```bash
# 建议使用虚拟环境（任选其一）
python -m venv .venv && source .venv/bin/activate
# 或
conda create -n az-five python=3.10 -y && conda activate az-five

# 安装依赖
pip install torch numpy pygame
```

如需 GPU，请按 PyTorch 官网指引安装支持 CUDA 的版本。

---

## 快速开始

### 1) 人机对战（可选先手/后手）

```bash
python main.py
```

- 启动后先出现“Choose Your Color”界面：
  - 选 Black (First Move)：你执黑先手
  - 选 White (Second Move)：你执白后手（AI 会先落黑子一手）
- 窗口四象限展示：棋盘、价值估计、访问次数、策略概率
- 鼠标左键在棋盘点击落子

### 2) 训练（自对弈 + 网络优化）

```bash
python train.py
```

- 脚本会循环“自对弈→收集数据→训练模型→定期保存数据/模型”
- 默认每步 MCTS 300 次模拟，前 5 步使用温度采样（更探索），之后趋于贪心
- 模型会保存为 `model.pth`，自对弈数据保存在 `data/d1.json`

提示：初次运行即可使用现有 `model.pth`，也可以删掉重新训练。

```bash
rm -f model.pth data/d1.json
python train.py
```

---

## 训练细节

- 自对弈驱动：
  - 每个回合使用 MCTS 搜索（中默认 300 次）
  - 生成 (state, π, z) 训练样本，其中 π 为搜索得到的落子分布，z 为对局结果的回溯
- 数据增强：
  - `net.py` 的 `train_model` 中对状态与策略做随机旋转/翻转
- 经验回放：
  - 环形缓冲区（默认 50,000 条），小批次随机采样（默认 128）
- 损失函数：
  - 交叉熵（策略）+ MSE（价值），策略为主，价值权重可调（默认 0.4）
- 优化器：
  - Adam（默认学习率 1e-3）

---

## 配置项调整

参见文件：`utils/config.py`。

该文件包括了大部分常用可调节配置项。

- 棋盘大小与连珠规则
- MCTS 搜索次数（训练时/对战时）
- 训练批次大小 / 数据增强 / 学习率 / 缓冲区大小
  - 旋转/翻转增强见 train_model 内部
- ...

如希望对参数进行调整，根据文件内docstring指引进行修改即可。

---

## 推荐的渐进式训练流程（代码已经支持此功能）

1) 6×6 + 连四（上手快）
- 修改：`GameCore.ChessboardSize = 6`, `GameCore.WinCount = 4`
- 清空旧模型/数据：`rm -f model.pth data/d1.json`
- 跑 100～200 局训练，验证模型能快速学到常规套路

2) 9×9 + 连五（标准）
- 修改：`GameCore.ChessboardSize = 9`, `GameCore.WinCount = 5`
- 清空旧模型/数据后重新训练 500～1000 局

3) 15×15 + 连五（进阶）
- 修改：`GameCore.ChessboardSize = 15`
- 清空旧模型/数据后长时间训练（建议 2000+ 局）

提示：棋盘越大，MCTS 搜索空间越大，训练/对战越慢。可相应降低 MCTS 次数或调小批次。

---

## 特性一览

- 轻量易读：几百行核心代码即可跑通 AlphaZero 思路
- 自对弈训练：MCTS + 策略-价值网络，闭环自学习
- 可视化对战：Pygame 窗口展示棋盘、价值、访问次数、策略概率
- 先后手选择：开局可选“我执黑先手 / 我执白后手（AI 先手）”
- 数据增强：旋转/翻转提升数据多样性
- 经验回放：固定容量循环缓冲，稳定训练
- 一键切板：修改配置项即可切换棋盘与规则
- 可 GPU 加速：自动检测 `cuda`

---

## 常见问题

- Q: 改了棋盘大小后报维度错误？
  - A: 删除旧的 `model.pth` 和 `data/d1.json` 后重新训练。

- Q: 训练/对战很慢？
  - A: 减小 MCTS 次数（`utils/config.py`），或用 6×6/9×9 棋盘，或开启 GPU。

- Q: 如何从头训练？
  - A: `rm -f model.pth data/d1.json && python train.py`

---

## 许可证

本项目用于学习与研究用途。若用于发布或商业化，请根据依赖项（PyTorch、Pygame 等）的许可证要求合规使用。
