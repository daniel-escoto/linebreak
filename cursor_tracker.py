#!/usr/bin/env python3
"""
Cursor Usage Tracker - macOS Menu Bar App
Tracks Cursor usage percentage and projects end-of-cycle usage
"""

import rumps
import json
from datetime import datetime, timedelta
from pathlib import Path


class CursorUsageTracker(rumps.App):
    def __init__(self):
        super(CursorUsageTracker, self).__init__("📊")
        self.data_file = Path.home() / ".cursor_usage_data.json"
        self.data = self.load_data()
        self.update_menu()
        
        # Set up auto-refresh timer (every hour)
        self.timer = rumps.Timer(self.update_menu, 3600)
        self.timer.start()
    
    def load_data(self):
        """Load usage data from JSON file or create default"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    
                    # Migrate old data structure if needed
                    if 'current_percentage' not in data:
                        # Old structure detected, create new structure
                        data = {
                            'reset_date': data.get('reset_date'),
                            'current_percentage': 0.0
                        }
                        # Save the migrated data
                        self.save_data(data)
                    
                    return data
            except (json.JSONDecodeError, KeyError):
                pass
        
        # Default data - prompt user for reset date on first run
        return {
            'reset_date': None,  # Will be set on first use
            'current_percentage': 0.0
        }
    
    def save_data(self, data=None):
        """Save usage data to JSON file"""
        if data is None:
            data = self.data
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_cycle_stats(self):
        """Calculate current cycle statistics"""
        now = datetime.now()
        
        if not self.data.get('reset_date'):
            return None
        
        try:
            reset_date = datetime.strptime(self.data['reset_date'], '%Y-%m-%d')
            days_since_reset = (now - reset_date).days
            
            # Calculate days in this billing cycle (30 days)
            days_in_cycle = 30
            days_remaining = max(0, days_in_cycle - days_since_reset)
            next_reset_date = reset_date + timedelta(days=30)
            
            return {
                'days_since_reset': days_since_reset,
                'days_in_cycle': days_in_cycle,
                'days_remaining': days_remaining,
                'reset_date': reset_date.strftime('%Y-%m-%d'),
                'next_reset': next_reset_date.strftime('%Y-%m-%d')
            }
        except ValueError:
            return None
    
    def calculate_prediction(self):
        """Calculate predicted end-of-cycle percentage"""
        stats = self.get_cycle_stats()
        if not stats or stats['days_since_reset'] <= 0:
            return self.data['current_percentage']
        
        current_percentage = self.data['current_percentage']
        
        # Linear extrapolation based on percentage growth per day
        daily_average = current_percentage / stats['days_since_reset']
        predicted_percentage = daily_average * stats['days_in_cycle']
        
        return predicted_percentage
    
    def update_menu(self, _=None):
        """Update the menu bar display"""
        self.menu.clear()
        
        current_percentage = self.data['current_percentage']
        stats = self.get_cycle_stats()
        
        # Update title with just the percentage
        self.title = f"{current_percentage:.0f}%"
        
        # Menu items
        self.menu.add(rumps.MenuItem("Cursor Usage Tracker", callback=None))
        self.menu.add(rumps.separator)
        
        # Current percentage
        self.menu.add(rumps.MenuItem(f"Current: {current_percentage:.1f}%", callback=None))
        self.menu.add(rumps.separator)
        
        # Cycle stats
        if stats:
            self.menu.add(rumps.MenuItem(f"Reset Date: {stats['reset_date']}", callback=None))
            self.menu.add(rumps.MenuItem(f"Day {stats['days_since_reset']} of {stats['days_in_cycle']}", callback=None))
            self.menu.add(rumps.MenuItem(f"{stats['days_remaining']} days remaining", callback=None))
            self.menu.add(rumps.separator)
            
            # Prediction
            predicted = self.calculate_prediction()
            self.menu.add(rumps.MenuItem(f"Projected: {predicted:.1f}%", callback=None))
        else:
            self.menu.add(rumps.MenuItem("No reset date set", callback=None))
            self.menu.add(rumps.MenuItem("Use 'Reset Cycle...' to set", callback=None))
        
        self.menu.add(rumps.separator)
        
        # Actions
        self.menu.add(rumps.MenuItem("Update Percentage...", callback=self.update_percentage))
        self.menu.add(rumps.MenuItem("Reset Cycle...", callback=self.reset_cycle))
        self.menu.add(rumps.separator)
        self.menu.add(rumps.MenuItem("Quit", callback=rumps.quit_application))
    
    @rumps.clicked("Update Percentage...")
    def update_percentage(self, _):
        """Prompt user to update current percentage"""
        current = self.data['current_percentage']
        response = rumps.Window(
            title="Update Current Percentage",
            message=f"Enter your current Cursor usage percentage (0-100):\n(Current: {current:.1f}%)",
            default_text=str(current),
            ok="Update",
            cancel="Cancel",
            dimensions=(320, 20)
        ).run()
        
        if response.clicked:
            try:
                new_percentage = float(response.text)
                if new_percentage < 0 or new_percentage > 100:
                    rumps.alert("Invalid Input", "Percentage must be between 0 and 100")
                    return
                
                self.data['current_percentage'] = new_percentage
                self.save_data()
                self.update_menu()
                
                # Show confirmation
                rumps.notification(
                    title="Percentage Updated",
                    subtitle=f"Current usage: {new_percentage:.1f}%",
                    message=""
                )
            except ValueError:
                rumps.alert("Invalid Input", "Please enter a valid number")
    
    @rumps.clicked("Reset Cycle...")
    def reset_cycle(self, _):
        """Reset cycle and set new reset date"""
        response = rumps.alert(
            title="Reset Cycle?",
            message="This will reset your percentage to 0 and ask for a new reset date. Continue?",
            ok="Reset",
            cancel="Cancel"
        )
        
        if response == 1:  # OK clicked
            # Ask for new reset date
            date_response = rumps.Window(
                title="Set Reset Date",
                message="Enter the reset date for the new cycle (YYYY-MM-DD):\n\nExample: 2025-10-21",
                default_text=datetime.now().strftime('%Y-%m-%d'),
                ok="Set",
                cancel="Cancel",
                dimensions=(400, 20)
            ).run()
            
            if date_response.clicked:
                try:
                    # Validate date format
                    test_date = datetime.strptime(date_response.text, '%Y-%m-%d')
                    self.data['reset_date'] = date_response.text
                    self.data['current_percentage'] = 0.0
                    self.save_data()
                    self.update_menu()
                    
                    rumps.notification(
                        title="Cycle Reset",
                        subtitle=f"Reset to 0% on {date_response.text}",
                        message=""
                    )
                except ValueError:
                    rumps.alert("Invalid Date", "Please use YYYY-MM-DD format (e.g., 2025-10-21)")


if __name__ == "__main__":
    app = CursorUsageTracker()
    app.run()

