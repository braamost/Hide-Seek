"""
game_logic.py - Game mechanics and rules for Hide & Seek

This module handles the core game logic, including turn processing,
score calculation, and game state management.
"""

from player import PlayerType

class GameLogic:
    """Handles the core game mechanics and rules."""
    
    def __init__(self, world, hider, seeker):
        """
        Initialize the game logic.
        
        Args:
            world (World): The game world
            hider (Player): The hiding player
            seeker (Player): The seeking player
        """
        self.world = world
        self.hider = hider
        self.seeker = seeker
        self.round_number = 0
        self.game_over = False
    
    def play_round(self):
        """
        Play a single round of the game.
        
        Returns:
            tuple: (hider_pos, seeker_pos, score, found)
        """
        # Get moves from both players
        hider_pos = self.hider.make_move(self.world)
        seeker_pos = self.seeker.make_move(self.world)
        
        # Calculate score
        score = self.world.get_score(hider_pos, seeker_pos)
        
        # Update player scores
        found = (hider_pos == seeker_pos)
        if found:
            # Seeker found the hider
            self.seeker.add_win()
            # Score is negative from hider's perspective
            self.seeker.add_score(-score)  # Convert to seeker's perspective
        else:
            # Hider successfully hid
            self.hider.add_win()
            self.hider.add_score(score)
        
        self.round_number += 1
        
        return hider_pos, seeker_pos, score, found
    
    def reset_game(self):
        """Reset the game state."""
        self.round_number = 0
        self.game_over = False
        self.hider.reset_stats()
        self.seeker.reset_stats()
    
    def get_player_stats(self):
        """
        Get the current game statistics.
        
        Returns:
            dict: Dictionary containing game statistics
        """
        return {
            'round': self.round_number,
            'hider_score': self.hider.score,
            'seeker_score': self.seeker.score,
            'hider_wins': self.hider.wins,
            'seeker_wins': self.seeker.wins
        }