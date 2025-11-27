# Adaptive Chip Selection Guide

##  Overview

The bot now supports **adaptive chip selection** - choosing different chip values (0.5, 1.0, 2.5, 5.0, 10.0) based on:
- **Streak length** (for entry bets)
- **Gale step** (for recovery bets)

This helps with **risk management** by using smaller chips for less confident situations and larger chips when more confident.

---

## ⚙️ Configuration

### Enable/Disable

In `config/default_config.json`:

```json
{
  "betting": {
    "adaptive_chip_selection": true,  // Set to false to disable
    ...
  }
}
```

### Chip Sizes Available

```json
{
  "betting": {
    "chip_sizes": [0.5, 1.0, 2.5, 5.0, 10.0]
  }
}
```

### Chip Selection Rules

```json
{
  "betting": {
    "chip_selection_rules": {
      "entry_streak_6": 1.0,    // Streak 6  use 1.0 chip
      "entry_streak_7": 2.5,    // Streak 7  use 2.5 chip
      "entry_streak_8": 5.0,    // Streak 8  use 5.0 chip
      "entry_streak_9+": 10.0,  // Streak 9+  use 10.0 chip
      "gale_step_0": 1.0,       // Entry bet  use 1.0 chip
      "gale_step_1": 2.5,       // First gale  use 2.5 chip
      "gale_step_2": 5.0,       // Second gale  use 5.0 chip
      "gale_step_3": 10.0       // Third gale  use 10.0 chip
    }
  }
}
```

### Chip Selection Coordinates

You need to configure the coordinates where each chip value is located on screen:

```json
{
  "betting": {
    "chip_selection_coordinates": {
      "0.5": [1309, 947],   // X, Y coordinates for 0.5 chip
      "1.0": [1309, 947],   // X, Y coordinates for 1.0 chip
      "2.5": [1309, 947],   // X, Y coordinates for 2.5 chip
      "5.0": [1309, 947],   // X, Y coordinates for 5.0 chip
      "10.0": [1309, 947]   // X, Y coordinates for 10.0 chip
    }
  }
}
```

** Important**: You need to find the actual coordinates for each chip on your platform. Use a coordinate capture tool or manually test.

---

## 📊 How It Works

### Entry Bets (Streak-Based)

When a streak triggers an entry:
- **Streak 6**: Uses chip from `entry_streak_6` rule (default: 1.0)
- **Streak 7**: Uses chip from `entry_streak_7` rule (default: 2.5)
- **Streak 8**: Uses chip from `entry_streak_8` rule (default: 5.0)
- **Streak 9+**: Uses chip from `entry_streak_9+` rule (default: 10.0)

**Example:**
- Streak 6  Bet 10.0  Uses 1.0 chip × 10 clicks = 10.0 total
- Streak 8  Bet 10.0  Uses 5.0 chip × 2 clicks = 10.0 total

### Gale Progression (Recovery Bets)

When in a cycle and recovering from losses:
- **Gale step 0** (entry): Uses chip from `gale_step_0` rule (default: 1.0)
- **Gale step 1** (first loss): Uses chip from `gale_step_1` rule (default: 2.5)
- **Gale step 2** (second loss): Uses chip from `gale_step_2` rule (default: 5.0)
- **Gale step 3** (third loss): Uses chip from `gale_step_3` rule (default: 10.0)

**Example:**
- Entry: Bet 10.0  Uses 1.0 chip × 10 clicks
- Loss  Gale 1: Bet 20.0  Uses 2.5 chip × 8 clicks = 20.0 total
- Loss  Gale 2: Bet 40.0  Uses 5.0 chip × 8 clicks = 40.0 total

### Priority

1. **Gale step rules** (if in cycle) - takes priority
2. **Streak length rules** (if entry bet)
3. **Fallback**: Closest chip size to bet_amount

---

##  Strategy Logic

### Conservative Approach (Current Default)

**Entry bets**: Start small (1.0 chip for streak 6)
- Lower risk on initial entries
- Less exposure if wrong

**Gale progression**: Increase chip size
- Step 0: 1.0 chip (conservative entry)
- Step 1: 2.5 chip (moderate recovery)
- Step 2: 5.0 chip (aggressive recovery)
- Step 3: 10.0 chip (maximum recovery)

### Aggressive Approach

If you want to bet larger on longer streaks:

```json
{
  "chip_selection_rules": {
    "entry_streak_6": 2.5,    // Larger chip for streak 6
    "entry_streak_7": 5.0,     // Even larger for streak 7
    "entry_streak_8": 10.0,    // Maximum for streak 8+
    "gale_step_0": 2.5,        // Start larger
    "gale_step_1": 5.0,
    "gale_step_2": 10.0,
    "gale_step_3": 10.0
  }
}
```

### Very Conservative Approach

If you want to minimize risk:

```json
{
  "chip_selection_rules": {
    "entry_streak_6": 0.5,     // Smallest chip
    "entry_streak_7": 1.0,
    "entry_streak_8": 2.5,
    "entry_streak_9+": 5.0,
    "gale_step_0": 0.5,
    "gale_step_1": 1.0,
    "gale_step_2": 2.5,
    "gale_step_3": 5.0
  }
}
```

---

## 🔧 Setup Instructions

### Step 1: Find Chip Coordinates

1. Open your roulette game
2. Use a coordinate capture tool (or manually note positions)
3. Find where each chip value (0.5, 1.0, 2.5, 5.0, 10.0) is located
4. Update `chip_selection_coordinates` in config

**Note**: Some platforms may have:
- A single chip selector that cycles through values
- Multiple chip buttons in a row
- A dropdown menu

You'll need to test and adjust coordinates accordingly.

### Step 2: Test Chip Selection

Run a test bet and verify:
- Correct chip is selected
- Correct number of chips are placed
- Total bet amount matches expected

### Step 3: Adjust Rules

Based on your risk tolerance:
- **Conservative**: Smaller chips for entries, moderate for gale
- **Balanced**: Current default (1.0 entry, increasing for gale)
- **Aggressive**: Larger chips for longer streaks

---

## 📊 Benefits

### Risk Management

 **Lower exposure** on uncertain entries (streak 6)
 **Gradual increase** as confidence grows (longer streaks)
 **Faster recovery** in gale progression (larger chips)

### Example Scenario

**Without adaptive chips:**
- All bets use same chip  same risk regardless of confidence

**With adaptive chips:**
- Streak 6 entry: 1.0 chip (lower risk)
- Streak 8 entry: 5.0 chip (higher confidence)
- Gale step 2: 5.0 chip (faster recovery)

---

##  Important Notes

### Win Probability

**Adaptive chip selection does NOT change win probability:**
- Each spin is still ~48.6% for Even/Odd
- This is about **risk management**, not prediction

### Chip Coordinates

**You MUST configure chip coordinates correctly:**
- Wrong coordinates = wrong chip selected
- Test thoroughly before live use
- Some platforms may require different approach

### Multiple Chips

If bet_amount requires multiple chips:
- Bot will click betting area multiple times
- Example: Bet 10.0 with 1.0 chip = 10 clicks
- Ensure platform supports this

---

## 🧪 Testing

### Test in Colab

The Colab test will show chip selection in logs:
```
Selected chip: 1.0 (x10 = 10.0)
Placing bet: odd - 10.0 (using chip: 1.0 x 10)
```

### Test Locally

1. Run bot in test mode
2. Watch chip selection behavior
3. Verify correct chips are used
4. Check bet amounts match expected

---

## 📝 Configuration Example

Complete example:

```json
{
  "betting": {
    "adaptive_chip_selection": true,
    "chip_sizes": [0.5, 1.0, 2.5, 5.0, 10.0],
    "chip_selection_rules": {
      "entry_streak_6": 1.0,
      "entry_streak_7": 2.5,
      "entry_streak_8": 5.0,
      "entry_streak_9+": 10.0,
      "gale_step_0": 1.0,
      "gale_step_1": 2.5,
      "gale_step_2": 5.0,
      "gale_step_3": 10.0
    },
    "chip_selection_coordinates": {
      "0.5": [1309, 947],
      "1.0": [1310, 947],
      "2.5": [1311, 947],
      "5.0": [1312, 947],
      "10.0": [1313, 947]
    }
  }
}
```

---

##  Recommendations

### For Your Current Setup

With `streak_length: 6`, `max_gales: 3`:

**Recommended chip rules:**
- Entry (streak 6): **1.0 chip** - Conservative start
- Gale step 1: **2.5 chip** - Moderate recovery
- Gale step 2: **5.0 chip** - Aggressive recovery
- Gale step 3: **10.0 chip** - Maximum recovery

This balances:
-  Lower risk on entries
-  Faster recovery in gale
-  Reasonable exposure

---

##  Summary

**Adaptive chip selection is now implemented!**

-  Configurable chip sizes
-  Rules based on streak length and gale step
-  Automatic chip selection
-  Multiple chip placement support

**Next steps:**
1. Find actual chip coordinates for your platform
2. Update `chip_selection_coordinates` in config
3. Test chip selection behavior
4. Adjust rules based on your risk tolerance

**Remember**: This is for **risk management**, not increasing win probability. The house edge remains the same.

