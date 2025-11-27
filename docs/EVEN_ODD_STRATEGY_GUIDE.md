# Even/Odd Counter-Sequence Strategy Guide

## Overview

The Even/Odd strategy is a **counter-sequence betting system** that bets against streaks of consecutive Even or Odd outcomes. It only enters when a streak reaches a specified length (default: 5), then applies Gale (Martingale) progression on losses.

---

## Core Concept

**Philosophy**: Long streaks of the same outcome (Even or Odd) are statistically unlikely to continue. The strategy bets **against** the streak, expecting it to break.

**Key Principle**: Wait for confirmation (streak of N), then bet the opposite with progressive betting on losses.

---

## How It Works

### 1. Streak Detection

The bot continuously monitors roulette outcomes and tracks:

- **Even streak**: Consecutive Even numbers (2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36)
- **Odd streak**: Consecutive Odd numbers (1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35)

**Streak Rules**:
- When an Even number appears, Even streak increases, Odd streak resets to 0
- When an Odd number appears, Odd streak increases, Even streak resets to 0
- Zero (0) is handled according to `zero_policy` setting

### 2. Entry Condition

**Trigger**: When streak length reaches the configured threshold (default: 5)

**Entry Logic**:
-  **5 consecutive Even**  Bet **Odd**
-  **5 consecutive Odd**  Bet **Even**
-  **No entry** if already in an active cycle
-  **No entry** if streak < 5

### 3. Betting Cycle

Once entry condition is met, a **cycle** begins:

1. **Initial Bet**: Base bet amount (e.g., 10.0)
2. **On Win**: Cycle ends, reset, wait for next entry
3. **On Loss**: Continue cycle, double bet (Gale progression)
4. **Max Gale**: After 5 losses, cycle ends automatically

### 4. Gale (Martingale) Progression

Bet amounts increase exponentially after each loss:

```
Gale Step 0: base_bet × (multiplier ^ 0) = 10.0 × 1 = 10.0
Gale Step 1: base_bet × (multiplier ^ 1) = 10.0 × 2 = 20.0
Gale Step 2: base_bet × (multiplier ^ 2) = 10.0 × 4 = 40.0
Gale Step 3: base_bet × (multiplier ^ 3) = 10.0 × 8 = 80.0
Gale Step 4: base_bet × (multiplier ^ 4) = 10.0 × 16 = 160.0
Gale Step 5: Max reached  Cycle ends
```

**Total Risk**: 10 + 20 + 40 + 80 + 160 = **310.0** (if all 5 steps lose)

---

## Configuration Parameters

### Strategy Settings

```json
{
  "strategy": {
    "type": "even_odd",
    "base_bet": 10.0,           // Starting bet amount
    "max_gales": 5,              // Maximum gale steps (0-5)
    "multiplier": 2.0,           // Bet multiplier after loss
    "streak_length": 5,          // Streak length to trigger entry
    "zero_policy": "count_as_loss", // How to handle zero
    "keepalive_stake": 1.0       // Minimum bet for keepalive
  }
}
```

### Parameter Descriptions

| Parameter | Default | Description |
|-----------|---------|-------------|
| `base_bet` | 10.0 | Initial bet amount when cycle starts |
| `max_gales` | 5 | Maximum number of losses before cycle ends |
| `multiplier` | 2.0 | Multiplier for Gale progression (2.0 = double) |
| `streak_length` | 5 | Number of consecutive outcomes needed to enter |
| `zero_policy` | "count_as_loss" | How to handle zero (0) outcome |
| `keepalive_stake` | 1.0 | Minimum bet for session keepalive |

---

## Zero Policy Options

### 1. `"count_as_loss"` (Default)

- **Zero = Loss**: Treated as a losing bet
- **Cycle continues**: Gale progression continues
- **Streaks**: Not updated (zero is neither even nor odd)
- **Use case**: Conservative approach, protects against zero

**Example**:
```
Cycle active, bet Odd 10.0
Result: 0 (zero)
 Counted as loss
 Next bet: Odd 20.0 (Gale step 1)
```

### 2. `"neutral"`

- **Zero = Ignored**: Doesn't affect cycle or streaks
- **Cycle**: Continues unchanged
- **Streaks**: Remain unchanged
- **Use case**: Zero doesn't break patterns

**Example**:
```
Cycle active, bet Odd 10.0
Result: 0 (zero)
 Ignored
 Next bet: Still Odd 10.0 (same gale step)
```

### 3. `"reset"`

- **Zero = Reset**: Resets streaks and ends cycle
- **Cycle**: Ends immediately
- **Streaks**: Reset to 0
- **Use case**: Zero breaks all patterns

**Example**:
```
Cycle active, bet Odd 10.0
Result: 0 (zero)
 Cycle ends
 Streaks reset
 Wait for new entry condition
```

---

## Keepalive System

### Purpose

Prevents game session from pausing or disconnecting by placing minimum bets when idle.

### Behavior

- **Interval**: Every 29 minutes (1800 seconds)
- **Condition**: Only when **no active cycle**
- **Bet Type**: Random Even or Odd
- **Amount**: `keepalive_stake` (default: 1.0)
- **Skip**: If cycle is active (strategy bets are sufficient)

### Example

```
Time 00:00 - Cycle ends, no entry condition
Time 00:29 - Keepalive: Bet Even 1.0
Time 00:58 - Keepalive: Bet Odd 1.0
Time 01:27 - Keepalive: Bet Even 1.0
...
Time 05:00 - Entry condition met  Cycle starts
Time 05:29 - Keepalive skipped (cycle active)
```

---

## Complete Example Scenario

### Scenario: Even Streak Triggers Entry

```
Initial State:
- Even streak: 0
- Odd streak: 0
- Cycle: Inactive
- Balance: 1000.0

Spin 1: 2 (even)
 Even streak: 1, Odd streak: 0
 No bet (streak < 5)

Spin 2: 4 (even)
 Even streak: 2, Odd streak: 0
 No bet (streak < 5)

Spin 3: 6 (even)
 Even streak: 3, Odd streak: 0
 No bet (streak < 5)

Spin 4: 8 (even)
 Even streak: 4, Odd streak: 0
 No bet (streak < 5)

Spin 5: 10 (even)
 Even streak: 5, Odd streak: 0
  ENTRY CONDITION MET!
 Start Cycle 1
 Bet: ODD 10.0
 Balance: 990.0 (after bet)

Spin 6: 12 (even)
 Result: LOSS (bet Odd, got Even)
 Even streak: 6, Odd streak: 0
 Cycle continues
 Gale step: 1
 Bet: ODD 20.0
 Balance: 970.0 (after bet)

Spin 7: 14 (even)
 Result: LOSS (bet Odd, got Even)
 Even streak: 7, Odd streak: 0
 Cycle continues
 Gale step: 2
 Bet: ODD 40.0
 Balance: 930.0 (after bet)

Spin 8: 15 (odd)
 Result: WIN! (bet Odd, got Odd)
 Even streak: 0, Odd streak: 1
  Cycle ends successfully
 Profit: -10 - 20 - 40 + 80 = +10.0
 Balance: 1010.0
 Wait for next entry condition
```

### Scenario: Max Gale Reached

```
Cycle 1 starts: Bet ODD 10.0
Loss 1: Bet ODD 20.0
Loss 2: Bet ODD 40.0
Loss 3: Bet ODD 80.0
Loss 4: Bet ODD 160.0
Loss 5: Max gale reached
 Cycle ends (max gale limit)
 Total loss: 310.0
 Wait for next entry condition
```

---

## Cycle Management

### Cycle Lifecycle

1. **Start**: Entry condition met (streak ≥ N)
2. **Active**: Placing bets, tracking wins/losses
3. **End**: Win OR max gale reached
4. **Reset**: Wait for next entry condition

### Rules

-  **One cycle at a time**: No concurrent cycles
-  **Must finish**: Previous cycle must end before new one starts
-  **Independent**: Each cycle is independent (new cycle number)

### Cycle States

```
IDLE  [Entry Condition]  ACTIVE  [Win/Max Gale]  IDLE
  ↑                                                      ↓
  └────────────────── Keepalive (if idle) ─────────────┘
```

---

## Risk Management

### Stop Loss

Configured in `risk.stop_loss`:

```json
{
  "risk": {
    "stop_loss": 500.0  // Stop if balance drops below this
  }
}
```

**Example**:
- Initial balance: 1000.0
- Stop loss: 500.0
- Bot stops when balance ≤ 500.0

### Guarantee Fund

Reserves a percentage of balance for Gale progression:

```json
{
  "risk": {
    "guarantee_fund_percentage": 20  // Reserve 20% for gale
  }
}
```

**Example**:
- Balance: 1000.0
- Guarantee fund: 200.0 (20%)
- Available for strategy: 800.0

### Max Gale Limit

Prevents unlimited losses:

```json
{
  "strategy": {
    "max_gales": 5  // Maximum 5 losses per cycle
  }
}
```

**Protection**: Even if all 5 bets lose, cycle ends automatically.

---

## Strategy Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    MONITOR OUTCOMES                      │
│         Track Even/Odd streaks continuously              │
└────────────────────┬──────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Streak ≥ 5?         │
         └───┬───────────┬──────┘
             │           │
         YES │           │ NO
             │           │
             ▼           ▼
    ┌──────────────┐  ┌──────────────┐
    │ START CYCLE  │  │  NO BET      │
    │ Bet Opposite │  │  (Wait)      │
    └──────┬───────┘  └──────────────┘
           │
           ▼
    ┌──────────────┐
    │  PLACE BET   │
    │  (Base bet)  │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │   RESULT?    │
    └───┬──────┬───┘
        │      │
    WIN │      │ LOSS
        │      │
        ▼      ▼
   ┌──────┐  ┌──────────────┐
   │ END  │  │ GALE STEP   │
   │ CYCLE│  │ Double Bet   │
   └──────┘  └──────┬───────┘
                    │
                    ▼
            ┌──────────────┐
            │ Max Gale?    │
            └───┬──────┬───┘
                │      │
            YES │      │ NO
                │      │
                ▼      ▼
           ┌──────┐  ┌──────────┐
           │ END  │  │ CONTINUE │
           │ CYCLE│  │ (Repeat) │
           └──────┘  └──────────┘
```

---

## Betting Areas Configuration

Even/Odd betting areas must be configured:

```json
{
  "betting": {
    "betting_areas": {
      "even": [907, 905],   // Even betting area coordinates
      "odd": [1111, 906]    // Odd betting area coordinates
    }
  }
}
```

**Coordinates**: `[x, y]` screen pixel coordinates where the bot clicks to place bets.

---

## Testing the Strategy

### 1. Video Simulation

Test with recorded video:

```powershell
python simulate_strategy.py roleta_brazileria.mp4 --config config/default_config.json --max-spins 50
```

### 2. Live Test Mode

Test with live casino (no real bets):

```powershell
python backend/app/bot.py --test --config config/default_config.json
```

### 3. Monitor Logs

Check `logs/` directory for:
- Bet decisions
- Cycle progression
- Streak tracking
- Win/loss outcomes

---

## Adjusting Parameters

### More Aggressive (Higher Risk)

```json
{
  "streak_length": 3,        // Enter earlier (3 instead of 5)
  "base_bet": 20.0,          // Higher base bet
  "max_gales": 6             // More gale steps
}
```

### More Conservative (Lower Risk)

```json
{
  "streak_length": 7,        // Enter later (7 instead of 5)
  "base_bet": 5.0,           // Lower base bet
  "max_gales": 3             // Fewer gale steps
}
```

### Faster Recovery

```json
{
  "multiplier": 2.5          // Faster bet increase (2.5x instead of 2x)
}
```

### Slower Recovery

```json
{
  "multiplier": 1.5          // Slower bet increase (1.5x instead of 2x)
}
```

---

## Common Questions

### Q: Why wait for 5 consecutive?

**A**: Reduces false signals. Shorter streaks (2-3) are common and can lead to many losing cycles. Waiting for 5 provides better confirmation.

### Q: What if streak continues beyond 5?

**A**: The bot continues betting against it with Gale progression. If it wins at any point, cycle ends profitably.

### Q: Can I change streak_length?

**A**: Yes! Lower (3-4) = more entries, higher risk. Higher (6-7) = fewer entries, lower risk.

### Q: What happens if I get multiple streaks?

**A**: Only one cycle at a time. Must finish current cycle before starting new one.

### Q: How does keepalive work?

**A**: Every 29 minutes when idle, places random Even/Odd bet with minimum stake (1.0) to prevent session timeout.

---

## Making the Strategy Successful

This section provides practical recommendations, optimizations, and best practices to maximize the strategy's effectiveness and minimize risks.

### 1. Optimal Parameter Configuration

#### Conservative Approach (Recommended for Beginners)

```json
{
  "strategy": {
    "type": "even_odd",
    "base_bet": 5.0,              // Lower base bet
    "max_gales": 4,                // Fewer gale steps (safer)
    "multiplier": 2.0,
    "streak_length": 6,            // Higher threshold (fewer entries)
    "zero_policy": "count_as_loss",
    "keepalive_stake": 1.0
  },
  "risk": {
    "initial_balance": 1000.0,
    "stop_loss": 600.0,            // Stop at 40% loss
    "stop_loss_count": 3,          // Stop after 3 losing cycles
    "stop_win": 150.0,              // Lock in profits early
    "stop_win_count": 5             // Stop after 5 winning cycles
  }
}
```

**Why this works**:
- Lower base bet = smaller risk per cycle (max: 75.0 vs 310.0)
- Higher streak_length = fewer false signals
- Multiple stop conditions = better risk control

#### Balanced Approach (Recommended)

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
    "stop_loss_count": 4,
    "stop_win": 200.0,
    "stop_win_count": 6
  }
}
```

#### Aggressive Approach (Higher Risk/Reward)

```json
{
  "strategy": {
    "type": "even_odd",
    "base_bet": 15.0,
    "max_gales": 6,
    "multiplier": 2.0,
    "streak_length": 4,             // Lower threshold (more entries)
    "zero_policy": "count_as_loss",
    "keepalive_stake": 1.0
  },
  "risk": {
    "initial_balance": 2000.0,      // Larger bankroll needed
    "stop_loss": 1000.0,
    "stop_loss_count": 5,
    "stop_win": 300.0,
    "stop_win_count": 8
  }
}
```

### 2. Bankroll Management

#### Rule of Thumb: 10x Rule

**Minimum bankroll** should be at least **10x** your maximum cycle risk:

```
Max cycle risk = base_bet × (multiplier^max_gales - 1) / (multiplier - 1)
Example: 10 × (2^5 - 1) / (2 - 1) = 10 × 31 = 310.0
Minimum bankroll: 310 × 10 = 3,100.0
```

#### Bankroll Allocation

```
Total Bankroll: 1000.0
├── Guarantee Fund (20%): 200.0    // Reserved for gale progression
├── Active Strategy (60%): 600.0   // Available for betting
└── Safety Buffer (20%): 200.0     // Emergency reserve
```

#### Progressive Bankroll Management

1. **Start Small**: Begin with minimum viable bankroll
2. **Scale Gradually**: Increase base_bet only after consistent profits
3. **Withdraw Profits**: Regularly withdraw 50% of profits
4. **Never Re-invest All**: Keep some profits separate

### 3. Risk Management Best Practices

#### Multi-Layer Stop Loss

```json
{
  "risk": {
    "stop_loss": 500.0,             // Hard stop: absolute loss limit
    "stop_loss_count": 3,           // Soft stop: consecutive losing cycles
    "stop_loss_percentage": 50,     // Percentage-based stop (optional)
    "daily_loss_limit": 200.0       // Daily loss cap (optional)
  }
}
```

#### Profit Protection

```json
{
  "risk": {
    "stop_win": 200.0,               // Lock in profits
    "stop_win_count": 5,            // Stop after X winning cycles
    "trailing_stop": true,          // Lock in profits as they grow
    "trailing_percentage": 30       // Lock 30% of peak profit
  }
}
```

#### Session Limits

- **Time Limits**: Maximum 2-4 hours per session
- **Cycle Limits**: Maximum 10-15 cycles per session
- **Win Limits**: Stop after reaching daily profit target

### 4. Testing and Validation

#### Pre-Production Testing Checklist

1. **Video Simulation** (100+ spins)
   ```powershell
   python simulate_strategy.py video.mp4 --max-spins 100
   ```
   - Verify detection accuracy >95%
   - Check strategy logic works correctly
   - Analyze win rate and profit/loss

2. **Paper Trading** (Live test mode)
   ```powershell
   python backend/app/bot.py --test --config config/default_config.json
   ```
   - Test with real game (no actual bets)
   - Verify coordinates are correct
   - Check timing and delays

3. **Small Stakes Testing** (1-2 weeks)
   - Start with minimum base_bet
   - Monitor for 1-2 weeks
   - Track all metrics

4. **Gradual Scaling**
   - Week 1: base_bet 5.0
   - Week 2: base_bet 7.5 (if profitable)
   - Week 3: base_bet 10.0 (if still profitable)

#### Key Metrics to Track

```
Daily Metrics:
- Total cycles: X
- Winning cycles: Y (Win rate: Y/X %)
- Average profit per cycle: $Z
- Maximum drawdown: $W
- Largest winning streak: A cycles
- Largest losing streak: B cycles

Performance Metrics:
- Profit Factor: (Total Wins / Total Losses)
- Risk/Reward Ratio: (Avg Win / Avg Loss)
- Sharpe Ratio: (Return / Volatility)
```

### 5. Advanced Optimization Techniques

#### Dynamic Streak Length

Adjust `streak_length` based on recent performance:

```python
# Pseudo-code concept
if win_rate > 60%:
    streak_length = 4  # More aggressive
elif win_rate < 40%:
    streak_length = 6  # More conservative
else:
    streak_length = 5  # Default
```

#### Adaptive Base Bet

Scale base bet based on bankroll growth:

```json
{
  "strategy": {
    "base_bet_percentage": 1.0,    // 1% of current balance
    "min_base_bet": 5.0,
    "max_base_bet": 20.0
  }
}
```

#### Zero Policy Selection

Choose zero policy based on table conditions:

- **High zero frequency**: Use `"neutral"` (ignore zeros)
- **Low zero frequency**: Use `"count_as_loss"` (default)
- **Very conservative**: Use `"reset"` (reset on zero)

#### Time-Based Adjustments

```json
{
  "strategy": {
    "time_based_adjustments": {
      "peak_hours": {
        "streak_length": 6,        // More conservative during busy times
        "base_bet_multiplier": 0.8
      },
      "off_peak_hours": {
        "streak_length": 5,        // Normal during quiet times
        "base_bet_multiplier": 1.0
      }
    }
  }
}
```

### 6. Monitoring and Alerts

#### Real-Time Monitoring

Set up alerts for:

1. **Critical Events**:
   - Stop loss triggered
   - Max gale reached
   - Detection failures
   - Balance drops below threshold

2. **Performance Alerts**:
   - Win rate drops below 40%
   - 3+ consecutive losing cycles
   - Unusual patterns detected

3. **System Alerts**:
   - Bot disconnection
   - Game session paused
   - Network issues

#### Log Analysis

Regularly review logs for:

```bash
# Check recent performance
grep "Cycle.*ended" logs/roulette_log_*.log | tail -20

# Check win rate
grep "WIN\|LOSS" logs/roulette_log_*.log | awk '{print $1}' | sort | uniq -c

# Check detection accuracy
grep "Detected:" logs/roulette_log_*.log | wc -l
```

### 7. Common Pitfalls to Avoid

####  Don't Do This

1. **Chasing Losses**
   - Don't increase base_bet after losses
   - Don't reduce streak_length to enter more
   - Stick to your plan

2. **Ignoring Stop Losses**
   - Never disable stop loss
   - Never increase limits after losses
   - Respect your risk management

3. **Over-Trading**
   - Don't reduce streak_length too much (enters too often)
   - Don't increase max_gales too high (higher risk)
   - Quality over quantity

4. **Emotional Decisions**
   - Don't manually override bot decisions
   - Don't change parameters mid-session
   - Trust the system

5. **Insufficient Testing**
   - Don't go live without testing
   - Don't skip simulation phase
   - Test thoroughly first

####  Do This Instead

1. **Stick to Plan**
   - Follow your configuration
   - Trust the strategy logic
   - Review and adjust only between sessions

2. **Regular Reviews**
   - Weekly performance analysis
   - Monthly parameter optimization
   - Quarterly strategy review

3. **Continuous Learning**
   - Track what works
   - Learn from losses
   - Adapt gradually

4. **Risk First**
   - Protect capital first
   - Profits second
   - Never risk more than you can afford

### 8. Success Checklist

Before going live, ensure:

- [ ] Video simulation tested (100+ spins)
- [ ] Live test mode verified (coordinates correct)
- [ ] Bankroll is 10x max cycle risk
- [ ] Stop loss configured (multiple layers)
- [ ] Stop win configured
- [ ] Logging enabled and monitored
- [ ] Alerts configured
- [ ] Backup plan ready
- [ ] Small stakes testing completed (1-2 weeks)
- [ ] Performance metrics baseline established

### 9. Performance Optimization Tips

#### Maximize Win Rate

1. **Higher Streak Length**: Reduces false signals
   - streak_length: 6-7 = fewer but better entries

2. **Better Entry Timing**: Wait for confirmation
   - Don't enter on partial streaks
   - Wait for full streak confirmation

3. **Table Selection**: Choose tables with:
   - Lower minimum bets
   - Higher maximum bets (for gale room)
   - Stable connection
   - Clear number display

#### Minimize Losses

1. **Conservative Gale**: Lower max_gales
   - max_gales: 4 instead of 5
   - Reduces max cycle risk by 50%

2. **Faster Exits**: Lower stop loss
   - stop_loss: 40% instead of 50%
   - Preserves more capital

3. **Zero Handling**: Choose appropriate policy
   - "neutral" if zeros are frequent
   - "count_as_loss" if zeros are rare

#### Optimize Bankroll Usage

1. **Base Bet Sizing**: 1-2% of bankroll
   - 1000 bankroll  base_bet: 10-20

2. **Guarantee Fund**: 20-30% reserved
   - Ensures gale progression can complete

3. **Profit Withdrawal**: Regular withdrawals
   - Withdraw 50% of profits weekly
   - Protects gains

### 10. Long-Term Success Strategy

#### Phase 1: Foundation (Weeks 1-4)
- Small stakes (base_bet: 5.0)
- Conservative parameters
- Focus on learning and data collection
- Build baseline metrics

#### Phase 2: Optimization (Weeks 5-8)
- Analyze performance data
- Optimize parameters
- Gradually increase stakes
- Refine risk management

#### Phase 3: Scaling (Weeks 9+)
- Increase base_bet if profitable
- Maintain strict risk controls
- Regular profit withdrawals
- Continuous monitoring

#### Success Indicators

 **Good Signs**:
- Win rate > 50%
- Profit factor > 1.2
- Consistent small profits
- Low drawdowns
- Stable performance

 **Warning Signs**:
- Win rate < 40%
- Large drawdowns
- Inconsistent results
- Multiple max gale hits
- Declining performance

### 11. Recommended Configuration Templates

#### Template 1: Ultra-Conservative

```json
{
  "strategy": {
    "type": "even_odd",
    "base_bet": 3.0,
    "max_gales": 3,
    "multiplier": 2.0,
    "streak_length": 7,
    "zero_policy": "neutral",
    "keepalive_stake": 1.0
  },
  "risk": {
    "initial_balance": 1000.0,
    "stop_loss": 700.0,
    "stop_loss_count": 2,
    "stop_win": 100.0,
    "stop_win_count": 3
  }
}
```
**Max cycle risk**: 21.0 | **Best for**: Beginners, small bankrolls

#### Template 2: Balanced (Recommended)

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
    "stop_loss_count": 4,
    "stop_win": 200.0,
    "stop_win_count": 6
  }
}
```
**Max cycle risk**: 310.0 | **Best for**: Most users

#### Template 3: Aggressive

```json
{
  "strategy": {
    "type": "even_odd",
    "base_bet": 20.0,
    "max_gales": 6,
    "multiplier": 2.0,
    "streak_length": 4,
    "zero_policy": "count_as_loss",
    "keepalive_stake": 1.0
  },
  "risk": {
    "initial_balance": 3000.0,
    "stop_loss": 1500.0,
    "stop_loss_count": 5,
    "stop_win": 500.0,
    "stop_win_count": 8
  }
}
```
**Max cycle risk**: 1260.0 | **Best for**: Experienced users, large bankrolls

---

## Summary

 **Wait** for streak of 5 consecutive Even or Odd  
 **Bet** the opposite (counter-sequence)  
 **Double** on loss (Gale progression)  
 **Stop** on win or max gale  
 **Keepalive** every 29 minutes when idle  

**Philosophy**: Bet against streaks, expecting them to break with progressive recovery on losses.

---

## Files Reference

- **Strategy Implementation**: `backend/app/strategy/even_odd_strategy.py`
- **Configuration**: `config/default_config.json`
- **Betting Controller**: `backend/app/betting/bet_controller.py`
- **Simulation Script**: `simulate_strategy.py`
- **Testing Guide**: `STRATEGY_TESTING_GUIDE.md`

---

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review console output for errors
3. Verify configuration syntax
4. Test with video simulation first

