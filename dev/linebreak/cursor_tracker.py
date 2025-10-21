#!/usr/bin/env python3
"""
Cursor Usage Tracker - macOS Menu Bar App
Tracks Cursor usage and predicts if you'll exceed monthly limits
"""

import rumps
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from calendar import monthrange


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
                    # Check if we've moved to a new month
                    last_month = data.get('last_update_month')
                    current_month = datetime.now().strftime('%Y-%m')
                    if last_month != current_month:
                        # New month - reset usage but keep limit
                        data['current_usage'] = 0
                        data['last_update_month'] = current_month
                        self.save_data(data)
                    return data
            except (json.JSONDecodeError, KeyError):
                pass
        
        # Default data
        return {
            'monthly_limit': 500,  # Default limit in requests/dollars/whatever unit
            'current_usage': 0,
            'last_update_month': datetime.now().strftime('%Y-%m'),
            'last_updated': None,
            'reset_date': None  # Custom reset date (YYYY-MM-DD format)
        }
    
    def save_data(self, data=None):
        """Save usage data to JSON file"""
        if data is None:
            data = self.data
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_month_stats(self):
        """Calculate current month statistics"""
        now = datetime.now()
        
        # Check if we have a custom reset date
        if self.data.get('reset_date'):
            try:
                reset_date = datetime.strptime(self.data['reset_date'], '%Y-%m-%d')
                # Calculate days since last reset
                days_since_reset = (now - reset_date).days
                
                # If it's been more than 30 days since reset, we're in a new cycle
                if days_since_reset >= 30:
                    # Update to new reset date (30 days from now)
                    new_reset = now + timedelta(days=30)
                    self.data['reset_date'] = new_reset.strftime('%Y-%m-%d')
                    self.data['current_usage'] = 0
                    self.data['last_updated'] = now.isoformat()
                    self.save_data()
                    days_since_reset = 0
                
                # Calculate days in this billing cycle (30 days)
                days_in_cycle = 30
                days_remaining = days_in_cycle - days_since_reset
                
                return {
                    'current_day': days_since_reset + 1,
                    'days_in_month': days_in_cycle,
                    'days_remaining': max(0, days_remaining),
                    'reset_date': reset_date.strftime('%Y-%m-%d'),
                    'next_reset': (reset_date + timedelta(days=30)).strftime('%Y-%m-%d')
                }
            except ValueError:
                # Invalid reset date format, fall back to monthly
                pass
        
        # Default monthly calculation
        current_day = now.day
        days_in_month = monthrange(now.year, now.month)[1]
        days_remaining = days_in_month - current_day
        
        return {
            'current_day': current_day,
            'days_in_month': days_in_month,
            'days_remaining': days_remaining,
            'reset_date': None,
            'next_reset': None
        }
    
    def calculate_prediction(self):
        """Calculate predicted end-of-month usage"""
        stats = self.get_month_stats()
        current_usage = self.data['current_usage']
        
        if stats['current_day'] == 0:
            return 0
        
        # Linear extrapolation
        daily_average = current_usage / stats['current_day']
        predicted_usage = daily_average * stats['days_in_month']
        
        return predicted_usage
    
    def get_status(self):
        """Determine current status (on track, warning, over)"""
        current_usage = self.data['current_usage']
        limit = self.data['monthly_limit']
        stats = self.get_month_stats()
        
        if stats['current_day'] == 0:
            return 'on_track', '🟢'
        
        # Calculate expected usage at this point in the month
        expected_usage = (limit / stats['days_in_month']) * stats['current_day']
        
        usage_ratio = current_usage / expected_usage if expected_usage > 0 else 0
        
        if usage_ratio < 0.8:
            return 'on_track', '🟢'
        elif usage_ratio < 1.0:
            return 'warning', '🟡'
        else:
            return 'over', '🔴'
    
    def update_menu(self, _=None):
        """Update the menu bar display"""
        self.menu.clear()
        
        current_usage = self.data['current_usage']
        limit = self.data['monthly_limit']
        stats = self.get_month_stats()
        predicted = self.calculate_prediction()
        status, icon = self.get_status()
        
        # Update title with status icon
        usage_pct = (current_usage / limit * 100) if limit > 0 else 0
        self.title = f"{icon} {usage_pct:.0f}%"
        
        # Menu items
        self.menu.add(rumps.MenuItem(f"Cursor Usage Tracker", callback=None))
        self.menu.add(rumps.separator)
        
        # Current stats
        self.menu.add(rumps.MenuItem(f"Current: {current_usage:.1f} / {limit:.1f}", callback=None))
        self.menu.add(rumps.MenuItem(f"Usage: {usage_pct:.1f}%", callback=None))
        self.menu.add(rumps.separator)
        
        # Time stats
        if stats.get('reset_date'):
            self.menu.add(rumps.MenuItem(f"Day {stats['current_day']} of {stats['days_in_month']}", callback=None))
            self.menu.add(rumps.MenuItem(f"Reset: {stats['reset_date']}", callback=None))
            if stats.get('next_reset'):
                self.menu.add(rumps.MenuItem(f"Next: {stats['next_reset']}", callback=None))
        else:
            self.menu.add(rumps.MenuItem(f"Day {stats['current_day']} of {stats['days_in_month']}", callback=None))
        
        self.menu.add(rumps.MenuItem(f"{stats['days_remaining']} days remaining", callback=None))
        self.menu.add(rumps.separator)
        
        # Prediction
        predicted_pct = (predicted / limit * 100) if limit > 0 else 0
        self.menu.add(rumps.MenuItem(f"Predicted: {predicted:.1f} ({predicted_pct:.0f}%)", callback=None))
        
        # Daily averages
        if stats['current_day'] > 0:
            daily_avg = current_usage / stats['current_day']
            self.menu.add(rumps.MenuItem(f"Daily avg: {daily_avg:.1f}", callback=None))
        
        if stats['days_remaining'] > 0:
            recommended_daily = (limit - current_usage) / stats['days_remaining']
            if recommended_daily < 0:
                self.menu.add(rumps.MenuItem(f"Over budget by {abs(recommended_daily * stats['days_remaining']):.1f}", callback=None))
            else:
                self.menu.add(rumps.MenuItem(f"Recommended: {recommended_daily:.1f}/day", callback=None))
        
        self.menu.add(rumps.separator)
        
        # Actions
        self.menu.add(rumps.MenuItem("Update Usage...", callback=self.update_usage))
        self.menu.add(rumps.MenuItem("Set Monthly Limit...", callback=self.set_limit))
        self.menu.add(rumps.MenuItem("Set Reset Date...", callback=self.set_reset_date))
        self.menu.add(rumps.MenuItem("Reset Month", callback=self.reset_month))
        self.menu.add(rumps.separator)
        
        # Last updated
        if self.data['last_updated']:
            last_update = datetime.fromisoformat(self.data['last_updated'])
            time_str = last_update.strftime('%b %d, %I:%M %p')
            self.menu.add(rumps.MenuItem(f"Updated: {time_str}", callback=None))
        
        self.menu.add(rumps.separator)
        self.menu.add(rumps.MenuItem("Quit", callback=rumps.quit_application))
    
    @rumps.clicked("Update Usage...")
    def update_usage(self, _):
        """Prompt user to update current usage"""
        current = self.data['current_usage']
        response = rumps.Window(
            title="Update Current Usage",
            message=f"Enter your current Cursor usage:\n(Current: {current:.1f})",
            default_text=str(current),
            ok="Update",
            cancel="Cancel",
            dimensions=(320, 20)
        ).run()
        
        if response.clicked:
            try:
                new_usage = float(response.text)
                if new_usage < 0:
                    rumps.alert("Invalid Input", "Usage cannot be negative")
                    return
                
                self.data['current_usage'] = new_usage
                self.data['last_updated'] = datetime.now().isoformat()
                self.save_data()
                self.update_menu()
                
                # Show confirmation
                rumps.notification(
                    title="Usage Updated",
                    subtitle=f"Current usage: {new_usage:.1f}",
                    message=""
                )
            except ValueError:
                rumps.alert("Invalid Input", "Please enter a valid number")
    
    @rumps.clicked("Set Monthly Limit...")
    def set_limit(self, _):
        """Prompt user to set monthly limit"""
        current_limit = self.data['monthly_limit']
        response = rumps.Window(
            title="Set Monthly Limit",
            message=f"Enter your monthly Cursor usage limit:\n(Current: {current_limit:.1f})",
            default_text=str(current_limit),
            ok="Set",
            cancel="Cancel",
            dimensions=(320, 20)
        ).run()
        
        if response.clicked:
            try:
                new_limit = float(response.text)
                if new_limit <= 0:
                    rumps.alert("Invalid Input", "Limit must be greater than zero")
                    return
                
                self.data['monthly_limit'] = new_limit
                self.save_data()
                self.update_menu()
                
                rumps.notification(
                    title="Limit Updated",
                    subtitle=f"Monthly limit: {new_limit:.1f}",
                    message=""
                )
            except ValueError:
                rumps.alert("Invalid Input", "Please enter a valid number")
    
    @rumps.clicked("Set Reset Date...")
    def set_reset_date(self, _):
        """Set custom reset date for billing cycle"""
        current_reset = self.data.get('reset_date', 'Not set')
        response = rumps.Window(
            title="Set Reset Date",
            message=f"Enter your billing cycle reset date (YYYY-MM-DD):\n(Current: {current_reset})\n\nExample: 2025-11-19",
            default_text="2025-11-19",
            ok="Set",
            cancel="Cancel",
            dimensions=(400, 20)
        ).run()
        
        if response.clicked:
            try:
                # Validate date format
                test_date = datetime.strptime(response.text, '%Y-%m-%d')
                self.data['reset_date'] = response.text
                self.save_data()
                self.update_menu()
                
                rumps.notification(
                    title="Reset Date Set",
                    subtitle=f"Billing cycle resets: {response.text}",
                    message=""
                )
            except ValueError:
                rumps.alert("Invalid Date", "Please use YYYY-MM-DD format (e.g., 2025-11-19)")
    
    @rumps.clicked("Reset Month")
    def reset_month(self, _):
        """Reset usage for a new month"""
        response = rumps.alert(
            title="Reset Month?",
            message="This will reset your usage to 0. Continue?",
            ok="Reset",
            cancel="Cancel"
        )
        
        if response == 1:  # OK clicked
            self.data['current_usage'] = 0
            self.data['last_update_month'] = datetime.now().strftime('%Y-%m')
            self.data['last_updated'] = datetime.now().isoformat()
            self.save_data()
            self.update_menu()
            
            rumps.notification(
                title="Month Reset",
                subtitle="Usage reset to 0",
                message=""
            )


if __name__ == "__main__":
    app = CursorUsageTracker()
    app.run()

