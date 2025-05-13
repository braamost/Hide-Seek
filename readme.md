# Hide & Seek Game

A game theory implementation of Hide & Seek with linear programming for optimal strategies.

## Project Description

This project implements a Hide & Seek game based on game theory concepts. The game is played on a linear world where two players (a hider and a seeker) compete. The game features:

- A linear world with places of different types (hard, neutral, easy)
- Human vs. Computer gameplay
- Linear programming solver for optimal strategies
- Simulation mode with random players
- Qt-based graphical user interface

## Project Structure

The project is organized into the following Python modules:

- `main.py`: Entry point for the application
- `game_logic.py`: Game mechanics and rules
- `lp_solver.py`: Linear programming problem formulation and solver
- `game_ui.py`: Qt GUI implementation
- `player.py`: Player classes (Human and Computer)
- `world.py`: Game world representation
- `simulation.py`: Simulation mode functionality

## Getting Started

### Prerequisites

- Python 3.7+
- Dependencies listed in `requirements.txt`

### Installation

1. Clone the repository or download the source code
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Running the Game

To launch the game, run:

```bash
python main.py
```

## Game Rules

The game is played on an N-sized linear world, where:

- The **Hider** chooses a location to hide
- The **Seeker** attempts to find the hider by exploring a location

### Scoring Mechanism

There are three types of places in the world:
1. **Hard places** for the seeker: The seeker gets higher points upon winning, the hider gets lower points
2. **Neutral places**: Both hider and seeker get the same points upon winning
3. **Easy places** for the seeker: The seeker gets lower points upon winning, the hider gets higher points

## Implementation Details

### Game Initialization

1. Create a world of size N
2. Randomly assign types to each place in the world
3. Generate a payoff matrix based on the place types
4. Solve the linear programming problem to find optimal strategies

### Linear Programming Formulation

The game is formulated as a linear programming problem:
- From the **hider's perspective**: Maximize the minimum expected payoff
- From the **seeker's perspective**: Minimize the maximum expected payoff

### Bonus Features

#### Proximity Score
- The hider is penalized if the seeker's choice is near the hider's place
- Score multipliers are applied based on the distance between locations

#### 2D World
- Instead of a linear world, places can be arranged in a 2D grid

## Development

To implement the project, focus on completing the TODO sections in each file. The key areas to implement are:

1. World initialization and payoff matrix generation
2. Linear programming problem formulation and solving
3. Player move logic implementation
4. GUI visualization components
5. Game simulation mode

Start by implementing the core game mechanics before working on the GUI components.

## github repo


