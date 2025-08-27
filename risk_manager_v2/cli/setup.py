"""
Setup & Authentication Menu

Handles initial setup, authentication, and configuration.
"""

from .base_menu import BaseMenu

class SetupMenu(BaseMenu):
    """Setup and authentication menu."""
    
    def run(self):
        """Run the setup menu."""
        while True:
            self.display_menu()
            choice = input("Choice: ").strip()
            
            if choice == "1":
                self.authenticate_user()
            elif choice == "2":
                self.test_connection()
            elif choice == "3":
                self.view_config()
            elif choice == "4":
                self.edit_config()
            elif choice == "0":
                break
            else:
                print("Invalid choice.")
    
    def display_menu(self):
        """Display setup menu options."""
        print("\n=== SETUP & AUTHENTICATION ===")
        
        # Show current status
        if self.auth.is_authenticated():
            print("âœ… Currently authenticated")
            username = self.config.get("auth.userName")
            print(f"   User: {username}")
            
            if self.client.test_connection():
                print("âœ… API connection working")
            else:
                print("âŒ API connection failed")
        else:
            print("âŒ Not authenticated")
        
        print("\nOptions:")
        print("1) Authenticate with TopStepX")
        print("2) Test API Connection")
        print("3) View Configuration")
        print("4) Edit Configuration")
        print("0) Back to main menu")
    
    def authenticate_user(self):
        """Authenticate user with TopStepX."""
        print("\n=== AUTHENTICATION ===")
        
        username = input("Username: ").strip()
        api_key = input("API Key: ").strip()
        
        if not username or not api_key:
            print("âŒ Username and API key are required")
            return
        
        print("Authenticating...")
        if self.auth.authenticate(username, api_key):
            print("âœ… Authentication successful!")
            
            if self.client.test_connection():
                print("âœ… API connection verified")
            else:
                print("âŒ API connection failed")
        else:
            print("âŒ Authentication failed")
    
    def test_connection(self):
        """Test API connection."""
        print("\nTesting API connection...")
        
        if self.auth.is_authenticated():
            if self.client.test_connection():
                print("âœ… API connection successful")
            else:
                print("âŒ API connection failed")
        else:
            print("âŒ Not authenticated")
    
    def view_config(self):
        """View current configuration."""
        print("\n=== CURRENT CONFIGURATION ===")
        
        # API Configuration
        print("API Configuration:")
        print(f"  Base URL: {self.config.get_api_url()}")
        print(f"  User Hub: {self.config.get_user_hub_url()}")
        print(f"  Market Hub: {self.config.get_market_hub_url()}")
        print(f"  Timeout: {self.config.get('api.timeout')}s")
        print(f"  Max Retries: {self.config.get('api.max_retries')}")
        
        # Risk Configuration
        print("\nRisk Configuration:")
        print(f"  Max Daily Loss: ${self.config.get('risk.max_daily_loss')}")
        print(f"  Max Position Size: {self.config.get('risk.max_position_size')} contracts")
        print(f"  Max Open Positions: {self.config.get('risk.max_open_positions')}")
        print(f"  Auto Flatten: {self.config.get('risk.auto_flatten')}")
        
        # Trading Hours
        print("\nTrading Hours:")
        print(f"  Start: {self.config.get('trading_hours.start')}")
        print(f"  End: {self.config.get('trading_hours.end')}")
        print(f"  Timezone: {self.config.get('trading_hours.timezone')}")
        
        input("\nPress Enter to continue...")
    
    def edit_config(self):
        """Edit configuration settings."""
        print("\n=== EDIT CONFIGURATION ===")
        print("(This will be implemented in the next phase)")
        print("Features:")
        print("- Edit risk limits")
        print("- Change trading hours")
        print("- Update API settings")
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    print("Testing SetupMenu...")
    
    # Test basic initialization
    setup = SetupMenu()
    print("âœ… SetupMenu created successfully!")
    
    # Test display menu
    setup.display_menu()
    print("âœ… SetupMenu test completed!")

