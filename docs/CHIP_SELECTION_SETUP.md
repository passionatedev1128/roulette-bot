# Chip Selection Setup Guide

## Overview

The bot now supports selecting different chip values (0.5, 1, 2.5, 5, 20, 50) before placing bets. This allows for more flexible betting strategies.

---

## Step 1: Capture Chip Selection Coordinates

### Using the Coordinate Capture Tool

Run the coordinate capture tool:

```bash
python scripts/coordinate_capture_tool.py
```

When prompted:
1. Answer **"y"** when asked about capturing chip coordinates
2. For each chip value (0.5, 1, 2.5, 5, 20, 50):
   - Move your mouse to the chip button/area
   - Press Enter
   - Wait 5 seconds
   - Coordinates will be captured automatically

### Manual Configuration

If you prefer to manually add coordinates, edit `config/default_config.json`:

```json
{
  "betting": {
    "chip_selection_coordinates": {
      "0.5": [1309, 947],
      "1": [1310, 947],
      "2.5": [1311, 947],
      "5": [1312, 947],
      "20": [1313, 947],
      "50": [1314, 947]
    }
  }
}
```

**Important**: Replace the coordinates with the actual positions of each chip on your screen.

---

## Step 2: Test Chip Selection Coordinates

### Test All Chip Coordinates

```bash
python scripts/test_browser_coordinates.py
```

This will:
- Move mouse to each chip coordinate
- Ask you to verify if each coordinate is correct
- Save results to `coordinate_test_results.json`

### Test with Actual Clicking

```bash
python scripts/test_browser_coordinates.py --click
```

⚠️ **Warning**: This will actually click on coordinates. Use only with a test account!

---

## Step 3: How Chip Selection Works

### Automatic Chip Selection

When placing a bet, the bot will:
1. **Select the appropriate chip** based on the bet amount
2. **Click the betting area** the required number of times
3. **Confirm the bet**

**Example:**
- Bet amount: 10.0
- Selected chip: 5.0
- Clicks needed: 2 (5.0 × 2 = 10.0)

### Manual Chip Selection

You can also specify which chip to use when calling `place_bet()`:

```python
bet_controller.place_bet('red', 10.0, chip_value=5.0)
```

This will:
1. Select chip 5.0
2. Click betting area 2 times (5.0 × 2 = 10.0)
3. Confirm bet

---

## Step 4: Configuration Options

### Option 1: Multiple Chip Coordinates (Recommended)

```json
{
  "betting": {
    "chip_selection_coordinates": {
      "0.5": [1309, 947],
      "1": [1310, 947],
      "2.5": [1311, 947],
      "5": [1312, 947],
      "20": [1313, 947],
      "50": [1314, 947]
    }
  }
}
```

**Benefits:**
- Bot can select any chip value
- More flexible betting strategies
- Better control over bet amounts

### Option 2: Single Chip Coordinate (Legacy)

```json
{
  "betting": {
    "chip_selection": [1309, 947]
  }
}
```

**Note**: If only `chip_selection` is provided, the bot will use that coordinate for all chip values. This is less flexible but works if your platform has a single chip selector.

---

## Step 5: Finding Chip Coordinates

### Method 1: Visual Inspection

1. Open your roulette game in browser
2. Look at the chip selection area (usually at bottom of screen)
3. Note the positions of each chip button
4. Use a coordinate capture tool or screenshot tool to find exact coordinates

### Method 2: Using Screenshot Tools

1. Take a screenshot of the game
2. Open in image editor (Paint, GIMP, etc.)
3. Hover over each chip button
4. Note the X, Y coordinates shown in status bar
5. Add to config file

### Method 3: Interactive Tool

```bash
python scripts/coordinate_capture_tool.py
```

Follow the prompts to capture each chip coordinate.

---

## Troubleshooting

### Chip Selection Not Working

**Problem**: Bot doesn't select chips before betting

**Solutions**:
1. Check that `chip_selection_coordinates` is in config
2. Verify coordinates are correct (use test script)
3. Check browser zoom is 100%
4. Ensure browser window hasn't moved

### Wrong Chip Selected

**Problem**: Bot selects wrong chip value

**Solutions**:
1. Verify coordinates for each chip are correct
2. Test each chip coordinate individually
3. Check if chip buttons are in a different order than expected

### Multiple Clicks Not Working

**Problem**: Bot doesn't click betting area multiple times

**Solutions**:
1. Check logs to see how many clicks are attempted
2. Verify bet amount calculation (bet_amount / chip_value)
3. Ensure platform supports multiple clicks on betting area

---

## Example Usage

### Basic Betting

```python
from backend.app.betting import BetController
from backend.app.config_loader import ConfigLoader

# Load config
config = ConfigLoader.load_config('config/default_config.json')

# Initialize bet controller
bet_controller = BetController(config)

# Place bet (chip will be auto-selected)
result = bet_controller.place_bet('red', 10.0)
print(f"Bet placed: {result['success']}")
print(f"Chip used: {result.get('chip_value')}")
```

### Custom Chip Selection

```python
# Place bet with specific chip
result = bet_controller.place_bet('black', 15.0, chip_value=5.0)
# Will use 5.0 chip × 3 clicks = 15.0 total
```

---

## Best Practices

1. **Test thoroughly**: Always test chip selection in test mode before live use
2. **Verify coordinates**: Use the test script to verify all chip coordinates
3. **Check logs**: Monitor logs to see which chips are being selected
4. **Start small**: Test with small bet amounts first
5. **Backup config**: Keep a backup of your working config

---

## Summary

✅ **What's been implemented:**
- Support for multiple chip values (0.5, 1, 2.5, 5, 20, 50)
- Automatic chip selection based on bet amount
- Manual chip selection option
- Coordinate capture tool updated
- Test script for verifying coordinates

✅ **Next steps:**
1. Capture chip coordinates using the tool
2. Test coordinates with test script
3. Update config file with coordinates
4. Test betting with different chip values
5. Monitor logs to verify chip selection works correctly

---

## Support

If you encounter issues:
1. Check the logs for error messages
2. Verify coordinates are correct
3. Test coordinates individually
4. Check browser window position and zoom level

