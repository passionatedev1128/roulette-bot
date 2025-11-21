# Debug: Bot Not Placing Bets

## Issue
The bot is not placing any bets during testing.

## Possible Causes & Solutions

### 1. **Entry Condition Not Met** ⚠️ Most Likely

**Current Configuration:**
- `streak_length: 3` - Requires **3 consecutive Even or Odd numbers** before betting
- Strategy: Even/Odd counter-sequence

**What This Means:**
- The bot will ONLY bet when it detects:
  - 3 consecutive Even numbers → Then bets Odd
  - 3 consecutive Odd numbers → Then bets Even

**Check:**
1. Are you seeing 3+ consecutive Even or Odd numbers in the results?
2. Check the logs for streak information:
   ```
   Before bet calculation: Even streak=X, Odd streak=Y, streak_length required=3
   ```

**Solution:**
- **Option A**: Lower `streak_length` to 2 for more frequent betting:
  ```json
  "streak_length": 2
  ```
- **Option B**: Wait for more results to see if a streak occurs
- **Option C**: Check if results are being detected correctly

---

### 2. **Results Not Being Detected**

**Check:**
- Are numbers being detected? Check "Resultados ao vivo" section
- Check logs for detection messages:
  ```
  Detection succeeded: number=X color=Y method=Z confidence=W
  ```

**Solution:**
- Verify detection is working
- Check if `screen_region` coordinates are correct
- Ensure templates are loaded properly

---

### 3. **Test Mode Behavior**

**Check:**
- Is the bot running in test mode?
- Test mode should still show bet decisions, but won't place real bets

**Solution:**
- Check if `test_mode` is enabled
- Even in test mode, you should see "Bet decision" logs

---

### 4. **Betting Controller Issues**

**Check Logs For:**
```
Placing bet: even - 10.0
Bet placement failed: [error message]
```

**Common Issues:**
- Betting coordinates not found
- Bet already exists
- Insufficient balance

**Solution:**
- Verify betting coordinates in config:
  ```json
  "even": [907, 905],
  "odd": [1111, 906]
  ```
- Check if balance is sufficient
- Ensure no existing bets are blocking

---

### 5. **Zero Policy Interfering**

**Current Setting:**
- `zero_policy: "neutral"` - Zeros are ignored for streak counting

**Impact:**
- If zeros appear frequently, they break streaks
- This is correct behavior, but may delay betting

**Solution:**
- This is working as intended
- Zeros should not break streaks with "neutral" policy

---

## Diagnostic Steps

### Step 1: Check Logs

Look for these log messages:

1. **Detection logs:**
   ```
   Detection succeeded: number=5 color=red method=template confidence=0.95
   ```

2. **Streak tracking:**
   ```
   Before bet calculation: Even streak=2, Odd streak=0, streak_length required=3
   ```

3. **Bet decisions:**
   ```
   Bet decision: odd for 10.0 (reason: Entry triggered: 3 consecutive even → betting odd)
   ```
   OR
   ```
   No bet decision: Even streak=2, Odd streak=0, streak_length required=3
   ```

4. **Bet placement:**
   ```
   Placing bet: odd - 10.0
   Bet placed: odd - 10.0
   ```

### Step 2: Verify Configuration

Check `config/default_config.json`:

```json
{
  "strategy": {
    "type": "even_odd",
    "streak_length": 3,  // ← This requires 3 consecutive
    "base_bet": 10.0,
    ...
  }
}
```

### Step 3: Test with Lower Streak Length

Temporarily change to `streak_length: 2` to see if bets start:

```json
"streak_length": 2
```

This will make the bot bet more frequently (after 2 consecutive instead of 3).

### Step 4: Check Result History

The bot needs to see results to build streaks. Verify:
- Results are being detected
- Results are being added to history
- Streaks are being tracked correctly

---

## Quick Fix: Lower Streak Length

If you want the bot to bet more frequently, change:

```json
{
  "strategy": {
    "streak_length": 2  // Changed from 3 to 2
  }
}
```

**Impact:**
- Before: Needs 3 consecutive Even/Odd → bets
- After: Needs 2 consecutive Even/Odd → bets
- More frequent betting opportunities

---

## Expected Behavior

### Normal Flow:
1. Bot detects number (e.g., 2 - Even)
2. Even streak = 1, Odd streak = 0
3. Bot detects number (e.g., 4 - Even)
4. Even streak = 2, Odd streak = 0
5. Bot detects number (e.g., 6 - Even)
6. Even streak = 3, Odd streak = 0
7. **Entry condition met!** → Bot bets Odd
8. Bet placed

### If No Betting:
- Check if you're seeing 3+ consecutive Even or Odd
- Check logs for streak values
- Verify detection is working

---

## Testing Recommendations

1. **Monitor Logs:**
   - Watch for streak values
   - Check for "Entry condition met" messages
   - Verify bet decisions are being made

2. **Check Results:**
   - Look at "Resultados ao vivo" section
   - Count consecutive Even/Odd numbers
   - Verify streaks are building

3. **Lower Threshold Temporarily:**
   - Set `streak_length: 2` for testing
   - This will make betting more frequent
   - Once confirmed working, adjust back to 3

---

## Most Common Issue

**90% of cases:** The bot is working correctly, but you haven't seen 3 consecutive Even or Odd numbers yet.

**Solution:** 
- Lower `streak_length` to 2 for more frequent betting
- OR wait for a streak to occur naturally
- OR check if results are alternating too much (preventing streaks)

---

*If the issue persists after checking these, please share the relevant log messages for further diagnosis.*

