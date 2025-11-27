# Brazilian Roulette Bot - Quick Reference Guide

## Project Overview

**Goal**: 24/7 automated Brazilian Roulette betting bot with color-based strategy, gale system, and web dashboard.

---

## Core Features

### 1. Betting Modes
- **Maintenance Mode**: Minimum bets every 30 min (keeps session active)
- **Full Auto Mode**: Strategy execution + maintenance bets
- **Manual Analysis Mode**: Creates roads, auto-gale when client manually enters

### 2. Strategy
- **Type**: Color-based (red/black)
- **Entry**: Every 30 minutes (prevents game pause)
- **Details**: To be specified by client

### 3. Gale System
- **Purpose**: Martingale progression after losses
- **Speed**: Must execute within 10 seconds of manual entry
- **Protection**: Guarantee fund reserved for gale bets

### 4. Session Management
- **Problem**: Game pauses after ~5 min, disconnects after 3-5 rounds without bets
- **Solution**: Maintenance bets every 30 minutes

---

## Technical Stack

**Backend**: Python + Flask/FastAPI  
**Automation**: Selenium/Playwright  
**Frontend**: React  
**Database**: SQLite (dev) / PostgreSQL (prod)  
**Hosting**: VPS ($10-20/month)

---

## Critical Requirements

| Requirement | Target | Priority |
|------------|--------|----------|
| Detection Accuracy | >99% | 🔴 Critical |
| Bet Placement Success | >99% | 🔴 Critical |
| Gale Response Time | <1 second | 🔴 Critical |
| Session Uptime | >99% | 🔴 Critical |
| 24hr Continuous Operation | Yes | 🔴 Critical |

---

## Key Technical Challenges

1. **Result Detection** - Must be 100% accurate
2. **10-Second Gale Window** - Fast execution critical
3. **Session Maintenance** - Prevent pauses/disconnections
4. **24/7 Reliability** - Handle crashes, errors, reconnections

---

## Development Phases

**Phase 1** (Week 1-2): Core detection + basic betting  
**Phase 2** (Week 2-3): Web interface + configuration  
**Phase 3** (Week 3-4): Gale system + advanced features  
**Phase 4** (Week 4-5): Polish + deployment

---

## Client Questions (Need Answers)

1. Platform URL/name?
2. Exact color strategy rules?
3. Gale multiplier (2x, 3x)?
4. Guarantee fund %?
5. How to signal manual entry?

---

## Project Structure

```
roulette-bot/
├── backend/       # Python API & bot logic
├── frontend/      # React dashboard
├── config/        # Configuration files
└── docs/          # Documentation
```

---

## Success Criteria

 Detection: >99% accurate  
 Betting: >99% success rate  
 Uptime: >99% (24/7 operation)  
 Gale: <1 second response  
 Interface: Intuitive, no coding needed

---

## Cost Estimate

**Development**: Per contract  
**Monthly Hosting**: $10-20 (VPS)  
**Maintenance**: Minimal (if platform stable)

---

## Next Steps

1. Get platform details from client
2. Clarify strategy specifics
3. Set up development environment
4. Build detection prototype
5. Test with small bets

---

**See full documentation:**
- `PROJECT_ANALYSIS.md` - Complete requirements analysis
- `TECHNICAL_SPECIFICATIONS.md` - Technical design details
- `DEVELOPMENT_CHECKLIST.md` - Step-by-step development guide
- `ANALYSIS_SUMMARY.md` - Key insights and recommendations

