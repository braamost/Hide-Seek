#!/usr/bin/env python3
"""
main.py - Entry point for the Hide & Seek Game application

This module initializes the game application, setting up the Qt GUI
and starting the game.
"""

import sys
from PyQt5.QtWidgets import QApplication

from game_ui import GameUI

def main():
    """Main function to start the application."""
    # Create a Qt application
    app = QApplication(sys.argv)
    
    # Create and show the main window
    window = GameUI()
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()