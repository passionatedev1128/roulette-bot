"""
Logging and Monitoring Module
Logs all spins, bets, and outcomes in CSV and JSON formats.
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

# Import standard library logging explicitly to avoid circular import with local logging module
# The local 'logging' directory conflicts with standard library 'logging' module
# Solution: Import from standard library path directly
import sys
import os
import importlib.util

# Get Python standard library path
_python_lib = os.path.dirname(os.__file__)
_stdlib_logging_path = os.path.join(_python_lib, 'logging', '__init__.py')

if os.path.exists(_stdlib_logging_path):
    # Load standard library logging module directly
    _spec = importlib.util.spec_from_file_location('_std_logging', _stdlib_logging_path)
    std_logging = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(std_logging)
else:
    # Fallback: try normal import (may fail if local logging module interferes)
    import logging as std_logging

logger = std_logging.getLogger(__name__)


class RouletteLogger:
    """Handles logging of all bot activities."""
    
    def __init__(self, config: Dict):
        """
        Initialize logger.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logs_dir = Path(config.get('logs_dir', 'logs'))
        self.logs_dir.mkdir(exist_ok=True)
        
        # File paths
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.csv_file = self.logs_dir / f"roulette_log_{timestamp}.csv"
        self.json_file = self.logs_dir / f"roulette_log_{timestamp}.json"
        self.error_log_file = self.logs_dir / f"errors_{timestamp}.log"
        
        # Initialize CSV with headers
        self._initialize_csv()
        
        # JSON log storage
        self.json_logs: List[Dict] = []
        
        logger.info(f"RouletteLogger initialized: CSV={self.csv_file}, JSON={self.json_file}")
    
    def _initialize_csv(self):
        """Initialize CSV file with headers."""
        self.csv_headers = [
            'timestamp',
            'table',
            'spin_number',
            'outcome_number',
            'outcome_color',
            'bet_category',
            'bet_color',
            'bet_amount',
            'stake',
            'balance_before',
            'balance_after',
            'result',
            'profit_loss',
            'strategy',
            'cycle_number',
            'gale_step',
            'streak_length',
            'is_keepalive',
            'detection_confidence',
            'detection_method',
            'errors'
        ]
        
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.csv_headers)
            writer.writeheader()
    
    def log_spin(self, spin_data: Dict):
        """
        Log a complete spin with result and bet information.
        
        Args:
            spin_data: Dictionary with spin information:
            {
                "spin_number": int,
                "outcome_number": int,
                "outcome_color": str,
                "bet_type": str,
                "bet_amount": float,
                "balance_before": float,
                "balance_after": float,
                "result": str ("win", "loss", "no_bet"),
                "profit_loss": float,
                "strategy": str,
                "gale_step": int,
                "detection_confidence": float,
                "detection_method": str,
                "errors": str
            }
        """
        # Add timestamp
        spin_data['timestamp'] = datetime.now().isoformat()
        
        # Ensure all required fields exist with default values
        row_data = {}
        for header in self.csv_headers:
            row_data[header] = spin_data.get(header, '')
        
        # Write to CSV
        try:
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.csv_headers)
                writer.writerow(row_data)
                f.flush()  # Ensure data is written immediately for stats API
        except Exception as e:
            logger.error(f"Error writing to CSV: {e}")
        
        # Add to JSON log
        self.json_logs.append(spin_data)
        
        # Save JSON periodically (every 10 entries)
        if len(self.json_logs) % 10 == 0:
            self._save_json_log()
        
        logger.info(f"Spin logged: #{spin_data.get('spin_number')}, Result: {spin_data.get('result')}")
    
    def update_spin_result(self, spin_number: int, result: str, profit_loss: float, balance_after: float):
        """
        Update an existing spin entry in CSV with final result after bet resolution.
        
        Args:
            spin_number: The spin number to update
            result: Final result ("win", "loss", or "no_bet")
            profit_loss: Profit/loss amount
            balance_after: Balance after the bet
        """
        try:
            # Read all rows from CSV
            rows = []
            with open(self.csv_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            # Find and update the matching row
            updated = False
            for row in rows:
                if str(row.get('spin_number', '')) == str(spin_number):
                    row['result'] = result
                    row['profit_loss'] = str(profit_loss)
                    row['balance_after'] = str(balance_after)
                    updated = True
                    break
            
            if updated:
                # Write all rows back to CSV
                with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=self.csv_headers)
                    writer.writeheader()
                    writer.writerows(rows)
                    f.flush()  # Ensure data is written immediately
                logger.info(f"Updated spin #{spin_number} in CSV: result={result}, profit_loss={profit_loss}")
            else:
                logger.warning(f"Spin #{spin_number} not found in CSV for update")
        except Exception as e:
            logger.error(f"Error updating spin result in CSV: {e}")
    
    def log_bet(self, bet_data: Dict):
        """
        Log a bet placement.
        
        Args:
            bet_data: Dictionary with bet information
        """
        logger.debug(f"Bet logged: {bet_data}")
    
    def log_error(self, error_data: Dict):
        """
        Log an error.
        
        Args:
            error_data: Dictionary with error information
        """
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "error": error_data.get("error", "Unknown error"),
            "type": error_data.get("type", "unknown"),
            "context": error_data.get("context", {}),
            "traceback": error_data.get("traceback")
        }
        
        # Write to error log file
        try:
            with open(self.error_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(error_entry, indent=2) + "\n")
        except Exception as e:
            logger.error(f"Error writing to error log: {e}")
        
        logger.error(f"Error logged: {error_data.get('error')}")
    
    def _save_json_log(self):
        """Save JSON log to file."""
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(self.json_logs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving JSON log: {e}")
    
    def get_statistics(self) -> Dict:
        """
        Calculate statistics from logs.
        
        Returns:
            Dictionary with statistics
        """
        try:
            df = pd.read_csv(self.csv_file)
            
            total_spins = len(df)
            total_bets = len(df[df['bet_amount'].notna() & (df['bet_amount'] > 0)])
            wins = len(df[df['result'] == 'win'])
            losses = len(df[df['result'] == 'loss'])
            
            win_rate = (wins / total_bets * 100) if total_bets > 0 else 0
            total_profit_loss = df['profit_loss'].sum() if 'profit_loss' in df.columns else 0
            
            # Calculate cycles
            cycle_numbers = df['cycle_number'].dropna().unique() if 'cycle_number' in df.columns else []
            total_cycles = len(cycle_numbers)
            
            # Calculate keepalive bets
            if 'is_keepalive' in df.columns:
                keepalive_count = len(df[df['is_keepalive'] == True])
            else:
                keepalive_count = 0
            
            # Calculate winning and losing cycles
            cycles_won = 0
            cycles_lost = 0
            if 'cycle_number' in df.columns and 'result' in df.columns:
                for cycle_num in cycle_numbers:
                    cycle_data = df[df['cycle_number'] == cycle_num]
                    if len(cycle_data[cycle_data['result'] == 'win']) > 0:
                        cycles_won += 1
                    elif len(cycle_data[cycle_data['result'] == 'loss']) > 0:
                        # Check if max gale was reached (last bet in cycle was a loss)
                        last_bet = cycle_data.iloc[-1] if len(cycle_data) > 0 else None
                        if last_bet is not None and last_bet.get('result') == 'loss':
                            max_gale = cycle_data['gale_step'].max() if 'gale_step' in cycle_data.columns else 0
                            if max_gale > 0:  # Had at least one gale
                                cycles_lost += 1
            
            return {
                "total_spins": int(total_spins),
                "total_bets": int(total_bets),
                "wins": int(wins),
                "losses": int(losses),
                "win_rate": round(win_rate, 2),
                "total_profit_loss": round(total_profit_loss, 2),
                "average_bet": round(df['bet_amount'].mean(), 2) if 'bet_amount' in df.columns and len(df[df['bet_amount'].notna()]) > 0 else 0,
                "total_cycles": int(total_cycles),
                "cycles_won": int(cycles_won),
                "cycles_lost": int(cycles_lost),
                "keepalive_bets": int(keepalive_count)
            }
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return {}
    
    def export_summary(self, output_file: Optional[str] = None, stop_triggers: Optional[Dict] = None) -> str:
        """
        Export summary report.
        
        Args:
            output_file: Optional output file path
            stop_triggers: Optional dictionary with stop condition information:
                {
                    "triggered": bool,
                    "type": str ("stop_loss_money", "stop_loss_count", "stop_win_money", "stop_win_count", "manual"),
                    "value": float or int,
                    "threshold": float or int
                }
            
        Returns:
            Path to exported file
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.logs_dir / f"summary_{timestamp}.json"
        
        stats = self.get_statistics()
        
        summary = {
            "session_info": {
                "start_time": self.json_logs[0].get('timestamp') if self.json_logs else None,
                "end_time": datetime.now().isoformat(),
                "total_spins": stats.get("total_spins", 0),
                "total_bets": stats.get("total_bets", 0)
            },
            "statistics": stats,
            "cycles": {
                "total_cycles": stats.get("total_cycles", 0),
                "cycles_won": stats.get("cycles_won", 0),
                "cycles_lost": stats.get("cycles_lost", 0)
            },
            "performance": {
                "wins": stats.get("wins", 0),
                "losses": stats.get("losses", 0),
                "win_rate": stats.get("win_rate", 0),
                "net_pnl": stats.get("total_profit_loss", 0),
                "average_bet": stats.get("average_bet", 0)
            },
            "keepalive": {
                "total_keepalive_bets": stats.get("keepalive_bets", 0)
            },
            "stop_conditions": stop_triggers if stop_triggers else {
                "triggered": False,
                "type": None,
                "value": None,
                "threshold": None
            },
            "log_files": {
                "csv": str(self.csv_file),
                "json": str(self.json_file),
                "errors": str(self.error_log_file)
            }
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            logger.info(f"Summary exported to {output_file}")
            return str(output_file)
        except Exception as e:
            logger.error(f"Error exporting summary: {e}")
            return ""

