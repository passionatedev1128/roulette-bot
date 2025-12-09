# Demo Mode - Show Frontend UI with Mock Data

## 🎭 How to Enable Demo Mode

### Method 1: URL Parameter (Easiest)

Add `?demo=true` to the URL:

```
http://localhost:3000?demo=true
```

### Method 2: Browser Console

Open browser console (F12) and run:

```javascript
localStorage.setItem('demoMode', 'true');
window.location.reload();
```

### Method 3: Direct Link

Just visit:
```
http://localhost:3000?demo=true
```

---

##  What Demo Mode Shows

When demo mode is enabled, the interface displays:

### 1. **Status Bar**
- Status: **RUNNING**
- Mode: **Full Auto Mode**
- Spins: **156**
- Last Activity: Current time

### 2. **Balance Cards**
- Current Balance: **$1,247.50**
- Initial Balance: **$1,000.00**
- Total P/L: **+$247.50** (green)
- Today's P/L: **+$47.50** (green)
- Total Bets: **156**
- Wins: **82** (green)
- Losses: **74** (red)

### 3. **Live Results**
- Shows 20 recent spins
- Numbers with correct colors (red/black/green)
- Latest result highlighted
- Updates every 5 seconds with new random results

### 4. **Active Bet**
- Bet Type: **ODD**
- Amount: **$20.00**
- Gale Step: **1**
- Placed At: Recent time

### 5. **Bet History Table**
- Shows 25 recent bets
- Mix of wins and losses
- Realistic profit/loss amounts
- Balance progression

### 6. **Performance Charts**
- Daily Performance: 7 days of data
- Gale Performance: Breakdown by gale step
- Strategy Breakdown: Win rates and P/L

### 7. **Configuration Form**
- Pre-filled with realistic settings
- All fields editable
- Save button works (shows alert in demo)

### 8. **Bot Controls**
- Start/Stop buttons work
- Mode selector works
- All interactive

---

## 🔄 Auto-Updates

In demo mode:
- **New results** appear every 5 seconds
- **Spin number** increments
- **Last activity** updates
- All data stays realistic

---

## 🚪 Exit Demo Mode

Click the **"Exit Demo"** button in the purple banner at the top, or:

1. Remove URL parameter: `?demo=true`
2. Or run in console:
   ```javascript
   localStorage.removeItem('demoMode');
   window.location.reload();
   ```

---

## 📋 Perfect for Client Presentation

Demo mode is perfect for:
-  Showing the interface without backend
-  Client presentations
-  UI/UX demonstrations
-  Screenshots and documentation
-  Testing the frontend design

**No backend server needed!** Just start the frontend and add `?demo=true` to the URL.

---

## 🚀 Quick Start

```powershell
# Start frontend
cd web
npm run dev

# Then visit:
# http://localhost:3000?demo=true
```

That's it! The interface will show with realistic mock data.

