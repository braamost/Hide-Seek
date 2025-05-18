"""
simulation.py - Simulation mode for Hide & Seek game

This module handles the simulation mode where the computer plays
against a random player for multiple rounds.
"""

import numpy as np
from player import ComputerPlayer, PlayerType
from world import World1D, World2D, BaseWorld
from game_logic import GameLogic
from lp_solver import LPSolver

class Simulation:
    """Manages the simulation mode of the game."""
    
    def __init__(self, world):
        """
        Initialize the simulation.
        
        Args:
            world (BaseWorld): The game world (either World1D or World2D)
        """
        self.world = world
        self.lp_solver = LPSolver()
        
        # Create players for both roles to simulate
        self.hider = ComputerPlayer(PlayerType.HIDER)
        self.seeker = ComputerPlayer(PlayerType.SEEKER)
        
        # Set strategies for both players
        payoff_matrix = self.world.generate_payoff_matrix()
        # Convert to numpy array
        payoff_matrix_np = np.array(payoff_matrix)
        
        # Important: For zero-sum games, the seeker's payoff matrix is the negative transpose
        # of the hider's payoff matrix
        seeker_payoff_matrix = -payoff_matrix_np.T
        
        # Solve for optimal strategies
        hider_strategy = self.lp_solver.solve_game(payoff_matrix_np, PlayerType.HIDER)
        seeker_strategy = self.lp_solver.solve_game(seeker_payoff_matrix, PlayerType.SEEKER)
        
        # Debug print
        print("Debug - Strategies:")
        print(f"Hider: {hider_strategy}")
        print(f"Seeker: {seeker_strategy}")
        
        self.hider.set_strategy(hider_strategy)
        self.seeker.set_strategy(seeker_strategy)
        
        # Create game logic
        self.game_logic = GameLogic(self.world, self.hider, self.seeker)
        
        # Track simulation statistics
        self.hider_wins = 0
        self.seeker_wins = 0
        self.total_payoff = 0
        self.rounds_played = 0
    
    def run(self, num_rounds=100):
        """
        Run the simulation for a specified number of rounds.
        
        Args:
            num_rounds (int): Number of rounds to simulate
            
        Returns:
            dict: Dictionary containing simulation results
        """
        self.hider_wins = 0
        self.seeker_wins = 0
        self.total_payoff = 0
        self.rounds_played = 0
        
        for _ in range(num_rounds):
            hider_pos, seeker_pos, payoff, found = self.game_logic.play_round()
            
            if found:
                self.seeker_wins += 1
            else:
                self.hider_wins += 1
                
            self.total_payoff += payoff
            self.rounds_played += 1
        
        return self.get_results()
    
    def next_round(self):
        """
        Generator that yields the next round of simulation.
        
        Yields:
            tuple: (hider_pos, seeker_pos, payoff, found, stats)
            where stats is a dictionary with current statistics
        """
        # Get moves from both players
        hider_pos = self.hider.make_move(self.world)
        seeker_pos = self.seeker.make_move(self.world)
        
        # Calculate score and update game state
        hider_pos, seeker_pos, payoff, found = self.game_logic.play_round()
        
        if found:
            self.seeker_wins += 1
        else:
            self.hider_wins += 1
            
        self.total_payoff += payoff
        self.rounds_played += 1
        
        # Return current round results and stats
        stats = self.get_results()
        
        return hider_pos, seeker_pos, payoff, found, stats
    
    def get_results(self):
        """
        Get the current simulation results.
        
        Returns:
            dict: Dictionary containing simulation results
        """
        if self.rounds_played == 0:
            return {
                'hider_win_rate': 0,
                'seeker_win_rate': 0,
                'avg_payoff': 0,
                'rounds_played': 0,
                'hider_wins': 0,
                'seeker_wins': 0
            }
        
        return {
            'hider_win_rate': (self.hider_wins / self.rounds_played) * 100,
            'seeker_win_rate': (self.seeker_wins / self.rounds_played) * 100,
            'avg_payoff': self.total_payoff / self.rounds_played,
            'rounds_played': self.rounds_played,
            'hider_wins': self.hider_wins,
            'seeker_wins': self.seeker_wins
        }
    
    def reset(self):
        """Reset the simulation."""
        self.game_logic.reset_game()
        self.hider_wins = 0
        self.seeker_wins = 0
        self.total_payoff = 0
        self.rounds_played = 0