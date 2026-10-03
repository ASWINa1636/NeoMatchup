# NeoMatchup [![Architecture diagram](https://gitdiagram.com/diagram-badge.svg)](https://gitdiagram.com/aswina1636/neomatchup?utm_source=readme&utm_medium=badge)

Welcome to **NeoMatchup** (formerly NeoPlato) — a modern, multi-game hub built with Python and Tkinter!

## Architecture

[![Architecture diagram of aswina1636/neomatchup](https://gitdiagram.com/aswina1636/neomatchup/diagram.png)](https://gitdiagram.com/aswina1636/neomatchup?utm_source=readme&utm_medium=picture)

## Technologies & Modules Used
This project was entirely built using native Python technologies without heavy external game engines (like Pygame or Unity). Here is everything we used:

1. **Python 3.x**: The core programming language.
2. **Tkinter (`tkinter`)**: The standard GUI library for Python, used for drawing all the graphics, window management, and handling user inputs.
3. **Tkinter Canvas**: Used extensively for drawing the games (Snake, Sudoku, Chess, 2048, etc.), rendering custom scrollbars, creating the data visualization charts (Pie Chart & Bar Chart) in the profile, and drawing micro-animations (like the sparkling particle effects).
4. **Custom Theme Engine**: A custom color interpolation and theming system (`core.theme`) that handles the dark mode UI, vibrant colors, and aesthetic styling.
5. **JSON Storage**: `json` and `os` modules were used to save and load player profiles, high scores, NeoCoins balance, and unlocked achievements locally (`core.storage`).
6. **Sockets (`socket`)**: Used for the P2P Online Multiplayer system. We created a local server/client architecture using standard TCP sockets.
7. **Threading (`threading`)**: Used to run the multiplayer server listener in the background without freezing the Tkinter main UI loop.
8. **Base64 (`base64`) & Struct (`struct`)**: Used in `multiplayer/utils.py` to seamlessly encode a player's IP address and Port into a simple alphanumeric "Connect Code" that friends can share to join games.

## Core Features

| Feature | Description |
| :--- | :--- |
| **🎮 10 Playable Games** | A diverse collection of 10 classic and modern games seamlessly integrated into one app. |
| **✨ Unified Interface** | Smooth navigation and a modern, beautiful dark-mode UI with particle animations and transitions. |
| **💰 Virtual Currency** | Earn "NeoCoins" by playing and winning games. Spend them in the built-in Shop! |
| **👤 Player Profile** | Detailed statistics tracking including interactive pie charts (games played) and bar charts (playtime). |
| **🏆 Achievements** | Over 30 unique achievements to unlock by hitting milestones and mastering the different games. |
| **🌐 Multiplayer** | Local hot-seat support and online peer-to-peer multiplayer using custom Connect Codes! |

## The Game Roster
NeoMatchup includes the following 10 fully-playable titles:
1. **Sudoku**: The classic number puzzle with multiple difficulty levels and a hint system.
2. **Chess**: Fully featured 2-player chess board with move validation and online multiplayer.
3. **Tic-Tac-Toe**: A quick, classic 3x3 game supporting both local and online versus modes.
4. **Snake**: The retro arcade classic where you eat food to grow, featuring variable speed settings.
5. **Minesweeper**: Clear the minefield without detonating any bombs. Supports custom grid sizes!
6. **2048**: Slide and merge tiles to reach the elusive 2048 tile in this addictive puzzle game.
7. **Connect Four**: Drop your colored discs to connect four in a row against a friend.
8. **Memory Match**: Test your memory by flipping cards and finding matching pairs.
9. **Roulette**: A casino-style game where you can bet your hard-earned NeoCoins on numbers and colors.
10. **Wordle**: Guess the hidden 5-letter word in 6 tries, with color-coded feedback on each guess.

## Running the Game

### Method 1: Using the Standalone Executable (No Python Required)
We provide standalone builds for both Windows and Linux!
- **Windows**: Navigate to the `dist/NeoPlato/` directory and simply double-click `NeoPlato.exe`.
- **Linux**: Compile your own Linux executable by opening your terminal in the root folder and running `bash build_linux.sh` (requires Python & PyInstaller installed locally). This will place the standalone binary in the `dist/NeoPlato` folder.

### Method 2: Running from Source
To run NeoMatchup natively via Python:
1. Make sure you have Python 3.x installed.
2. Ensure you've installed required packages from `requirements.txt` (if applicable).
3. Run the following command in your terminal:
   ```bash
   python main.py
   ```

## Multiplayer Setup (Online)
Some games support online play! To play with a friend in a different location:
1. The **Host** clicks "Host Game".
2. The **Host** either sets up Port Forwarding on their router (port `52401`) OR both players join a Virtual LAN like **Hamachi** or **ZeroTier**.
3. The **Client** clicks "Join Game" and enters the Host's Public IP (or Virtual LAN IP) to connect!

## Why `.pyc` Instead of `.py`?
If you browse the source code for this project, you may notice that the core game logic is stored in `.pyc` (Python Compiled) bytecode files instead of traditional `.py` source text files. 

During the development cycle, a critical file corruption event occurred that wiped the raw `.py` source text files. As professional developers, we leveraged Python's `__pycache__` mechanism to fully recover the game. Python automatically compiles all imported `.py` files into `.pyc` bytecode files before execution. These `.pyc` files contain the exact same logic, are perfectly valid for the Python interpreter to run, and actually execute *slightly faster* than `.py` files because the compilation step is skipped! 

To add new features and updates, we use a single uncompiled `main.py` file that imports these `.pyc` modules and dynamically "monkey-patches" the compiled classes at runtime—a powerful advanced Python technique that allows us to seamlessly update the game without needing the original uncompiled source code.

Enjoy playing NeoMatchup!
