"""
Strategy Manager / Navigator
Manages multiple strategies and switches between them based on performance.
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import deque

from .base_strategy import StrategyBase
from .even_odd_strategy import EvenOddStrategy
from .martingale_strategy import MartingaleStrategy
from .fibonacci_strategy import FibonacciStrategy
from .custom_strategy import CustomStrategy

logger = logging.getLogger(__name__)


class StrategyPerformance:
    """Tracks performance metrics for a strategy."""
    
    def __init__(self, strategy_name: str):
        self.strategy_name = strategy_name
        self.total_bets = 0
        self.wins = 0
        self.losses = 0
        self.total_profit = 0.0
        self.total_loss = 0.0
        self.cycles_completed = 0
        self.cycles_won = 0
        self.cycles_lost = 0
        self.recent_performance = deque(maxlen=20)  # Last 20 bets
        self.last_used = None
        self.is_active = False
        
    def update(self, bet_result: Dict):
        """Update performance metrics."""
        self.total_bets += 1
        self.last_used = datetime.now()
        
        result = bet_result.get('result')
        bet_amount = bet_result.get('bet_amount', 0)
        
        if result == 'win':
            self.wins += 1
            self.total_profit += bet_amount
            self.recent_performance.append(1)  # 1 = win
        elif result == 'loss':
            self.losses += 1
            self.total_loss += bet_amount
            self.recent_performance.append(0)  # 0 = loss
        
        # Update cycle stats if available
        if bet_result.get('cycle_ended'):
            self.cycles_completed += 1
            if result == 'win':
                self.cycles_won += 1
            else:
                self.cycles_lost += 1
    
    def get_win_rate(self) -> float:
        """Get overall win rate."""
        if self.total_bets == 0:
            return 0.0
        return (self.wins / self.total_bets) * 100.0
    
    def get_recent_win_rate(self) -> float:
        """Get win rate of last N bets."""
        if len(self.recent_performance) == 0:
            return 0.0
        wins = sum(self.recent_performance)
        return (wins / len(self.recent_performance)) * 100.0
    
    def get_net_profit(self) -> float:
        """Get net profit (profit - loss)."""
        return self.total_profit - self.total_loss
    
    def get_profit_per_bet(self) -> float:
        """Get average profit per bet."""
        if self.total_bets == 0:
            return 0.0
        return self.get_net_profit() / self.total_bets
    
    def get_cycle_win_rate(self) -> float:
        """Get cycle win rate."""
        if self.cycles_completed == 0:
            return 0.0
        return (self.cycles_won / self.cycles_completed) * 100.0
    
    def get_score(self) -> float:
        """
        Calculate strategy score for selection.
        Higher score = better strategy.
        """
        score = 0.0
        
        # Factor 1: Recent win rate (40% weight)
        recent_wr = self.get_recent_win_rate()
        score += (recent_wr / 100.0) * 0.4
        
        # Factor 2: Overall win rate (20% weight)
        overall_wr = self.get_win_rate()
        score += (overall_wr / 100.0) * 0.2
        
        # Factor 3: Profit per bet (30% weight)
        profit_per_bet = self.get_profit_per_bet()
        # Normalize: assume max profit per bet is 20.0
        normalized_profit = max(0, min(profit_per_bet / 20.0, 1.0))
        score += normalized_profit * 0.3
        
        # Factor 4: Cycle win rate (10% weight)
        cycle_wr = self.get_cycle_win_rate()
        score += (cycle_wr / 100.0) * 0.1
        
        return score
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for logging/reporting."""
        return {
            "strategy_name": self.strategy_name,
            "total_bets": self.total_bets,
            "wins": self.wins,
            "losses": self.losses,
            "win_rate": self.get_win_rate(),
            "recent_win_rate": self.get_recent_win_rate(),
            "net_profit": self.get_net_profit(),
            "profit_per_bet": self.get_profit_per_bet(),
            "cycles_completed": self.cycles_completed,
            "cycles_won": self.cycles_won,
            "cycle_win_rate": self.get_cycle_win_rate(),
            "score": self.get_score(),
            "is_active": self.is_active
        }


class StrategyManager:
    """
    Manages multiple strategies and intelligently switches between them.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize strategy manager.
        
        Args:
            config: Configuration dictionary with strategy settings
        """
        self.config = config
        self.strategies: Dict[str, StrategyBase] = {}
        self.performance: Dict[str, StrategyPerformance] = {}
        self.current_strategy: Optional[StrategyBase] = None
        self.current_strategy_name: Optional[str] = None
        
        # Strategy navigation configuration
        self.navigation_config = config.get('strategy_navigation', {})
        self.enable_navigation = self.navigation_config.get('enabled', True)
        self.evaluation_interval = self.navigation_config.get('evaluation_interval', 10)  # Evaluate every N bets
        self.min_bets_before_switch = self.navigation_config.get('min_bets_before_switch', 5)
        self.switch_threshold = self.navigation_config.get('switch_threshold', 0.15)  # 15% performance difference
        
        # Initialize all available strategies
        self._initialize_strategies(config)
        
        # Select initial strategy
        self._select_initial_strategy()
        
        # Bet counter for evaluation
        self.bet_counter = 0
        
        logger.info(f"StrategyManager initialized with {len(self.strategies)} strategies")
        logger.info(f"Initial strategy: {self.current_strategy_name}")
    
    def _initialize_strategies(self, config: Dict):
        """Initialize all available strategies."""
        strategy_configs = config.get('strategies', {})
        default_strategy_config = config.get('strategy', {})
        
        # Even/Odd Strategy (default - always include if not in strategies)
        if 'even_odd' in strategy_configs:
            even_odd_config = strategy_configs['even_odd']
        elif default_strategy_config.get('type') == 'even_odd':
            even_odd_config = default_strategy_config
        else:
            # Use default config as even_odd
            even_odd_config = default_strategy_config.copy()
            even_odd_config['type'] = 'even_odd'
        
        self.strategies['even_odd'] = EvenOddStrategy(even_odd_config)
        self.performance['even_odd'] = StrategyPerformance('even_odd')
        logger.info("Initialized Even/Odd strategy")
        
        # Martingale Strategy
        if 'martingale' in strategy_configs:
            self.strategies['martingale'] = MartingaleStrategy(strategy_configs['martingale'])
            self.performance['martingale'] = StrategyPerformance('martingale')
            logger.info("Initialized Martingale strategy")
        
        # Fibonacci Strategy
        if 'fibonacci' in strategy_configs:
            self.strategies['fibonacci'] = FibonacciStrategy(strategy_configs['fibonacci'])
            self.performance['fibonacci'] = StrategyPerformance('fibonacci')
            logger.info("Initialized Fibonacci strategy")
        
        # Custom Strategy
        if 'custom' in strategy_configs:
            self.strategies['custom'] = CustomStrategy(strategy_configs['custom'])
            self.performance['custom'] = StrategyPerformance('custom')
            logger.info("Initialized Custom strategy")
        
        # If no strategies configured, use default even_odd
        if not self.strategies:
            default_config = config.get('strategy', {})
            self.strategies['even_odd'] = EvenOddStrategy(default_config)
            self.performance['even_odd'] = StrategyPerformance('even_odd')
            logger.info("Using default Even/Odd strategy")
    
    def _select_initial_strategy(self):
        """Select initial strategy to use."""
        initial_strategy = self.navigation_config.get('initial_strategy', 'even_odd')
        
        if initial_strategy in self.strategies:
            self.current_strategy = self.strategies[initial_strategy]
            self.current_strategy_name = initial_strategy
            self.performance[initial_strategy].is_active = True
        else:
            # Fallback to first available strategy
            if self.strategies:
                self.current_strategy_name = list(self.strategies.keys())[0]
                self.current_strategy = self.strategies[self.current_strategy_name]
                self.performance[self.current_strategy_name].is_active = True
    
    def get_current_strategy(self) -> StrategyBase:
        """Get currently active strategy."""
        return self.current_strategy
    
    def calculate_bet(self, history: List[Dict], current_balance: float, last_result: Dict) -> Optional[Dict]:
        """
        Calculate bet using current strategy.
        
        Args:
            history: List of previous results
            current_balance: Current account balance
            last_result: Last roulette result
            
        Returns:
            Bet decision dictionary or None
        """
        if not self.current_strategy:
            logger.error("No strategy selected")
            return None
        
        return self.current_strategy.calculate_bet(history, current_balance, last_result)
    
    def update_after_bet(self, bet_result: Dict):
        """
        Update strategy state after bet is resolved.
        
        Args:
            bet_result: Result of bet (win/loss)
        """
        if not self.current_strategy:
            return
        
        # Update current strategy
        self.current_strategy.update_after_bet(bet_result)
        
        # Update performance tracking
        if self.current_strategy_name in self.performance:
            performance = self.performance[self.current_strategy_name]
            performance.update(bet_result)
        
        # Increment bet counter
        self.bet_counter += 1
        
        # Evaluate strategy performance and switch if needed
        if self.enable_navigation and self.bet_counter >= self.evaluation_interval:
            self._evaluate_and_switch()
            self.bet_counter = 0
    
    def _evaluate_and_switch(self):
        """
        Evaluate all strategies and switch if a better one is found.
        """
        if len(self.strategies) < 2:
            return  # Need at least 2 strategies to switch
        
        current_perf = self.performance.get(self.current_strategy_name)
        if not current_perf or current_perf.total_bets < self.min_bets_before_switch:
            return  # Not enough data to evaluate
        
        # Find best performing strategy
        best_strategy = None
        best_score = -float('inf')
        
        for name, strategy in self.strategies.items():
            perf = self.performance[name]
            
            # Skip if not enough data
            if perf.total_bets < self.min_bets_before_switch:
                continue
            
            score = perf.get_score()
            
            if score > best_score:
                best_score = score
                best_strategy = name
        
        # Switch if significantly better
        if best_strategy and best_strategy != self.current_strategy_name:
            current_score = current_perf.get_score()
            score_diff = best_score - current_score
            
            if score_diff >= self.switch_threshold:
                self._switch_strategy(best_strategy, reason=f"Better performance (score: {best_score:.3f} vs {current_score:.3f})")
    
    def _switch_strategy(self, new_strategy_name: str, reason: str = ""):
        """
        Switch to a different strategy.
        
        Args:
            new_strategy_name: Name of strategy to switch to
            reason: Reason for switching
        """
        if new_strategy_name not in self.strategies:
            logger.error(f"Strategy {new_strategy_name} not found")
            return
        
        old_strategy_name = self.current_strategy_name
        
        # Transfer state to new strategy
        new_strategy = self.strategies[new_strategy_name]
        new_strategy.current_balance = self.current_strategy.current_balance
        new_strategy.bet_history = self.current_strategy.bet_history[-10:]  # Transfer recent history
        
        # Update active status
        if old_strategy_name:
            self.performance[old_strategy_name].is_active = False
        self.performance[new_strategy_name].is_active = True
        
        # Switch
        self.current_strategy = new_strategy
        self.current_strategy_name = new_strategy_name
        
        logger.info(f"Strategy switched: {old_strategy_name} -> {new_strategy_name} ({reason})")
        
        # Emit event
        self._emit_strategy_switch_event(old_strategy_name, new_strategy_name, reason)
    
    def _emit_strategy_switch_event(self, old_strategy: str, new_strategy: str, reason: str):
        """Emit strategy switch event (can be connected to bot's event system)."""
        # This can be connected to bot's event dispatcher if needed
        pass
    
    def force_switch(self, strategy_name: str, reason: str = "Manual switch"):
        """
        Force switch to a specific strategy (manual override).
        
        Args:
            strategy_name: Name of strategy to switch to
            reason: Reason for switching
        """
        self._switch_strategy(strategy_name, reason)
    
    def get_strategy_performance(self, strategy_name: Optional[str] = None) -> Dict:
        """
        Get performance metrics for a strategy.
        
        Args:
            strategy_name: Strategy name (None for current strategy)
            
        Returns:
            Performance dictionary
        """
        if strategy_name is None:
            strategy_name = self.current_strategy_name
        
        if strategy_name in self.performance:
            return self.performance[strategy_name].to_dict()
        
        return {}
    
    def get_all_performance(self) -> Dict:
        """Get performance metrics for all strategies."""
        return {
            name: perf.to_dict()
            for name, perf in self.performance.items()
        }
    
    def get_strategy_info(self) -> Dict:
        """Get current strategy information."""
        if not self.current_strategy:
            return {}
        
        info = self.current_strategy.get_strategy_info()
        info['manager'] = {
            'current_strategy': self.current_strategy_name,
            'total_strategies': len(self.strategies),
            'navigation_enabled': self.enable_navigation,
            'performance': self.get_strategy_performance()
        }
        
        return info
    
    def reset_performance(self, strategy_name: Optional[str] = None):
        """
        Reset performance metrics for a strategy.
        
        Args:
            strategy_name: Strategy name (None for all strategies)
        """
        if strategy_name:
            if strategy_name in self.performance:
                self.performance[strategy_name] = StrategyPerformance(strategy_name)
                logger.info(f"Reset performance for {strategy_name}")
        else:
            # Reset all
            for name in self.performance.keys():
                self.performance[name] = StrategyPerformance(name)
            logger.info("Reset performance for all strategies")

