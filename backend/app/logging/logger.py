"""
Logging and Monitoring Module
Logs all spins, bets, and outcomes in CSV and JSON formats.
"""

import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

logger = logging.getLogger(__name__)


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
            'spin_number',
            'outcome_number',
            'outcome_color',
            'bet_category',
            'bet_color',
            'bet_amount',
            'balance_before',
            'balance_after',
            'result',
            'profit_loss',
            'strategy',
            'gale_step',
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
        except Exception as e:
            logger.error(f"Error writing to CSV: {e}")
        
        # Add to JSON log
        self.json_logs.append(spin_data)
        
        # Save JSON periodically (every 10 entries)
        if len(self.json_logs) % 10 == 0:
            self._save_json_log()
        
        logger.info(f"Spin logged: #{spin_data.get('spin_number')}, Result: {spin_data.get('result')}")
    
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
            total_bets = len(df[df['bet_type'].notna()])
            wins = len(df[df['result'] == 'win'])
            losses = len(df[df['result'] == 'loss'])
            
            win_rate = (wins / total_bets * 100) if total_bets > 0 else 0
            total_profit_loss = df['profit_loss'].sum() if 'profit_loss' in df.columns else 0
            
            return {
                "total_spins": int(total_spins),
                "total_bets": int(total_bets),
                "wins": int(wins),
                "losses": int(losses),
                "win_rate": round(win_rate, 2),
                "total_profit_loss": round(total_profit_loss, 2),
                "average_bet": round(df['bet_amount'].mean(), 2) if 'bet_amount' in df.columns else 0
            }
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return {}
    
    def export_summary(self, output_file: Optional[str] = None) -> str:
        """
        Export summary report.
        
        Args:
            output_file: Optional output file path
            
        Returns:
            Path to exported file
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.logs_dir / f"summary_{timestamp}.json"
        
        summary = {
            "statistics": self.get_statistics(),
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

