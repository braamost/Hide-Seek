"""
simulation.py - Simulation mode for Hide & Seek game

This module handles the simulation mode where the computer plays
against a random player for multiple rounds.
"""

from player import ComputerPlayer, PlayerType
from world import World1D, World2D, BaseWorld
from game_logic import GameLogic
from lp_solver import LPSolver

class Simulation:
    """Manages the simulation mode of the game."""
    
    def __init__(self, world_size, computer_player_type):
        """
        Initialize the simulation.
        
        Args:
            world_size (int): Size of the game world
            computer_player_type (PlayerType): Type of the computer player (HIDER/SEEKER)
        """
        self.world = World1D(world_size)
        self.lp_solver = LPSolver()
        
        # Create players
        if computer_player_type == PlayerType.HIDER:
            self.computer = ComputerPlayer(PlayerType.HIDER)
        else:
            self.computer = ComputerPlayer(PlayerType.SEEKER)
        
        # Set computer strategy
        payoff_matrix = self.world.generate_payoff_matrix()
        strategy = self.lp_solver.solve_game(payoff_matrix, computer_player_type)
        self.computer.set_strategy(strategy)
        
        # Create game logic
        if computer_player_type == PlayerType.HIDER:
            self.game = GameLogic(self.world, self.computer, self.random)
        else:
            self.game = GameLogic(self.world, self.random, self.computer)
    
    def run_simulation(self, num_rounds=100):
        """
        Run the simulation for a specified number of rounds.
        
        Args:
            num_rounds (int): Number of rounds to simulate
            
        Returns:
            dict: Dictionary containing simulation results
        """
        results = []
        
        for _ in range(num_rounds):
            result = self.game.play_round()
            results.append(result)
        
        stats = self.game.get_player_stats()
        
        return {
            'stats': stats,
            'results': results
        }
    
    def reset(self):
        """Reset the simulation."""
        self.game.reset_game()