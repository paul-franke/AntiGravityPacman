# Project Rules and Import Standards

This file contains rules and coding standards for the **AntiGravityPacman** project to guide agent behavior in this and future sessions.

## 1. Project Context & Objectives
* **Project Name**: AntiGravityPacman
* **Goal**: Build a modern, high-performance Pacman game using Python and Pygame with rich aesthetics, smooth animations, and retro-futuristic arcade styling.
* **Technology Stack**:
  * Python 3.10+
  * Pygame (2D game library) for graphics, input, and audio rendering.

## 2. Import and Dependency Standards
To ensure consistency and clean code structure, adhere to the following import guidelines:
* **Python Modules**:
  * Use standard PEP 8 import standards. Group imports: standard library first, third-party libraries (e.g., `pygame`) second, and local project modules third.
  * Use absolute imports where possible (e.g., `from src.settings import WIDTH, HEIGHT`) or clean relative imports if appropriate.
  * Keep module imports clean, grouped, and sorted alphabetically at the top of files.
* **Asset Loading**:
  * Load images, audio files, and external fonts using relative paths relative to the project root.
  * Cache loaded assets to avoid reloading during the main game loop.
  * Organize assets cleanly under an `/assets/` directory (e.g., `/assets/images/`, `/assets/audio/`).

## 3. Code Readability and Quality Standards (No Hacks)
* **High Readability**: Code must be extremely clean, modular, and self-documenting. Use descriptive, meaningful variable and function names.
* **No Hacks**: Avoid clever, obscure, or "hacky" workarounds. Write explicit, standard Pythonic code. Prefer maintainability and clarity over micro-optimizations.
* **Type Hinting**: Use Python type annotations for all function signatures and class attributes to clarify design intent.
* **Comments and Docstrings**: Write clear docstrings for all classes and public functions following PEP 257. Use inline comments sparingly to explain the *why*, not the *what*.

## 4. Virtual Environment (Local Env)
* The project uses a local Python virtual environment in the `.venv/` directory.
* Always run commands, run tests, or execute script files using the virtual environment's python/pip:
  * Windows (PowerShell): `.venv\Scripts\python.exe`
  * Activation: `& .venv\Scripts\Activate.ps1`

## 5. Git Branching & Review Standards
* **Feature Branches**: For every subsequent change, create a new Git feature branch (e.g., `feature/description` or `branch-name`) off of the `main` branch.
* **Review Process**: Implement changes on the feature branch, stage and commit them to that branch, and present the changes (e.g., in a walkthrough/diff format) to the user for review.
* **Merge to Main**: Do not merge or commit directly to the `main` branch until the user explicitly reviews and approves the changes.

## 6. Session Resumption Guidelines
* At the start of a new session, read this file (`.agents/AGENTS.md`) and the workspace-root `GEMINI.md` to restore the project context, import rules, and python environment details.
* Maintain a clean directory structure and update the project documentation as development progresses.
