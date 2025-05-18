"""
player.py - Player classes for the Hide & Seek game

This module defines the player classes for the game, including
both human and computer players.
"""

import random
from enum import Enum

class PlayerType(Enum):
    """Enumeration for different player types."""
    HIDER = 1
    SEEKER = 2

class Player:
    """Base class for all players."""
    
    def __init__(self, player_type):
        """
        Initialize a player.
        
        Args:
            player_type (PlayerType): Type of the player (HIDER or SEEKER)
        """
        self.player_type = player_type
        self.score = 0
        self.wins = 0
    
    def make_move(self, world):
        """
        Make a move in the game.
        
        Args:
            world (World): The game world
            
        Returns:
            int: The position chosen by the player
        """
        raise NotImplementedError("Subclasses must implement make_move()")
    
    def add_score(self, points):
        """
        Add points to the player's score.
        
        Args:
            points (int): Points to add
        """
        self.score += points
    
    def add_win(self):
        """Record a win for the player."""
        self.wins += 1
    
    def reset_stats(self):
        """Reset the player's statistics."""
        self.score = 0
        self.wins = 0

class HumanPlayer(Player):
    """Human player class."""
    
    def __init__(self, player_type):
        """Initialize a human player."""
        super().__init__(player_type)
    
    def make_move(self, world, choice):
        """
        Make a move in the game based on user input.
        
        Args:
            world (World): The game world
            
        Returns:
            int: The position chosen by the player
        """
        # The UI will handle getting the player's input

        return choice

class ComputerPlayer(Player):
    """Computer player using optimal strategy based on linear programming."""
    
    def __init__(self, player_type):
        """Initialize a computer player."""
        super().__init__(player_type)
        self.strategy_probabilities = []
    
    def set_strategy(self, probabilities):
        """
        Set the computer's strategy based on LP solution.
        
        Args:
            probabilities (list): List of probabilities for each position
        """
        self.strategy_probabilities = probabilities
    
    def make_move(self, world):
        """
        Make a move based on the optimal strategy.
        
        Args:
            world (World): The game world
            
        Returns:
            int: The position chosen by the computer
        """
        # TODO: Implement move selection based on strategy probabilities
        # Choose a position randomly based on the probability distribution
        pass
