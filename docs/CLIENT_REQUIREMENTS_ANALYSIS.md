# Client Requirements Analysis - Even/Odd Strategy

## Critical Finding: Strategy Mismatch

###  **MAJOR ISSUE: Wrong Strategy Type**

**Client Wants:** Even/Odd counter-sequence strategy  
**Current Implementation:** Red/Black color-based strategy

**This is a fundamental mismatch!** The bot needs to be completely redesigned.

---

## Detailed Requirements Comparison

### 1. Strategy Type

| Requirement | Client Wants | Current Implementation | Status |
|------------|--------------|----------------------|--------|
| **Betting Type** | Even/Odd (number-based) | Red/Black (color-based) |  **WRONG** |
| **Entry Logic** | Bet against streaks | Bet opposite of last result |  **WRONG** |
| **Entry Trigger** | Only when streak length N reached | Always bets every round |  **WRONG** |

**Client Requirement:**
- Monitor Even/Odd outcomes
- Detect streaks (e.g., 5 consecutive Odds)
- Bet against the streak (e.g., bet Even after 5 Odds)
- Only enter when streak length N is reached

**Current Implementation:**
- Monitors Red/Black colors
- Always bets opposite of last result
- No streak detection
- Bets every round

**Action Required:** Complete strategy rewrite

---

### 2. Entry Conditions

| Requirement | Client Wants | Current Implementation | Status |
|------------|--------------|----------------------|--------|
| **Entry Trigger** | Streak length N (e.g., 5 consecutive) | Always bets |  **MISSING** |
| **Streak Detection** | Count consecutive Even/Odd | Not implemented |  **MISSING** |
| **Entry Timing** | Next betting window after streak | Every round |  **WRONG** |
| **Missed Window** | Wait for new streak | Not handled |  **MISSING** |

**Client Requirement:**
```
When streak of N consecutive Even (or Odd) is detected:
- Place bet on opposite (Odd or Even) on next spin
- If betting window missed, wait for new streak
- Do not enter late
```

**Current Implementation:**
- No streak detection
- Always bets every round
- No entry condition logic

**Action Required:** Implement streak detection and entry condition logic

---

### 3. Gale System

| Requirement | Client Wants | Current Implementation | Status |
|------------|--------------|----------------------|--------|
| **Progression** | 2x after each loss | 2x after each loss |  **CORRECT** |
| **Max Gales** | Configurable limit | Configurable limit |  **CORRECT** |
| **Cycle End** | On first win or max gale | On first win or max gale |  **CORRECT** |
| **Concurrent Cycles** | Not allowed | Not explicitly prevented |  **NEEDS CHECK** |

**Client Requirement:**
- Each loss triggers 2x stake
- Cycle ends on first win or max gale
- No concurrent cycles allowed

**Current Implementation:**
-  Gale progression works correctly
-  Need to verify no concurrent cycles

**Action Required:** Verify cycle management

---

### 4. StopLoss & StopWin

| Requirement | Client Wants | Current Implementation | Status |
|------------|--------------|----------------------|--------|
| **StopLoss by Count** | Number of losing rounds |  Not implemented |  **MISSING** |
| **StopLoss by Money** | Net PnL amount |  Implemented |  **CORRECT** |
| **StopWin by Count** | Number of winning rounds |  Not implemented |  **MISSING** |
| **StopWin by Money** | Net PnL amount |  Not implemented |  **MISSING** |
| **Stop Behavior** | Stop after current spin | Not specified |  **NEEDS CHECK** |

**Client Requirement:**
```
StopLoss:
- By count: Total losing rounds in session
- By money: Net PnL (negative threshold)

StopWin:
- By count: Total winning rounds in session
- By money: Net PnL (positive threshold)

Behavior: Stop immediately after current spin, no new cycles
```

**Current Implementation:**
-  StopLoss by money only
-  StopLoss by count: Missing
-  StopWin: Completely missing

**Action Required:** Implement StopWin and count-based stops

---

### 5. Keepalive System

| Requirement | Client Wants | Current Implementation | Status |
|------------|--------------|----------------------|--------|
| **Interval** | 29 minutes | 30 minutes |  **WRONG** |
| **Bet Type** | Random Even/Odd | Strategy-based (Red/Black) |  **WRONG** |
| **Stake** | Minimal keepalive stake | Strategy bet amount |  **WRONG** |
| **Timing** | Only when idle (no active cycle) | Every interval |  **PARTIAL** |
| **Logging** | Distinct keepalive logs | Mixed with strategy |  **NEEDS IMPROVEMENT** |

**Client Requirement:**
```
Every 29 minutes when idle:
- Random pick: Even or Odd
- Use minimal keepalive stake
- Do not interrupt active cycles
- Log distinctly as keepalive
```

**Current Implementation:**
- Interval: 30 minutes (should be 29)
- Bet type: Uses strategy (should be random Even/Odd)
- Stake: Uses strategy amount (should be minimal)
- Timing: Every interval (should check for active cycle)

**Action Required:** Complete keepalive rewrite

---

### 6. Zero (0) Handling

| Requirement | Client Wants | Current Implementation | Status |
|------------|--------------|----------------------|--------|
| **Policy** | Client confirmation needed | Configurable options |  **NEEDS CONFIRMATION** |
| **Options** | Count as loss / Neutral / Reset | Continue/Reset/Skip |  **NEEDS MAPPING** |

**Client Requirement:**
```
Options:
1. Count as loss (continue cycle)
2. Treat as neutral (ignore for streak, wait next spin)
3. Reset streaks (less common)

Must confirm with client before implementation
```

**Current Implementation:**
- Has zero handling options
- But needs confirmation for Even/Odd context

**Action Required:** Confirm zero policy with client

---

### 7. Cycle Management

| Requirement | Client Wants | Current Implementation | Status |
|------------|--------------|----------------------|--------|
| **Cycle Definition** | Entry  Win or Max Gale | Similar concept |  **CORRECT** |
| **No Concurrent** | Must finish before new cycle | Not explicitly enforced |  **NEEDS CHECK** |
| **Cycle End** | First win or max gale | First win or max gale |  **CORRECT** |

**Client Requirement:**
```
Cycle:
- Begins: Initial entry after streak detected
- Ends: First win OR max gale reached
- No new cycle while current cycle active
```

**Current Implementation:**
- Concept exists but needs verification
- Need to ensure no concurrent cycles

**Action Required:** Verify and enforce cycle exclusivity

---

### 8. Logging & Reporting

| Requirement | Client Wants | Current Implementation | Status |
|------------|--------------|----------------------|--------|
| **Per Event Logs** | Timestamp, table, outcome, stake, result, cycle, gale, streak, keepalive flag | Partial |  **NEEDS ENHANCEMENT** |
| **Session Summary** | Cycles, wins/losses, PnL, keepalive count, stop triggers | Partial |  **NEEDS ENHANCEMENT** |
| **Export Format** | CSV or dashboard | CSV exists |  **NEEDS CONFIRMATION** |

**Client Requirement:**
```
Per event: timestamp, table, outcome, stake, result, cycle#, gale#, streak, keepalive flag
Session: total cycles, wins/losses, net PnL, keepalive count, stop triggers
```

**Current Implementation:**
- Has logging but missing some fields
- Missing keepalive flag
- Missing streak tracking

**Action Required:** Enhance logging with all required fields

---

## Summary of Gaps

###  **Critical - Complete Rewrite Needed:**

1. **Strategy Type:** Even/Odd vs Red/Black
2. **Entry Logic:** Streak-based vs Always bet
3. **Streak Detection:** Not implemented
4. **Entry Conditions:** Not implemented

###  **Major - Missing Features:**

5. **StopWin:** Completely missing
6. **StopLoss by Count:** Missing
7. **Keepalive System:** Wrong implementation
8. **Zero Policy:** Needs client confirmation

###  **Minor - Needs Adjustment:**

9. **Keepalive Interval:** 29 vs 30 minutes
10. **Cycle Management:** Needs verification
11. **Logging:** Needs enhancement

---

## Implementation Plan

### Phase 1: Core Strategy Rewrite (CRITICAL)

1. **Change from Red/Black to Even/Odd**
   - Modify number-to-attribute mapping
   - Even: 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36
   - Odd: 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35
   - Zero: 0 (special handling)

2. **Implement Streak Detection**
   - Track consecutive Even/Odd outcomes
   - Maintain separate counters for Even and Odd streaks
   - Reset on opposite outcome

3. **Implement Entry Conditions**
   - Only bet when streak length N is reached
   - Bet against the streak (counter-sequence)
   - Wait for next betting window

### Phase 2: StopWin & Enhanced StopLoss

4. **Implement StopWin**
   - By count: Track winning rounds
   - By money: Track positive PnL threshold
   - Stop behavior: After current spin

5. **Enhance StopLoss**
   - Add count-based stop
   - Keep money-based stop
   - Stop behavior: After current spin

### Phase 3: Keepalive System

6. **Rewrite Keepalive**
   - Change interval to 29 minutes
   - Random Even/Odd selection
   - Minimal stake (separate from strategy)
   - Only when idle (no active cycle)
   - Distinct logging

### Phase 4: Cycle Management & Zero

7. **Enforce Cycle Exclusivity**
   - Prevent new cycle while current active
   - Clear cycle state management

8. **Zero Handling**
   - Confirm policy with client
   - Implement chosen option

### Phase 5: Logging & Reporting

9. **Enhance Logging**
   - Add all required fields
   - Add keepalive flag
   - Add streak tracking
   - Add cycle/gale numbers

10. **Session Summary**
    - Total cycles
    - Wins/losses
    - Net PnL
    - Keepalive count
    - Stop triggers

---

## Immediate Actions Required

### 1. **Confirm Zero Policy**
Ask client:
- Count zero as loss? (continue cycle)
- Treat as neutral? (ignore for streak)
- Reset streaks? (less common)

### 2. **Confirm Configuration Values**
Ask client:
- Base stake amount
- Maximum number of Gales
- Streak length N for entry
- StopLoss thresholds (count and money)
- StopWin thresholds (count and money)
- Keepalive stake value
- Currency and timezone

### 3. **Confirm Table/Platform**
Ask client:
- Which provider/platform for "Roleta Brasileira"?
- Table URL or identifier?

---

## Code Changes Required

### Files to Modify:

1. **`backend/app/strategy/base_strategy.py`**
   - Change from color-based to Even/Odd
   - Add streak detection
   - Add entry condition logic

2. **`backend/app/strategy/martingale_strategy.py`**
   - Rewrite for Even/Odd
   - Add streak-based entry
   - Remove "always bet" logic

3. **`backend/app/bot.py`**
   - Add StopWin logic
   - Enhance StopLoss (add count)
   - Rewrite keepalive system
   - Enforce cycle exclusivity

4. **`backend/app/logging/logger.py`**
   - Add keepalive flag
   - Add streak tracking
   - Add cycle/gale numbers
   - Enhance session summary

5. **`config/default_config.json`**
   - Change strategy type
   - Add streak length parameter
   - Add StopWin configuration
   - Add keepalive configuration

---

## Conclusion

**Current Status:**  **Strategy is completely wrong**

The current implementation is for **Red/Black color betting**, but the client wants **Even/Odd number betting with streak-based entry conditions**.

**Required Actions:**
1. Complete strategy rewrite (Even/Odd)
2. Implement streak detection
3. Implement entry conditions
4. Add StopWin
5. Rewrite keepalive system
6. Confirm zero policy with client

**This is a significant change that requires substantial code modifications.**

