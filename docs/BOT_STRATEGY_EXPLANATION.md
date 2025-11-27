# Bot Strategy Explanation

## Overview

The bot uses a **color-based betting strategy** with **Martingale (Gale) progression**. It bets on Red or Black based on the last result, and doubles the bet after each loss.

---

## Current Strategy: Martingale with Opposite Color

### How It Works

**Basic Logic:**
1. **Detects winning number** from roulette result
2. **Determines color** (Red, Black, or Green/Zero)
3. **Bets on opposite color** of last result
4. **Doubles bet** after each loss (Gale/Martingale)
5. **Resets to base bet** after win

### Example Flow

```
Round 1: Result = 17 (Black)  Bot bets Red with R$ 10.00
Round 2: Result = 5 (Red)  Bot WINS!  Reset to base bet
Round 3: Result = 20 (Black)  Bot bets Red with R$ 10.00
Round 4: Result = 14 (Red)  Bot LOSES  Next bet: R$ 20.00 (double)
Round 5: Result = 8 (Black)  Bot bets Red with R$ 20.00
Round 6: Result = 12 (Red)  Bot LOSES  Next bet: R$ 40.00 (double)
Round 7: Result = 3 (Red)  Bot LOSES  Next bet: R$ 80.00 (double)
Round 8: Result = 19 (Red)  Bot LOSES  Next bet: R$ 160.00 (double)
Round 9: Result = 2 (Black)  Bot WINS!  Reset to base bet R$ 10.00
```

---

## Strategy Components

### 1. Color Selection: "Opposite" Pattern

**Current setting:** `"bet_color_pattern": "opposite"`

**How it works:**
- If last result was **Red**  Bet **Black**
- If last result was **Black**  Bet **Red**
- If last result was **Green/Zero**  Bet **Red** (default)

**Other options:**
- `"same"` - Bet same color as last result
- `"custom"` - Use custom pattern logic

### 2. Bet Amount: Martingale Progression

**Formula:** `Bet = Base Bet × (Multiplier ^ Gale Step)`

**Example with Base Bet = R$ 10.00, Multiplier = 2.0:**

| Loss Count | Gale Step | Bet Amount | Total Lost So Far |
|------------|-----------|------------|------------------|
| 0 (Win)    | 0         | R$ 10.00   | R$ 0.00          |
| 1          | 1         | R$ 20.00   | R$ 10.00         |
| 2          | 2         | R$ 40.00   | R$ 30.00         |
| 3          | 3         | R$ 80.00   | R$ 70.00         |
| 4          | 4         | R$ 160.00  | R$ 150.00        |
| 5          | 5         | R$ 320.00  | R$ 310.00        |

**After win:** Resets to base bet (R$ 10.00)

### 3. Maximum Gales (Loss Limit)

**Current setting:** `"max_gales": 5`

**What it means:**
- Bot will double bet up to 5 times after losses
- After 5 losses, stops betting (reaches max gale)
- Protects against excessive losses

**Example:**
- Base bet: R$ 10.00
- Max gales: 5
- Maximum bet: R$ 320.00 (after 5 losses)
- If 6th loss would occur  Bot stops (max gale reached)

### 4. Zero (Green) Handling

**Current setting:**
```json
"zero_handling": {
  "rule": "continue_sequence",
  "reset_on_zero": false
}
```

**Options:**

**A. Continue Sequence (Current)**
- Treats zero as a loss
- Continues gale progression
- Doubles bet after zero

**B. Reset**
- Resets to base bet when zero appears
- Stops gale progression

**C. Skip**
- Skips bet when zero appears
- Doesn't change gale step

---

## Risk Management

### 1. Stop Loss

**Current setting:** `"stop_loss": 500.0`

**What it does:**
- Bot stops if balance drops to R$ 500.00
- Prevents total loss
- Protects your capital

### 2. Guarantee Fund

**Current setting:** `"guarantee_fund_percentage": 20`

**What it does:**
- Reserves 20% of balance for gale bets
- Ensures you can complete gale sequence
- Example: Balance R$ 1000  Reserve R$ 200 for gales

**Calculation:**
```
Total Balance: R$ 1000.00
Guarantee Fund: 20% = R$ 200.00
Available for Strategy: R$ 800.00
```

### 3. Initial Balance

**Current setting:** `"initial_balance": 1000.0`

**What it does:**
- Starting balance for calculations
- Used for risk management
- Should match your actual game balance

---

## Session Management

### Maintenance Bets

**Current setting:** `"maintenance_bet_interval": 1800` (30 minutes)

**What it does:**
- Places small bet every 30 minutes
- Prevents game from pausing/disconnecting
- Keeps session active 24/7

**Minimum bet:** `"min_bet_amount": 1.0` (R$ 1.00)

---

## Strategy Configuration

### Current Config

```json
{
  "strategy": {
    "type": "martingale",
    "base_bet": 10.0,                // Starting bet amount
    "max_gales": 5,                  // Maximum loss doubling steps
    "multiplier": 2.0,               // Bet multiplier after loss
    "bet_color_pattern": "opposite", // Bet opposite of last result
    "zero_handling": {
      "rule": "continue_sequence",   // Treat zero as loss
      "reset_on_zero": false
    }
  }
}
```

---

## Available Strategies

### 1. Martingale (Current)

**Best for:** Quick recovery from losses

**Pros:**
- Fast recovery (one win recovers all losses)
- Simple logic
- Works well for short sessions

**Cons:**
- Requires large balance for long losing streaks
- Can lose everything if max gale reached

**When to use:**
- You have sufficient balance
- You want quick recovery
- Short betting sessions

---

### 2. Fibonacci

**How it works:**
- Uses Fibonacci sequence: 1, 1, 2, 3, 5, 8, 13, 21...
- More conservative than Martingale
- Slower progression

**Example:**
- Base: R$ 10.00
- Loss 1: R$ 10.00
- Loss 2: R$ 10.00
- Loss 3: R$ 20.00
- Loss 4: R$ 30.00
- Loss 5: R$ 50.00

**Best for:** Conservative betting, longer sessions

---

### 3. Custom Sequence

**How it works:**
- You define exact bet amounts for each loss
- Full control over progression
- Can be safer than Martingale

**Example:**
```json
"custom_sequence": [10, 20, 40, 80, 160]
```

**Best for:** Specific risk tolerance, custom progression

---

## Strategy Logic Flow

```
1. Bot detects winning number
   ↓
2. Determines color (Red/Black/Green)
   ↓
3. Updates strategy history
   ↓
4. Checks if should bet (entry conditions)
   ↓
5. If yes:
   - Determines bet color (opposite of last)
   - Calculates bet amount (based on gale step)
   - Checks risk limits (balance, max gale)
   - Places bet
   ↓
6. Waits for result
   ↓
7. Updates strategy:
   - If WIN  Reset to base bet
   - If LOSS  Increase gale step (double bet)
   - If ZERO  Follow zero handling rule
   ↓
8. Repeat
```

---

## Entry Conditions

**Currently:** Bot bets on EVERY round (opposite color)

**Future options (can be added):**
- Bet after N consecutive same color
- Bet after specific pattern (R-B-R-B)
- Bet based on color frequency
- Bet only when certain conditions met

---

## Example Scenarios

### Scenario 1: Winning Streak

```
Result: Black  Bet Red R$ 10  WIN  Reset
Result: Red  Bet Black R$ 10  WIN  Reset
Result: Black  Bet Red R$ 10  WIN  Reset
```

**Profit:** +R$ 30.00 (3 wins)

---

### Scenario 2: Losing Streak (Then Win)

```
Result: Black  Bet Red R$ 10  LOSS  Next: R$ 20
Result: Red  Bet Black R$ 20  LOSS  Next: R$ 40
Result: Black  Bet Red R$ 40  LOSS  Next: R$ 80
Result: Red  Bet Black R$ 80  WIN  Reset
```

**Losses:** R$ 10 + R$ 20 + R$ 40 = R$ 70.00
**Win:** R$ 80.00
**Net:** +R$ 10.00 (recovered all losses + profit)

---

### Scenario 3: Max Gale Reached

```
Result: Black  Bet Red R$ 10  LOSS  Next: R$ 20
Result: Red  Bet Black R$ 20  LOSS  Next: R$ 40
Result: Black  Bet Red R$ 40  LOSS  Next: R$ 80
Result: Red  Bet Black R$ 80  LOSS  Next: R$ 160
Result: Black  Bet Red R$ 160  LOSS  Next: R$ 320
Result: Red  Bet Black R$ 320  LOSS  STOP (max gale reached)
```

**Total Loss:** R$ 630.00
**Bot stops** (max gale = 5 reached)

---

## Recommendations

### For Testing

```json
{
  "base_bet": 1.0,      // Minimum bet
  "max_gales": 3,       // Conservative limit
  "multiplier": 2.0,    // Standard doubling
  "stop_loss": 50.0     // Safe limit
}
```

### For Production

```json
{
  "base_bet": 10.0,     // Your comfortable starting bet
  "max_gales": 5,       // Reasonable limit
  "multiplier": 2.0,    // Standard doubling
  "stop_loss": 500.0    // 50% of balance
}
```

---

## Important Notes

###  Risk Warning

- **Martingale can lose everything** if max gale reached
- **Always set stop_loss** to protect capital
- **Use guarantee fund** to ensure gale completion
- **Start with small base_bet** for testing

###  Best Practices

1. **Start small:** Test with minimum bets first
2. **Set limits:** Use stop_loss and max_gales
3. **Monitor closely:** Watch first few hours
4. **Adjust as needed:** Change settings based on results

---

## Summary

**Current Strategy:**
- **Type:** Martingale (Gale)
- **Color:** Opposite of last result
- **Progression:** Double after each loss
- **Reset:** After win
- **Zero:** Continue sequence (treat as loss)
- **Max Gales:** 5 steps
- **Risk:** Stop loss at 50% balance

**This is a simple, effective strategy for color-based roulette betting!**

