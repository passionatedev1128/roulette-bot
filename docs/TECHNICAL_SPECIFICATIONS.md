# Brazilian Roulette Bot - Technical Specifications

## System Components Detailed Design

### 1. Game Detection Module

#### 1.1 Result Capture Strategy

**Primary Method: DOM Element Inspection**
```python
# Pseudocode Structure
class ResultDetector:
    - Monitor DOM elements for result display
    - Extract: number, color, round_id
    - Validate result before storing
    - Handle multiple result formats (text, images, CSS classes)
```

**Detection Points:**
- Result number (0-36)
- Color mapping:
  - Red: 1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36
  - Black: 2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35
  - Green: 0
- Round completion indicator
- Timer/next round countdown

**Error Handling:**
- Retry mechanism (3 attempts)
- Fallback to OCR if DOM fails
- Logging of missed results
- Alert on detection failure

#### 1.2 Detection Timing

- **Polling Interval**: Check every 0.5 seconds during active round
- **Result Confirmation**: Wait for result to stabilize (2-3 seconds)
- **Round Tracking**: Detect new round start vs. same round update

---

### 2. Strategy Engine

#### 2.1 Color-Based Strategy Logic

**Basic Pattern Recognition:**
```
Entry Conditions (Examples - to be confirmed):
- After N consecutive same color
- After color pattern: R-B-R-B  bet opposite
- After specific sequence length
- Based on color frequency in last X rounds
```

**Strategy Configuration Structure:**
```json
{
  "strategy_type": "color_pattern",
  "entry_condition": {
    "type": "consecutive_same",
    "count": 3,
    "action": "bet_opposite"
  },
  "bet_amount": 10.00,
  "enable_gale": true,
  "gale_config": {
    "multiplier": 2.0,
    "max_steps": 5,
    "guarantee_fund_percentage": 20
  }
}
```

#### 2.2 Entry Signal Generation

**Process Flow:**
1. Receive new result
2. Update pattern history
3. Evaluate entry conditions
4. Generate entry signal if conditions met
5. Calculate bet details (amount, color)
6. Queue bet for execution

---

### 3. Betting Controller

#### 3.1 Bet Placement Workflow

**Steps:**
1. Navigate to betting area (if needed)
2. Select color (Red/Black/Green)
3. Enter bet amount
4. Confirm bet placement
5. Wait for confirmation message
6. Log bet details
7. Handle errors (insufficient funds, timeout, etc.)

**Bet Types:**
- **Strategy Bet**: Based on entry conditions
- **Maintenance Bet**: Minimum bet to keep session active
- **Gale Bet**: Progressive bet after loss

#### 3.2 Maintenance Bet System

**30-Minute Interval Logic:**
```python
class MaintenanceScheduler:
    - Track last bet time
    - Place minimum bet every 30 minutes
    - Ensure bet is different from last strategy bet (if any)
    - Log maintenance activity
    - Skip if strategy bet placed within last 5 minutes
```

**Minimum Bet Rules:**
- Use platform's minimum allowed bet
- Distribute across colors to appear natural
- Alternate between red/black randomly

---

### 4. Gale (Martingale) System

#### 4.1 Progression Calculation

**Standard Martingale:**
```
Loss 1: Bet = Base Amount
Loss 2: Bet = Base × 2
Loss 3: Bet = Base × 4
Loss 4: Bet = Base × 8
Loss 5: Bet = Base × 16
```

**Configuration Options:**
- Linear progression (add fixed amount)
- Multiplier progression (multiply by factor)
- Custom progression table

#### 4.2 Guarantee Fund Management

**Reservation Logic:**
```
Total Balance: $1000
Guarantee Fund: 20% = $200
Available for Strategy: $800

Gale Sequence Reserve:
- Step 1: $10
- Step 2: $20
- Step 3: $40
- Step 4: $80
- Step 5: $160
Total Reserved: $310 (if all steps needed)

If insufficient: Stop progression, alert user
```

#### 4.3 Auto-Gale on Manual Entry

**10-Second Window Handling:**
```
Client manually places bet  Bot detects within 1 second
 Immediately calculate gale progression
 Pre-load bet amounts for next 5 steps
 Monitor for loss
 Auto-place next gale bet if loss occurs
```

**Detection of Manual Entry:**
- Monitor DOM for bet confirmation changes
- Track balance changes
- Detect betting area activity

---

### 5. Session Management

#### 5.1 Connection Monitoring

**Health Checks:**
- Verify page is loaded (every 10 seconds)
- Check for "Paused" indicators
- Monitor connection status
- Detect "Disconnected" messages

**Prevention Strategies:**
- Proactive bet placement before timeout
- Mouse movement simulation (if needed)
- Periodic page refresh (last resort)

#### 5.2 Reconnection Logic

**Failure Detection:**
- Timeout on bet placement (>10 seconds)
- Error messages in DOM
- Network failure indicators

**Recovery Actions:**
1. Refresh page
2. Re-login (if session expired)
3. Navigate back to game
4. Resume monitoring
5. Log reconnection event

---

### 6. Database Schema

#### 6.1 Tables Structure

**Results Table:**
```sql
CREATE TABLE results (
    id INTEGER PRIMARY KEY,
    round_number INTEGER,
    result_number INTEGER,
    color TEXT,  -- 'red', 'black', 'green'
    timestamp DATETIME,
    detected_at DATETIME
);
```

**Bets Table:**
```sql
CREATE TABLE bets (
    id INTEGER PRIMARY KEY,
    bet_type TEXT,  -- 'strategy', 'maintenance', 'gale'
    color TEXT,
    amount REAL,
    round_number INTEGER,
    status TEXT,  -- 'pending', 'won', 'lost', 'cancelled'
    placed_at DATETIME,
    result_at DATETIME,
    profit_loss REAL
);
```

**Gale Sequences Table:**
```sql
CREATE TABLE gale_sequences (
    id INTEGER PRIMARY KEY,
    started_at DATETIME,
    base_amount REAL,
    current_step INTEGER,
    total_invested REAL,
    status TEXT  -- 'active', 'won', 'stopped', 'failed'
);
```

**Configuration Table:**
```sql
CREATE TABLE config (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at DATETIME
);
```

#### 6.2 Statistics Views

**Performance Metrics:**
- Total bets placed
- Win rate by bet type
- Average profit/loss
- Gale success rate
- Longest win/loss streaks

---

### 7. API Endpoints

#### 7.1 REST API Structure

**Configuration:**
- `GET /api/config` - Get all settings
- `PUT /api/config` - Update settings
- `POST /api/config/preset` - Save preset
- `GET /api/config/presets` - List presets

**Monitoring:**
- `GET /api/status` - Bot status
- `GET /api/balance` - Current balance
- `GET /api/results/latest` - Last N results
- `GET /api/bets/active` - Active bets
- `GET /api/bets/history` - Bet history

**Control:**
- `POST /api/bot/start` - Start bot
- `POST /api/bot/stop` - Stop bot
- `POST /api/bot/mode` - Change mode

**Statistics:**
- `GET /api/stats/daily` - Daily performance
- `GET /api/stats/strategy` - Strategy effectiveness
- `GET /api/stats/gale` - Gale performance

#### 7.2 WebSocket Events

**Real-time Updates:**
```javascript
// Client subscribes to:
- 'new_result' - New roulette result
- 'bet_placed' - Bet confirmation
- 'bet_resolved' - Bet won/lost
- 'balance_update' - Balance changed
- 'status_change' - Bot status changed
- 'error' - Error occurred
```

---

### 8. Frontend Components

#### 8.1 Dashboard Layout

**Main Components:**
1. **Header Bar**
   - Bot status indicator
   - Current mode selector
   - Balance display
   - Start/Stop button

2. **Game Display**
   - Visual roulette wheel
   - Last 20 results (color chips)
   - Current round number
   - Next bet prediction

3. **Active Bets Panel**
   - List of pending bets
   - Gale progression display
   - Time until resolution

4. **Statistics Panel**
   - Today's P&L
   - Win rate
   - Total bets
   - Charts (profit over time)

5. **Settings Panel**
   - Strategy configuration
   - Risk management settings
   - Mode selection
   - Save/Load presets

#### 8.2 Real-time Updates

**Update Strategy:**
- WebSocket for immediate updates
- Polling fallback (every 2 seconds)
- Optimistic UI updates
- Error state handling

---

### 9. Security Considerations

#### 9.1 Credential Management

**Storage:**
- Encrypt credentials in database
- Environment variables for sensitive data
- Never log passwords or tokens

**Authentication:**
- Secure login to casino platform
- Session token management
- Auto-logout on suspicious activity

#### 9.2 Rate Limiting

**Betting Limits:**
- Maximum bets per hour
- Cooldown between strategy bets
- Respect platform rate limits

#### 9.3 Data Protection

**Logging:**
- No sensitive data in logs
- Sanitize user inputs
- Secure log file storage

---

### 10. Error Handling

#### 10.1 Error Categories

**Detection Errors:**
- Missed result  Alert, attempt recovery
- False detection  Validation checks
- Timeout  Retry with backoff

**Betting Errors:**
- Insufficient funds  Stop, alert
- Network error  Retry, reconnect
- Invalid bet  Log, skip round
- Platform error  Alert, pause bot

**System Errors:**
- Browser crash  Auto-restart
- Memory leak  Monitor, restart
- Database error  Fallback to file storage

#### 10.2 Recovery Procedures

**Automatic:**
- Retry failed operations (max 3 times)
- Reconnect on disconnection
- Restart browser on crash
- Load last known state

**Manual:**
- Alert user on critical errors
- Provide error logs
- Allow manual intervention
- Emergency stop button

---

### 11. Performance Optimization

#### 11.1 Detection Optimization

- Reduce DOM queries (cache elements)
- Use efficient selectors
- Batch result processing
- Minimize screenshot/OCR usage

#### 11.2 Betting Optimization

- Pre-calculate bet amounts
- Queue bets for execution
- Parallel processing where safe
- Optimize wait times

#### 11.3 Frontend Optimization

- Virtual scrolling for history
- Lazy load charts
- Debounce updates
- Efficient WebSocket message handling

---

### 12. Testing Strategy

#### 12.1 Unit Tests

- Result detection accuracy
- Strategy logic correctness
- Gale calculation
- Configuration parsing

#### 12.2 Integration Tests

- End-to-end bet placement
- Session maintenance
- Reconnection flow
- Database operations

#### 12.3 Performance Tests

- Detection latency
- Bet placement speed
- Dashboard responsiveness
- Memory usage over time

#### 12.4 Stress Tests

- 24-hour continuous operation
- High-frequency result detection
- Multiple concurrent bets
- Error scenario simulation

---

## Implementation Priority

### Must Have (MVP):
1. Result detection
2. Basic betting
3. Maintenance bet system
4. Simple dashboard
5. Configuration interface

### Should Have:
1. Gale system
2. Advanced strategy options
3. Performance reports
4. Error recovery
5. WebSocket real-time updates

### Nice to Have:
1. Multiple strategy presets
2. Advanced analytics
3. Telegram notifications
4. Mobile-responsive design
5. Export functionality

