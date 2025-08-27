#!/usr/bin/env python3

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

"""
Main CLI Router

Routes to different menu modules - keeps main file small and focused.
"""

from .setup import SetupMenu
from .accounts import AccountsMenu
from .rules import RulesMenu

class MainMenu:
    """Main menu router - delegates to specialized menu modules."""
    
    def __init__(self):
        # Initialize menu modules
        self.setup_menu = SetupMenu()
        self.accounts_menu = AccountsMenu()
        self.rules_menu = RulesMenu()
        # TODO: Initialize other menu modules when they're created
        # self.monitoring_menu = MonitoringMenu()
        # self.status_menu = StatusMenu()
        # self.logs_menu = LogsMenu()
        self.running = True
    
    def display_menu(self):
        """Display main menu options."""
        print("\n" + "="*50)
        print("           RISK MANAGER v2")
        print("="*50)
        print("1) Setup & Authentication")
        print("2) Account Management")
        print("3) Risk Rules Configuration")
        print("4) Start Monitoring")
        print("5) System Status")
        print("6) View Logs")
        print("0) Exit")
        print("-"*50)
    
    def handle_choice(self, choice):
        """Route to appropriate menu module."""
        if choice == "1":
            self.setup_menu.run()
        elif choice == "2":
            self.accounts_menu.run()
        elif choice == "3":
            self.rules_menu.run()
        elif choice == "4":
            print("Monitoring menu - coming soon!")
        elif choice == "5":
            print("Status menu - coming soon!")
        elif choice == "6":
            print("Logs menu - coming soon!")
        elif choice == "0":
            self.running = False
        else:
            print("Invalid choice. Please try again.")
    
    def run(self):
        """Run the main menu loop."""
        while self.running:
            try:
                self.display_menu()
                choice = input("Choice: ").strip()
                self.handle_choice(choice)
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")

def main():
    """Main entry point for CLI."""
    menu = MainMenu()
    menu.run()

if __name__ == "__main__":
    main()

