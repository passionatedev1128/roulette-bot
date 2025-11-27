# Strategy Navigation System Guide

##  Overview

The bot now supports **intelligent strategy navigation** - automatically switching between multiple strategies based on performance. This allows the bot to adapt to changing conditions and use the best-performing strategy at any given time.

---

## 🧠 How It Works

### Core Concept

The **StrategyManager** tracks performance of all available strategies and automatically switches to the best-performing one when:
1. A strategy significantly outperforms the current one (15%+ better score)
2. Enough data has been collected (minimum 5 bets per strategy)
3. Evaluation interval is reached (every 10 bets by default)

### Performance Scoring

Each strategy is scored based on:
- **Recent Win Rate** (40% weight) - Last 20 bets
- **Overall Win Rate** (20% weight) - All-time performance
- **Profit per Bet** (30% weight) - Average profit/loss
- **Cycle Win Rate** (10% weight) - How often cycles complete successfully

**Higher score = Better strategy**

---

## ⚙️ Configuration

### Enable Strategy Navigation

In `config/default_config.json`:

```json
{
  "strategy_navigation": {
    "enabled": true,                    // Enable/disable navigation
    "initial_strategy": "even_odd",     // Starting strategy
    "evaluation_interval": 10,           // Evaluate every N bets
    "min_bets_before_switch": 5,        // Minimum bets before switching
    "switch_threshold": 0.15             // 15% performance difference to switch
  }
}
```

### Configure Multiple Strategies

```json
{
  "strategies": {
    "even_odd": {
      "type": "even_odd",
      "base_bet": 10.0,
      "max_gales": 3,
      "multiplier": 2.0,
      "streak_length": 6,
      "zero_policy": "count_as_loss"
    },
    "martingale": {
      "type": "martingale",
      "base_bet": 10.0,
      "max_gales": 5,
      "multiplier": 2.0
    },
    "fibonacci": {
      "type": "fibonacci",
      "base_bet": 10.0,
      "max_gales": 8
    }
  }
}
```

---

## 📊 Strategy Performance Tracking

### Metrics Tracked

For each strategy, the system tracks:
- **Total Bets**: Number of bets placed
- **Wins/Losses**: Win/loss count
- **Win Rate**: Overall and recent (last 20 bets)
- **Profit/Loss**: Total profit and loss amounts
- **Net Profit**: Profit - Loss
- **Profit per Bet**: Average profit per bet
- **Cycles**: Completed cycles, win/loss ratio
- **Score**: Calculated performance score

### Viewing Performance

The bot logs strategy performance and switches. You can also access it programmatically:

```python
# Get current strategy performance
performance = bot.strategy_manager.get_strategy_performance()

# Get all strategies' performance
all_performance = bot.strategy_manager.get_all_performance()
```

---

## 🔄 Strategy Switching Logic

### Automatic Switching

The bot automatically switches strategies when:

1. **Evaluation Interval Reached**: Every N bets (default: 10)
2. **Minimum Data Collected**: At least 5 bets per strategy
3. **Performance Difference**: New strategy is 15%+ better (configurable)

### Switching Example

```
Current Strategy: even_odd
- Score: 0.45
- Recent Win Rate: 48%

Alternative Strategy: martingale
- Score: 0.52 (15.5% better)
- Recent Win Rate: 52%

 Bot switches to martingale
```

### Manual Switching

You can also force a switch:

```python
bot.strategy_manager.force_switch("fibonacci", reason="Manual override")
```

---

##  Available Strategies

### 1. Even/Odd Strategy (Default)

**How it works:**
- Monitors Even/Odd outcomes
- Enters when streak length ≥ 6
- Bets against the streak
- Uses Gale progression

**Best for:**
- Pattern-based betting
- Conservative approach
- Streak detection

### 2. Martingale Strategy

**How it works:**
- Standard Martingale progression
- Doubles bet after each loss
- Resets after win

**Best for:**
- Aggressive recovery
- High balance scenarios
- Quick profit recovery

### 3. Fibonacci Strategy

**How it works:**
- Uses Fibonacci sequence for bet sizing
- 1, 1, 2, 3, 5, 8, 13, 21...
- More gradual progression than Martingale

**Best for:**
- Moderate risk
- Longer cycles
- Balanced approach

---

## 📈 Expected Benefits

### 1. **Adaptive Performance**

- Bot automatically uses best-performing strategy
- Adapts to current variance conditions
- Maximizes opportunities

### 2. **Risk Management**

- Switches away from underperforming strategies
- Reduces exposure during bad periods
- Protects capital better

### 3. **Performance Optimization**

- Always uses optimal strategy
- Better long-term results
- More consistent performance

---

##  Important Notes

### What Strategy Navigation CAN Do:

-  Switch to better-performing strategies
-  Adapt to current conditions
-  Optimize performance
-  Reduce risk during bad periods

### What Strategy Navigation CANNOT Do:

-  Overcome the house edge
-  Guarantee profits
-  Predict future outcomes
-  Change win probability (still ~48.6%)

### Limitations:

1. **Requires Data**: Needs minimum bets before switching
2. **Variance**: Short-term performance may not reflect long-term
3. **Switching Cost**: Frequent switching may reduce consistency
4. **Strategy Compatibility**: All strategies must work with same bet types

---

## 🔧 Configuration Examples

### Conservative Setup

```json
{
  "strategy_navigation": {
    "enabled": true,
    "initial_strategy": "even_odd",
    "evaluation_interval": 20,        // Evaluate less frequently
    "min_bets_before_switch": 10,    // More data required
    "switch_threshold": 0.25          // 25% difference (more conservative)
  }
}
```

### Aggressive Setup

```json
{
  "strategy_navigation": {
    "enabled": true,
    "initial_strategy": "martingale",
    "evaluation_interval": 5,        // Evaluate more frequently
    "min_bets_before_switch": 3,     // Less data required
    "switch_threshold": 0.10          // 10% difference (more aggressive)
  }
}
```

### Balanced Setup (Recommended)

```json
{
  "strategy_navigation": {
    "enabled": true,
    "initial_strategy": "even_odd",
    "evaluation_interval": 10,       // Every 10 bets
    "min_bets_before_switch": 5,     // Minimum 5 bets
    "switch_threshold": 0.15          // 15% difference
  }
}
```

---

## 📊 Monitoring Strategy Performance

### Log Messages

The bot logs strategy switches:

```
INFO: Strategy switched: even_odd -> martingale (Better performance (score: 0.52 vs 0.45))
```

### Performance Reports

You can check strategy performance:

```python
# Get all performance data
all_perf = bot.strategy_manager.get_all_performance()

for name, perf in all_perf.items():
    print(f"{name}:")
    print(f"  Win Rate: {perf['win_rate']:.2f}%")
    print(f"  Recent Win Rate: {perf['recent_win_rate']:.2f}%")
    print(f"  Net Profit: {perf['net_profit']:.2f}")
    print(f"  Score: {perf['score']:.3f}")
    print(f"  Active: {perf['is_active']}")
```

---

## 🚀 Quick Start

### Step 1: Enable Navigation

Set `"enabled": true` in `strategy_navigation` config.

### Step 2: Configure Strategies

Add multiple strategies in `strategies` section.

### Step 3: Run Bot

The bot will:
1. Start with `initial_strategy`
2. Track performance of all strategies
3. Automatically switch when better strategy found
4. Log all switches and performance

### Step 4: Monitor

Watch logs for:
- Strategy switches
- Performance updates
- Score changes

---

##  Best Practices

### 1. **Start Conservative**

- Use higher `switch_threshold` (0.20-0.25)
- Longer `evaluation_interval` (15-20)
- More `min_bets_before_switch` (8-10)

### 2. **Monitor Performance**

- Check strategy performance regularly
- Adjust thresholds based on results
- Don't switch too frequently

### 3. **Strategy Selection**

- Start with strategies you understand
- Test each strategy individually first
- Ensure strategies are compatible

### 4. **Balance**

- Don't switch too often (causes instability)
- Don't switch too rarely (misses opportunities)
- Find the right balance for your risk tolerance

---

##  Summary

**Strategy Navigation** allows your bot to:
- 🧠 **Intelligently switch** between strategies
- 📊 **Track performance** of all strategies
-  **Use best strategy** at any time
- 🛡️ **Reduce risk** during bad periods
- 📈 **Optimize performance** automatically

**Remember**: This is an **optimization tool**, not a magic solution. The house edge remains, but strategy navigation helps you:
- Use the best strategy for current conditions
- Adapt to variance
- Maximize opportunities
- Protect capital better

**Enable it and let the bot navigate to better performance!** 🚀

