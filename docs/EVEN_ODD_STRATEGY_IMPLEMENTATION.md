# Even/Odd Strategy Implementation Summary

##  Implementation Complete

The Even/Odd counter-sequence strategy has been implemented while keeping the existing Red/Black color-based strategies intact.

## What Was Implemented

### 1. **EvenOddStrategy Class** 
- **Location:** `backend/app/strategy/even_odd_strategy.py`
- **Features:**
  - Streak detection (tracks consecutive Even/Odd outcomes)
  - Entry conditions (only bets when streak length N is reached)
  - Counter-sequence logic (bets against the streak)
  - Gale progression (2x after each loss)
  - Cycle management (no concurrent cycles)
  - Keepalive bet generation (random Even/Odd)
  - Zero handling (configurable: count_as_loss, neutral, reset)

### 2. **Bot Integration** 
- **Updated:** `backend/app/bot.py`
- **Changes:**
  - Added EvenOddStrategy to strategy factory
  - Updated keepalive system (29 minutes for Even/Odd, uses strategy's keepalive method)
  - Added StopWin functionality (by count and money)
  - Enhanced StopLoss (added count-based)
  - Tracks winning/losing rounds for count-based stops

### 3. **Betting Controller** 
- **Updated:** `backend/app/betting/bet_controller.py`
- **Changes:**
  - Added support for 'even' and 'odd' bet types

### 4. **Configuration** 
- **Created:** `config/even_odd_config_example.json`
- **Shows:**
  - Even/Odd strategy configuration
  - Streak length parameter
  - Zero policy setting
  - Keepalive stake
  - StopWin/StopLoss configuration

## Key Features

### Streak Detection
- Tracks consecutive Even outcomes
- Tracks consecutive Odd outcomes
- Resets opposite streak when pattern breaks

### Entry Conditions
- Only bets when streak length N is reached (e.g., 5 consecutive)
- Bets against the streak (counter-sequence)
- Waits for next betting window

### Cycle Management
- Cycle starts: When entry condition met
- Cycle ends: On first win OR max gale reached
- No concurrent cycles: Must finish before starting new one

### Keepalive System
- Every 29 minutes when idle
- Random Even or Odd selection
- Minimal stake (configurable)
- Does not interrupt active cycles

### StopWin & StopLoss
- **StopLoss by money:** Balance threshold
- **StopLoss by count:** Number of losing rounds
- **StopWin by money:** Net PnL threshold
- **StopWin by count:** Number of winning rounds

### Zero Handling
- **count_as_loss:** Treats zero as loss, continues cycle
- **neutral:** Ignores zero for streak counting
- **reset:** Resets streaks and ends cycle

## Configuration Example

```json
{
  "strategy": {
    "type": "even_odd",
    "base_bet": 10.0,
    "max_gales": 5,
    "multiplier": 2.0,
    "streak_length": 5,
    "zero_policy": "count_as_loss",
    "keepalive_stake": 1.0
  },
  "risk": {
    "initial_balance": 1000.0,
    "stop_loss": 500.0,
    "stop_loss_count": null,
    "stop_win": null,
    "stop_win_count": null
  }
}
```

## How to Use

### 1. Update Configuration
Set strategy type to `"even_odd"` in your config file:

```json
{
  "strategy": {
    "type": "even_odd",
    "streak_length": 5,
    ...
  }
}
```

### 2. Add Even/Odd Betting Areas
Add coordinates for Even and Odd betting areas:

```json
{
  "betting": {
    "betting_areas": {
      "even": [x, y],
      "odd": [x, y],
      ...
    }
  }
}
```

### 3. Configure StopWin/StopLoss
Set your stop conditions:

```json
{
  "risk": {
    "stop_loss": 500.0,
    "stop_loss_count": 10,
    "stop_win": 200.0,
    "stop_win_count": 5
  }
}
```

## Strategy Flow

```
1. Monitor outcomes  Track Even/Odd streaks
2. Streak reaches N?  Start cycle, bet against streak
3. Win?  End cycle, reset
4. Loss?  Continue cycle, double bet (gale)
5. Max gale?  End cycle
6. Every 29 min (idle)  Place keepalive bet
7. StopWin/StopLoss?  Stop bot
```

## What's Still Needed

### 1. **Betting Area Coordinates**
- Need to capture Even/Odd betting area coordinates
- Use `capture_betting-numbers.py` or similar tool
- Add to config file

### 2. **Zero Policy Confirmation**
- Confirm with client which zero policy to use
- Options: `count_as_loss`, `neutral`, `reset`

### 3. **Testing**
- Test streak detection
- Test entry conditions
- Test cycle management
- Test keepalive system
- Test StopWin/StopLoss

### 4. **Logging Enhancement**
- Add cycle numbers to logs
- Add streak information
- Add keepalive flags
- Add session summary with all required fields

## Red/Black Strategies Preserved

 All existing Red/Black strategies remain intact:
- `MartingaleStrategy` (Red/Black)
- `FibonacciStrategy` (Red/Black)
- `CustomStrategy` (Red/Black)

You can switch between strategies by changing `"type"` in config:
- `"martingale"`  Red/Black Martingale
- `"even_odd"`  Even/Odd counter-sequence

## Next Steps

1. **Capture Even/Odd betting coordinates**
2. **Test the strategy with video simulation**
3. **Confirm zero policy with client**
4. **Enhance logging with cycle/streak info**
5. **Test StopWin/StopLoss conditions**

