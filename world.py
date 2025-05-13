"""
world.py - Game world representation for the Hide & Seek game

This module handles the creation and management of the game world,
including place types and scoring.
"""

import random
from enum import Enum

class PlaceType(Enum):
    """Enumeration for different types of places in the world."""
    EASY = 1    # Easy for seeker
    NEUTRAL = 2 # Neutral
    HARD = 3    # Hard for seeker

class World:
    """Represents the game world with places of different types."""
    
    def __init__(self, size):
        """
        Initialize the game world.
        
        Args:
            size (int): The size of the linear world (number of places)
        """
        self.size = size
        self.places = []
        self.payoff_matrix = []
        self.initialize_world()
    
    def initialize_world(self):
        """Initialize the world with random place types and scores."""
        # TODO: Implement world initialization with random place types
        # TODO: Assign scores to each place based on type
        # TODO: Create payoff matrix based on scores and place types
        pass
    
    def get_place_type(self, position):
        """
        Get the type of place at the given position.
        
        Args:
            position (int): Position in the world
            
        Returns:
            PlaceType: The type of the place
        """
        # TODO: Implement getting place type
        pass
    
    def get_score(self, hider_pos, seeker_pos):
        """
        Get the score for a given hider and seeker position.
        
        Args:
            hider_pos (int): Hider's position
            seeker_pos (int): Seeker's position
            
        Returns:
            int: The score from the hider's perspective
        """
        # TODO: Implement score calculation based on positions
        # If hider is found (hider_pos == seeker_pos), return negative score
        # Otherwise return positive score based on place type
        pass
    
    def generate_payoff_matrix(self):
        """
        Generate the game payoff matrix from the hider's perspective.
        
        Returns:
            list: 2D list representing the payoff matrix
        """
        # TODO: Implement payoff matrix generation
        pass
    
    def apply_proximity_score(self, base_score, hider_pos, seeker_pos):
        """
        Apply proximity score adjustment (Bonus feature).
        
        Args:
            base_score (float): Original score
            hider_pos (int): Hider's position
            seeker_pos (int): Seeker's position
            
        Returns:
            float: Adjusted score based on proximity
        """
        # TODO: Implement proximity score adjustment
        pass