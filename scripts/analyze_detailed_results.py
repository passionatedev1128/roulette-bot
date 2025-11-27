#!/usr/bin/env python3
"""
Detailed analysis of strategy test results JSON file.
"""

import json
import sys
from collections import defaultdict
from typing import Dict, List, Any

def analyze_results(json_file: str):
    """Analyze strategy test results."""
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    results = data.get('results', [])
    stats = data.get('statistics', {})
    config = data.get('config', {})
    
    print("=" * 80)
    print("DETAILED STRATEGY TEST ANALYSIS")
    print("=" * 80)
    print()
    
    # Basic stats
    print("[BASIC STATISTICS]")
    print("-" * 80)
    print(f"Total spins: {stats.get('total_spins', 0)}")
    print(f"Total bets: {stats.get('total_bets', 0)}")
    print(f"Wins: {stats.get('wins', 0)}")
    print(f"Losses: {stats.get('losses', 0)}")
    print(f"Win rate: {stats.get('win_rate', 0):.2f}%")
    print(f"Net profit: {stats.get('net_profit', 0):.2f}")
    print(f"Initial balance: {stats.get('initial_balance', 0):.2f}")
    print(f"Final balance: {stats.get('final_balance', 0):.2f}")
    print()
    
    # Analyze cycles
    print("[CYCLE ANALYSIS]")
    print("-" * 80)
    
    cycles = []
    current_cycle = None
    cycle_number = 0
    
    for i, result in enumerate(results):
        bet_decision = result.get('bet_decision')
        bet_outcome = result.get('bet_outcome')
        in_cycle = result.get('in_cycle', False)
        gale_step = result.get('gale_step', 0)
        
        # Detect cycle start (entry bet)
        if bet_decision and bet_decision.get('reason', '').startswith('Entry'):
            cycle_number += 1
            current_cycle = {
                'cycle_number': cycle_number,
                'start_spin': result.get('spin'),
                'entry_streak': bet_decision.get('streak_length', 0),
                'bets': [],
                'outcome': None,
                'final_gale_step': 0,
                'total_bet': 0,
                'profit': 0
            }
            cycles.append(current_cycle)
        
        # Track bets in cycle
        if current_cycle and bet_decision:
            bet_info = {
                'spin': result.get('spin'),
                'gale_step': gale_step,
                'bet_amount': bet_decision.get('bet_amount', 0),
                'bet_type': bet_decision.get('bet_type'),
                'outcome': bet_outcome
            }
            current_cycle['bets'].append(bet_info)
            current_cycle['total_bet'] += bet_info['bet_amount']
            current_cycle['final_gale_step'] = max(current_cycle['final_gale_step'], gale_step)
            
            if bet_outcome == 'win':
                current_cycle['outcome'] = 'win'
                current_cycle['profit'] = bet_info['bet_amount']
            elif bet_outcome == 'loss':
                current_cycle['profit'] -= bet_info['bet_amount']
        
        # Detect cycle end
        if current_cycle and not in_cycle and current_cycle['bets']:
            # Cycle ended
            if current_cycle['outcome'] is None:
                current_cycle['outcome'] = 'max_gale'  # Reached max gale
            current_cycle = None
    
    # Cycle statistics
    total_cycles = len(cycles)
    winning_cycles = sum(1 for c in cycles if c['outcome'] == 'win')
    losing_cycles = sum(1 for c in cycles if c['outcome'] == 'max_gale')
    cycle_win_rate = (winning_cycles / total_cycles * 100) if total_cycles > 0 else 0
    
    print(f"Total cycles: {total_cycles}")
    print(f"Winning cycles: {winning_cycles} ({cycle_win_rate:.1f}%)")
    print(f"Losing cycles (max gale): {losing_cycles}")
    print()
    
    # Gale step distribution
    print("[GALE STEP DISTRIBUTION]")
    print("-" * 80)
    gale_distribution = defaultdict(int)
    for cycle in cycles:
        gale_distribution[cycle['final_gale_step']] += 1
    
    for gale_step in sorted(gale_distribution.keys()):
        count = gale_distribution[gale_step]
        percentage = (count / total_cycles * 100) if total_cycles > 0 else 0
        print(f"Gale step {gale_step}: {count} cycles ({percentage:.1f}%)")
    print()
    
    # Cycle profit analysis
    print("[CYCLE PROFIT ANALYSIS]")
    print("-" * 80)
    total_cycle_profit = sum(c['profit'] for c in cycles)
    avg_cycle_profit = total_cycle_profit / total_cycles if total_cycles > 0 else 0
    winning_cycle_profit = sum(c['profit'] for c in cycles if c['outcome'] == 'win')
    losing_cycle_loss = sum(abs(c['profit']) for c in cycles if c['outcome'] == 'max_gale')
    
    print(f"Total cycle profit: {total_cycle_profit:.2f}")
    print(f"Average cycle profit: {avg_cycle_profit:.2f}")
    print(f"Total winning cycle profit: {winning_cycle_profit:.2f}")
    print(f"Total losing cycle loss: {losing_cycle_loss:.2f}")
    print()
    
    # Drawdown analysis
    print("[DRAWDOWN ANALYSIS]")
    print("-" * 80)
    balance_history = [result.get('balance', stats.get('initial_balance', 1000)) for result in results]
    initial_balance = stats.get('initial_balance', 1000)
    peak_balance = initial_balance
    max_drawdown = 0
    max_drawdown_percent = 0
    
    for balance in balance_history:
        if balance > peak_balance:
            peak_balance = balance
        drawdown = peak_balance - balance
        if drawdown > max_drawdown:
            max_drawdown = drawdown
            max_drawdown_percent = (drawdown / peak_balance * 100) if peak_balance > 0 else 0
    
    min_balance = min(balance_history)
    print(f"Peak balance: {peak_balance:.2f}")
    print(f"Minimum balance: {min_balance:.2f}")
    print(f"Maximum drawdown: {max_drawdown:.2f} ({max_drawdown_percent:.2f}%)")
    print()
    
    # Streak analysis
    print("[STREAK ANALYSIS]")
    print("-" * 80)
    entry_streaks = [c['entry_streak'] for c in cycles]
    streak_distribution = defaultdict(int)
    for streak in entry_streaks:
        streak_distribution[streak] += 1
    
    print("Entry streak distribution:")
    for streak in sorted(streak_distribution.keys()):
        count = streak_distribution[streak]
        percentage = (count / total_cycles * 100) if total_cycles > 0 else 0
        print(f"  Streak {streak}: {count} cycles ({percentage:.1f}%)")
    print()
    
    # Bet frequency by streak length
    print("[BET FREQUENCY BY STREAK LENGTH]")
    print("-" * 80)
    streak_bet_count = defaultdict(int)
    for result in results:
        bet_decision = result.get('bet_decision')
        if bet_decision:
            streak_length = bet_decision.get('streak_length', 0)
            if streak_length > 0:
                streak_bet_count[streak_length] += 1
    
    for streak in sorted(streak_bet_count.keys()):
        count = streak_bet_count[streak]
        print(f"  Streak {streak}: {count} bets")
    print()
    
    # Win/Loss by gale step
    print("[WIN/LOSS BY GALE STEP]")
    print("-" * 80)
    gale_wins = defaultdict(int)
    gale_losses = defaultdict(int)
    
    for cycle in cycles:
        for bet in cycle['bets']:
            gale_step = bet['gale_step']
            if bet['outcome'] == 'win':
                gale_wins[gale_step] += 1
            elif bet['outcome'] == 'loss':
                gale_losses[gale_step] += 1
    
    for gale_step in sorted(set(list(gale_wins.keys()) + list(gale_losses.keys()))):
        wins = gale_wins[gale_step]
        losses = gale_losses[gale_step]
        total = wins + losses
        win_rate = (wins / total * 100) if total > 0 else 0
        print(f"Gale step {gale_step}: {wins} wins, {losses} losses ({win_rate:.1f}% win rate)")
    print()
    
    # Longest losing streak
    print("[LOSING STREAK ANALYSIS]")
    print("-" * 80)
    max_losing_streak = 0
    current_losing_streak = 0
    
    for result in results:
        bet_outcome = result.get('bet_outcome')
        if bet_outcome == 'loss':
            current_losing_streak += 1
            max_losing_streak = max(max_losing_streak, current_losing_streak)
        elif bet_outcome == 'win':
            current_losing_streak = 0
    
    print(f"Longest losing streak: {max_losing_streak} consecutive losses")
    print()
    
    # Balance progression
    print("[BALANCE PROGRESSION]")
    print("-" * 80)
    balance_changes = []
    for i in range(1, len(balance_history)):
        change = balance_history[i] - balance_history[i-1]
        if change != 0:  # Only track actual changes
            balance_changes.append(change)
    
    if balance_changes:
        avg_change = sum(balance_changes) / len(balance_changes)
        print(f"Average balance change per bet: {avg_change:.2f}")
        print(f"Largest single gain: {max(balance_changes):.2f}")
        print(f"Largest single loss: {min(balance_changes):.2f}")
    print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"[OK] Win rate: {stats.get('win_rate', 0):.2f}% (expected ~48.6%)")
    print(f"[OK] Cycle win rate: {cycle_win_rate:.1f}%")
    print(f"[OK] Net profit: {stats.get('net_profit', 0):.2f} ({stats.get('net_profit', 0) / stats.get('initial_balance', 1000) * 100:.1f}% return)")
    print(f"[OK] Maximum drawdown: {max_drawdown:.2f} ({max_drawdown_percent:.2f}%)")
    print(f"[OK] Longest losing streak: {max_losing_streak}")
    print(f"[OK] Total cycles: {total_cycles}")
    print()
    
    # Recommendations
    print("[RECOMMENDATIONS]")
    print("-" * 80)
    if cycle_win_rate < 50:
        print("[WARNING] Cycle win rate below 50% - consider adjusting strategy parameters")
    if max_drawdown_percent > 20:
        print("[WARNING] High drawdown detected - consider lower max_gales or smaller base_bet")
    if max_losing_streak > 5:
        print(f"[WARNING] Long losing streak ({max_losing_streak}) - ensure sufficient balance")
    
    if stats.get('win_rate', 0) > 48 and stats.get('win_rate', 0) < 50:
        print("[OK] Win rate is within expected range")
    if max_drawdown_percent < 15:
        print("[OK] Drawdown is manageable")
    if total_cycles > 0:
        print(f"[OK] Strategy is active ({total_cycles} cycles completed)")
    
    print()
    print("=" * 80)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python analyze_detailed_results.py <json_file>")
        sys.exit(1)
    
    analyze_results(sys.argv[1])

