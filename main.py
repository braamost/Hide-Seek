#!/usr/bin/env python3
"""
main.py - Main entry point for Hide & Seek game

This script launches the main menu for the Hide & Seek game.
"""

import sys
from PyQt5.QtWidgets import QApplication
from main_menu import MainMenu

def main():
    """Main function to run the application."""
    app = QApplication(sys.argv)
    menu = MainMenu()
    menu.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()