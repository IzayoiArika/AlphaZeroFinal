# AlphaZero Five (Gomoku)

一个轻量级的 AlphaZero 五子棋项目：自对弈生成数据，MCTS 引导策略，卷积神经网络训练，带可视化对战与“先手/后手”选择。

- 语言: Python 3.9+（3.8 也可）
- 框架: PyTorch, NumPy, Pygame
- 棋盘: 默认 9×9（可切换 6×6, 11×11, 15×15 等）

---

## 目录结构

```
AlphaZero_Five/
├─ Game.py           # 棋盘与规则（size、win_num）
├─ net.py            # 策略-价值网络 + 训练逻辑
├─ train.py          # 自对弈 + 训练主循环（生成数据并优化模型）
├─ main.py           # 可视化人机对战（支持先手/后手选择）
├─ model.pth         # 训练好的模型（运行后产生/更新）
├─ data/
│  └─ d1.json        # 自对弈数据缓存（运行后产生/更新）
└─ MCTS/
   ├─ Tree.py        # 蒙特卡洛树搜索（MCTS）
   └─ __init__.py
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
  - 选 Black (First)：你执黑先手
  - 选 White (Second)：你执白后手（AI 会先落黑子一手）
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
  - 每个回合使用 MCTS 搜索（`train.py` 中默认 300 次）
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

## 配置与常用参数位置

- 棋盘大小与连珠规则（强烈建议先小后大）：
  - 文件：`Game.py`
  - 字段：
    ```python
    class Game():
        size = 9      # 棋盘边长：6/9/11/13/15 ...
        win_num = 5   # 连珠数：6×6 建议 4，其它一般为 5
    ```
  - 修改后请删除旧模型与数据以避免维度不一致：
    ```bash
    rm -f model.pth data/d1.json
    ```

- MCTS 搜索次数（训练时）：
  - 文件：`train.py`
  - 位置：`for i in range(300): tree.update()`（可改为 100/500/800 …）

- MCTS 搜索次数（对战时）：
  - 文件：`main.py`
  - 位置：`for i in range(500): node.update()`（首回合也有一段搜索）

- 训练批次大小 / 数据增强 / 学习率 / 缓冲区大小：
  - 文件：`net.py` 的 `Alpha0_Module.train_model`
  - 关键处：
    ```python
    batch = random.sample(self.buffers, min(128, len(self.buffers)))  # 批次
    self.optimizer = torch.optim.Adam(self.parameters(), 0.001)       # 学习率
    self.buffersize = 50000                                           # 缓冲区
    # 旋转/翻转增强见 train_model 内部
    ```

---

## 推荐的渐进式训练流程（代码已经支持此功能）

1) 6×6 + 连四（上手快）
- 修改：`Game.size = 6`, `Game.win_num = 4`
- 清空旧模型/数据：`rm -f model.pth data/d1.json`
- 跑 100～200 局训练，验证模型能快速学到常规套路

2) 9×9 + 连五（标准）
- 修改：`Game.size = 9`, `Game.win_num = 5`
- 清空旧模型/数据后重新训练 500～1000 局

3) 15×15 + 连五（进阶）
- 修改：`Game.size = 15`
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
- 一键切板：改 `Game.size`/`win_num` 即可切换棋盘与规则
- 可 GPU 加速：自动检测 `cuda`

---

## 常见问题

- Q: 改了棋盘大小后报维度错误？
  - A: 删除旧的 `model.pth` 和 `data/d1.json` 后重新训练。

- Q: 训练/对战很慢？
  - A: 减小 MCTS 次数（`train.py`/`main.py`），或用 6×6/9×9 棋盘，或开启 GPU。

- Q: 如何从头训练？
  - A: `rm -f model.pth data/d1.json && python train.py`

---

## 许可证

本项目用于学习与研究用途。若用于发布或商业化，请根据依赖项（PyTorch、Pygame 等）的许可证要求合规使用。
