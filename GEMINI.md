# Project Standards: AntiGravityPacman (Python)

This file outlines the coding standards, directory structure, and import guidelines for the Python/Pygame-based AntiGravityPacman project. All agent interactions should follow these definitions.

## 1. Directory Structure
Ensure files are organized logically according to this structure:
```
AntiGravityPacman/
├── .agents/
│   └── AGENTS.md          # Workspace rules and session persistence
├── .venv/                 # Python local virtual environment
├── assets/
│   ├── images/            # Game sprites, backgrounds, logos
│   └── audio/             # Sound effects and music tracks
├── src/
│   ├── __init__.py
│   ├── main.py            # Main game entry point and loop
│   ├── pacman.py          # Pacman player entity logic
│   ├── ghost.py           # Ghost entity behaviors and AI
│   ├── board.py           # Maze layout, tiles, and collision
│   └── settings.py        # Game configurations (colors, tile size, speeds)
├── requirements.txt       # Python package dependencies
└── GEMINI.md              # Project standards (this file)
```

## 2. Coding & Import Conventions
* **PEP 8 Guidelines**: Adhere to standard Python styling guidelines (PEP 8) for class names (PascalCase), function/variable names (snake_case), and constants (UPPER_CASE).
* **Modular Architecture**: Separate game state management and main loop (`main.py`) from entities (`pacman.py`, `ghost.py`) and level representation (`board.py`).
* **Pygame Conventions**:
  * Utilize `pygame.sprite.Sprite` and sprite groups for entities.
  * Implement double-buffering using `pygame.display.flip()` or `pygame.display.update()`.
  * Control frame rates using `pygame.time.Clock()`.

## 3. Code Readability and Design Quality
* **High Readability**: Code must be explicit, modular, and readable.
* **No Hacks**: No magic numbers, hacky shortcuts, or obscure logic. Use named constants (defined in `settings.py`) for all configurations.
* **Type Annotations**: Annotate functions and variables to ensure clarity of data types and return signatures.

## 4. Aesthetic & UI Rules
* **Theme**: Modern neon/dark theme matching Pacman's arcade retro-futurism (cyberpunk blue, hot pink, lime green, and dark grid lines).
* **Smooth Animation**: Implement delta time-based movements to ensure frame-rate independent gameplay.

## 5. Git Branching & Review Process
* **Workflow**: Make all feature edits on separate git feature branches. Commit modifications to the feature branch, and submit the changes to the user for review.
* **Master Branch Safeguard**: Never commit directly to `main` (or `master`) without explicit user code-review confirmation.
