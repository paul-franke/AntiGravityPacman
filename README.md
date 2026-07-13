# AntiGravityPacman

An implementation of Pacman using Google's Antigravity. 
The purpose of this game is to experience the power and enablement AntiGravity offers during development.

There are still some anoying bugs in this pacman implementation, however it's playable. Take it for a spin!!
Top prio pr's to fix: ghosts movements and that terrible sound implementation.

---

## Features
* **Arcade-Accurate Ghost AI**: Standard individual AI target targeting for Blinky (chase), Pinky (intercept), Inky (sandwich vector), and Clyde (shy/distracted scatter).
* **60Hz VBLANK Simulation**: Game loop and rendering updates are synced exactly to a 60Hz tick count to simulate vertical blanking.



---

## Installation & Setup

1. **Prerequisites**: Ensure you have Python 3.10+ installed.
2. **Setup Virtual Environment**:
   ```powershell
   python -m venv .venv
   ```
3. **Install Dependencies**:
   Activate the virtual environment and install the required packages:
   ```powershell
   # Windows (PowerShell)
   & .venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```

---

## How to Run the Game

You can run the game directly from the project root using the virtual environment interpreter:

```powershell
.venv\Scripts\python.exe -m src.main
```

Alternatively, activate the virtual environment first:
```powershell
# 1. Activate the environment
& .venv\Scripts\Activate.ps1

# 2. Run the game
python -m src.main
```

---

## Controls
* **Move**: `W` / `A` / `S` / `D` or `Arrow Keys` (supports queue-turning at corners)
* **Pause**: `ESC`
* **Quit**: Close the window or press `ESC` in paused menu

---

## Project Standards
Coding standards, directory layout, and development guidelines are stored in:
* **[GEMINI.md](GEMINI.md)**: Coding conventions and directory architectures.
* **[.agents/AGENTS.md](.agents/AGENTS.md)**: Workspace environment paths, module import rules, and Git branching guidelines.
