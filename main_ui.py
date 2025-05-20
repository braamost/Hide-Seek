"""
main_ui.py - Main UI for Hide & Seek game

This module implements the main user interface for the Hide & Seek game
using PyQt5.
"""

import sys
import numpy as np
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLabel, QComboBox, QSpinBox,
                            QGridLayout, QGroupBox, QRadioButton, QButtonGroup, 
                            QTabWidget, QScrollArea)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor

from player import PlayerType
from world import World1D, World2D, PlaceType, BaseWorld
from game_logic import GameLogic
from lp_solver import LPSolver
from simulation import Simulation

from visualization import GameVisualization
from gameplay import GamePlay

class GameUI(QMainWindow, GameVisualization, GamePlay):
    """Main window for the Hide & Seek game."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        self.world = None
        self.game_logic = None
        self.human_player = None
        self.computer_player = None
        self.lp_solver = LPSolver()
        self.simulation = None
        
        # Set color scheme
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #121212;
                color: #e0e0e0;
            }
            QGroupBox {
                border: 1px solid #1e88e5;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #1e88e5;
            }
            QPushButton {
                background-color: #1e88e5;
                color: white;
                border-radius: 4px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2196f3;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
            QPushButton:disabled {
                background-color: #757575;
                color: #bdbdbd;
            }
            QComboBox, QSpinBox {
                background-color: #263238;
                color: white;
                border: 1px solid #1e88e5;
                padding: 2px;
                border-radius: 3px;
            }
            QLabel {
                color: #e0e0e0;
            }
            QRadioButton {
                color: #e0e0e0;
            }
            QRadioButton::indicator {
                border: 1px solid #1e88e5;
            }
            QRadioButton::indicator:checked {
                background-color: #1e88e5;
            }
            QTableWidget {
                background-color: #263238;
                color: white;
                gridline-color: #1e88e5;
                border: 1px solid #1e88e5;
            }
            QHeaderView::section {
                background-color: #0d47a1;
                color: white;
                padding: 4px;
                border: 1px solid #1e88e5;
            }
            QTableCornerButton::section {
                background-color: #0d47a1;
                border: 1px solid #1e88e5;
            }
            QTabWidget::pane {
                border: 1px solid #1e88e5;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #263238;
                color: white;
                border: 1px solid #1e88e5;
                border-bottom-color: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #1e88e5;
                color: white;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
        """)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('Hide & Seek Game - Dark Blue Theme')
        self.setGeometry(100, 100, 1000, 800)
        self.setMinimumSize(800, 600)
        self.setMaximumHeight(900)  # Set maximum height to prevent window from being too tall
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Game setup section
        self.create_setup_section(main_layout)
        
        # Create tab widget for game views
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create game visualization tab
        self.game_tab = QWidget()
        game_layout = QVBoxLayout(self.game_tab)
        
        # Create a scroll area for the game board
        game_scroll = QScrollArea()
        game_scroll.setWidgetResizable(True)
        game_scroll.setFrameShape(QScrollArea.NoFrame)
        
        # Create container widget for the game content
        game_content = QWidget()
        game_content_layout = QVBoxLayout(game_content)
        game_scroll.setWidget(game_content)
        
        # Add scroll area to the game tab
        game_layout.addWidget(game_scroll)
        
        self.tab_widget.addTab(self.game_tab, "Game Board")
        
        # Create strategy visualization tab
        self.strategy_tab = QWidget()
        strategy_layout = QVBoxLayout(self.strategy_tab)
        
        # Create a scroll area for the strategy visualization
        strategy_scroll = QScrollArea()
        strategy_scroll.setWidgetResizable(True)
        strategy_scroll.setFrameShape(QScrollArea.NoFrame)
        
        # Create container widget for the strategy content
        strategy_content = QWidget()
        self.strategy_content_layout = QVBoxLayout(strategy_content)
        strategy_scroll.setWidget(strategy_content)
        
        # Add scroll area to the strategy tab
        strategy_layout.addWidget(strategy_scroll)
        
        self.tab_widget.addTab(self.strategy_tab, "Strategy Visualization")
        
        # Create payoff matrix tab
        self.payoff_tab = QWidget()
        payoff_layout = QVBoxLayout(self.payoff_tab)
        
        # Create a scroll area for the payoff matrix
        payoff_scroll = QScrollArea()
        payoff_scroll.setWidgetResizable(True)
        payoff_scroll.setFrameShape(QScrollArea.NoFrame)
        
        # Create container widget for the payoff content
        payoff_content = QWidget()
        self.payoff_content_layout = QVBoxLayout(payoff_content)
        payoff_scroll.setWidget(payoff_content)
        
        # Add scroll area to the payoff tab
        payoff_layout.addWidget(payoff_scroll)
        
        self.tab_widget.addTab(self.payoff_tab, "Payoff Matrix")
        
        # Game visualization section in game tab
        self.create_visualization_section(game_content_layout)
        
        # Strategy visualization in strategy tab
        self.create_strategy_section(self.strategy_content_layout)
        
        # Payoff matrix visualization in payoff tab
        self.create_payoff_section(self.payoff_content_layout)
        
        # Game controls section (below tabs)
        self.create_controls_section(main_layout)
        
        # Game stats section
        self.create_stats_section(main_layout)
    
    def create_setup_section(self, parent_layout):
        """
        Create the game setup section.
        
        Args:
            parent_layout (QLayout): Parent layout
        """
        setup_group = QGroupBox("Game Setup")
        setup_layout = QHBoxLayout()
        
        # World dimension selection
        world_dim_layout = QVBoxLayout()
        world_dim_layout.addWidget(QLabel("World Dimension:"))
        self.world_dim_group = QButtonGroup()
        
        dim_1d_radio = QRadioButton("1D")
        dim_1d_radio.setChecked(True)
        self.world_dim_group.addButton(dim_1d_radio, 1)
        world_dim_layout.addWidget(dim_1d_radio)
        
        dim_2d_radio = QRadioButton("2D")
        self.world_dim_group.addButton(dim_2d_radio, 2)
        world_dim_layout.addWidget(dim_2d_radio)
        
        setup_layout.addLayout(world_dim_layout)
        
        # World size input
        world_size_layout = QVBoxLayout()
        world_size_layout.addWidget(QLabel("World Size:"))
        self.world_size_spin = QSpinBox()
        self.world_size_spin.setRange(2, 20)
        self.world_size_spin.setValue(4)
        world_size_layout.addWidget(self.world_size_spin)
        setup_layout.addLayout(world_size_layout)
        
        # Player type selection
        player_type_layout = QVBoxLayout()
        player_type_layout.addWidget(QLabel("Play as:"))
        self.player_type_group = QButtonGroup()
        
        hider_radio = QRadioButton("Hider")
        hider_radio.setChecked(True)
        self.player_type_group.addButton(hider_radio, PlayerType.HIDER.value)
        player_type_layout.addWidget(hider_radio)
        
        seeker_radio = QRadioButton("Seeker")
        self.player_type_group.addButton(seeker_radio, PlayerType.SEEKER.value)
        player_type_layout.addWidget(seeker_radio)
        
        setup_layout.addLayout(player_type_layout)
        
        # Initialize game button
        self.init_game_btn = QPushButton("Initialize Game")
        self.init_game_btn.clicked.connect(self.initialize_game)
        setup_layout.addWidget(self.init_game_btn)
        
        # Simulation button
        self.sim_game_btn = QPushButton("Run Simulation")
        self.sim_game_btn.clicked.connect(self.run_simulation)
        setup_layout.addWidget(self.sim_game_btn)
        
        setup_group.setLayout(setup_layout)
        parent_layout.addWidget(setup_group)
    
    def create_controls_section(self, parent_layout):
        """
        Create the game controls section.
        
        Args:
            parent_layout (QLayout): Parent layout
        """
        controls_group = QGroupBox("Game Controls")
        controls_layout = QHBoxLayout()
        
        # Instructions label
        instruction_label = QLabel("Click on a position in the grid above to make your move")
        controls_layout.addWidget(instruction_label)
        
        # Play button
        self.play_btn = QPushButton("Play Round")
        self.play_btn.clicked.connect(self.play_round)
        self.play_btn.setEnabled(False)
        controls_layout.addWidget(self.play_btn)
        
        # Reset button
        self.reset_btn = QPushButton("Reset Game")
        self.reset_btn.clicked.connect(self.reset_game)
        self.reset_btn.setEnabled(False)
        controls_layout.addWidget(self.reset_btn)
        
        controls_group.setLayout(controls_layout)
        parent_layout.addWidget(controls_group)
    
    def create_stats_section(self, parent_layout):
        """
        Create the game statistics section.
        
        Args:
            parent_layout (QLayout): Parent layout
        """
        stats_group = QGroupBox("Game Statistics")
        stats_layout = QHBoxLayout()
        
        # Human player stats
        human_stats_layout = QVBoxLayout()
        human_stats_layout.addWidget(QLabel("Human Player:"))
        self.human_score_label = QLabel("Score: 0")
        self.human_wins_label = QLabel("Wins: 0")
        human_stats_layout.addWidget(self.human_score_label)
        human_stats_layout.addWidget(self.human_wins_label)
        stats_layout.addLayout(human_stats_layout)
        
        # Computer player stats
        computer_stats_layout = QVBoxLayout()
        computer_stats_layout.addWidget(QLabel("Computer Player:"))
        self.computer_score_label = QLabel("Score: 0")
        self.computer_wins_label = QLabel("Wins: 0")
        computer_stats_layout.addWidget(self.computer_score_label)
        computer_stats_layout.addWidget(self.computer_wins_label)
        stats_layout.addLayout(computer_stats_layout)
        
        # Round info
        round_layout = QVBoxLayout()
        round_layout.addWidget(QLabel("Game Info:"))
        self.round_label = QLabel("Round: 0")
        self.result_label = QLabel("Result: -")
        round_layout.addWidget(self.round_label)
        round_layout.addWidget(self.result_label)
        stats_layout.addLayout(round_layout)
        
        # Status message
        status_layout = QVBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        self.status_label = QLabel("Ready to play")
        self.status_label.setWordWrap(True)
        self.status_label.setMinimumHeight(80)
        self.status_label.setStyleSheet("background-color: #1e2430; padding: 8px; border-radius: 4px;")
        status_layout.addWidget(self.status_label)
        stats_layout.addLayout(status_layout)
        
        stats_group.setLayout(stats_layout)
        parent_layout.addWidget(stats_group)
    
    def update_probability_visualization(self):
        """Update the visualization of computer strategy probabilities."""
        if not hasattr(self, 'computer_player') or not hasattr(self.computer_player, 'strategy_probabilities'):
            return
            
        # Clear existing visualization
        for i in reversed(range(self.probability_grid.count())):
            item = self.probability_grid.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
        
        # Get strategy probabilities
        probabilities = self.computer_player.strategy_probabilities
        
        # Find max probability for scaling
        max_prob = max(probabilities) if len(probabilities) > 0 else 1.0
        min_prob = min(probabilities) if len(probabilities) > 0 else 0.0
        
        # Title and player role
        title_label = QLabel("COMPUTER STRATEGY ANALYSIS")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; background-color: #0d47a1; padding: 8px; border-radius: 4px;")
        title_label.setAlignment(Qt.AlignCenter)
        self.probability_grid.addWidget(title_label, 0, 0, 1, 5)
        
        role_label = QLabel(f"Computer Player Role: {self.computer_player.type.name}")
        role_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #1e88e5; margin-top: 10px;")
        self.probability_grid.addWidget(role_label, 1, 0, 1, 5)
        
        # Add explanation of what the probabilities mean
        if self.computer_player.type == PlayerType.HIDER:
            explanation = QLabel(
                "The computer is playing as the HIDER. The probabilities below show how likely the computer is to hide in each position. "
                "Positions with higher probabilities (darker blue) are strategic hiding spots that maximize the computer's expected payoff.")
        else:
            explanation = QLabel(
                "The computer is playing as the SEEKER. The probabilities below show how likely the computer is to search in each position. "
                "Positions with higher probabilities (darker blue) are strategic seeking spots that maximize the computer's expected payoff.")
            
        explanation.setWordWrap(True)
        explanation.setStyleSheet("margin-top: 5px; margin-bottom: 15px;")
        self.probability_grid.addWidget(explanation, 2, 0, 1, 5)
        
        # Legend for probability colors
        legend_layout = QHBoxLayout()
        legend_layout.addWidget(QLabel("Low"))
        
        # Create color gradient for legend
        for i in range(10):
            intensity = i / 9.0  # 0.0 to 1.0
            color_box = QLabel()
            color_box.setFixedSize(15, 15)
            color_box.setStyleSheet(f"background-color: rgba(33, 150, 243, {intensity}); border: 1px solid #1e88e5;")
            legend_layout.addWidget(color_box)
        
        legend_layout.addWidget(QLabel("High"))
        
        # Add legend to grid
        legend_widget = QWidget()
        legend_widget.setLayout(legend_layout)
        self.probability_grid.addWidget(legend_widget, 3, 0, 1, 5)
        
        # Create a grid of colored squares representing probabilities
        if isinstance(self.world, World1D):
            # Create 1D grid of probabilities
            grid_row = 4  # Start after the legend
            
            # Add header row
            for i in range(self.world.size):
                pos_header = QLabel(f"Position {i}")
                pos_header.setAlignment(Qt.AlignCenter)
                pos_header.setStyleSheet("color: #1e88e5; font-weight: bold;")
                self.probability_grid.addWidget(pos_header, grid_row, i)
            
            # Add probability boxes
            for i in range(self.world.size):
                # Create colored box
                color_box = QLabel()
                color_box.setFixedSize(60, 60)
                
                # Calculate color intensity based on probability
                prob = probabilities[i]
                intensity = prob / max_prob if max_prob > 0 else 0
                
                # Set background color with intensity
                color_box.setStyleSheet(f"background-color: rgba(33, 150, 243, {intensity}); border: 1px solid #1e88e5; border-radius: 4px;")
                self.probability_grid.addWidget(color_box, grid_row + 1, i)
                
                # Create probability label
                prob_label = QLabel(f"{prob:.4f}")
                prob_label.setAlignment(Qt.AlignCenter)
                self.probability_grid.addWidget(prob_label, grid_row + 2, i)
                
                # Create place type indicator
                place_type = self.world.get_place_type(i)
                type_label = QLabel()
                if place_type == PlaceType.EASY:
                    type_str = "Easy"
                    type_label.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 2px; padding: 2px;")
                elif place_type == PlaceType.NEUTRAL:
                    type_str = "Neutral"
                    type_label.setStyleSheet("background-color: #FFC107; color: black; border-radius: 2px; padding: 2px;")
                else:  # HARD
                    type_str = "Hard"
                    type_label.setStyleSheet("background-color: #F44336; color: white; border-radius: 2px; padding: 2px;")
                type_label.setText(type_str)
                type_label.setAlignment(Qt.AlignCenter)
                self.probability_grid.addWidget(type_label, grid_row + 3, i)
            
        elif isinstance(self.world, World2D):
            # 2D world - display as a grid
            grid_row = 4  # Start after the legend
            
            # Create better legends similar to simulation mode
            place_legend_widget = QWidget()
            place_legend_layout = QHBoxLayout(place_legend_widget)
            place_legend_layout.setContentsMargins(0, 5, 0, 10)
            
            place_legend_label = QLabel("Place Types:")
            place_legend_label.setStyleSheet("font-weight: bold;")
            place_legend_layout.addWidget(place_legend_label)
            
            easy_legend = QLabel("■ Easy (best for hider)")
            easy_legend.setStyleSheet("color: #4CAF50; font-weight: bold;")
            neutral_legend = QLabel("■ Neutral")
            neutral_legend.setStyleSheet("color: #FFC107; font-weight: bold;")
            hard_legend = QLabel("■ Hard (best for seeker)")
            hard_legend.setStyleSheet("color: #F44336; font-weight: bold;")
            
            place_legend_layout.addWidget(easy_legend)
            place_legend_layout.addWidget(neutral_legend)
            place_legend_layout.addWidget(hard_legend)
            place_legend_layout.addStretch(1)
            
            self.probability_grid.addWidget(place_legend_widget, 3, 0, 1, self.world.cols + 2)
            
            # Add column headers
            for c in range(self.world.cols):
                col_label = QLabel(f"Col {c}")
                col_label.setAlignment(Qt.AlignCenter)
                col_label.setStyleSheet("color: #1e88e5; font-weight: bold;")
                self.probability_grid.addWidget(col_label, grid_row, c + 1)
            
            # Add row headers and probability cells
            index = 0
            for r in range(self.world.rows):
                # Row header
                row_label = QLabel(f"Row {r}")
                row_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                row_label.setStyleSheet("color: #1e88e5; font-weight: bold;")
                self.probability_grid.addWidget(row_label, grid_row + r + 1, 0)
                
                for c in range(self.world.cols):
                    # Create better container for probability info
                    cell_container = QLabel()
                    cell_container.setFixedSize(80, 80)
                    
                    # Calculate color intensity
                    prob = probabilities[index]
                    intensity = prob / max_prob if max_prob > 0 else 0
                    
                    # Set place type indicator as border color
                    place_type = self.world.get_place_type((r, c))
                    if place_type == PlaceType.EASY:
                        border_color = "#4CAF50"  # Green
                        place_icon = "E"  # Easy
                    elif place_type == PlaceType.NEUTRAL:
                        border_color = "#FFC107"  # Yellow
                        place_icon = "N"  # Neutral
                    else:  # HARD
                        border_color = "#F44336"  # Red
                        place_icon = "H"  # Hard
                    
                    # Use darker text for light backgrounds and light text for dark backgrounds
                    text_color = "white" if intensity > 0.3 else "#121212"
                    
                    # Set background color with intensity and border indicating place type
                    cell_container.setText(f"<div align='center'><b>{prob:.4f}</b><br>{place_icon}</div>")
                    cell_container.setAlignment(Qt.AlignCenter)
                    cell_container.setStyleSheet(f"""
                        background-color: rgba(33, 150, 243, {intensity});
                        border: 3px solid {border_color};
                        border-radius: 8px;
                        color: {text_color};
                        font-weight: bold;
                        font-size: 16px;
                        padding: 4px;
                    """)
                    
                    # Add to grid
                    self.probability_grid.addWidget(cell_container, grid_row + r + 1, c + 1)
                    
                    index += 1
        
        # Make the tab visible to ensure rendering
        self.tab_widget.setCurrentIndex(1)  # Switch to the strategy visualization tab
        # Switch back to the game board tab
        self.tab_widget.setCurrentIndex(0)

    def update_simulation_probability_visualization(self):
        """Display both hider and seeker strategies in simulation mode"""
        if not hasattr(self, 'simulation') or not hasattr(self, 'hider_player') or not hasattr(self, 'seeker_player'):
            return
            
        # Clear existing visualization
        for i in reversed(range(self.probability_grid.count())):
            item = self.probability_grid.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
        
        # Show title
        title_label = QLabel("SIMULATION STRATEGY ANALYSIS")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; background-color: #0d47a1; padding: 8px; border-radius: 4px;")
        title_label.setAlignment(Qt.AlignCenter)
        self.probability_grid.addWidget(title_label, 0, 0, 1, 6)
        
        # Add explanation
        explanation = QLabel(
            "This simulation shows both players using optimal mixed strategies. "
            "The colors below show the probability distribution for each player's strategy. "
            "Blue for Hider (darker = higher probability), Red for Seeker (darker = higher probability).")
        explanation.setWordWrap(True)
        explanation.setStyleSheet("margin-top: 5px; margin-bottom: 15px;")
        self.probability_grid.addWidget(explanation, 1, 0, 1, 6)
        
        # Get strategies
        hider_probs = self.hider_player.strategy_probabilities
        seeker_probs = self.seeker_player.strategy_probabilities
        
        # Find max values for scaling
        hider_max = max(hider_probs) if len(hider_probs) > 0 else 1.0
        seeker_max = max(seeker_probs) if len(seeker_probs) > 0 else 1.0
        
        # Create headers for both players
        hider_header = QLabel("HIDER STRATEGY")
        hider_header.setStyleSheet("font-size: 14px; font-weight: bold; color: #2196F3;")
        hider_header.setAlignment(Qt.AlignCenter)
        self.probability_grid.addWidget(hider_header, 2, 0, 1, 3)
        
        seeker_header = QLabel("SEEKER STRATEGY")
        seeker_header.setStyleSheet("font-size: 14px; font-weight: bold; color: #F44336;")
        seeker_header.setAlignment(Qt.AlignCenter)
        self.probability_grid.addWidget(seeker_header, 2, 3, 1, 3)
        
        if isinstance(self.world, World1D):
            # 1D world - show as two side-by-side grids
            grid_row = 3
            
            # Position labels column
            for i in range(self.world.size):
                # Position label
                pos_label = QLabel(f"Position {i}")
                pos_label.setAlignment(Qt.AlignCenter)
                self.probability_grid.addWidget(pos_label, grid_row + i, 0)
                
                # Hider probability box
                h_box = QLabel()
                h_box.setFixedSize(60, 40)
                h_prob = hider_probs[i]
                h_intensity = h_prob / hider_max if hider_max > 0 else 0
                
                # Place type indicator as border
                place_type = self.world.get_place_type(i)
                if place_type == PlaceType.EASY:
                    border_color = "#4CAF50"  # Green
                elif place_type == PlaceType.NEUTRAL:
                    border_color = "#FFC107"  # Yellow
                else:  # HARD
                    border_color = "#F44336"  # Red
                    
                h_box.setStyleSheet(f"background-color: rgba(33, 150, 243, {h_intensity}); border: 2px solid {border_color}; border-radius: 4px;")
                self.probability_grid.addWidget(h_box, grid_row + i, 1)
                
                # Hider probability value
                h_label = QLabel(f"{h_prob:.4f}")
                h_label.setAlignment(Qt.AlignCenter)
                self.probability_grid.addWidget(h_label, grid_row + i, 2)
                
                # Seeker probability box
                s_box = QLabel()
                s_box.setFixedSize(60, 40)
                s_prob = seeker_probs[i]
                s_intensity = s_prob / seeker_max if seeker_max > 0 else 0
                s_box.setStyleSheet(f"background-color: rgba(244, 67, 54, {s_intensity}); border: 2px solid {border_color}; border-radius: 4px;")
                self.probability_grid.addWidget(s_box, grid_row + i, 4)
                
                # Seeker probability value
                s_label = QLabel(f"{s_prob:.4f}")
                s_label.setAlignment(Qt.AlignCenter)
                self.probability_grid.addWidget(s_label, grid_row + i, 5)
            
        elif isinstance(self.world, World2D):
            # For 2D world, use tabs to switch between hider and seeker visualizations
            # Create a tab widget
            strat_tabs = QTabWidget()
            strat_tabs.setStyleSheet("""
                QTabWidget::pane {
                    border: 1px solid #1e88e5;
                    border-radius: 5px;
                    padding: 10px;
                }
                QTabBar::tab {
                    background-color: #263238;
                    color: white;
                    border: 1px solid #1e88e5;
                    border-bottom-color: none;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    padding: 8px 16px;
                    margin-right: 2px;
                    font-weight: bold;
                }
                QTabBar::tab:selected {
                    background-color: #1e88e5;
                    color: white;
                }
            """)
            
            hider_tab = QWidget()
            seeker_tab = QWidget()
            
            hider_layout = QGridLayout(hider_tab)
            hider_layout.setSpacing(8)
            seeker_layout = QGridLayout(seeker_tab)
            seeker_layout.setSpacing(8)
            
            # Create legend for place types and probability
            legend_widget = QWidget()
            legend_layout = QVBoxLayout(legend_widget)
            legend_layout.setContentsMargins(0, 5, 0, 10)
            
            # Place type legend
            place_type_widget = QWidget()
            place_type_layout = QHBoxLayout(place_type_widget)
            place_type_layout.setContentsMargins(0, 0, 0, 0)
            
            place_legend_label = QLabel("Place Types:")
            place_legend_label.setStyleSheet("font-weight: bold;")
            place_type_layout.addWidget(place_legend_label)
            
            easy_legend = QLabel("■ Easy (best for hider)")
            easy_legend.setStyleSheet("color: #4CAF50; font-weight: bold;")
            neutral_legend = QLabel("■ Neutral")
            neutral_legend.setStyleSheet("color: #FFC107; font-weight: bold;")
            hard_legend = QLabel("■ Hard (best for seeker)")
            hard_legend.setStyleSheet("color: #F44336; font-weight: bold;")
            
            place_type_layout.addWidget(easy_legend)
            place_type_layout.addWidget(neutral_legend)
            place_type_layout.addWidget(hard_legend)
            place_type_layout.addStretch(1)
            
            legend_layout.addWidget(place_type_widget)
            
            # Probability scale legend
            prob_scale_widget = QWidget()
            prob_scale_layout = QHBoxLayout(prob_scale_widget)
            prob_scale_layout.setContentsMargins(0, 0, 0, 0)
            
            prob_legend_label = QLabel("Probability Scale:")
            prob_legend_label.setStyleSheet("font-weight: bold;")
            prob_scale_layout.addWidget(prob_legend_label)
            
            # Create color gradient for legend
            prob_scale_layout.addWidget(QLabel("Low"))
            
            for i in range(5):
                intensity = i / 4.0  # 0.0 to 1.0
                hider_box = QLabel()
                hider_box.setFixedSize(15, 15)
                hider_box.setStyleSheet(f"background-color: rgba(33, 150, 243, {intensity}); border: 1px solid #1e88e5;")
                prob_scale_layout.addWidget(hider_box)
                
                seeker_box = QLabel()
                seeker_box.setFixedSize(15, 15)
                seeker_box.setStyleSheet(f"background-color: rgba(244, 67, 54, {intensity}); border: 1px solid #F44336;")
                prob_scale_layout.addWidget(seeker_box)
            
            prob_scale_layout.addWidget(QLabel("High"))
            prob_scale_layout.addStretch(1)
            
            legend_layout.addWidget(prob_scale_widget)
            
            # Add legend to both tabs
            hider_layout.addWidget(legend_widget, 0, 0, 1, self.world.cols + 2)
            
            # Create a duplicate legend for seeker tab
            seeker_legend_widget = QWidget()
            seeker_legend_layout = QVBoxLayout(seeker_legend_widget)
            seeker_legend_layout.setContentsMargins(0, 5, 0, 10)
            
            # Place type legend for seeker tab
            seeker_place_widget = QWidget()
            seeker_place_layout = QHBoxLayout(seeker_place_widget)
            seeker_place_layout.setContentsMargins(0, 0, 0, 0)
            
            seeker_place_label = QLabel("Place Types:")
            seeker_place_label.setStyleSheet("font-weight: bold;")
            seeker_place_layout.addWidget(seeker_place_label)
            
            seeker_easy_legend = QLabel("■ Easy (best for hider)")
            seeker_easy_legend.setStyleSheet("color: #4CAF50; font-weight: bold;")
            seeker_neutral_legend = QLabel("■ Neutral")
            seeker_neutral_legend.setStyleSheet("color: #FFC107; font-weight: bold;")
            seeker_hard_legend = QLabel("■ Hard (best for seeker)")
            seeker_hard_legend.setStyleSheet("color: #F44336; font-weight: bold;")
            
            seeker_place_layout.addWidget(seeker_easy_legend)
            seeker_place_layout.addWidget(seeker_neutral_legend)
            seeker_place_layout.addWidget(seeker_hard_legend)
            seeker_place_layout.addStretch(1)
            
            seeker_legend_layout.addWidget(seeker_place_widget)
            
            # Probability scale for seeker tab
            seeker_prob_widget = QWidget()
            seeker_prob_layout = QHBoxLayout(seeker_prob_widget)
            seeker_prob_layout.setContentsMargins(0, 0, 0, 0)
            
            seeker_prob_label = QLabel("Probability Scale:")
            seeker_prob_label.setStyleSheet("font-weight: bold;")
            seeker_prob_layout.addWidget(seeker_prob_label)
            
            # Create color gradient for legend on seeker tab
            seeker_prob_layout.addWidget(QLabel("Low"))
            
            for i in range(5):
                intensity = i / 4.0  # 0.0 to 1.0
                hider_box = QLabel()
                hider_box.setFixedSize(15, 15)
                hider_box.setStyleSheet(f"background-color: rgba(33, 150, 243, {intensity}); border: 1px solid #1e88e5;")
                seeker_prob_layout.addWidget(hider_box)
                
                seeker_box = QLabel()
                seeker_box.setFixedSize(15, 15)
                seeker_box.setStyleSheet(f"background-color: rgba(244, 67, 54, {intensity}); border: 1px solid #F44336;")
                seeker_prob_layout.addWidget(seeker_box)
            
            seeker_prob_layout.addWidget(QLabel("High"))
            seeker_prob_layout.addStretch(1)
            
            seeker_legend_layout.addWidget(seeker_prob_widget)
            
            seeker_layout.addWidget(seeker_legend_widget, 0, 0, 1, self.world.cols + 2)
            
            # Populate hider tab
            index = 0
            for r in range(self.world.rows):
                # Row label
                row_label = QLabel(f"Row {r}")
                row_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                row_label.setStyleSheet("color: #1e88e5; font-weight: bold;")
                hider_layout.addWidget(row_label, r + 2, 0)
                
                for c in range(self.world.cols):
                    # Column headers (only once)
                    if r == 0:
                        col_label = QLabel(f"Col {c}")
                        col_label.setAlignment(Qt.AlignCenter)
                        col_label.setStyleSheet("color: #1e88e5; font-weight: bold;")
                        hider_layout.addWidget(col_label, 1, c + 1)
                    
                    # Place type indicator
                    place_type = self.world.get_place_type((r, c))
                    if place_type == PlaceType.EASY:
                        border_color = "#4CAF50"  # Green
                        place_icon = "E"  # Easy
                    elif place_type == PlaceType.NEUTRAL:
                        border_color = "#FFC107"  # Yellow
                        place_icon = "N"  # Neutral
                    else:  # HARD
                        border_color = "#F44336"  # Red
                        place_icon = "H"  # Hard
                    
                    # Create a better container for the probability info
                    h_container = QLabel()
                    h_container.setFixedSize(80, 80)
                    h_prob = hider_probs[index]
                    h_intensity = h_prob / hider_max if hider_max > 0 else 0
                    
                    # Use darker text for light backgrounds and light text for dark backgrounds
                    text_color = "white" if h_intensity > 0.3 else "#121212"
                    
                    # Display probability more clearly
                    h_container.setText(f"<div align='center'><b>{h_prob:.4f}</b><br>{place_icon}</div>")
                    h_container.setAlignment(Qt.AlignCenter)
                    h_container.setStyleSheet(f"""
                        background-color: rgba(33, 150, 243, {h_intensity});
                        border: 3px solid {border_color};
                        border-radius: 8px;
                        color: {text_color};
                        font-weight: bold;
                        font-size: 16px;
                        padding: 4px;
                    """)
                    hider_layout.addWidget(h_container, r + 2, c + 1)
                    
                    index += 1
            
            # Populate seeker tab
            index = 0
            for r in range(self.world.rows):
                # Row label
                row_label = QLabel(f"Row {r}")
                row_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                row_label.setStyleSheet("color: #1e88e5; font-weight: bold;")
                seeker_layout.addWidget(row_label, r + 2, 0)
                
                for c in range(self.world.cols):
                    # Column headers (only once)
                    if r == 0:
                        col_label = QLabel(f"Col {c}")
                        col_label.setAlignment(Qt.AlignCenter)
                        col_label.setStyleSheet("color: #1e88e5; font-weight: bold;")
                        seeker_layout.addWidget(col_label, 1, c + 1)
                    
                    # Place type indicator
                    place_type = self.world.get_place_type((r, c))
                    if place_type == PlaceType.EASY:
                        border_color = "#4CAF50"  # Green
                        place_icon = "E"  # Easy
                    elif place_type == PlaceType.NEUTRAL:
                        border_color = "#FFC107"  # Yellow
                        place_icon = "N"  # Neutral
                    else:  # HARD
                        border_color = "#F44336"  # Red
                        place_icon = "H"  # Hard
                    
                    # Create a better container for the probability info
                    s_container = QLabel()
                    s_container.setFixedSize(80, 80)
                    s_prob = seeker_probs[index]
                    s_intensity = s_prob / seeker_max if seeker_max > 0 else 0
                    
                    # Use darker text for light backgrounds and light text for dark backgrounds
                    text_color = "white" if s_intensity > 0.3 else "#121212"
                    
                    # Display probability more clearly
                    s_container.setText(f"<div align='center'><b>{s_prob:.4f}</b><br>{place_icon}</div>")
                    s_container.setAlignment(Qt.AlignCenter)
                    s_container.setStyleSheet(f"""
                        background-color: rgba(244, 67, 54, {s_intensity});
                        border: 3px solid {border_color};
                        border-radius: 8px;
                        color: {text_color};
                        font-weight: bold;
                        font-size: 16px;
                        padding: 4px;
                    """)
                    seeker_layout.addWidget(s_container, r + 2, c + 1)
                    
                    index += 1
            
            # Add tabs to tab widget
            strat_tabs.addTab(hider_tab, "Hider Strategy")
            strat_tabs.addTab(seeker_tab, "Seeker Strategy")
            
            # Add tab widget to grid
            self.probability_grid.addWidget(strat_tabs, 3, 0, 10, 6)
        
        # Make the tab visible to ensure rendering
        self.tab_widget.setCurrentIndex(1)  # Switch to the strategy visualization tab
        # Switch back to the game board tab
        self.tab_widget.setCurrentIndex(0) 