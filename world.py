"""
world.py - Game world representation for the Hide & Seek game

This module handles the creation and management of the game world,
including place types and scoring.
"""

import random
import numpy as np
from enum import Enum
from player import PlayerType

class PlaceType(Enum):
    """Enumeration for different types of places in the world."""
    EASY = 1    # Easy for seeker
    NEUTRAL = 2 # Neutral
    HARD = 3    # Hard for seeker

class BaseWorld:
    """Base class for different world dimensions (1D, 2D "bonus" )"""
    def __init__(self, human_choice=PlayerType.HIDER, use_proximity=False):
        """
        Initialize the base world.
        
        Args:
            human_choice (PlayerType): The player's choice (HIDER or SEEKER)
            use_proximity (bool): Whether to use proximity in scoring
        """
        self.human_choice = human_choice
        self.use_proximity = use_proximity

    def get_place_type(self, position):
        """Get the type of place at the given position."""
        raise NotImplementedError("Subclasses must implement this method")

    def get_score(self, hider_pos, seeker_pos):
        """Get the score for a given hider and seeker position."""
        raise NotImplementedError("Subclasses must implement this method")

    def generate_payoff_matrix(self):
        """Generate the game payoff matrix from the hider's perspective."""
        raise NotImplementedError("Subclasses must implement this method")

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
        raise NotImplementedError("Subclasses must implement this method")

class World1D(BaseWorld):
    """Represents the game world in a 1-dimensional linear array of places."""
    def __init__(self, size, human_choice=PlayerType.HIDER, use_proximity=False):
        """
        Initialize the 1D game world.
        
        Args:
            size (int): The size of the linear world (number of places)
            human_choice (PlayerType): The player's choice (HIDER or SEEKER)
            use_proximity (bool): Whether to use proximity in scoring
        """
        super().__init__(human_choice, use_proximity)
        self.size = size
        self.places = [random.choice(list(PlaceType)) for _ in range(size)]
        self.payoff_matrix = np.ones((size, size))
        self.generate_payoff_matrix()

    def get_place_type(self, position):
        """
        Get the type of place at the given position.
        
        Args:
            position (int): Position in the world
            
        Returns:
            PlaceType: The type of the place
        """
        if position < 0 or position >= self.size:
            raise ValueError("Position out of bounds")
        return self.places[position]

    def get_score(self, hider_pos, seeker_pos):
        """
        Get the score for a given hider and seeker position.
        
        Args:
            hider_pos (int): Hider's position
            seeker_pos (int): Seeker's position
            
        Returns:
            int: the score for the human player if he chooses this position
        """
        if hider_pos < 0 or seeker_pos < 0 or hider_pos >= self.size or seeker_pos >= self.size:
            raise ValueError("Position out of bounds")
        score = self.payoff_matrix[hider_pos][seeker_pos]
        if self.use_proximity:
            score = self.apply_proximity_score(score, hider_pos, seeker_pos)
        return score

    def generate_payoff_matrix(self):
        """
        Generate the game payoff matrix from the hider's perspective.
        
        Returns:
            list: 2D list representing the payoff matrix
        """
        for i in range(self.size):
            for j in range(self.size):
                if (i == j and self.human_choice == PlayerType.HIDER) or (i != j and self.human_choice == PlayerType.SEEKER):
                    self.payoff_matrix[i][j] *= -1
                if i != j and self.places[i] == PlaceType.EASY:
                    self.payoff_matrix[i][j] *= 2
                if i == j and self.places[i] == PlaceType.HARD:
                    self.payoff_matrix[i][j] *= 3

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
        diff = abs(hider_pos - seeker_pos)
        if diff == 1:
            return base_score * 0.5
        elif diff == 2:
            return base_score * 0.75
        return base_score

class World2D(BaseWorld):
    """Represents the game world in a 2-dimensional grid of places."""
    def __init__(self, rows, cols, human_choice=PlayerType.HIDER, use_proximity=False):
        """
        Initialize the 2D game world.
        
        Args:
            rows (int): Number of rows in the grid
            cols (int): Number of columns in the grid
            human_choice (PlayerType): The player's choice (HIDER or SEEKER)
            use_proximity (bool): Whether to use proximity in scoring
        """
        super().__init__(human_choice, use_proximity)
        self.rows = rows
        self.cols = cols
        self.size = rows * cols
        self.places = [[random.choice(list(PlaceType)) for _ in range(cols)] for _ in range(rows)]
        self.payoff_matrix = np.ones((self.size, self.size))
        self.generate_payoff_matrix()

    def pos_to_index(self, position):
        """Convert 2D position (row, col) to 1D index."""
        row, col = position
        return row * self.cols + col

    def index_to_pos(self, index):
        """Convert 1D index to 2D position (row, col)."""
        return divmod(index, self.cols)

    def get_place_type(self, position):
        """
        Get the type of place at the given 2D position.
        
        Args:
            position (tuple): (row, col) position in the world
            
        Returns:
            PlaceType: The type of the place
        """
        row, col = position
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            raise ValueError("Position out of bounds")
        return self.places[row][col]

    def get_score(self, hider_pos, seeker_pos):
        """
        Get the score for a given hider and seeker position.
        
        Args:
            hider_pos (tuple): Hider's (row, col) position
            seeker_pos (tuple): Seeker's (row, col) position
            
        Returns:
            int: the score for the human player if he chooses this position
        """
        hider_index = self.pos_to_index(hider_pos)
        seeker_index = self.pos_to_index(seeker_pos)
        if hider_index < 0 or seeker_index < 0 or hider_index >= self.size or seeker_index >= self.size:
            raise ValueError("Position out of bounds")
        

        score = self.payoff_matrix[hider_index][seeker_index]

        if self.use_proximity:
            score = self.apply_proximity_score(score, hider_pos, seeker_pos)
        return score

    def generate_payoff_matrix(self):
        """
        Generate the game payoff matrix from the hider's perspective.
        
        Returns:
            list: 2D list representing the payoff matrix
        """
        for i in range(self.size):
            for j in range(self.size):
                h_row, h_col = self.index_to_pos(i)
                score = 1
                if (i == j and self.human_choice == PlayerType.HIDER) or (i != j and self.human_choice == PlayerType.SEEKER):
                    score *= -1
                if i != j and self.places[h_row][h_col] == PlaceType.EASY:
                    score *= 2
                if i == j and self.places[h_row][h_col] == PlaceType.HARD:
                    score *= 3
                self.payoff_matrix[i][j] = score

    def apply_proximity_score(self, base_score, hider_pos, seeker_pos):
        """
        Apply proximity score adjustment (Bonus feature).
        
        Args:
            base_score (float): Original score
            hider_pos (tuple): Hider's (row, col) position
            seeker_pos (tuple): Seeker's (row, col) position
            
        Returns:
            float: Adjusted score based on proximity
        """
        h_row, h_col = hider_pos
        s_row, s_col = seeker_pos
        diff = abs(h_row - s_row) + abs(h_col - s_col)
        if diff == 1:
            return base_score * 0.5
        elif diff == 2:
            return base_score * 0.75
        return base_score
    

# if __name__ == "__main__":
#     # Example usage
#     world_1d = World1D(size=4, human_choice=PlayerType.HIDER, use_proximity=True)
#     print("1D World Payoff Matrix:")
#     print(world_1d.payoff_matrix)
#     print("score:", world_1d.get_score(0, 1)) #2
#     print("score:", world_1d.get_score(1, 0)) #1
#     print("score:", world_1d.get_score(0, 0)) #-1

#     # world_2d = World2D(rows=2, cols=2, human_choice=PlayerType.SEEKER, use_proximity=True)
#     # print("2D World Payoff Matrix:")
#     # print(world_2d.payoff_matrix)
#     # print("score:", world_2d.get_score((0, 0), (1, 1))) #2
#     # print("score:", world_2d.get_score((0, 1), (1, 0))) #1
