"""
main_menu.py - Main menu for the Hide & Seek game

This module implements a main menu interface that appears before the game starts,
offering various options to the user.
"""

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QLabel, QStackedWidget, QHBoxLayout,
                             QGroupBox, QRadioButton, QSpinBox, QButtonGroup)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap

from main_ui import GameUI

class MainMenu(QMainWindow):
    """Main menu window for the Hide & Seek game."""
    
    def __init__(self):
        """Initialize the main menu."""
        super().__init__()
        
        # Set window properties
        self.setWindowTitle('Hide & Seek Game')
        self.setGeometry(100, 100, 800, 600)
        
        # Apply black and blue style
        self.apply_dark_blue_style()
        
        # Create central widget and stacked layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create stacked widget to handle different screens
        self.stacked_widget = QStackedWidget()
        
        # Create pages
        self.create_home_page()
        self.create_new_game_page()
        self.create_instructions_page()
        self.create_credits_page()
        
        # Add stacked widget to main layout
        self.main_layout.addWidget(self.stacked_widget)
        
        # Show home page first
        self.stacked_widget.setCurrentIndex(0)
    
    def apply_dark_blue_style(self):
        """Apply the dark blue color scheme to the application."""
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #121212;
                color: #e0e0e0;
            }
            QPushButton {
                background-color: #1e88e5;
                color: white;
                border-radius: 4px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
                min-width: 200px;
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
            QLabel {
                color: #e0e0e0;
                font-size: 16px;
            }
            QLabel#title {
                color: #1e88e5;
                font-size: 36px;
                font-weight: bold;
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
            QRadioButton {
                color: #e0e0e0;
                font-size: 14px;
            }
            QRadioButton::indicator {
                border: 1px solid #1e88e5;
            }
            QRadioButton::indicator:checked {
                background-color: #1e88e5;
            }
            QSpinBox {
                background-color: #263238;
                color: white;
                border: 1px solid #1e88e5;
                padding: 2px;
                border-radius: 3px;
            }
        """)
    
    def create_home_page(self):
        """Create the home/main menu page."""
        home_page = QWidget()
        layout = QVBoxLayout(home_page)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("HIDE & SEEK")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("A Game of Strategy")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # Add spacer
        layout.addSpacing(30)
        
        # New Game button
        new_game_btn = QPushButton("New Game")
        new_game_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(new_game_btn)
        
        # Instructions button
        instructions_btn = QPushButton("Instructions")
        instructions_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        layout.addWidget(instructions_btn)
        
        # Credits button
        credits_btn = QPushButton("Credits")
        credits_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        layout.addWidget(credits_btn)
        
        # Quit button
        quit_btn = QPushButton("Quit")
        quit_btn.clicked.connect(self.close)
        layout.addWidget(quit_btn)
        
        # Add page to stacked widget
        self.stacked_widget.addWidget(home_page)
    
    def create_new_game_page(self):
        """Create the new game setup page."""
        new_game_page = QWidget()
        layout = QVBoxLayout(new_game_page)
        
        # Title
        title = QLabel("Game Setup")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Settings container
        settings_container = QWidget()
        settings_layout = QHBoxLayout(settings_container)
        
        # World settings
        world_group = QGroupBox("World Settings")
        world_layout = QVBoxLayout(world_group)
        
        # World dimension selection
        dim_layout = QVBoxLayout()
        dim_label = QLabel("World Dimension:")
        dim_layout.addWidget(dim_label)
        
        self.dim_group = QButtonGroup()
        
        dim_1d_radio = QRadioButton("1D (Linear)")
        dim_1d_radio.setChecked(True)
        self.dim_group.addButton(dim_1d_radio, 1)
        dim_layout.addWidget(dim_1d_radio)
        
        dim_2d_radio = QRadioButton("2D (Grid)")
        self.dim_group.addButton(dim_2d_radio, 2)
        dim_layout.addWidget(dim_2d_radio)
        
        world_layout.addLayout(dim_layout)
        
        # World size
        size_layout = QVBoxLayout()
        size_label = QLabel("World Size:")
        size_layout.addWidget(size_label)
        
        self.size_spin = QSpinBox()
        self.size_spin.setRange(2, 20)
        self.size_spin.setValue(4)
        size_layout.addWidget(self.size_spin)
        
        world_layout.addLayout(size_layout)
        settings_layout.addWidget(world_group)
        
        # Player settings
        player_group = QGroupBox("Player Settings")
        player_layout = QVBoxLayout(player_group)
        
        role_label = QLabel("Play as:")
        player_layout.addWidget(role_label)
        
        self.role_group = QButtonGroup()
        
        hider_radio = QRadioButton("Hider")
        hider_radio.setChecked(True)
        self.role_group.addButton(hider_radio, 0)  # 0 for HIDER
        player_layout.addWidget(hider_radio)
        
        seeker_radio = QRadioButton("Seeker")
        self.role_group.addButton(seeker_radio, 1)  # 1 for SEEKER
        player_layout.addWidget(seeker_radio)
        
        settings_layout.addWidget(player_group)
        
        layout.addWidget(settings_container)
        
        # Buttons container
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setAlignment(Qt.AlignCenter)
        
        # Back button
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        buttons_layout.addWidget(back_btn)
        
        # Start Game button
        start_btn = QPushButton("Start Game")
        start_btn.clicked.connect(self.start_game)
        buttons_layout.addWidget(start_btn)
        
        layout.addWidget(buttons_container)
        
        # Add page to stacked widget
        self.stacked_widget.addWidget(new_game_page)
    
    def create_instructions_page(self):
        """Create the instructions page."""
        instructions_page = QWidget()
        layout = QVBoxLayout(instructions_page)
        
        # Title
        title = QLabel("Instructions")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Instructions text
        instructions_text = QLabel(
            "Hide & Seek Game Rules:\n\n"
            "This is a strategic two-player game where one player is the Hider and the other is the Seeker.\n\n"
            "1. The Hider chooses a position to hide in.\n"
            "2. The Seeker attempts to find the Hider by selecting a position.\n"
            "3. The Hider wins if they remain hidden.\n"
            "4. The Seeker wins if they find the Hider.\n\n"
            "The game is solved using linear programming to calculate optimal mixed strategies.\n"
            "You can play against the computer as either the Hider or the Seeker.\n"
            "The computer uses optimal strategies to minimize its losses.\n\n"
            "The payoff matrix shown in the game represents the utility value for each possible "
            "combination of Hider and Seeker positions."
        )
        instructions_text.setWordWrap(True)
        layout.addWidget(instructions_text)
        
        # Back button
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        back_btn.setMaximumWidth(200)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(back_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # Add page to stacked widget
        self.stacked_widget.addWidget(instructions_page)
    
    def create_credits_page(self):
        """Create the credits page."""
        credits_page = QWidget()
        layout = QVBoxLayout(credits_page)
        
        # Title
        title = QLabel("Credits")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Credits text
        credits_text = QLabel(
            "Hide & Seek Game\n\n"
            "Developed as a demonstration of game theory and linear programming.\n\n"
            "This game implements concepts from:\n"
            "- Zero-sum games\n"
            "- Mixed strategies\n"
            "- Linear programming\n"
            "- Minimax theorem\n\n"
            "UI developed with PyQt5."
        )
        credits_text.setAlignment(Qt.AlignCenter)
        credits_text.setWordWrap(True)
        layout.addWidget(credits_text)
        
        # Back button
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        back_btn.setMaximumWidth(200)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(back_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # Add page to stacked widget
        self.stacked_widget.addWidget(credits_page)
    
    def start_game(self):
        """Start the game with the selected options."""
        # Get selected options
        dimension = self.dim_group.checkedId()
        size = self.size_spin.value()
        role = self.role_group.checkedId()
        
        # Create and show the game UI
        self.game_ui = GameUI()
        
        # Set initial game options
        # We need to set the options before initializing the game
        # For dimension selection
        if dimension == 1:
            self.game_ui.world_dim_group.button(1).setChecked(True)
        else:
            self.game_ui.world_dim_group.button(2).setChecked(True)
        
        # For size
        self.game_ui.world_size_spin.setValue(size)
        
        # For player role - use the buttons directly by index instead of by ID
        if role == 0:  # HIDER
            buttons = self.game_ui.player_type_group.buttons()
            if buttons and len(buttons) > 0:
                buttons[0].setChecked(True)  # First button is Hider
        else:  # SEEKER
            buttons = self.game_ui.player_type_group.buttons()
            if buttons and len(buttons) > 1:
                buttons[1].setChecked(True)  # Second button is Seeker
        
        # Initialize the game with these settings
        self.game_ui.initialize_game()
        
        # Show the game UI
        self.game_ui.show()
        
        # Hide the main menu
        self.hide()

# Main function to run the application
def main():
    app = QApplication(sys.argv)
    menu = MainMenu()
    menu.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 