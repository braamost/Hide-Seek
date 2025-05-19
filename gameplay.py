"""
gameplay.py - Gameplay methods for the Hide & Seek game

This module contains gameplay-related methods for the Hide & Seek game UI.
"""

from PyQt5.QtWidgets import QMessageBox, QLabel
from PyQt5.QtCore import Qt, QTimer

from player import PlayerType, HumanPlayer, ComputerPlayer
from world import World1D, World2D
from game_logic import GameLogic
from lp_solver import LPSolver
from simulation import Simulation
import numpy as np

class GamePlay:
    """Handles gameplay methods for the Hide & Seek game UI."""
    
    def initialize_game(self):
        """Initialize the game with the selected parameters."""
        world_size = self.world_size_spin.value()
        player_type = PlayerType(self.player_type_group.checkedId())
        world_dimension = self.world_dim_group.checkedId()
        
        # Initialize world based on selected dimension
        if world_dimension == 1:
            self.world = World1D(world_size, human_choice=player_type, use_proximity=True)
        else:  # 2D world
            self.world = World2D(world_size, world_size, human_choice=player_type, use_proximity=True)
        
        # Initialize LP solver
        self.lp_solver = LPSolver()
        
        # Reset selection tracking
        if hasattr(self, 'selected_position'):
            self.selected_position = None

        payoff_matrix_np = np.array(self.world.get_payoff_matrix())

        # Initialize players
        if player_type == PlayerType.HIDER:
            self.human_player = HumanPlayer(PlayerType.HIDER)
            self.computer_player = ComputerPlayer(PlayerType.SEEKER)

            strategy = self.lp_solver.solve_game(payoff_matrix_np, PlayerType.SEEKER)
            self.computer_player.set_strategy(strategy)
            
            # Create game logic
            self.game_logic = GameLogic(self.world, self.human_player, self.computer_player)
        else:
            self.human_player = HumanPlayer(PlayerType.SEEKER)
            self.computer_player = ComputerPlayer(PlayerType.HIDER)
            

            strategy = self.lp_solver.solve_game(payoff_matrix_np, PlayerType.HIDER)
            self.computer_player.set_strategy(strategy)
            
            # Create game logic
            self.game_logic = GameLogic(self.world, self.computer_player, self.human_player)
        
        # Update UI
        self.update_world_grid()
        self.update_payoff_matrix()
        self.update_probability_visualization()
        
        # Switch to the game board tab after initialization
        self.tab_widget.setCurrentIndex(0)
        
        # Enable game controls
        self.play_btn.setEnabled(False)  # Disabled until player makes a move
        self.reset_btn.setEnabled(True)
        
        # Show strategy explanation
        self.show_status_message(f"Game initialized. You are playing as {player_type.name}.\nClick on a position in the grid to make a move.\nCheck the Strategy Visualization tab to see computer probabilities.")
    
    def handle_button_click(self, position):
        """Handle a button click on the grid."""
        if not self.game_logic:
            return
            
        # Reset all buttons to their base style first
        self.reset_all_buttons_to_base_style()
        
        # Set the human player's move
        self.human_player.set_move(position)
        
        # Enable play button to execute the round
        self.play_btn.setEnabled(True)
        
        # Switch to the game board tab if not already there
        if self.tab_widget.currentIndex() != 0:
            self.tab_widget.setCurrentIndex(0)
        
        # Show visual feedback for selected position
        self.show_selection_feedback(position)
        
        # Show status message
        self.show_position_info(position)
    
    def play_round(self):
        """Play a round of the game."""
        if not self.game_logic:
            return
        
        # Switch to the game board tab if not already there
        if self.tab_widget.currentIndex() != 0:
            self.tab_widget.setCurrentIndex(0)
        
        # Human player's move was already set by button click
        
        # Execute round (game_logic.play_round will get the computer's move internally)
        result = self.game_logic.play_round()
        hider_pos, seeker_pos, score, found = result
        
        # Determine which position is the computer's move
        if self.human_player.type == PlayerType.HIDER:
            computer_move = seeker_pos
        else:
            computer_move = hider_pos
        
        # Update UI with the result
        self.update_game_ui(result, self.human_player.move, computer_move)
        
        # Update statistics
        self.update_stats()
        
        # Clear selection
        self.selected_position = None
        
        # Disable play button until next move is selected
        self.play_btn.setEnabled(False)
    
    def update_game_ui(self, result, human_move, computer_move):
        """Update the UI with the result of the round."""
        # Update result label
        hider_pos, seeker_pos, score, found = result
        self.result_label.setText(f"Result: {'Seeker found Hider' if found else 'Hider escaped'}")
        
        # Update round number
        round_num = int(self.round_label.text().split(':')[-1].strip()) + 1
        self.round_label.setText(f"Round: {round_num}")
        
        # Show results in status message
        human_role = self.human_player.type.name
        computer_role = self.computer_player.type.name
        
        if isinstance(self.world, World1D):
            msg = f"Round {round_num} results:\n"
            msg += f"Human ({human_role}) played position {human_move}\n"
            msg += f"Computer ({computer_role}) played position {computer_move}\n"
            msg += f"Outcome: {'Seeker found Hider' if found else 'Hider escaped'}\n"
            msg += f"Score: {score}\n\n"
            msg += "Check the Strategy Visualization tab to see computer probabilities."
        else:  # 2D world
            h_row, h_col = human_move
            c_row, c_col = computer_move
            msg = f"Round {round_num} results:\n"
            msg += f"Human ({human_role}) played position ({h_row}, {h_col})\n"
            msg += f"Computer ({computer_role}) played position ({c_row}, {c_col})\n"
            msg += f"Outcome: {'Seeker found Hider' if found else 'Hider escaped'}\n"
            msg += f"Score: {score}\n\n"
            msg += "Check the Strategy Visualization tab to see computer probabilities."
            
        # Update status message
        self.show_status_message(msg)
        
        # Update visuals
        self.highlight_positions()
        
        # Update the strategy visualization as the computer's strategy may have changed
        self.update_probability_visualization()
    
    def reset_game(self):
        """Reset the game."""
        if not self.world:
            return
            
        # Get current settings
        player_type = PlayerType(self.player_type_group.checkedId())
            
        # Clear game state
        if isinstance(self.world, World1D):
            self.world = World1D(self.world.size, human_choice=player_type, use_proximity=True)
        elif isinstance(self.world, World2D):
            self.world = World2D(self.world.rows, self.world.cols, human_choice=player_type, use_proximity=True)
            
        # Reset players
        if player_type == PlayerType.HIDER:
            self.human_player = HumanPlayer(PlayerType.HIDER)
            self.computer_player = ComputerPlayer(PlayerType.SEEKER)
        else:
            self.human_player = HumanPlayer(PlayerType.SEEKER)
            self.computer_player = ComputerPlayer(PlayerType.HIDER)
            
        # Set computer strategy
        payoff_matrix = self.world.get_payoff_matrix()

        strategy = self.lp_solver.solve_game(payoff_matrix, self.computer_player.type)
        self.computer_player.set_strategy(strategy)
        
        # Reset game logic
        if player_type == PlayerType.HIDER:
            self.game_logic = GameLogic(self.world, self.human_player, self.computer_player)
        else:
            self.game_logic = GameLogic(self.world, self.computer_player, self.human_player)
        
        # Reset UI
        self.update_world_grid()
        self.update_payoff_matrix()
        self.update_probability_visualization()
        
        # Reset play button state
        self.play_btn.setEnabled(False)
        
        # Reset stats
        self.human_score_label.setText("Score: 0")
        self.human_wins_label.setText("Wins: 0")
        self.computer_score_label.setText("Score: 0")
        self.computer_wins_label.setText("Wins: 0")
        self.round_label.setText("Round: 0")
        self.result_label.setText("Result: -")
    
    def run_simulation(self):
        """Initialize and prepare a step-by-step simulation."""
        # Get world dimension and size
        world_dimension = self.world_dim_group.checkedId()
        world_size = self.world_size_spin.value()
        player_type = PlayerType(self.player_type_group.checkedId())
        
        # Clear the world grid and reset visualization
        self.reset_all_buttons_to_base_style()
        
        # Clear probability visualization
        for i in reversed(range(self.probability_grid.count())):
            item = self.probability_grid.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
        
        # Reset stats display
        self.human_score_label.setText("Score: 0")
        self.human_wins_label.setText("Wins: 0")
        self.computer_score_label.setText("Score: 0")
        self.computer_wins_label.setText("Wins: 0")
        self.round_label.setText("Round: 0")
        self.result_label.setText("Result: -")
        
        # # Create appropriate world
        # if world_dimension == 1:
        #     world = World1D(world_size, human_choice=player_type, use_proximity=True)
        # else:  # 2D world
        #     world = World2D(world_size, world_size, human_choice=player_type, use_proximity=True)
            
        # Create the simulation
        self.simulation = Simulation(self.world)
        self.simulation_active = True
        
        # Reset game_logic to ensure no positions are displayed
        if hasattr(self, 'game_logic'):
            self.game_logic = None
            
        # Reset selected position
        if hasattr(self, 'selected_position'):
            self.selected_position = None
            
        # Update UI - we'll use the existing game world to visualize

        self.prepare_simulation_ui()
        
        # Make sure the payoff matrix is displayed
        self.update_payoff_matrix()
        
        # Switch to each tab once to ensure they're all properly rendered
        for i in range(self.tab_widget.count()):
            self.tab_widget.setCurrentIndex(i)
            # A small delay could be added here if needed
            
        # Switch back to the game board tab
        self.tab_widget.setCurrentIndex(0)
        
        # Show status message
        self.show_status_message("Step-by-step simulation started.\nClick 'Next Round' to proceed with each round.\nCheck the Strategy Visualization tab to see both players' strategies.")
        
        # Update probability visualization after a short delay to ensure UI is cleared
        QTimer.singleShot(100, self.update_simulation_probability_visualization)
    
    def prepare_simulation_ui(self):
        """Prepare the UI for simulation mode."""
        # Update world grid and payoff matrix
        self.update_world_grid()
        self.update_payoff_matrix()
        
        # Store both players for the UI to access
        self.hider_player = self.simulation.hider
        self.seeker_player = self.simulation.seeker
        
        # Set up buttons for the simulation
        self.play_btn.setText("Next Round")
        self.play_btn.setEnabled(True)
        self.play_btn.clicked.disconnect()  # Disconnect existing connections
        self.play_btn.clicked.connect(self.play_simulation_round)
        
        self.reset_btn.setText("Stop Simulation")
        self.reset_btn.setEnabled(True)
        self.reset_btn.clicked.disconnect()  # Disconnect existing connections
        self.reset_btn.clicked.connect(self.stop_simulation)
        
        # Initialize stats display
        self.human_score_label.setText("Hider Score: 0")
        self.human_wins_label.setText("Hider Wins: 0") 
        self.computer_score_label.setText("Seeker Score: 0")
        self.computer_wins_label.setText("Seeker Wins: 0")
        self.round_label.setText("Round: 0")
        self.result_label.setText("Simulation Started")
    
    def play_simulation_round(self):
        """Play one round of the simulation."""
        if not hasattr(self, 'simulation') or not self.simulation_active:
            return
            
        # Play one round
        results = self.simulation.next_round()
        hider_pos, seeker_pos, payoff, found, stats = results
        
        # Update the world to show positions
        self.game_logic = self.simulation.game_logic
        
        # Update stats display
        self.human_score_label.setText(f"Hider Score: {self.simulation.hider.score}")
        self.human_wins_label.setText(f"Hider Wins: {stats['hider_wins']}")
        self.computer_score_label.setText(f"Seeker Score: {self.simulation.seeker.score}")
        self.computer_wins_label.setText(f"Seeker Wins: {stats['seeker_wins']}")
        self.round_label.setText(f"Round: {stats['rounds_played']}")
        
        # Update result
        result_text = "Seeker found Hider!" if found else "Hider escaped!"
        self.result_label.setText(f"Result: {result_text}")
        
        # Show positions on grid
        self.highlight_positions()
        
        # Update strategy visualization
        self.update_simulation_probability_visualization()
        
        # Show status message with details
        if isinstance(self.world, World1D):
            msg = f"Round {stats['rounds_played']} results:\n"
            msg += f"Hider played position {hider_pos}\n"
            msg += f"Seeker played position {seeker_pos}\n"
            msg += f"Outcome: {result_text}\n"
            msg += f"Payoff: {payoff}\n\n"
            msg += f"Hider win rate: {stats['hider_win_rate']:.2f}%\n"
            msg += f"Seeker win rate: {stats['seeker_win_rate']:.2f}%\n\n"
            msg += "Check the Strategy Visualization tab to see both players' strategies."
        else:  # 2D world
            h_row, h_col = hider_pos
            s_row, s_col = seeker_pos
            msg = f"Round {stats['rounds_played']} results:\n"
            msg += f"Hider played position ({h_row}, {h_col})\n"
            msg += f"Seeker played position ({s_row}, {s_col})\n"
            msg += f"Outcome: {result_text}\n"
            msg += f"Payoff: {payoff}\n\n"
            msg += f"Hider win rate: {stats['hider_win_rate']:.2f}%\n"
            msg += f"Seeker win rate: {stats['seeker_win_rate']:.2f}%\n\n"
            msg += "Check the Strategy Visualization tab to see both players' strategies."
        
        self.show_status_message(msg)
        
    def stop_simulation(self):
        """Stop the step-by-step simulation and show results."""
        if not hasattr(self, 'simulation'):
            return
            
        self.simulation_active = False
        
        # Get final results
        results = self.simulation.get_results()
        
        # Restore buttons
        self.play_btn.setText("Play Round")
        self.play_btn.clicked.disconnect()
        self.play_btn.clicked.connect(self.play_round)
        self.play_btn.setEnabled(False)
        
        self.reset_btn.setText("Reset Game")
        self.reset_btn.clicked.disconnect()
        self.reset_btn.clicked.connect(self.reset_game)
        
        # Clear the world grid and reset visualization
        self.reset_all_buttons_to_base_style()
        
        # Clear probability visualization
        for i in reversed(range(self.probability_grid.count())):
            item = self.probability_grid.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
        
        # Reset stats display
        self.human_score_label.setText("Score: 0")
        self.human_wins_label.setText("Wins: 0")
        self.computer_score_label.setText("Score: 0")
        self.computer_wins_label.setText("Wins: 0")
        self.round_label.setText("Round: 0")
        self.result_label.setText("Result: -")
        
        # Show final results
        msg = "Simulation Results:\n\n"
        msg += f"Rounds played: {results['rounds_played']}\n\n"
        msg += f"Hider Win Rate: {results['hider_win_rate']:.2f}%\n"
        msg += f"Seeker Win Rate: {results['seeker_win_rate']:.2f}%\n\n"
        msg += f"Average Payoff: {results['avg_payoff']:.2f}"
        
        self.show_styled_message_box("Simulation Results", msg)
    
    def update_stats(self):
        """Update the game statistics display."""
        if not self.game_logic:
            return
            
        # Update score labels
        human_score = self.human_player.score
        computer_score = self.computer_player.score
        
        self.human_score_label.setText(f"Score: {human_score}")
        self.computer_score_label.setText(f"Score: {computer_score}")
        
        # Update win counts
        human_wins = self.human_player.wins
        computer_wins = self.computer_player.wins
        
        self.human_wins_label.setText(f"Wins: {human_wins}")
        self.computer_wins_label.setText(f"Wins: {computer_wins}")
    
    def show_styled_message_box(self, title, message):
        """Show a styled message box with the game's color scheme."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Information)
        
        # Style the message box
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #121212;
                color: #e0e0e0;
            }
            QPushButton {
                background-color: #1e88e5;
                color: white;
                min-width: 80px;
                border-radius: 4px;
                padding: 5px;
                font-weight: bold;
            }
            QLabel {
                color: #e0e0e0;
            }
        """)
        
        msg_box.exec_()

    def show_status_message(self, message):
        """Display a status message in the UI.
        
        Args:
            message (str): Message to display
        """
        self.status_label.setText(message) 