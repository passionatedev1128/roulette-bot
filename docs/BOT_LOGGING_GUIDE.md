# Bot Logging Guide

## 📝 Overview

The bot automatically logs all its work to text files. This guide explains what's logged and where to find the logs.

---

## 📂 Log File Locations

### 1. Bot Activity Log (TXT)
**Location**: `backend/logs/bot_log_{timestamp}.txt`

**Example**: `backend/logs/bot_log_20250103_143022.txt`

**Contains**:
- All bot activity and operations
- Detection attempts and results
- Bet decisions and placements
- Errors and warnings
- Status changes
- Debug information

**Format**:
```
2025-01-03 14:30:22,123 - backend.app.bot - INFO - Starting roulette bot...
2025-01-03 14:30:23,456 - backend.app.bot - INFO - Detection succeeded: number=17 color=black method=template_badge confidence=0.92
2025-01-03 14:30:24,789 - backend.app.bot - INFO - Bet decision: even for 10.0 (reason: Entry triggered: 5 consecutive odd  betting even)
2025-01-03 14:30:25,012 - backend.app.bot - INFO - Bet placed successfully: even - 10.0
```

---

### 2. Spin Data Log (CSV)
**Location**: `logs/roulette_log_{timestamp}.csv`

**Example**: `logs/roulette_log_20250103_143022.csv`

**Contains**:
- All spin data in CSV format
- Can be opened in Excel
- Includes: spin number, outcome, bets, results, balance, etc.

**Columns**:
- timestamp, table, spin_number, outcome_number, outcome_color
- bet_category, bet_color, bet_amount, stake
- balance_before, balance_after, result, profit_loss
- strategy, cycle_number, gale_step, streak_length
- is_keepalive, detection_confidence, detection_method, errors

---

### 3. Spin Data Log (JSON)
**Location**: `logs/roulette_log_{timestamp}.json`

**Example**: `logs/roulette_log_20250103_143022.json`

**Contains**:
- Same data as CSV but in JSON format
- Useful for programmatic access

---

### 4. Error Log
**Location**: `logs/errors_{timestamp}.log`

**Example**: `logs/errors_20250103_143022.log`

**Contains**:
- All errors and exceptions
- Error context and stack traces

---

## 📊 What Gets Logged

### Detection Events
-  Frame capture attempts
-  Detection results (number, color, confidence, method)
-  Failed detections
-  Duplicate detection filtering
-  Template matching scores

### Betting Events
-  Bet decisions (type, amount, reason)
-  Bet placement attempts
-  Bet success/failure
-  Bet resolution (win/loss)
-  Balance updates

### Strategy Events
-  Strategy calculations
-  Gale step changes
-  Cycle starts/ends
-  Streak tracking
-  Keepalive bets

### System Events
-  Bot start/stop
-  Status changes
-  Stop conditions triggered
-  Configuration changes
-  Errors and exceptions

---

## 🔍 Viewing Logs

### View Latest Bot Log
```bash
# Windows PowerShell
Get-Content backend\logs\bot_log_*.txt | Select-Object -Last 50

# Windows CMD
type backend\logs\bot_log_*.txt | more

# Linux/Mac
tail -f backend/logs/bot_log_*.txt
```

### View in Real-Time
```bash
# Windows PowerShell
Get-Content backend\logs\bot_log_*.txt -Wait -Tail 20

# Linux/Mac
tail -f backend/logs/bot_log_*.txt
```

### Open in Text Editor
- Navigate to `backend/logs/` directory
- Open `bot_log_{timestamp}.txt`
- Use any text editor (Notepad, VS Code, etc.)

---

## ⚙️ Logging Configuration

### Current Configuration
**File**: `config/default_config.json`

```json
{
  "logging": {
    "logs_dir": "logs",
    "log_level": "INFO"
  }
}
```

### Log Levels

- **DEBUG**: Very detailed information (all operations)
- **INFO**: General information (default)
- **WARNING**: Warnings (non-critical issues)
- **ERROR**: Errors (critical issues)

### Change Log Level

**For more detail** (DEBUG level):
```json
{
  "logging": {
    "log_level": "DEBUG"
  }
}
```

**For less detail** (WARNING level):
```json
{
  "logging": {
    "log_level": "WARNING"
  }
}
```

---

## 📋 Log File Format

### Standard Format
```
TIMESTAMP - MODULE - LEVEL - MESSAGE
```

**Example**:
```
2025-01-03 14:30:22,123 - backend.app.bot - INFO - Detection succeeded: number=17 color=black method=template_badge confidence=0.92
```

### Components
- **TIMESTAMP**: Date and time with milliseconds
- **MODULE**: Python module name (e.g., `backend.app.bot`)
- **LEVEL**: Log level (DEBUG, INFO, WARNING, ERROR)
- **MESSAGE**: Actual log message

---

## 🔄 Log File Rotation

**Current Behavior**:
- New log file created each time bot starts
- Timestamp in filename: `bot_log_YYYYMMDD_HHMMSS.txt`
- Old log files are kept (not deleted)

**Example**:
- `bot_log_20250103_143022.txt` (started at 14:30:22)
- `bot_log_20250103_150145.txt` (started at 15:01:45)

---

## 📊 Log File Size

**Typical sizes**:
- **1 hour of operation**: ~1-5 MB
- **1 day of operation**: ~10-50 MB
- **1 week of operation**: ~100-500 MB

**Note**: Log file size depends on:
- Log level (DEBUG = larger files)
- Detection frequency
- Number of events

---

##  Verification

### Check if Logging is Working

**1. Start bot:**
```bash
python main.py --test
```

**2. Check log file created:**
```bash
# Windows
dir backend\logs\bot_log_*.txt

# Linux/Mac
ls -la backend/logs/bot_log_*.txt
```

**3. Check log file content:**
```bash
# View first few lines
head -20 backend/logs/bot_log_*.txt

# View last few lines
tail -20 backend/logs/bot_log_*.txt
```

**4. Look for these messages:**
- `"Bot logging configured: Logs saved to ..."`
- `"Starting roulette bot..."`
- `"Detection succeeded: ..."`
- `"Bet placed successfully: ..."`

---

## 🐛 Troubleshooting

### Issue: No Log Files Created

**Check**:
1. Bot started successfully
2. `backend/logs/` directory exists
3. Write permissions on directory

**Fix**:
```bash
# Create logs directory manually
mkdir backend\logs
```

---

### Issue: Log File is Empty

**Check**:
1. Bot is actually running
2. Log level is not too high (WARNING/ERROR only)
3. No errors during logging setup

**Fix**:
- Set log level to `INFO` or `DEBUG`
- Check console output for errors

---

### Issue: Can't Find Log Files

**Check**:
1. Current working directory
2. Log file location (relative vs absolute path)

**Log files are created in**:
- `backend/logs/bot_log_*.txt` (relative to project root)
- Or `logs/roulette_log_*.csv` (relative to project root)

**Find log files**:
```bash
# Windows
dir /s bot_log_*.txt

# Linux/Mac
find . -name "bot_log_*.txt"
```

---

## 📝 Example Log Output

```
2025-01-03 14:30:22,123 - backend.app.bot - INFO - Bot logging configured: Logs saved to E:\...\backend\logs\bot_log_20250103_143022.txt
2025-01-03 14:30:22,456 - backend.app.bot - INFO - RouletteBot initialized
2025-01-03 14:30:22,789 - backend.app.bot - INFO - Starting roulette bot...
2025-01-03 14:30:23,012 - backend.app.bot - INFO - Real-time mode - processing with optimized delays (delay_no_detection=0.1s, frame_skip=30)
2025-01-03 14:30:25,345 - backend.app.bot - INFO - Detection succeeded: number=17 color=black method=template_badge confidence=0.92
2025-01-03 14:30:25,678 - backend.app.bot - INFO - Bet decision: even for 10.0 (reason: Entry triggered: 5 consecutive odd  betting even)
2025-01-03 14:30:25,901 - backend.app.bot - INFO - Bet placed successfully: even - 10.0
2025-01-03 14:30:26,234 - backend.app.bot - INFO - Round completed: win, Balance: 1010.0, Bet: even, Result: 18
2025-01-03 14:30:26,567 - backend.app.bot - INFO - Spin 1 processed: number=18, color=black
```

---

##  Summary

**Bot logging is already configured and working!**

**Log files are automatically created in**:
- `backend/logs/bot_log_{timestamp}.txt` - All bot activity
- `logs/roulette_log_{timestamp}.csv` - Spin data (CSV)
- `logs/roulette_log_{timestamp}.json` - Spin data (JSON)
- `logs/errors_{timestamp}.log` - Errors only

**To view logs**:
- Open `backend/logs/bot_log_*.txt` in any text editor
- Or use command line: `tail -f backend/logs/bot_log_*.txt`

**No additional configuration needed** - logging works automatically!

