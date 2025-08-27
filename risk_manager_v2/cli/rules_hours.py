"""
Trading Hours Rules

Handles trading hours and timezone configuration.
"""

from .base_menu import BaseMenu
from datetime import datetime, time

class RulesHoursMenu(BaseMenu):
    """Trading hours configuration menu."""
    
    def run(self):
        """Run the trading hours menu."""
        while True:
            self.display_menu()
            choice = input("Choice: ").strip()
            
            if choice == "1":
                self.view_rules()
            elif choice == "2":
                self.set_regular_hours()
            elif choice == "3":
                self.set_pre_market()
            elif choice == "4":
                self.set_after_hours()
            elif choice == "5":
                self.set_timezone()
            elif choice == "6":
                self.set_session_types()
            elif choice == "0":
                break
            else:
                print("Invalid choice.")
    
    def display_menu(self):
        """Display trading hours menu options."""
        print("\n=== TRADING HOURS ===")
        print("1) View Current Hours")
        print("2) Set Regular Trading Hours")
        print("3) Set Pre-Market Hours")
        print("4) Set After-Hours")
        print("5) Set Timezone")
        print("6) Set Session Types")
        print("0) Back to rules menu")
    
    def view_rules(self):
        """View current trading hours."""
        print("\n=== CURRENT TRADING HOURS ===")
        print("-" * 50)
        
        # Get current values with defaults
        start_time = self.config.get('trading_hours.start', '09:30')
        end_time = self.config.get('trading_hours.end', '16:00')
        timezone = self.config.get('trading_hours.timezone', 'America/New_York')
        pre_market_start = self.config.get('trading_hours.pre_market_start', '04:00')
        pre_market_end = self.config.get('trading_hours.pre_market_end', '09:30')
        after_hours_start = self.config.get('trading_hours.after_hours_start', '16:00')
        after_hours_end = self.config.get('trading_hours.after_hours_end', '20:00')
        enable_pre_market = self.config.get('trading_hours.enable_pre_market', False)
        enable_after_hours = self.config.get('trading_hours.enable_after_hours', False)
        
        print(f"Regular Hours: {start_time} - {end_time}")
        print(f"Timezone: {timezone}")
        print(f"Pre-Market: {pre_market_start} - {pre_market_end} {'âœ… ENABLED' if enable_pre_market else 'âŒ DISABLED'}")
        print(f"After-Hours: {after_hours_start} - {after_hours_end} {'âœ… ENABLED' if enable_after_hours else 'âŒ DISABLED'}")
        
        # Show session status
        print("\nSession Status:")
        if self._is_valid_time_range(start_time, end_time):
            print("âœ… Regular hours: VALID")
        else:
            print("âŒ Regular hours: INVALID (start > end)")
            
        if enable_pre_market and self._is_valid_time_range(pre_market_start, pre_market_end):
            print("âœ… Pre-market hours: VALID")
        elif enable_pre_market:
            print("âŒ Pre-market hours: INVALID")
        else:
            print("âŒ Pre-market hours: DISABLED")
            
        if enable_after_hours and self._is_valid_time_range(after_hours_start, after_hours_end):
            print("âœ… After-hours: VALID")
        elif enable_after_hours:
            print("âŒ After-hours: INVALID")
        else:
            print("âŒ After-hours: DISABLED")
        
        input("\nPress Enter to continue...")
    
    def set_regular_hours(self):
        """Set regular trading hours."""
        current_start = self.config.get('trading_hours.start', '09:30')
        current_end = self.config.get('trading_hours.end', '16:00')
        
        print(f"\n=== SET REGULAR TRADING HOURS ===")
        print(f"Current Hours: {current_start} - {current_end}")
        
        try:
            new_start = input("New Start Time (HH:MM): ").strip()
            if new_start and self._validate_time_format(new_start):
                new_end = input("New End Time (HH:MM): ").strip()
                if new_end and self._validate_time_format(new_end):
                    
                    # Validate time range
                    if self._is_valid_time_range(new_start, new_end):
                        self.config.set('trading_hours.start', new_start)
                        self.config.set('trading_hours.end', new_end)
                        print(f"âœ… Regular hours set to {new_start} - {new_end}")
                    else:
                        print("âŒ Invalid time range. Start time must be before end time.")
                else:
                    print("âŒ Invalid end time format. Use HH:MM")
            else:
                print("âŒ Invalid start time format. Use HH:MM")
                
        except Exception as e:
            self.logger.error(f"Error setting regular hours: {e}")
            print("âŒ Error saving configuration.")
        
        input("\nPress Enter to continue...")
    
    def set_pre_market(self):
        """Set pre-market hours."""
        current_start = self.config.get('trading_hours.pre_market_start', '04:00')
        current_end = self.config.get('trading_hours.pre_market_end', '09:30')
        enabled = self.config.get('trading_hours.enable_pre_market', False)
        
        print(f"\n=== SET PRE-MARKET HOURS ===")
        print(f"Current Pre-Market: {current_start} - {current_end} {'âœ… ENABLED' if enabled else 'âŒ DISABLED'}")
        
        # Toggle enable/disable
        toggle = input("Enable pre-market trading? (y/N): ").strip().lower()
        if toggle == 'y':
            try:
                new_start = input("Pre-Market Start Time (HH:MM): ").strip()
                if new_start and self._validate_time_format(new_start):
                    new_end = input("Pre-Market End Time (HH:MM): ").strip()
                    if new_end and self._validate_time_format(new_end):
                        
                        # Validate time range
                        if self._is_valid_time_range(new_start, new_end):
                            self.config.set('trading_hours.pre_market_start', new_start)
                            self.config.set('trading_hours.pre_market_end', new_end)
                            self.config.set('trading_hours.enable_pre_market', True)
                            print(f"âœ… Pre-market hours enabled: {new_start} - {new_end}")
                        else:
                            print("âŒ Invalid time range. Start time must be before end time.")
                    else:
                        print("âŒ Invalid end time format. Use HH:MM")
                else:
                    print("âŒ Invalid start time format. Use HH:MM")
                    
            except Exception as e:
                self.logger.error(f"Error setting pre-market hours: {e}")
                print("âŒ Error saving configuration.")
        else:
            self.config.set('trading_hours.enable_pre_market', False)
            print("âœ… Pre-market trading disabled")
        
        input("\nPress Enter to continue...")
    
    def set_after_hours(self):
        """Set after-hours trading."""
        current_start = self.config.get('trading_hours.after_hours_start', '16:00')
        current_end = self.config.get('trading_hours.after_hours_end', '20:00')
        enabled = self.config.get('trading_hours.enable_after_hours', False)
        
        print(f"\n=== SET AFTER-HOURS TRADING ===")
        print(f"Current After-Hours: {current_start} - {current_end} {'âœ… ENABLED' if enabled else 'âŒ DISABLED'}")
        
        # Toggle enable/disable
        toggle = input("Enable after-hours trading? (y/N): ").strip().lower()
        if toggle == 'y':
            try:
                new_start = input("After-Hours Start Time (HH:MM): ").strip()
                if new_start and self._validate_time_format(new_start):
                    new_end = input("After-Hours End Time (HH:MM): ").strip()
                    if new_end and self._validate_time_format(new_end):
                        
                        # Validate time range
                        if self._is_valid_time_range(new_start, new_end):
                            self.config.set('trading_hours.after_hours_start', new_start)
                            self.config.set('trading_hours.after_hours_end', new_end)
                            self.config.set('trading_hours.enable_after_hours', True)
                            print(f"âœ… After-hours enabled: {new_start} - {new_end}")
                        else:
                            print("âŒ Invalid time range. Start time must be before end time.")
                    else:
                        print("âŒ Invalid end time format. Use HH:MM")
                else:
                    print("âŒ Invalid start time format. Use HH:MM")
                    
            except Exception as e:
                self.logger.error(f"Error setting after-hours: {e}")
                print("âŒ Error saving configuration.")
        else:
            self.config.set('trading_hours.enable_after_hours', False)
            print("âœ… After-hours trading disabled")
        
        input("\nPress Enter to continue...")
    
    def set_timezone(self):
        """Set trading timezone."""
        current = self.config.get('trading_hours.timezone', 'America/New_York')
        print(f"\n=== SET TRADING TIMEZONE ===")
        print(f"Current Timezone: {current}")
        
        print("\nCommon timezones:")
        print("1) America/New_York (EST/EDT) - US Eastern")
        print("2) America/Chicago (CST/CDT) - US Central")
        print("3) America/Denver (MST/MDT) - US Mountain")
        print("4) America/Los_Angeles (PST/PDT) - US Pacific")
        print("5) Europe/London (GMT/BST) - UK")
        print("6) Europe/Paris (CET/CEST) - Central Europe")
        print("7) Asia/Tokyo (JST) - Japan")
        print("8) Custom timezone")
        
        choice = input("Select timezone (1-8): ").strip()
        
        timezone_map = {
            '1': 'America/New_York',
            '2': 'America/Chicago',
            '3': 'America/Denver',
            '4': 'America/Los_Angeles',
            '5': 'Europe/London',
            '6': 'Europe/Paris',
            '7': 'Asia/Tokyo'
        }
        
        try:
            if choice in timezone_map:
                new_tz = timezone_map[choice]
                self.config.set('trading_hours.timezone', new_tz)
                print(f"âœ… Timezone set to {new_tz}")
            elif choice == '8':
                custom_tz = input("Enter custom timezone (e.g., America/New_York): ").strip()
                if custom_tz:
                    self.config.set('trading_hours.timezone', custom_tz)
                    print(f"âœ… Timezone set to {custom_tz}")
                else:
                    print("âŒ No timezone entered.")
            else:
                print("âŒ Invalid choice.")
                
        except Exception as e:
            self.logger.error(f"Error setting timezone: {e}")
            print("âŒ Error saving configuration.")
        
        input("\nPress Enter to continue...")
    
    def set_session_types(self):
        """Set session type preferences."""
        print(f"\n=== SET SESSION TYPES ===")
        print("Configure which session types are allowed for trading:")
        
        # Get current settings
        allow_regular = self.config.get('trading_hours.allow_regular', True)
        allow_pre_market = self.config.get('trading_hours.allow_pre_market', False)
        allow_after_hours = self.config.get('trading_hours.allow_after_hours', False)
        
        print(f"1) Regular Hours: {'âœ… ALLOWED' if allow_regular else 'âŒ BLOCKED'}")
        print(f"2) Pre-Market: {'âœ… ALLOWED' if allow_pre_market else 'âŒ BLOCKED'}")
        print(f"3) After-Hours: {'âœ… ALLOWED' if allow_after_hours else 'âŒ BLOCKED'}")
        
        choice = input("Select session to toggle (1-3): ").strip()
        
        try:
            if choice == '1':
                new_value = not allow_regular
                self.config.set('trading_hours.allow_regular', new_value)
                print(f"âœ… Regular hours: {'ALLOWED' if new_value else 'BLOCKED'}")
            elif choice == '2':
                new_value = not allow_pre_market
                self.config.set('trading_hours.allow_pre_market', new_value)
                print(f"âœ… Pre-market: {'ALLOWED' if new_value else 'BLOCKED'}")
            elif choice == '3':
                new_value = not allow_after_hours
                self.config.set('trading_hours.allow_after_hours', new_value)
                print(f"âœ… After-hours: {'ALLOWED' if new_value else 'BLOCKED'}")
            else:
                print("âŒ Invalid choice.")
                
        except Exception as e:
            self.logger.error(f"Error setting session types: {e}")
            print("âŒ Error saving configuration.")
        
        input("\nPress Enter to continue...")
    
    def _validate_time_format(self, time_str: str) -> bool:
        """Validate time format HH:MM."""
        if len(time_str) != 5 or time_str[2] != ':':
            return False
        
        try:
            hour, minute = time_str.split(':')
            hour_int, minute_int = int(hour), int(minute)
            return 0 <= hour_int <= 23 and 0 <= minute_int <= 59
        except ValueError:
            return False
    
    def _is_valid_time_range(self, start_time: str, end_time: str) -> bool:
        """Check if start time is before end time."""
        try:
            start = datetime.strptime(start_time, '%H:%M').time()
            end = datetime.strptime(end_time, '%H:%M').time()
            return start < end
        except ValueError:
            return False

if __name__ == "__main__":
    print("Testing RulesHoursMenu...")
    
    # Test basic initialization
    hours_rules = RulesHoursMenu()
    print("âœ… RulesHoursMenu created successfully!")
    
    # Test display menu
    hours_rules.display_menu()
    print("âœ… RulesHoursMenu test completed!")


