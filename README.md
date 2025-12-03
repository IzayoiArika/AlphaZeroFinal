# AlphaZero Five (Gomoku)

A lightweight AlphaZero Gomoku project: generates data through self-play, employs MCTS-guided policy, utilises convolutional neural network training, and features visualised matches with “first move/second move” selection.

- Language: Python 3.12+
- Frameworks: PyTorch, NumPy, Pygame
- Board: Default 9×9 (switchable to 6×6, 11×11, 15×15, etc.)

---

## Directory Structure

```AlphaZero_Five/
│
├─ main.py          # Game launch entry point
├─ train.py         # Model training entry point
├─ model.pth        # Trained model (generated/updated upon execution)
│
├─ alg/             # Algorithm core: policy-value networks, training logic
│  ├─ a0.py         # AlphaZero prerequisite
│  ├─ a0_node.py    # AlphaZero node implementation `AlphaZeroNode`
│  └─ mcts_node.py  # Abstract base class for Monte Carlo Tree Search (MCTS) nodes `MCTSNode`
│
├─ core/            # Main programme functionality
│  ├─ game.py       # Visualised human-vs-AI matches `ChessGame`
│  ├─ game_core.py  # Board and rule definitions `ChessGameCore`
│  ├─ trainer.py    # Self-play + main training loop (generating data and optimising the model)
│  └─ ui.py         # Game UI
│
├─ data/            # Data cache
│  └─ d1.json       # Self-play data cache (generated/updated upon running)
│
└─ utils/           # Technical miscellany
   ├─ clsprop.py    # `classproperty` decorator (for simplifying code only)
   ├─ enums.py      # Enums (enhancing code readability)
   └─ config.py     # Modifiable programme parameters and configuration items
```

---

## Environment Setup

```bash
# Recommended: Use a virtual environment (choose one)
python -m venv .venv && source .venv/bin/activate
# Or
conda create -n az-five python=3.10 -y && conda activate az-five

# Install dependencies
pip install torch numpy pygame
```

For GPU usage, follow PyTorch's official documentation to install a CUDA-compatible version.

---

## Quick Start

### 1) Human vs AI Match (Optional First/Second Move)

```bash
python main.py
```

- Upon launch, the ‘Choose Your Colour’ interface appears:
  - Select Black (First Move): You play Black first
  - Select White (Second Move): You play White second (AI will make the first Black move)
- Window displays four quadrants: Board, Value Estimate, Access Count, Policy Probability
- Left-click on the board to place a stone

### 2) Training (Self-play + Network Optimisation)

```bash
python train.py
```

- The script cycles through ‘self-play → data collection → model training → periodic data/model saving’
- Default settings: 300 MCTS simulations per move, temperature sampling for first 5 moves (more exploratory), then converging towards greedy play
- Model saved as `model.pth`, self-play data stored in `data/d1.json`

Note: Existing `model.pth` can be used upon first run, or deleted to retrain.

```bash
rm -f model.pth data/d1.json
python train.py
```

---

## Training Details

- Self-play Driven:
  - Employing MCTS search per round (default 300 iterations)
  - Generating (state, π, z) training samples, where π denotes the search-derived move distribution and z represents the game outcome through backtracking
- Data Augmentation:
  - Random rotation/flipping of states and policies within `train_model` in `net.py`
- Experience Replay:
  - Circular buffer (default 50,000 entries), random sampling in small batches (default 128)
- Loss Function:
  - Cross-entropy (policy) + MSE (value), with policy as primary component; value weighting adjustable (default 0.4)
- Optimiser:
  - Adam (default learning rate 1e-3)

---

## Configuration Adjustments

Refer to file: `utils/config.py`.

This file contains most commonly adjustable configuration parameters.

- Board size and Connect-Four rules
- MCTS search depth (training/matches)
- Training batch size / Data augmentation / Learning rate / Buffer size
  - Rotation/flip augmentation details in `train_model` internal
- ...

To adjust parameters, modify according to the docstring guidance within the file.

---

## Recommended Progressive Training Workflow (code already supports this functionality)

1) 6×6 + Connect Four (quickest to grasp)
- Modify: `GameCore.ChessboardSize = 6`, `GameCore.WinCount = 4`
- Clear old model/data: `rm -f model.pth data/d1.json`
- Run 100–200 training games to verify model rapidly learns standard patterns

2) 9×9 + Five-in-a-row (Standard)
- Modify: `GameCore.ChessboardSize = 9`, `GameCore.WinCount = 5`
- Clear old model/data and retrain for 500–1000 games

3) 15×15 + Connect Five (Advanced)
- Modify: `GameCore.ChessboardSize = 15`
- Clear old model/data and conduct extended training (recommended 2000+ games)

Note: Larger boards increase the MCTS search space, slowing training/matches. Adjust MCTS iterations or reduce batch size accordingly.

---

## Feature Overview

- Lightweight and readable: Core implementation of AlphaZero's approach in hundreds of lines of code
- Self-play training: MCTS + policy-value network, closed-loop self-learning
- Visualised matches: Pygame window displays board, values, visit counts, policy probabilities
- Move order selection: Opening options include ‘I play Black first / I play White second (AI plays first)’
- Data Augmentation: Rotation/flipping enhances data diversity
- Experience Replay: Fixed-capacity circular buffer ensures stable training
- One-Click Board Switching: Modify configuration to change board and rules
- GPU Acceleration Support: Automatic detection of `cuda`

---

## Frequently Asked Questions

- Q: Dimension error after changing board size?
  - A: Delete old `model.pth` and `data/d1.json` then retrain.

- Q: Training/matches running slowly?
  - A: Reduce MCTS iterations (`utils/config.py`), use 6×6/9×9 boards, or enable GPU.

- Q: How do I train from scratch?
  - A: `rm -f model.pth data/d1.json && python train.py`

---

## Licence

This project is intended for educational and research purposes. For distribution or commercial use, please comply with the licence requirements of its dependencies (PyTorch, Pygame, etc.).