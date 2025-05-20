"""
visualization.py - Visualization components for the Hide & Seek game

This module contains visualization-related methods for the Hide & Seek game UI.
"""

from PyQt5.QtWidgets import (QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout, 
                            QGroupBox, QTableWidget, QTableWidgetItem,QWidget)
from PyQt5.QtCore import Qt
import numpy as np

from player import PlayerType
from world import World1D, World2D, PlaceType

class GameVisualization:
    """Handles visualization methods for the Hide & Seek game UI."""
    
    def create_visualization_section(self, parent_layout):
        """
        Create the game visualization section.
        
        Args:
            parent_layout (QLayout): Parent layout
        """
        # Payoff matrix explanation
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
        
        # Directly add to parent layout
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

        # Create a vertical layout for this section
        section_layout = QVBoxLayout()
        section_layout.addWidget(explanation)  # Top, left-aligned by default
        section_layout.addWidget(self.payoff_table, alignment=Qt.AlignHCenter)  # Center table horizontally
        section_layout.setSpacing(10)  # Add some spacing between elements
        section_layout.setContentsMargins(10, 10, 10, 10)  # Add margins around the layout

        # Create a container widget for the section
        section_widget = QWidget()
        section_widget.setLayout(section_layout)

        # Add the section widget to the parent layout
        if isinstance(parent_layout, QWidget):
            if parent_layout.layout():
                parent_layout.layout().addWidget(section_widget, alignment=Qt.AlignTop)
            else:
                layout = QVBoxLayout(parent_layout)
                layout.addWidget(section_widget, alignment=Qt.AlignTop)
        else:
            parent_layout.addWidget(section_widget, alignment=Qt.AlignTop)
    
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
        payoff_matrix = self.world.get_payoff_matrix()
        
        # Clear the table
        self.payoff_table.clear()
        size = 0
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
            size = total_positions
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

        # Set table size
        self.payoff_table.setFixedSize(self.payoff_table.horizontalHeader().length() + size * 12,
                                       self.payoff_table.verticalHeader().length() + size * 12)
        
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