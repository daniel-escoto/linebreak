# Cursor Usage Tracker

A macOS menu bar application that helps you track and manage your Cursor usage limits throughout the month. The app predicts whether you'll exceed your monthly limit based on your current usage pattern.

## Features

- 📊 **Real-time tracking**: Monitor your current Cursor usage vs. your monthly limit
- 🎯 **Smart predictions**: Linear extrapolation to predict end-of-month usage
- 🚦 **Status indicators**: 
  - 🟢 Green: On track (< 80% of expected usage)
  - 🟡 Yellow: Warning (80-100% of expected usage)  
  - 🔴 Red: Over pace (> 100% of expected usage)
- 📈 **Helpful metrics**:
  - Current usage percentage
  - Predicted end-of-month usage
  - Daily average so far
  - Recommended daily usage to stay under limit
- 🔄 **Auto-refresh**: Updates every hour
- 💾 **Persistent storage**: Your data is saved locally and persists between app restarts
- 🗓️ **Auto-reset**: Automatically resets usage at the start of each new month

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

The app will appear in your menu bar (top right) with a status icon and percentage.

### Initial Setup

1. Click on the menu bar icon
2. Select "Set Monthly Limit..." to configure your monthly usage limit
3. Select "Update Usage..." to enter your current Cursor usage

### Updating Your Usage

Periodically check your actual Cursor usage and update it in the app:

1. Click the menu bar icon
2. Select "Update Usage..."
3. Enter your current usage amount
4. Click "Update"

### Menu Options

- **Current: X / Y**: Your current usage vs. monthly limit
- **Usage: X%**: Percentage of limit used
- **Day X of Y**: Current day in the month
- **X days remaining**: Days left in the current month
- **Predicted: X (Y%)**: Predicted end-of-month usage based on current pace
- **Daily avg: X**: Your average daily usage so far
- **Recommended: X/day**: Suggested daily usage to stay under limit
- **Update Usage...**: Manually update your current usage
- **Set Monthly Limit...**: Change your monthly limit
- **Reset Month**: Manually reset usage (useful if you want to start fresh)

### Interpretation

The menu bar shows a colored indicator and your current usage percentage:

- **🟢**: You're using less than expected for this point in the month - you're good!
- **🟡**: You're close to the expected pace - watch your usage
- **🔴**: You're over the expected pace - slow down or you'll exceed your limit

## Data Storage

Usage data is stored in `~/.cursor_usage_data.json` in your home directory. This file contains:
- Your monthly limit
- Current usage
- Last update timestamp
- Current month (for auto-reset detection)

## Building a Standalone App (Optional)

To create a standalone macOS app that doesn't require running from terminal:

```bash
uv pip install -e ".[dev]"
python setup.py py2app
```

The app will be created in `dist/cursor_tracker.app` which you can move to your Applications folder.

## Tips

- Update your usage daily or every few days for accurate predictions
- The app uses simple linear extrapolation - if your usage pattern changes, the prediction will adjust
- Set notifications to remind yourself to check and update usage regularly
- The auto-reset feature means you don't have to manually reset each month

## Troubleshooting

### App doesn't appear in menu bar
- Make sure you have the required permissions for the app to run
- Try running with `python cursor_tracker.py` directly to see any error messages

### Calculation seems wrong
- Verify your current usage is correct
- Check that your monthly limit is set properly
- Remember the prediction assumes your usage pattern continues linearly

## License

MIT License - feel free to modify and distribute as needed!

