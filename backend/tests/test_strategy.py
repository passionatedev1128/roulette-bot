"""
Example test file for strategies.
"""

import unittest
from backend.app.strategy import MartingaleStrategy, FibonacciStrategy, CustomStrategy


class TestMartingaleStrategy(unittest.TestCase):
    """Test Martingale strategy."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "type": "martingale",
            "base_bet": 10.0,
            "max_gales": 5,
            "multiplier": 2.0,
            "zero_handling": {"rule": "continue_sequence"}
        }
        self.strategy = MartingaleStrategy(self.config)
    
    def test_initial_bet(self):
        """Test initial bet amount."""
        bet = self.strategy.calculate_bet([], 1000.0, {})
        self.assertIsNotNone(bet)
        self.assertEqual(bet['bet_amount'], 10.0)
    
    def test_gale_progression(self):
        """Test gale progression after losses."""
        # Simulate losses
        for _ in range(3):
            self.strategy.update_after_bet({"result": "loss", "balance_after": 1000.0})
        
        bet = self.strategy.calculate_bet([], 1000.0, {"color": "red"})
        expected_amount = 10.0 * (2.0 ** 3)  # 80.0
        self.assertEqual(bet['bet_amount'], expected_amount)


if __name__ == '__main__':
    unittest.main()

