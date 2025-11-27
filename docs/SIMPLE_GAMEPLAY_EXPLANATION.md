# Simple Roulette Gameplay - Even Simpler!

## The Simplest Explanation

**Roulette = Guess which color wins (Red or Black)**

That's it! You don't need to know anything else for the bot.

---

## What Happens in a Game

### Step 1: Ball Spins
- Wheel spins
- Ball bounces around
- Eventually stops on a number

### Step 2: Result Shows
- Number appears (e.g., 17)
- Color is shown (e.g., Black)
- You see if you won or lost

### Step 3: You Bet (or Bot Does)
- Choose Red or Black
- Place your bet
- Wait for next spin

### Step 4: Win or Lose
- If you bet the right color  Win money
- If you bet wrong color  Lose money

---

## What the Bot Does

**The bot:**
1. **Sees the result** (what color won)
2. **Decides what to bet** (Red or Black)
3. **Clicks the buttons** (places bet)
4. **Repeats** (does it again and again)

**You don't need to do anything!**

---

## What You Need to Tell the Bot

**Just 3 things:**

1. **Where is Red button?**
   - Look for "Vermelho" area on screen
   - Tell bot where it is (coordinates)

2. **Where is Black button?**
   - Look for "Preto" area on screen
   - Tell bot where it is (coordinates)

3. **Where does result appear?**
   - Where the winning number shows
   - Tell bot where to look (for detection)

**That's all!**

---

## Visual Simplification

```
Game Screen:
┌─────────────────────┐
│  [Wheel Spinning]   │
│  Result: 17 (Black) │ ← Bot reads this
└─────────────────────┘
         ↓
    Bot decides:
    "I'll bet Red"
         ↓
┌─────────────────────┐
│  [Vermelho] [Preto] │
│       ↑              │
│  Bot clicks here     │
└─────────────────────┘
         ↓
    Next spin...
    Result: 3 (Red)
         ↓
    Bot wins! 
```

---

## Don't Worry About

**You don't need to understand:**
-  Complex betting strategies
-  Payout calculations
-  All the different bet types
-  Advanced game mechanics

**You just need to know:**
-  Where Red button is
-  Where Black button is
-  Where result appears

**The bot handles everything else!**

---

## Quick Test

**To understand your game:**

1. **Open the game**
2. **Click on "Vermelho" (Red) area**
3. **See what happens:**
   - Does a chip/bet appear?  Good!
   - Does nothing happen?  May need to select chip first

4. **That's it!** You now understand how betting works.

---

## For Bot Configuration

**You need to find:**

1. **Red betting area** = "Vermelho" on betting grid
2. **Black betting area** = "Preto" on betting grid
3. **Result display** = Where winning number appears (usually center)

**Use the coordinate capture tool to find these:**
```bash
python coordinate_capture_tool.py
```

**That's all you need to know!**

---

## Summary

**Roulette = Bet on Red or Black**

**Bot = Does it automatically**

**You = Just tell bot where buttons are**

**Simple!**

