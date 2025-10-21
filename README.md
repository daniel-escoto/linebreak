# Cursor Usage Tracker

A macOS menu bar application that helps you track your Cursor usage percentage and projects your usage at the end of your billing cycle.

## Features

- 📊 **Percentage tracking**: Track your current Cursor usage as a percentage (0-100%)
- 🎯 **Projection**: Linear projection of your percentage at the end of the 30-day cycle
- 📅 **Custom reset dates**: Set your billing cycle reset date
- 🔄 **Auto-refresh**: Updates every hour
- 💾 **Persistent storage**: Your data is saved locally and persists between app restarts

## Installation

### Prerequisites

- macOS
- Python 3.9 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Install uv (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install Dependencies

```bash
cd linebreak
uv pip install -e .
```

## Usage

### Running the App

```bash
uv run python cursor_tracker.py
```

The app will appear in your menu bar (top right) showing your current percentage.

### Initial Setup

On first run, you'll need to:

1. Click on the menu bar icon
2. Select "Reset Cycle..." to set your billing cycle reset date
3. Select "Update Percentage..." to enter your current usage percentage

### Updating Your Percentage

Check your actual Cursor usage and update it in the app:

1. Click the menu bar icon
2. Select "Update Percentage..."
3. Enter your current usage percentage (0-100)
4. Click "Update"

### Menu Display

The menu bar shows your current usage percentage (e.g., "47%").

When you click the icon, you'll see:

- **Current: X%** - Your current usage percentage
- **Reset Date: YYYY-MM-DD** - Your billing cycle reset date
- **Day X of 30** - Current day in your 30-day cycle
- **X days remaining** - Days left in the current cycle
- **Projected: X%** - Projected usage at the end of the cycle based on current pace
- **Update Percentage...** - Update your current usage percentage
- **Reset Cycle...** - Reset to 0% and set a new reset date

### Reset Cycle

When you need to start a new billing cycle:

1. Click "Reset Cycle..."
2. Confirm the reset
3. Enter your new reset date (YYYY-MM-DD format)
4. Your percentage will be reset to 0%

## How It Works

The app uses simple linear extrapolation to predict your end-of-cycle usage:

- It calculates your average percentage increase per day
- Multiplies that by 30 days to project your end-of-cycle usage
- Updates the projection as you update your current percentage

For example, if you're at 20% on day 10, that's 2% per day, so the projection would be 60% by day 30.

## Data Storage

Usage data is stored in `~/.cursor_usage_data.json` in your home directory. This file contains:
- Your reset date (YYYY-MM-DD format)
- Current percentage (0-100)

## Tips

- Update your percentage every few days for accurate projections
- The app assumes a 30-day billing cycle
- The projection is linear, so if your usage pattern changes, update the percentage more frequently

## Troubleshooting

### App doesn't appear in menu bar
- Make sure you have the required permissions for the app to run
- Try running with `python cursor_tracker.py` directly to see any error messages

### Projection seems wrong
- Verify your current percentage is correct
- Check that your reset date is accurate
- Remember the projection assumes your usage pattern continues linearly

## License

MIT License - feel free to modify and distribute as needed!
