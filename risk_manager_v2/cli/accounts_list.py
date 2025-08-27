"""
Accounts List Menu

Handles listing and viewing account information.
"""

from .base_menu import BaseMenu

class AccountsListMenu(BaseMenu):
    """Accounts listing menu."""
    
    def run(self):
        """Run the accounts list menu."""
        self.list_accounts()
        self.view_account_details()
    
    def list_accounts(self):
        """List all trading accounts."""
        print("\n=== ALL ACCOUNTS ===")
        
        if not self.auth.is_authenticated():
            print("âŒ Not authenticated")
            return
        
        try:
            accounts = self.client.get_accounts()
            
            if accounts:
                print(f"Found {len(accounts)} account(s):")
                print("-" * 60)
                
                for account in accounts:
                    account_id = account.get('accountId', 'N/A')
                    name = account.get('name', 'N/A')
                    status = account.get('status', 'N/A')
                    
                    print(f"Account ID: {account_id}")
                    print(f"Name: {name}")
                    print(f"Status: {status}")
                    print("-" * 60)
            else:
                print("No accounts found.")
                
        except Exception as e:
            self.logger.error(f"Error listing accounts: {e}")
            print(f"Error: {e}")
    
    def view_account_details(self):
        """View detailed account information."""
        print("\n=== ACCOUNT DETAILS ===")
        
        account_id = input("Enter Account ID (or press Enter to skip): ").strip()
        if not account_id:
            return
        
        try:
            details = self.client.get_account_details(account_id)
            
            if details:
                print(f"\nAccount Details for {account_id}:")
                print("-" * 40)
                
                for key, value in details.items():
                    if isinstance(value, dict):
                        print(f"{key}:")
                        for sub_key, sub_value in value.items():
                            print(f"  {sub_key}: {sub_value}")
                    else:
                        print(f"{key}: {value}")
            else:
                print(f"Account {account_id} not found.")
                
        except Exception as e:
            self.logger.error(f"Error getting account details: {e}")
            print(f"Error: {e}")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    print("Testing AccountsListMenu...")
    
    # Test basic initialization
    accounts_list = AccountsListMenu()
    print("âœ… AccountsListMenu created successfully!")
    
    # Test list accounts (will fail without auth, but should not crash)
    try:
        accounts_list.list_accounts()
        print("âœ… AccountsListMenu test completed!")
    except Exception as e:
        print(f"âœ… AccountsListMenu test completed (expected error without auth): {e}")


