"""
player.py - Player classes for the Hide & Seek game

This module defines the player classes for the game, including
both human and computer players.
"""

import random
import numpy as np
from enum import Enum

class PlayerType(Enum):
    HIDER = 1
    SEEKER = 2

class Player:
    def __init__(self, player_type):
        self.type = player_type
        self.score = 0
        self.wins = 0
    
    def make_move(self, world):
        raise NotImplementedError("Subclasses must implement make_move()")
    
    def add_score(self, points):
        self.score += points
    
    def add_win(self):
        self.wins += 1
    
    def reset_stats(self):
        self.score = 0
        self.wins = 0

class HumanPlayer(Player):
    def __init__(self, player_type):
        """Initialize a human player."""
        super().__init__(player_type)
        self.move = None
    
    def set_move(self, move):
        """Set the player's move."""
        self.move = move
    
    def make_move(self, world):
        """Make a move based on the player's input."""
        return self.move

class ComputerPlayer(Player):
    def __init__(self, player_type):
        """Initialize a computer player."""
        super().__init__(player_type)
        self.strategy_probabilities = []
    
    def set_strategy(self, probabilities):
        self.strategy_probabilities = probabilities
    
    def make_move(self, world):
        if (isinstance(self.strategy_probabilities, list) and not self.strategy_probabilities) or \
           (isinstance(self.strategy_probabilities, np.ndarray) and self.strategy_probabilities.size == 0) or \
           len(self.strategy_probabilities) != world.size:
            raise ValueError("Strategy probabilities not set or do not match world size")
        else:
            idx = np.random.choice(world.size, p=self.strategy_probabilities)
        # For 2D world, convert index to (row, col)
        if hasattr(world, 'index_to_pos'):
            return world.index_to_pos(idx)
        else:
            return idx

class RandomPlayer(Player):
    def __init__(self, player_type):
        """Initialize a random player."""
        super().__init__(player_type)
    
    def make_move(self, world):
        """Make a random move."""
        if hasattr(world, 'rows') and hasattr(world, 'cols'):
            # For 2D world
            row = random.randint(0, world.rows - 1)
            col = random.randint(0, world.cols - 1)
            return (row, col)
        else:
            # For 1D world
            return random.randint(0, world.size - 1)
