"""
game_ui.py - Qt GUI implementation for Hide & Seek game

This module implements the graphical user interface for the game
using PyQt5.
"""

import sys
import numpy as np
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLabel, QComboBox, QSpinBox,
                            QGridLayout, QGroupBox, QRadioButton, QTableWidget,
                            QTableWidgetItem, QMessageBox, QButtonGroup, QTabWidget, QScrollArea)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor

from player import PlayerType, HumanPlayer, ComputerPlayer
from world import World1D, World2D, PlaceType, BaseWorld
from game_logic import GameLogic
from lp_solver import LPSolver
from simulation import Simulation

class GameUI(QMainWindow):
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
    
    def create_visualization_section(self, parent_layout):
        """
        Create the game visualization section.
        
        Args:
            parent_layout (QLayout): Parent layout
        """
        visual_group = QGroupBox("Game World")
        visual_layout = QVBoxLayout()
        
        # World grid
        self.world_grid = QGridLayout()
        self.world_buttons = []
        
        # Placeholder for the world grid
        placeholder = QLabel("Initialize the game to see the world")
        placeholder.setAlignment(Qt.AlignCenter)
        self.world_grid.addWidget(placeholder, 0, 0)
        
        visual_layout.addLayout(self.world_grid)
        
        visual_group.setLayout(visual_layout)
        
        # Check if parent_layout is a QWidget or QLayout
        if isinstance(parent_layout, QWidget):
            if parent_layout.layout():
                parent_layout.layout().addWidget(visual_group)
            else:
                layout = QVBoxLayout(parent_layout)
                layout.addWidget(visual_group)
        else:
            parent_layout.addWidget(visual_group)
    
    def create_strategy_section(self, parent_layout):
        """
        Create the strategy visualization section.
        
        Args:
            parent_layout (QLayout): Parent layout
        """
        strategy_group = QGroupBox("Computer Strategy Probabilities")
        strategy_layout = QVBoxLayout()
        
        # Strategy explanation
        explanation = QLabel("This tab shows the probability distribution of the computer player's strategy. " + 
                           "The intensity of blue color indicates the probability - darker blue means higher probability.")
        explanation.setWordWrap(True)
        strategy_layout.addWidget(explanation)
        
        # Strategy probabilities visualization
        self.probability_grid = QGridLayout()
        strategy_layout.addLayout(self.probability_grid)
        
        # Color scale legend
        legend_layout = QHBoxLayout()
        legend_layout.addWidget(QLabel("Low"))
        
        # Create color gradient for legend
        for i in range(10):
            intensity = i / 9.0  # 0.0 to 1.0
            color_box = QLabel()
            color_box.setFixedSize(20, 20)
            color_box.setStyleSheet(f"background-color: rgba(33, 150, 243, {intensity});")
            legend_layout.addWidget(color_box)
        
        legend_layout.addWidget(QLabel("High"))
        strategy_layout.addLayout(legend_layout)
        
        strategy_group.setLayout(strategy_layout)
        
        # Check if parent_layout is a QWidget or QLayout
        if isinstance(parent_layout, QWidget):
            if parent_layout.layout():
                parent_layout.layout().addWidget(strategy_group)
            else:
                layout = QVBoxLayout(parent_layout)
                layout.addWidget(strategy_group)
        else:
            parent_layout.addWidget(strategy_group)
    
    def create_payoff_section(self, parent_layout):
        """
        Create the payoff matrix visualization section.
        
        Args:
            parent_layout (QLayout): Parent layout
        """
        # Payoff matrix explanation
        explanation = QLabel("This tab shows the payoff matrix for the game. " + 
                           "Each cell represents the payoff when the hider chooses the row position and " + 
                           "the seeker chooses the column position.")
        explanation.setWordWrap(True)
        
        # Payoff matrix visualization
        self.payoff_table = QTableWidget()
        self.payoff_table.setMinimumHeight(400)  # Increased height
        self.payoff_table.setMinimumWidth(600)   # Set minimum width
        
        # Directly add to parent layout
        if isinstance(parent_layout, QWidget):
            if parent_layout.layout():
                parent_layout.layout().addWidget(explanation)
                parent_layout.layout().addWidget(self.payoff_table)
            else:
                layout = QVBoxLayout(parent_layout)
                layout.addWidget(explanation)
                layout.addWidget(self.payoff_table)
        else:
            parent_layout.addWidget(explanation)
            parent_layout.addWidget(self.payoff_table)
    
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
        
        # Initialize players
        if player_type == PlayerType.HIDER:
            self.human_player = HumanPlayer(PlayerType.HIDER)
            self.computer_player = ComputerPlayer(PlayerType.SEEKER)
            
            # Set computer strategy
            payoff_matrix = self.world.generate_payoff_matrix()
            # Convert to numpy array if it's not already
            payoff_matrix_np = np.array(payoff_matrix)
            strategy = self.lp_solver.solve_game(payoff_matrix_np, PlayerType.SEEKER)
            self.computer_player.set_strategy(strategy)
            
            # Create game logic
            self.game_logic = GameLogic(self.world, self.human_player, self.computer_player)
        else:
            self.human_player = HumanPlayer(PlayerType.SEEKER)
            self.computer_player = ComputerPlayer(PlayerType.HIDER)
            
            # Set computer strategy
            payoff_matrix = self.world.generate_payoff_matrix()
            # Convert to numpy array if it's not already
            payoff_matrix_np = np.array(payoff_matrix)
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
    
    def update_world_grid(self):
        """Update the world grid visualization."""
        # Clear existing grid
        for i in reversed(range(self.world_grid.count())):
            self.world_grid.itemAt(i).widget().deleteLater()
            
        # Create new grid
        self.world_buttons = []
        
        # Base button style
        button_style = """
            QPushButton {
                background-color: #263238;
                color: white;
                border: 1px solid #1e88e5;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                border: 2px solid #2196f3;
            }
        """
        
        if not self.world:
            # Create empty placeholder
            placeholder = QLabel("Create a world first")
            placeholder.setAlignment(Qt.AlignCenter)
            self.world_grid.addWidget(placeholder, 0, 0)
            return
            
        if isinstance(self.world, World1D):
            # Create 1D grid
            for i in range(self.world.size):
                btn = QPushButton()
                btn.setFixedSize(60, 60)  # Increased button size
                btn.setStyleSheet(button_style)
                btn.setText("")  # Ensure empty text initially
                btn.setToolTip(f"Position {i}")
                # Connect button click to make_move
                btn.clicked.connect(lambda checked, i=i: self.handle_button_click(i))
                
                # Connect hover events for proximity visualization
                btn.enterEvent = lambda event, pos=i: self.show_proximity_effect(pos)
                btn.leaveEvent = lambda event: self.hide_proximity_effect()
                
                self.world_grid.addWidget(btn, 0, i)
                self.world_buttons.append(btn)
                
        elif isinstance(self.world, World2D):
            rows = self.world.rows
            cols = self.world.cols
            
            # Create 2D grid
            for r in range(rows):
                row_buttons = []
                for c in range(cols):
                    btn = QPushButton()
                    btn.setFixedSize(60, 60)  # Increased button size
                    btn.setStyleSheet(button_style)
                    btn.setText("")  # Ensure empty text initially
                    btn.setToolTip(f"Position ({r}, {c})")
                    # Connect button click to make_move
                    btn.clicked.connect(lambda checked, r=r, c=c: self.handle_button_click((r, c)))
                    
                    self.world_grid.addWidget(btn, r, c)
                    row_buttons.append(btn)
                self.world_buttons.append(row_buttons)
        
        # Apply place type colors to buttons
        self.apply_place_type_colors()
        # Highlight available positions based on player type
        self.highlight_positions()
    
    def update_payoff_matrix(self):
        """Update the payoff matrix visualization."""
        if not self.world:
            return
        
        # Generate payoff matrix
        payoff_matrix = self.world.generate_payoff_matrix()
        # Convert to numpy array for consistent handling
        payoff_matrix = np.array(payoff_matrix)
        
        # Clear the table
        self.payoff_table.clear()
        
        # Set table dimensions based on the world type
        if isinstance(self.world, World1D):
            size = self.world.size
            self.payoff_table.setRowCount(size)
            self.payoff_table.setColumnCount(size)
            
            # Set headers
            headers = [f"Pos {i}" for i in range(size)]
            self.payoff_table.setHorizontalHeaderLabels(headers)
            self.payoff_table.setVerticalHeaderLabels(headers)
            
            # Fill the table with payoff values
            for h in range(size):
                for s in range(size):
                    payoff = payoff_matrix[h][s]
                    item = QTableWidgetItem(str(payoff))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.payoff_table.setItem(h, s, item)
                    
        elif isinstance(self.world, World2D):
            rows = self.world.rows
            cols = self.world.cols
            
            # In 2D world, the payoff matrix is (rows*cols) x (rows*cols)
            total_positions = rows * cols
            self.payoff_table.setRowCount(total_positions)
            self.payoff_table.setColumnCount(total_positions)
            
            # Set headers
            h_headers = []
            for r in range(rows):
                for c in range(cols):
                    h_headers.append(f"({r},{c})")
            
            self.payoff_table.setHorizontalHeaderLabels(h_headers)
            self.payoff_table.setVerticalHeaderLabels(h_headers)
            
            # Fill the table with payoff values
            for h in range(total_positions):
                for s in range(total_positions):
                    payoff = payoff_matrix[h][s]
                    item = QTableWidgetItem(str(payoff))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.payoff_table.setItem(h, s, item)
        
        # Auto-adjust columns to content
        self.payoff_table.resizeColumnsToContents()
        self.payoff_table.resizeRowsToContents()
        
        # Make sure table is visible
        self.payoff_table.show()
        self.payoff_table.setVisible(True)
        
        # Make sure the parent is also visible
        if hasattr(self, 'payoff_content_layout'):
            parent_widget = self.payoff_content_layout.parentWidget()
            if parent_widget:
                parent_widget.show()
                parent_widget.setVisible(True)
        
        # Switch to the payoff tab to ensure it's rendered
        self.tab_widget.setCurrentIndex(2)  # Index 2 is the payoff tab
        # Switch back to the game board tab
        self.tab_widget.setCurrentIndex(0)
        
        # Update strategy for computer player
        strategy = self.lp_solver.solve_game(payoff_matrix, self.computer_player.type)
        self.computer_player.set_strategy(strategy)
    
    def handle_button_click(self, position):
        """Handle a button click on the grid."""
        if not self.game_logic:
            return
        
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
    
    def show_selection_feedback(self, position):
        """Show visual feedback for the selected position."""
        self.selected_position = position
        
        # Define the selected style - bright yellow border to highlight
        selected_style = """
            QPushButton {
                background-color: #263238;
                color: white;
                border: 3px solid #FFEB3B;
                font-size: 20px;
                font-weight: bold;
            }
        """
        
        # Apply style based on world type
        if isinstance(self.world, World1D):
            # Store current text before changing style
            current_text = self.world_buttons[position].text()
            self.world_buttons[position].setStyleSheet(selected_style)
            # Restore text
            self.world_buttons[position].setText(current_text)
        elif isinstance(self.world, World2D):
            row, col = position
            # Store current text before changing style
            current_text = self.world_buttons[row][col].text() 
            self.world_buttons[row][col].setStyleSheet(selected_style)
            # Restore text
            self.world_buttons[row][col].setText(current_text)
            
        # Show position info
        self.show_position_info(position)
    
    def show_position_info(self, position):
        """Display information about the selected position."""
        # Get place type
        if isinstance(self.world, World1D):
            place_type = self.world.get_place_type(position)
            pos_str = f"Position {position}"
            
            # Get expected payoff for this position
            payoff_text = ""
            if self.human_player.type == PlayerType.HIDER:
                payoffs = [self.world.get_score(position, j) for j in range(self.world.size)]
                avg_payoff = sum(payoffs) / len(payoffs)
                payoff_text = f"Avg Payoff: {avg_payoff:.2f}"
            else:  # SEEKER
                payoffs = [self.world.get_score(i, position) for i in range(self.world.size)]
                avg_payoff = sum(payoffs) / len(payoffs)
                payoff_text = f"Avg Payoff: {avg_payoff:.2f}"
                
        else:  # 2D
            row, col = position
            place_type = self.world.get_place_type(position)
            pos_str = f"Position ({row}, {col})"
            
            # Get expected payoff for this position (2D)
            payoff_text = ""
            if self.human_player.type == PlayerType.HIDER:
                payoffs = []
                for r in range(self.world.rows):
                    for c in range(self.world.cols):
                        seeker_pos = (r, c)
                        payoffs.append(self.world.get_score(position, seeker_pos))
                avg_payoff = sum(payoffs) / len(payoffs)
                payoff_text = f"Avg Payoff: {avg_payoff:.2f}"
            else:  # SEEKER
                payoffs = []
                for r in range(self.world.rows):
                    for c in range(self.world.cols):
                        hider_pos = (r, c)
                        payoffs.append(self.world.get_score(hider_pos, position))
                avg_payoff = sum(payoffs) / len(payoffs)
                payoff_text = f"Avg Payoff: {avg_payoff:.2f}"
            
        # Determine place type description
        if place_type == PlaceType.EASY:
            type_str = "Easy (better for hider)"
        elif place_type == PlaceType.NEUTRAL:
            type_str = "Neutral"
        else:  # HARD
            type_str = "Hard (better for seeker)"
            
        # Create message box with position info
        message = f"Selected: {pos_str}\nType: {type_str}\n{payoff_text}\n\nClick 'Play Round' to continue."
        self.show_status_message(message)
    
    def play_round(self):
        """Play a round of the game."""
        if not self.game_logic:
            return
        
        # Switch to the game board tab if not already there
        if self.tab_widget.currentIndex() != 0:
            self.tab_widget.setCurrentIndex(0)
        
        # Human player's move was already set by button click
        
        # Get computer's move based on strategy
        computer_move = self.computer_player.make_move(self.world)
        
        # Execute round
        result = self.game_logic.play_round()
        
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
            self.world = World1D(self.world.size, human_choice=player_type, use_proximity=False)
        elif isinstance(self.world, World2D):
            self.world = World2D(self.world.rows, self.world.cols, human_choice=player_type, use_proximity=False)
            
        # Reset players
        if player_type == PlayerType.HIDER:
            self.human_player = HumanPlayer(PlayerType.HIDER)
            self.computer_player = ComputerPlayer(PlayerType.SEEKER)
        else:
            self.human_player = HumanPlayer(PlayerType.SEEKER)
            self.computer_player = ComputerPlayer(PlayerType.HIDER)
            
        # Set computer strategy
        payoff_matrix = self.world.generate_payoff_matrix()
        # Convert to numpy array
        payoff_matrix_np = np.array(payoff_matrix)
        strategy = self.lp_solver.solve_game(payoff_matrix_np, self.computer_player.type)
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
        
        # Create appropriate world
        if world_dimension == 1:
            world = World1D(world_size, human_choice=player_type, use_proximity=False)
        else:  # 2D world
            world = World2D(world_size, world_size, human_choice=player_type, use_proximity=False)
            
        # Create the simulation
        self.simulation = Simulation(world)
        self.simulation_active = True
        
        # Update UI - we'll use the existing game world to visualize
        self.world = world
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
        
        # Update probability visualization for both players
        self.update_simulation_probability_visualization()

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

    def highlight_positions(self):
        """Highlight the available positions based on the current game state."""
        if not self.world:
            return
            
        # Reset to base styles first
        self.reset_all_buttons_to_base_style()
        
        # Re-apply selection highlight if there's a selected position
        if hasattr(self, 'selected_position') and self.selected_position is not None and not hasattr(self, 'simulation_active'):
            self.show_selection_feedback(self.selected_position)
            
        # Define highlight styles
        human_style = """
            QPushButton {
                background-color: white;  /* White for human */
                color: black;
                border: 3px solid #E0E0E0;
                font-weight: bold;
                font-size: 20px;  /* Larger text */
            }
        """
        
        computer_style = """
            QPushButton {
                background-color: #2196F3;  /* Blue for computer */
                color: white;
                border: 3px solid #64B5F6;
                font-weight: bold;
                font-size: 20px;  /* Larger text */
            }
        """
        
        overlap_style = """
            QPushButton {
                background-color: #212121;  /* Black for catch */
                color: white;
                border: 3px solid #757575;
                font-weight: bold;
                font-size: 20px;  /* Larger text */
            }
        """
        
        # Get current positions
        if self.game_logic:
            hider_pos = self.game_logic.get_hider_position()
            seeker_pos = self.game_logic.get_seeker_position()
            
            # Determine which positions belong to human and computer players (or hider/seeker in simulation)
            if hasattr(self, 'simulation_active') and self.simulation_active:
                # In simulation mode, highlight hider and seeker positions directly
                positions_overlap = (hider_pos is not None and seeker_pos is not None and hider_pos == seeker_pos)
                
                # Apply styles based on world type
                if isinstance(self.world, World1D):
                    # Check for overlap first
                    if positions_overlap and hider_pos is not None and 0 <= hider_pos < len(self.world_buttons):
                        self.world_buttons[hider_pos].setStyleSheet(overlap_style)
                        self.world_buttons[hider_pos].setText("X")  # X symbol for overlap
                    else:
                        # Apply styles for individual positions
                        if hider_pos is not None and 0 <= hider_pos < len(self.world_buttons):
                            self.world_buttons[hider_pos].setStyleSheet(human_style)
                            self.world_buttons[hider_pos].setText("H")  # H for hider
                            
                        if seeker_pos is not None and 0 <= seeker_pos < len(self.world_buttons):
                            self.world_buttons[seeker_pos].setStyleSheet(computer_style)
                            self.world_buttons[seeker_pos].setText("S")  # S for seeker
                    
                elif isinstance(self.world, World2D):
                    # Check for overlap first
                    if positions_overlap and hider_pos is not None:
                        h_row, h_col = hider_pos
                        if 0 <= h_row < len(self.world_buttons) and 0 <= h_col < len(self.world_buttons[h_row]):
                            self.world_buttons[h_row][h_col].setStyleSheet(overlap_style)
                            self.world_buttons[h_row][h_col].setText("X")  # X symbol for overlap
                    else:
                        # Apply styles for individual positions
                        if hider_pos is not None:
                            h_row, h_col = hider_pos
                            if 0 <= h_row < len(self.world_buttons) and 0 <= h_col < len(self.world_buttons[h_row]):
                                self.world_buttons[h_row][h_col].setStyleSheet(human_style)
                                self.world_buttons[h_row][h_col].setText("H")  # H for hider
                                
                        if seeker_pos is not None:
                            s_row, s_col = seeker_pos
                            if 0 <= s_row < len(self.world_buttons) and 0 <= s_col < len(self.world_buttons[s_row]):
                                self.world_buttons[s_row][s_col].setStyleSheet(computer_style)
                                self.world_buttons[s_row][s_col].setText("S")  # S for seeker
            else:
                # Normal game mode - use human/computer distinction
                human_pos = None
                computer_pos = None
                
                if self.human_player.type == PlayerType.HIDER:
                    human_pos = hider_pos
                    computer_pos = seeker_pos
                else:
                    human_pos = seeker_pos
                    computer_pos = hider_pos
                
                # Check if positions overlap (same position chosen by both players)
                positions_overlap = (hider_pos is not None and seeker_pos is not None and hider_pos == seeker_pos)
                
                # Apply styles based on world type
                if isinstance(self.world, World1D):
                    # Check for overlap first
                    if positions_overlap and 0 <= human_pos < len(self.world_buttons):
                        self.world_buttons[human_pos].setStyleSheet(overlap_style)
                        self.world_buttons[human_pos].setText("X")  # X symbol for overlap
                    else:
                        # Apply styles for individual positions
                        if human_pos is not None and 0 <= human_pos < len(self.world_buttons):
                            self.world_buttons[human_pos].setStyleSheet(human_style)
                            self.world_buttons[human_pos].setText("H")  # H for human
                            
                        if computer_pos is not None and 0 <= computer_pos < len(self.world_buttons):
                            self.world_buttons[computer_pos].setStyleSheet(computer_style)
                            self.world_buttons[computer_pos].setText("C")  # C for computer
                    
                elif isinstance(self.world, World2D):
                    # Check for overlap first
                    if positions_overlap:
                        h_row, h_col = human_pos
                        if 0 <= h_row < len(self.world_buttons) and 0 <= h_col < len(self.world_buttons[h_row]):
                            self.world_buttons[h_row][h_col].setStyleSheet(overlap_style)
                            self.world_buttons[h_row][h_col].setText("X")  # X symbol for overlap
                    else:
                        # Apply styles for individual positions
                        if human_pos is not None:
                            h_row, h_col = human_pos
                            if 0 <= h_row < len(self.world_buttons) and 0 <= h_col < len(self.world_buttons[h_row]):
                                self.world_buttons[h_row][h_col].setStyleSheet(human_style)
                                self.world_buttons[h_row][h_col].setText("H")  # H for human
                                
                        if computer_pos is not None:
                            c_row, c_col = computer_pos
                            if 0 <= c_row < len(self.world_buttons) and 0 <= c_col < len(self.world_buttons[c_row]):
                                self.world_buttons[c_row][c_col].setStyleSheet(computer_style)
                                self.world_buttons[c_row][c_col].setText("C")  # C for computer

    def apply_place_type_colors(self):
        """Apply colors to grid buttons based on place types."""
        if not self.world:
            return
            
        # Define place type styles
        easy_style = """
            QPushButton {
                background-color: #4CAF50;  /* Green for easy */
                color: white;
                border: 1px solid #1e88e5;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #388E3C;
                border: 2px solid #2196f3;
            }
        """
        
        neutral_style = """
            QPushButton {
                background-color: #FFC107;  /* Yellow for neutral */
                color: black;
                border: 1px solid #1e88e5;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FFA000;
                border: 2px solid #2196f3;
            }
        """
        
        hard_style = """
            QPushButton {
                background-color: #F44336;  /* Red for hard */
                color: white;
                border: 1px solid #1e88e5;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D32F2F;
                border: 2px solid #2196f3;
            }
        """
        
        # Store the original styles for each button
        if not hasattr(self, 'button_styles'):
            self.button_styles = {}
        
        # Apply styles based on world type
        if isinstance(self.world, World1D):
            for i in range(self.world.size):
                place_type = self.world.get_place_type(i)
                if place_type == PlaceType.EASY:
                    style = easy_style
                elif place_type == PlaceType.NEUTRAL:
                    style = neutral_style
                else:  # HARD
                    style = hard_style
                    
                self.button_styles[i] = style
                self.world_buttons[i].setStyleSheet(style)
                # Preserve any text on the button
                
        elif isinstance(self.world, World2D):
            for r in range(self.world.rows):
                for c in range(self.world.cols):
                    place_type = self.world.get_place_type((r, c))
                    if place_type == PlaceType.EASY:
                        style = easy_style
                    elif place_type == PlaceType.NEUTRAL:
                        style = neutral_style
                    else:  # HARD
                        style = hard_style
                        
                    self.button_styles[(r, c)] = style
                    self.world_buttons[r][c].setStyleSheet(style)
                    # Preserve any text on the button

    def reset_all_buttons_to_base_style(self):
        """Reset all buttons to their base style based on place type."""
        if not hasattr(self, 'button_styles'):
            self.apply_place_type_colors()
            return
            
        if isinstance(self.world, World1D):
            for i in range(self.world.size):
                if i < len(self.world_buttons):
                    self.world_buttons[i].setStyleSheet(self.button_styles[i])
                    self.world_buttons[i].setText("")  # Clear text
                
        elif isinstance(self.world, World2D):
            for r in range(self.world.rows):
                for c in range(self.world.cols):
                    if r < len(self.world_buttons) and c < len(self.world_buttons[r]):
                        self.world_buttons[r][c].setStyleSheet(self.button_styles[(r, c)])
                        self.world_buttons[r][c].setText("")  # Clear text

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

    def update_simulation_probability_visualization(self):
        """Update the visualization of strategy probabilities for both players in simulation mode."""
        if not hasattr(self, 'hider_player') or not hasattr(self, 'seeker_player'):
            return
            
        # Clear existing visualization
        for i in reversed(range(self.probability_grid.count())):
            item = self.probability_grid.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
        
        # Get strategy probabilities for both players
        hider_probabilities = self.hider_player.strategy_probabilities
        seeker_probabilities = self.seeker_player.strategy_probabilities
        
        # Find max probability for scaling
        hider_max_prob = max(hider_probabilities) if len(hider_probabilities) > 0 else 1.0
        hider_min_prob = min(hider_probabilities) if len(hider_probabilities) > 0 else 0.0
        
        seeker_max_prob = max(seeker_probabilities) if len(seeker_probabilities) > 0 else 1.0
        seeker_min_prob = min(seeker_probabilities) if len(seeker_probabilities) > 0 else 0.0
        
        # Show title for the strategy analysis section
        title_label = QLabel("SIMULATION STRATEGIES ANALYSIS")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; background-color: #0d47a1; padding: 8px; border-radius: 4px;")
        title_label.setAlignment(Qt.AlignCenter)
        self.probability_grid.addWidget(title_label, 0, 0, 1, 5)
        
        # Add explanation of what the simulation is showing
        explanation = QLabel(
            "This simulation shows both Hider and Seeker playing with their optimal strategies calculated using linear programming. "
            "The probabilities below show how likely each player is to choose each position based on game theory calculations.")
        explanation.setWordWrap(True)
        explanation.setStyleSheet("margin-top: 5px; margin-bottom: 15px;")
        self.probability_grid.addWidget(explanation, 1, 0, 1, 5)
        
        # HIDER STRATEGIES SECTION
        hider_title = QLabel("HIDER STRATEGY")
        hider_title.setStyleSheet("font-size: 14px; font-weight: bold; color: white; background-color: #388E3C; padding: 5px; border-radius: 4px; margin-top: 15px;")
        hider_title.setAlignment(Qt.AlignCenter)
        self.probability_grid.addWidget(hider_title, 2, 0, 1, 5)
        
        # Add hider strategy statistics
        stats_label = QLabel("HIDER STATISTICS:")
        stats_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        self.probability_grid.addWidget(stats_label, 3, 0, 1, 5)
        
        hider_stats_grid = QGridLayout()
        # Headers
        hider_stats_grid.addWidget(QLabel("Highest Probability:"), 0, 0)
        hider_stats_grid.addWidget(QLabel("Lowest Probability:"), 1, 0)
        hider_stats_grid.addWidget(QLabel("Uniform Distribution:"), 2, 0)
        
        # Values
        max_prob_label = QLabel(f"{hider_max_prob:.4f}")
        max_prob_label.setStyleSheet("font-weight: bold; color: #388E3C;")
        hider_stats_grid.addWidget(max_prob_label, 0, 1)
        
        min_prob_label = QLabel(f"{hider_min_prob:.4f}")
        min_prob_label.setStyleSheet("font-weight: bold;")
        hider_stats_grid.addWidget(min_prob_label, 1, 1)
        
        uniform_prob = 1.0 / len(hider_probabilities) if len(hider_probabilities) > 0 else 0
        uniform_label = QLabel(f"{uniform_prob:.4f}")
        uniform_label.setStyleSheet("font-weight: bold; color: #9E9E9E;")
        hider_stats_grid.addWidget(uniform_label, 2, 1)
        
        # Visualization boxes for the statistics
        max_box = QLabel()
        max_box.setFixedSize(100, 25)
        max_box.setStyleSheet(f"background-color: rgba(56, 142, 60, 1.0); border: 1px solid #bdbdbd;")
        hider_stats_grid.addWidget(max_box, 0, 2)
        
        min_box = QLabel()
        min_box.setFixedSize(100, 25)
        min_intensity = hider_min_prob / hider_max_prob if hider_max_prob > 0 else 0
        min_box.setStyleSheet(f"background-color: rgba(56, 142, 60, {min_intensity}); border: 1px solid #bdbdbd;")
        hider_stats_grid.addWidget(min_box, 1, 2)
        
        uniform_box = QLabel()
        uniform_box.setFixedSize(100, 25)
        uniform_intensity = uniform_prob / hider_max_prob if hider_max_prob > 0 else 0
        uniform_box.setStyleSheet(f"background-color: rgba(56, 142, 60, {uniform_intensity}); border: 1px solid #bdbdbd;")
        hider_stats_grid.addWidget(uniform_box, 2, 2)
        
        self.probability_grid.addLayout(hider_stats_grid, 4, 0, 1, 5)
        
        # Starting row for the hider probability grid
        hider_grid_start_row = 6
        
        # Add hider probabilities header
        pos_prob_label = QLabel("HIDER POSITION PROBABILITIES:")
        pos_prob_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        self.probability_grid.addWidget(pos_prob_label, hider_grid_start_row, 0, 1, 5)
        
        # Add grid headers
        hider_grid_row = hider_grid_start_row + 1
        
        pos_header = QLabel("POSITION")
        pos_header.setStyleSheet("font-weight: bold; background-color: #388E3C; color: white; padding: 5px;")
        pos_header.setAlignment(Qt.AlignCenter)
        
        viz_header = QLabel("VISUALIZATION")
        viz_header.setStyleSheet("font-weight: bold; background-color: #388E3C; color: white; padding: 5px;")
        viz_header.setAlignment(Qt.AlignCenter)
        
        prob_header = QLabel("PROBABILITY")
        prob_header.setStyleSheet("font-weight: bold; background-color: #388E3C; color: white; padding: 5px;")
        prob_header.setAlignment(Qt.AlignCenter)
        
        rank_header = QLabel("RANK")
        rank_header.setStyleSheet("font-weight: bold; background-color: #388E3C; color: white; padding: 5px;")
        rank_header.setAlignment(Qt.AlignCenter)
        
        self.probability_grid.addWidget(pos_header, hider_grid_row, 0)
        self.probability_grid.addWidget(viz_header, hider_grid_row, 1)
        self.probability_grid.addWidget(prob_header, hider_grid_row, 2)
        self.probability_grid.addWidget(rank_header, hider_grid_row, 3)
        
        # Sort probabilities for ranking
        sorted_indices = sorted(range(len(hider_probabilities)), key=lambda i: hider_probabilities[i], reverse=True)
        ranks = {idx: rank + 1 for rank, idx in enumerate(sorted_indices)}
        
        # Create a grid showing hider probabilities
        if isinstance(self.world, World1D):
            for i, prob in enumerate(hider_probabilities):
                # Position label
                pos_label = QLabel(f"Position {i}")
                pos_label.setAlignment(Qt.AlignCenter)
                pos_label.setStyleSheet("padding: 8px; background-color: #263238; border: 1px solid #388E3C;")
                
                # Create a colored box showing the probability intensity
                intensity = prob / hider_max_prob
                color_box = QLabel()
                color_box.setFixedSize(150, 30)
                color_box.setStyleSheet(f"background-color: rgba(56, 142, 60, {intensity}); border: 1px solid #bdbdbd;")
                
                # Probability value
                prob_label = QLabel(f"{prob:.4f}")
                prob_label.setAlignment(Qt.AlignCenter)
                if prob == hider_max_prob:
                    prob_label.setStyleSheet("padding: 8px; font-weight: bold; color: #388E3C;")
                else:
                    prob_label.setStyleSheet("padding: 8px;")
                
                # Rank
                rank_label = QLabel(f"#{ranks[i]}")
                rank_label.setAlignment(Qt.AlignCenter)
                if ranks[i] == 1:
                    rank_label.setStyleSheet("padding: 8px; font-weight: bold; color: #388E3C;")
                else:
                    rank_label.setStyleSheet("padding: 8px;")
                
                row = hider_grid_row + i + 1
                
                self.probability_grid.addWidget(pos_label, row, 0)
                self.probability_grid.addWidget(color_box, row, 1)
                self.probability_grid.addWidget(prob_label, row, 2)
                self.probability_grid.addWidget(rank_label, row, 3)
                
        elif isinstance(self.world, World2D):
            rows = self.world.rows
            cols = self.world.cols
            
            # Add top positions table for hider
            top_pos_label = QLabel("TOP HIDER POSITIONS:")
            top_pos_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
            self.probability_grid.addWidget(top_pos_label, hider_grid_row + 1, 0, 1, 5)
            
            # Headers for the sorted table
            rank_header = QLabel("RANK")
            pos_header = QLabel("POSITION")
            prob_header = QLabel("PROBABILITY")
            viz_header = QLabel("VISUALIZATION")
            
            rank_header.setStyleSheet("font-weight: bold; background-color: #388E3C; color: white; padding: 5px;")
            pos_header.setStyleSheet("font-weight: bold; background-color: #388E3C; color: white; padding: 5px;")
            prob_header.setStyleSheet("font-weight: bold; background-color: #388E3C; color: white; padding: 5px;")
            viz_header.setStyleSheet("font-weight: bold; background-color: #388E3C; color: white; padding: 5px;")
            
            rank_header.setAlignment(Qt.AlignCenter)
            pos_header.setAlignment(Qt.AlignCenter)
            prob_header.setAlignment(Qt.AlignCenter)
            viz_header.setAlignment(Qt.AlignCenter)
            
            self.probability_grid.addWidget(rank_header, hider_grid_row + 2, 0)
            self.probability_grid.addWidget(pos_header, hider_grid_row + 2, 1)
            self.probability_grid.addWidget(prob_header, hider_grid_row + 2, 2)
            self.probability_grid.addWidget(viz_header, hider_grid_row + 2, 3)
            
            # Show top positions (limit to 5 or fewer for hider)
            num_to_show = min(5, len(sorted_indices))
            for rank in range(num_to_show):
                idx = sorted_indices[rank]
                prob = hider_probabilities[idx]
                pos = self.world.index_to_pos(idx)
                r, c = pos
                
                # Rank label
                rank_label = QLabel(f"#{rank + 1}")
                rank_label.setAlignment(Qt.AlignCenter)
                rank_label.setStyleSheet("padding: 5px;")
                
                # Position label
                pos_label = QLabel(f"({r}, {c})")
                pos_label.setAlignment(Qt.AlignCenter)
                pos_label.setStyleSheet("padding: 5px;")
                
                # Probability label
                prob_label = QLabel(f"{prob:.4f}")
                prob_label.setAlignment(Qt.AlignCenter)
                prob_label.setStyleSheet("padding: 5px;")
                
                # Visualization box
                intensity = prob / hider_max_prob
                color_box = QLabel()
                color_box.setFixedSize(150, 30)
                color_box.setStyleSheet(f"background-color: rgba(56, 142, 60, {intensity}); border: 1px solid #bdbdbd;")
                
                self.probability_grid.addWidget(rank_label, hider_grid_row + 3 + rank, 0)
                self.probability_grid.addWidget(pos_label, hider_grid_row + 3 + rank, 1)
                self.probability_grid.addWidget(prob_label, hider_grid_row + 3 + rank, 2)
                self.probability_grid.addWidget(color_box, hider_grid_row + 3 + rank, 3)
        
        # Spacer between hider and seeker sections
        spacer = QLabel("")
        spacer.setFixedHeight(30)
        seeker_start_row = hider_grid_row + 15
        self.probability_grid.addWidget(spacer, seeker_start_row - 1, 0)
        
        # SEEKER STRATEGIES SECTION
        seeker_title = QLabel("SEEKER STRATEGY")
        seeker_title.setStyleSheet("font-size: 14px; font-weight: bold; color: white; background-color: #1E88E5; padding: 5px; border-radius: 4px; margin-top: 15px;")
        seeker_title.setAlignment(Qt.AlignCenter)
        self.probability_grid.addWidget(seeker_title, seeker_start_row, 0, 1, 5)
        
        # Add seeker strategy statistics
        seeker_stats_label = QLabel("SEEKER STATISTICS:")
        seeker_stats_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        self.probability_grid.addWidget(seeker_stats_label, seeker_start_row + 1, 0, 1, 5)
        
        seeker_stats_grid = QGridLayout()
        # Headers
        seeker_stats_grid.addWidget(QLabel("Highest Probability:"), 0, 0)
        seeker_stats_grid.addWidget(QLabel("Lowest Probability:"), 1, 0)
        seeker_stats_grid.addWidget(QLabel("Uniform Distribution:"), 2, 0)
        
        # Values
        seeker_max_prob_label = QLabel(f"{seeker_max_prob:.4f}")
        seeker_max_prob_label.setStyleSheet("font-weight: bold; color: #1E88E5;")
        seeker_stats_grid.addWidget(seeker_max_prob_label, 0, 1)
        
        seeker_min_prob_label = QLabel(f"{seeker_min_prob:.4f}")
        seeker_min_prob_label.setStyleSheet("font-weight: bold;")
        seeker_stats_grid.addWidget(seeker_min_prob_label, 1, 1)
        
        seeker_uniform_prob = 1.0 / len(seeker_probabilities) if len(seeker_probabilities) > 0 else 0
        seeker_uniform_label = QLabel(f"{seeker_uniform_prob:.4f}")
        seeker_uniform_label.setStyleSheet("font-weight: bold; color: #9E9E9E;")
        seeker_stats_grid.addWidget(seeker_uniform_label, 2, 1)
        
        # Visualization boxes for the statistics
        seeker_max_box = QLabel()
        seeker_max_box.setFixedSize(100, 25)
        seeker_max_box.setStyleSheet(f"background-color: rgba(33, 150, 243, 1.0); border: 1px solid #bdbdbd;")
        seeker_stats_grid.addWidget(seeker_max_box, 0, 2)
        
        seeker_min_box = QLabel()
        seeker_min_box.setFixedSize(100, 25)
        seeker_min_intensity = seeker_min_prob / seeker_max_prob if seeker_max_prob > 0 else 0
        seeker_min_box.setStyleSheet(f"background-color: rgba(33, 150, 243, {seeker_min_intensity}); border: 1px solid #bdbdbd;")
        seeker_stats_grid.addWidget(seeker_min_box, 1, 2)
        
        seeker_uniform_box = QLabel()
        seeker_uniform_box.setFixedSize(100, 25)
        seeker_uniform_intensity = seeker_uniform_prob / seeker_max_prob if seeker_max_prob > 0 else 0
        seeker_uniform_box.setStyleSheet(f"background-color: rgba(33, 150, 243, {seeker_uniform_intensity}); border: 1px solid #bdbdbd;")
        seeker_stats_grid.addWidget(seeker_uniform_box, 2, 2)
        
        self.probability_grid.addLayout(seeker_stats_grid, seeker_start_row + 2, 0, 1, 5)
        
        # Starting row for the seeker probability grid
        seeker_grid_start_row = seeker_start_row + 4
        
        # Add seeker probabilities header
        seeker_pos_prob_label = QLabel("SEEKER POSITION PROBABILITIES:")
        seeker_pos_prob_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        self.probability_grid.addWidget(seeker_pos_prob_label, seeker_grid_start_row, 0, 1, 5)
        
        # Add grid headers
        seeker_grid_row = seeker_grid_start_row + 1
        
        pos_header = QLabel("POSITION")
        pos_header.setStyleSheet("font-weight: bold; background-color: #1E88E5; color: white; padding: 5px;")
        pos_header.setAlignment(Qt.AlignCenter)
        
        viz_header = QLabel("VISUALIZATION")
        viz_header.setStyleSheet("font-weight: bold; background-color: #1E88E5; color: white; padding: 5px;")
        viz_header.setAlignment(Qt.AlignCenter)
        
        prob_header = QLabel("PROBABILITY")
        prob_header.setStyleSheet("font-weight: bold; background-color: #1E88E5; color: white; padding: 5px;")
        prob_header.setAlignment(Qt.AlignCenter)
        
        rank_header = QLabel("RANK")
        rank_header.setStyleSheet("font-weight: bold; background-color: #1E88E5; color: white; padding: 5px;")
        rank_header.setAlignment(Qt.AlignCenter)
        
        self.probability_grid.addWidget(pos_header, seeker_grid_row, 0)
        self.probability_grid.addWidget(viz_header, seeker_grid_row, 1)
        self.probability_grid.addWidget(prob_header, seeker_grid_row, 2)
        self.probability_grid.addWidget(rank_header, seeker_grid_row, 3)
        
        # Sort probabilities for ranking
        seeker_sorted_indices = sorted(range(len(seeker_probabilities)), key=lambda i: seeker_probabilities[i], reverse=True)
        seeker_ranks = {idx: rank + 1 for rank, idx in enumerate(seeker_sorted_indices)}
        
        # Create a grid showing seeker probabilities
        if isinstance(self.world, World1D):
            for i, prob in enumerate(seeker_probabilities):
                # Position label
                pos_label = QLabel(f"Position {i}")
                pos_label.setAlignment(Qt.AlignCenter)
                pos_label.setStyleSheet("padding: 8px; background-color: #263238; border: 1px solid #1E88E5;")
                
                # Create a colored box showing the probability intensity
                intensity = prob / seeker_max_prob
                color_box = QLabel()
                color_box.setFixedSize(150, 30)
                color_box.setStyleSheet(f"background-color: rgba(33, 150, 243, {intensity}); border: 1px solid #bdbdbd;")
                
                # Probability value
                prob_label = QLabel(f"{prob:.4f}")
                prob_label.setAlignment(Qt.AlignCenter)
                if prob == seeker_max_prob:
                    prob_label.setStyleSheet("padding: 8px; font-weight: bold; color: #1E88E5;")
                else:
                    prob_label.setStyleSheet("padding: 8px;")
                
                # Rank
                rank_label = QLabel(f"#{seeker_ranks[i]}")
                rank_label.setAlignment(Qt.AlignCenter)
                if seeker_ranks[i] == 1:
                    rank_label.setStyleSheet("padding: 8px; font-weight: bold; color: #1E88E5;")
                else:
                    rank_label.setStyleSheet("padding: 8px;")
                
                row = seeker_grid_row + i + 1
                
                self.probability_grid.addWidget(pos_label, row, 0)
                self.probability_grid.addWidget(color_box, row, 1)
                self.probability_grid.addWidget(prob_label, row, 2)
                self.probability_grid.addWidget(rank_label, row, 3)
                
        elif isinstance(self.world, World2D):
            rows = self.world.rows
            cols = self.world.cols
            
            # Add top positions table for seeker
            top_pos_label = QLabel("TOP SEEKER POSITIONS:")
            top_pos_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
            self.probability_grid.addWidget(top_pos_label, seeker_grid_row + 1, 0, 1, 5)
            
            # Headers for the sorted table
            rank_header = QLabel("RANK")
            pos_header = QLabel("POSITION")
            prob_header = QLabel("PROBABILITY")
            viz_header = QLabel("VISUALIZATION")
            
            rank_header.setStyleSheet("font-weight: bold; background-color: #1E88E5; color: white; padding: 5px;")
            pos_header.setStyleSheet("font-weight: bold; background-color: #1E88E5; color: white; padding: 5px;")
            prob_header.setStyleSheet("font-weight: bold; background-color: #1E88E5; color: white; padding: 5px;")
            viz_header.setStyleSheet("font-weight: bold; background-color: #1E88E5; color: white; padding: 5px;")
            
            rank_header.setAlignment(Qt.AlignCenter)
            pos_header.setAlignment(Qt.AlignCenter)
            prob_header.setAlignment(Qt.AlignCenter)
            viz_header.setAlignment(Qt.AlignCenter)
            
            self.probability_grid.addWidget(rank_header, seeker_grid_row + 2, 0)
            self.probability_grid.addWidget(pos_header, seeker_grid_row + 2, 1)
            self.probability_grid.addWidget(prob_header, seeker_grid_row + 2, 2)
            self.probability_grid.addWidget(viz_header, seeker_grid_row + 2, 3)
            
            # Show top positions (limit to 5 or fewer for seeker)
            num_to_show = min(5, len(seeker_sorted_indices))
            for rank in range(num_to_show):
                idx = seeker_sorted_indices[rank]
                prob = seeker_probabilities[idx]
                pos = self.world.index_to_pos(idx)
                r, c = pos
                
                # Rank label
                rank_label = QLabel(f"#{rank + 1}")
                rank_label.setAlignment(Qt.AlignCenter)
                rank_label.setStyleSheet("padding: 5px;")
                
                # Position label
                pos_label = QLabel(f"({r}, {c})")
                pos_label.setAlignment(Qt.AlignCenter)
                pos_label.setStyleSheet("padding: 5px;")
                
                # Probability label
                prob_label = QLabel(f"{prob:.4f}")
                prob_label.setAlignment(Qt.AlignCenter)
                prob_label.setStyleSheet("padding: 5px;")
                
                # Visualization box
                intensity = prob / seeker_max_prob
                color_box = QLabel()
                color_box.setFixedSize(150, 30)
                color_box.setStyleSheet(f"background-color: rgba(33, 150, 243, {intensity}); border: 1px solid #bdbdbd;")
                
                self.probability_grid.addWidget(rank_label, seeker_grid_row + 3 + rank, 0)
                self.probability_grid.addWidget(pos_label, seeker_grid_row + 3 + rank, 1)
                self.probability_grid.addWidget(prob_label, seeker_grid_row + 3 + rank, 2)
                self.probability_grid.addWidget(color_box, seeker_grid_row + 3 + rank, 3)