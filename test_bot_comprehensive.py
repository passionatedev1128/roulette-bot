"""
Comprehensive Bot Testing Script
Tests detection, strategy, and betting logic with detailed diagnostics.
Works in both local and Colab environments.
"""

import sys
import os
import cv2
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Colab compatibility - mock pyautogui if needed
try:
    import pyautogui
except (ImportError, OSError, KeyError, RuntimeError):
    from unittest.mock import MagicMock
    sys.modules['pyautogui'] = MagicMock()
    mock_pyautogui = sys.modules['pyautogui']
    mock_pyautogui.screenshot = MagicMock(return_value=None)
    mock_pyautogui.moveTo = MagicMock()
    mock_pyautogui.click = MagicMock()
    mock_pyautogui.write = MagicMock()
    mock_pyautogui.press = MagicMock()
    mock_pyautogui.PAUSE = 0.1
    mock_pyautogui.FAILSAFE = False

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

from backend.app.config_loader import ConfigLoader
from backend.app.bot import RouletteBot
from backend.app.detection.frame_detector import FrameDetector
from backend.app.detection.screen_detector import ScreenDetector


class BotTester:
    """Comprehensive bot testing class."""
    
    def __init__(
        self,
        video_path: str,
        config_path: str = 'config/default_config.json',
        start_frame: int = 0,
        max_spins: Optional[int] = None,
        max_detection_failures: int = 500,  # Increased for full video scan
        frame_skip: int = 1,
        verbose: bool = True
    ):
        """
        Initialize bot tester.
        
        Args:
            video_path: Path to video file
            config_path: Path to configuration file
            start_frame: Frame to start from
            max_spins: Maximum spins to process (None = unlimited)
            max_detection_failures: Max consecutive detection failures before stopping
            frame_skip: Process every Nth frame (1 = all frames)
            verbose: Print detailed output
        """
        self.video_path = video_path
        self.config_path = config_path
        self.start_frame = start_frame
        self.max_spins = max_spins
        self.max_detection_failures = max_detection_failures
        self.frame_skip = frame_skip
        self.verbose = verbose
        
        # Statistics
        self.stats = {
            'total_frames_processed': 0,
            'total_spins': 0,
            'successful_detections': 0,
            'detection_failures': 0,
            'bets_placed': 0,
            'wins': 0,
            'losses': 0,
            'zeros': 0,
            'cycles_completed': 0,
            'cycles_won': 0,
            'cycles_lost': 0,
            'max_gale_reached': 0,
            'detection_methods': {},
            'numbers_detected': []
        }
        
        # Results storage
        self.results: List[Dict[str, Any]] = []
        self.pending_bet: Optional[Dict[str, Any]] = None
        self.last_detected_number: Optional[int] = None
        
        # Load config
        self.config = ConfigLoader.load_config(config_path)
        self.detection_config = self.config.get('detection', {})
        
        # Initialize bot
        self.bot = RouletteBot(config_path, test_mode=True)
        
        # Initialize frame detector
        self.frame_detector = FrameDetector(self.config, video_path)
        self.frame_detector.cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        self.bot.detector = self.frame_detector
        
        # Get initial balance
        self.initial_balance = self.config.get('risk', {}).get('initial_balance', 1000.0)
        self.bot.current_balance = self.initial_balance
    
    def print_header(self):
        """Print test header with configuration info."""
        print("\n" + "=" * 80)
        print("COMPREHENSIVE BOT TEST")
        print("=" * 80)
        print(f"Video: {self.video_path}")
        print(f"Config: {self.config_path}")
        print(f"Start frame: {self.start_frame}")
        print(f"Max spins: {self.max_spins or 'unlimited'}")
        print(f"Frame skip: {self.frame_skip}")
        print("-" * 80)
        
        # Strategy info
        strategy = self.bot.strategy
        if hasattr(self.bot, 'strategy_manager') and self.bot.strategy_manager:
            nav_enabled = self.config.get('strategy_navigation', {}).get('enabled', False)
            print(f"Strategy Navigation: {'ENABLED ✅' if nav_enabled else 'DISABLED'}")
            if nav_enabled:
                print(f"Current Strategy: {self.bot.strategy_manager.current_strategy_name}")
            strategy = self.bot.strategy_manager.get_current_strategy()
        
        print(f"Strategy Type: {strategy.strategy_type}")
        print(f"Base Bet: {self.config.get('strategy', {}).get('base_bet', 10.0)}")
        print(f"Streak Length: {self.config.get('strategy', {}).get('streak_length', 6)}")
        print(f"Max Gales: {self.config.get('strategy', {}).get('max_gales', 3)}")
        print(f"Zero Policy: {getattr(strategy, 'zero_policy', 'count_as_loss')}")
        print(f"Initial Balance: {self.initial_balance:.2f}")
        print("-" * 80)
        
        # Detection info
        detector = self.bot.detector
        if isinstance(detector, ScreenDetector):
            print(f"Templates Loaded: {len(detector.winning_templates)}")
            if detector.winning_templates:
                template_numbers = sorted([t[0] for t in detector.winning_templates])
                print(f"Template Numbers: {template_numbers}")
            print(f"Template Threshold: {detector.winning_template_threshold}")
            print(f"OCR Fallback: {'ENABLED' if detector.enable_ocr_fallback else 'DISABLED'}")
            print(f"OCR Confidence Threshold: {detector.ocr_confidence_threshold}")
        print("=" * 80 + "\n")
    
    def check_detection_setup(self) -> bool:
        """Check if detection is properly configured."""
        detector = self.bot.detector
        if not isinstance(detector, ScreenDetector):
            return True
        
        issues = []
        
        # Check templates
        if len(detector.winning_templates) == 0:
            issues.append("⚠️  No winning number templates loaded")
            if not detector.enable_ocr_fallback:
                issues.append("⚠️  OCR fallback is disabled - detection may fail")
        
        # Check screen region
        screen_region = self.detection_config.get('screen_region', [])
        if not screen_region or len(screen_region) != 4:
            issues.append("⚠️  Screen region not configured properly")
        
        if issues:
            print("DETECTION SETUP WARNINGS:")
            for issue in issues:
                print(f"  {issue}")
            print()
        
        return len(issues) == 0
    
    def process_spin(self, detection: Dict, frame_number: int) -> bool:
        """
        Process a single spin.
        
        Args:
            detection: Detection result
            frame_number: Current frame number
            
        Returns:
            True if spin was processed, False otherwise
        """
        current_number = detection.get('number')
        if current_number is None:
            return False
        
        # Skip if same number (not a new spin)
        if current_number == self.last_detected_number:
            return False
        
        self.last_detected_number = current_number
        self.stats['total_spins'] += 1
        self.stats['successful_detections'] += 1
        self.stats['numbers_detected'].append(current_number)
        
        # Track detection method
        method = detection.get('method', 'unknown')
        self.stats['detection_methods'][method] = self.stats['detection_methods'].get(method, 0) + 1
        
        # Track zeros
        if current_number == 0:
            self.stats['zeros'] += 1
        
        # Get strategy state before processing
        strategy = self.bot.strategy
        if hasattr(self.bot, 'strategy_manager') and self.bot.strategy_manager:
            strategy = self.bot.strategy_manager.get_current_strategy()
        
        even_streak = getattr(strategy, 'current_even_streak', 0)
        odd_streak = getattr(strategy, 'current_odd_streak', 0)
        gale_step = strategy.gale_step
        in_cycle = getattr(strategy, 'cycle_active', False)
        
        # Determine even/odd
        is_even = (current_number % 2 == 0 and current_number != 0)
        is_odd = (current_number % 2 == 1)
        is_zero = (current_number == 0)
        even_odd_str = "EVEN" if is_even else "ODD" if is_odd else "ZERO"
        
        if self.verbose:
            print(f"\n[Spin {self.stats['total_spins']}] Frame {frame_number}")
            print(f"  Number: {current_number} ({even_odd_str})")
            print(f"  Method: {method}, Confidence: {detection.get('confidence', 0):.2f}")
            print(f"  Even streak: {even_streak}, Odd streak: {odd_streak}")
            print(f"  Gale step: {gale_step}, In cycle: {in_cycle}")
            print(f"  Balance: {self.bot.current_balance:.2f}")
        
        # Handle pending bet (result of previous bet)
        if self.pending_bet:
            bet_type = self.pending_bet['bet_type']
            bet_amount = self.pending_bet['bet_amount']
            
            # Determine win/loss
            won = False
            cycle_ended = False
            
            if bet_type == 'even' and is_even:
                won = True
            elif bet_type == 'odd' and is_odd:
                won = True
            elif is_zero:
                zero_policy = getattr(strategy, 'zero_policy', 'count_as_loss')
                if zero_policy == 'count_as_win':
                    won = True
                elif zero_policy == 'reset':
                    # Reset cycle
                    strategy.cycle_active = False
                    strategy.gale_step = 0
                    self.pending_bet = None
                    if self.verbose:
                        print(f"  ⚠️  ZERO - Cycle reset (zero_policy: reset)")
                    return True
            
            # Process win/loss
            if won:
                self.stats['wins'] += 1
                self.bot.current_balance += bet_amount
                if self.verbose:
                    print(f"  🎉 WIN! +{bet_amount:.2f} (Balance: {self.bot.current_balance:.2f})")
                
                # Check if cycle ended
                if gale_step == 0:  # First bet in cycle won
                    cycle_ended = True
                    self.stats['cycles_completed'] += 1
                    self.stats['cycles_won'] += 1
            else:
                self.stats['losses'] += 1
                self.bot.current_balance -= bet_amount
                if self.verbose:
                    print(f"  ❌ LOSS! -{bet_amount:.2f} (Balance: {self.bot.current_balance:.2f})")
                
                # Check if max gale reached
                if gale_step >= getattr(strategy, 'max_gales', 3):
                    cycle_ended = True
                    self.stats['cycles_completed'] += 1
                    self.stats['cycles_lost'] += 1
                    self.stats['max_gale_reached'] += 1
                    if self.verbose:
                        print(f"  ⚠️  Max gale reached - cycle ended")
            
            # Update strategy
            bet_result_data = {
                'result': 'win' if won else 'loss',
                'bet_amount': bet_amount,
                'balance_after': self.bot.current_balance,
                'cycle_ended': cycle_ended
            }
            
            if hasattr(self.bot, 'strategy_manager') and self.bot.strategy_manager:
                self.bot.strategy_manager.update_after_bet(bet_result_data)
                self.bot.strategy = self.bot.strategy_manager.get_current_strategy()
            else:
                self.bot.strategy.update_after_bet(bet_result_data)
            
            self.pending_bet = None
        
        # Process new spin (calculate bet decision)
        try:
            spin_result = self.bot.process_spin(detection)
            bet_decision = spin_result.get('bet_decision')
            
            if bet_decision:
                self.stats['bets_placed'] += 1
                bet_type = bet_decision.get('bet_type')
                bet_amount = bet_decision.get('bet_amount', 0.0)
                
                # Store as pending bet
                self.pending_bet = {
                    'bet_type': bet_type,
                    'bet_amount': bet_amount,
                    'gale_step': bet_decision.get('gale_step', 0),
                    'streak_length': bet_decision.get('streak_length', 0)
                }
                
                # Get updated strategy state
                strategy = self.bot.strategy
                if hasattr(self.bot, 'strategy_manager') and self.bot.strategy_manager:
                    strategy = self.bot.strategy_manager.get_current_strategy()
                    strategy_name = f" [{self.bot.strategy_manager.current_strategy_name}]"
                else:
                    strategy_name = ""
                
                even_streak = getattr(strategy, 'current_even_streak', 0)
                odd_streak = getattr(strategy, 'current_odd_streak', 0)
                gale_step = strategy.gale_step
                
                if self.verbose:
                    print(f"  ✅ BET: {bet_type.upper()} - {bet_amount:.2f} (Gale: {gale_step}){strategy_name}")
                    print(f"     Entry streak: {bet_decision.get('streak_length', 0)}")
            else:
                if self.verbose:
                    print(f"  → No bet (strategy conditions not met)")
        
        except Exception as e:
            if self.verbose:
                print(f"  ❌ Error processing spin: {e}")
            import traceback
            traceback.print_exc()
        
        # Store result
        self.results.append({
            'spin': self.stats['total_spins'],
            'frame': frame_number,
            'number': current_number,
            'even_odd': even_odd_str,
            'detection_method': method,
            'confidence': detection.get('confidence', 0),
            'bet_decision': bet_decision if 'bet_decision' in locals() else None,
            'pending_bet': self.pending_bet,
            'balance': self.bot.current_balance,
            'even_streak': even_streak,
            'odd_streak': odd_streak,
            'gale_step': gale_step,
            'in_cycle': in_cycle
        })
        
        return True
    
    def run(self) -> Dict[str, Any]:
        """Run the comprehensive test."""
        self.print_header()
        
        # Check detection setup
        self.check_detection_setup()
        
        if self.verbose:
            print("Starting test...\n")
        
        frame_counter = self.start_frame
        consecutive_failures = 0
        
        # Get video info for progress tracking
        total_frames = int(self.frame_detector.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = self.frame_detector.cap.get(cv2.CAP_PROP_FPS)
        estimated_duration = (total_frames - self.start_frame) / fps if fps > 0 else 0
        
        if self.verbose:
            print(f"Video info:")
            print(f"  Total frames: {total_frames}")
            print(f"  Start frame: {self.start_frame}")
            print(f"  Frames to process: {total_frames - self.start_frame}")
            print(f"  Estimated duration: {estimated_duration:.1f} seconds")
            if self.max_spins:
                print(f"  Max spins limit: {self.max_spins}")
            else:
                print(f"  Max spins: unlimited (will process entire video)")
            print()
        
        last_progress = 0
        last_spin_count = 0
        
        try:
            while True:
                # Check limits
                if self.max_spins and self.stats['total_spins'] >= self.max_spins:
                    if self.verbose:
                        print(f"\n✅ Reached maximum spins limit: {self.max_spins}")
                    break
                
                # Only stop on detection failures if we haven't detected anything yet
                # Once we start detecting, be more lenient
                if consecutive_failures >= self.max_detection_failures:
                    if self.stats['total_spins'] == 0:
                        # No detections at all - might be wrong region
                        if self.verbose:
                            print(f"\n⚠️  Too many consecutive detection failures ({consecutive_failures})")
                            print(f"   No numbers detected - check screen_region and templates")
                        break
                    else:
                        # We've detected before, but now failing - might be end of game section
                        # Continue for a bit more before stopping
                        if consecutive_failures >= self.max_detection_failures * 2:
                            if self.verbose:
                                print(f"\n⚠️  Extended detection failures ({consecutive_failures}) - likely end of game")
                            break
                
                # Capture frame
                frame = self.frame_detector.capture_screen()
                if frame is None:
                    if self.verbose:
                        print("\n✅ End of video reached")
                    break
                
                self.stats['total_frames_processed'] += 1
                
                # Skip frames if needed
                if self.frame_skip > 1 and (self.stats['total_frames_processed'] % self.frame_skip != 0):
                    frame_counter += 1
                    continue
                
                frame_counter += 1
                
                # Progress indicator
                if self.verbose and total_frames > 0:
                    progress = int((frame_counter - self.start_frame) / (total_frames - self.start_frame) * 100)
                    if progress >= last_progress + 5:  # Update every 5%
                        print(f"\n📊 Progress: {progress}% | Frame: {frame_counter}/{total_frames} | "
                              f"Spins: {self.stats['total_spins']} | "
                              f"Bets: {self.stats['bets_placed']} | "
                              f"Balance: {self.bot.current_balance:.2f}")
                        last_progress = progress
                
                # Detect result
                detection = self.bot.detector.detect_result(frame)
                
                if detection is None or detection.get('number') is None:
                    consecutive_failures += 1
                    self.stats['detection_failures'] += 1
                    if self.verbose and consecutive_failures % 100 == 0:
                        print(f"  ... {consecutive_failures} consecutive detection failures ...")
                    continue
                
                # Reset failure counter
                consecutive_failures = 0
                
                # Process spin
                if self.process_spin(detection, frame_counter):
                    # Show progress when spins detected
                    if self.verbose and self.stats['total_spins'] > last_spin_count + 10:
                        print(f"\n📊 Progress: {self.stats['total_spins']} spins detected | "
                              f"Frame: {frame_counter}/{total_frames} | "
                              f"Balance: {self.bot.current_balance:.2f}")
                        last_spin_count = self.stats['total_spins']
                    pass
        
        except KeyboardInterrupt:
            if self.verbose:
                print("\n\n⚠️  Test stopped by user")
        except Exception as e:
            print(f"\n❌ Error during test: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.frame_detector.release()
        
        return self.get_results()
    
    def get_results(self) -> Dict[str, Any]:
        """Get comprehensive test results."""
        # Calculate statistics
        win_rate = 0.0
        if (self.stats['wins'] + self.stats['losses']) > 0:
            win_rate = (self.stats['wins'] / (self.stats['wins'] + self.stats['losses'])) * 100
        
        balance_change = self.bot.current_balance - self.initial_balance
        roi = 0.0
        if self.initial_balance > 0:
            roi = (balance_change / self.initial_balance) * 100
        
        # Get final strategy state
        strategy = self.bot.strategy
        if hasattr(self.bot, 'strategy_manager') and self.bot.strategy_manager:
            strategy = self.bot.strategy_manager.get_current_strategy()
        
        results = {
            'test_info': {
                'video_path': self.video_path,
                'config_path': self.config_path,
                'start_frame': self.start_frame,
                'timestamp': datetime.now().isoformat()
            },
            'statistics': {
                **self.stats,
                'win_rate': win_rate,
                'initial_balance': self.initial_balance,
                'final_balance': self.bot.current_balance,
                'balance_change': balance_change,
                'roi_percent': roi,
                'avg_bet_amount': 0.0,
                'total_wagered': 0.0
            },
            'strategy_state': {
                'even_streak': getattr(strategy, 'current_even_streak', 0),
                'odd_streak': getattr(strategy, 'current_odd_streak', 0),
                'gale_step': strategy.gale_step,
                'in_cycle': getattr(strategy, 'cycle_active', False)
            },
            'results': self.results
        }
        
        # Calculate average bet and total wagered
        if self.results:
            bet_amounts = [r['bet_decision']['bet_amount'] for r in self.results 
                          if r.get('bet_decision') and 'bet_amount' in r['bet_decision']]
            if bet_amounts:
                results['statistics']['avg_bet_amount'] = sum(bet_amounts) / len(bet_amounts)
                results['statistics']['total_wagered'] = sum(bet_amounts)
        
        return results
    
    def print_results(self, results: Dict[str, Any]):
        """Print comprehensive test results."""
        stats = results['statistics']
        strategy_state = results['strategy_state']
        
        print("\n" + "=" * 80)
        print("TEST RESULTS")
        print("=" * 80)
        print(f"Total frames processed: {stats['total_frames_processed']}")
        print(f"Total spins: {stats['total_spins']}")
        print(f"Successful detections: {stats['successful_detections']}")
        print(f"Detection failures: {stats['detection_failures']}")
        print(f"Detection success rate: {(stats['successful_detections'] / max(stats['total_frames_processed'], 1) * 100):.1f}%")
        print("-" * 80)
        print(f"Bets placed: {stats['bets_placed']}")
        print(f"Wins: {stats['wins']} | Losses: {stats['losses']}")
        if (stats['wins'] + stats['losses']) > 0:
            print(f"Win rate: {stats['win_rate']:.2f}%")
        else:
            print("Win rate: N/A (no bets placed)")
        print("-" * 80)
        print(f"Initial balance: {stats['initial_balance']:.2f}")
        print(f"Final balance: {stats['final_balance']:.2f}")
        print(f"Balance change: {stats['balance_change']:+.2f}")
        if stats['initial_balance'] > 0:
            print(f"ROI: {stats['roi_percent']:+.2f}%")
        print("-" * 80)
        print(f"Zeros detected: {stats['zeros']}")
        print(f"Cycles completed: {stats['cycles_completed']}")
        print(f"  - Cycles won: {stats['cycles_won']}")
        print(f"  - Cycles lost: {stats['cycles_lost']}")
        print(f"  - Max gale reached: {stats['max_gale_reached']}")
        print("-" * 80)
        print("Detection Methods:")
        for method, count in stats['detection_methods'].items():
            print(f"  - {method}: {count}")
        print("-" * 80)
        print("Final Strategy State:")
        print(f"  Even streak: {strategy_state['even_streak']}")
        print(f"  Odd streak: {strategy_state['odd_streak']}")
        print(f"  Gale step: {strategy_state['gale_step']}")
        print(f"  In cycle: {strategy_state['in_cycle']}")
        print("=" * 80)
        
        # Warnings
        if stats['total_spins'] == 0:
            print("\n⚠️  WARNING: No numbers detected from video!")
            print("   Try:")
            print(f"   1. Adjust start_frame (currently {self.start_frame})")
            print("   2. Check if OCR fallback is enabled in config")
            print("   3. Verify video contains roulette game")
            print("   4. Check screen_region in config matches video")
            print("   5. Verify winning-number templates are loaded")
        
        if stats['bets_placed'] == 0 and stats['total_spins'] > 0:
            print("\n⚠️  WARNING: No bets were placed!")
            print("   This might mean:")
            print("   1. Entry conditions not met (streak length too low)")
            print("   2. Strategy is waiting for entry signal")
        
        print()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive bot testing script')
    parser.add_argument('video', type=str, help='Path to video file')
    parser.add_argument('--config', type=str, default='config/default_config.json',
                       help='Path to configuration file')
    parser.add_argument('--start-frame', type=int, default=0,
                       help='Frame to start from (default: 0)')
    parser.add_argument('--max-spins', type=int, default=None,
                       help='Maximum spins to process (default: None = process entire video)')
    parser.add_argument('--max-failures', type=int, default=500,
                       help='Max consecutive detection failures (default: 500)')
    parser.add_argument('--frame-skip', type=int, default=1,
                       help='Process every Nth frame (default: 1 = all frames)')
    parser.add_argument('--quiet', action='store_true',
                       help='Reduce output verbosity')
    parser.add_argument('--save-results', type=str, default=None,
                       help='Save results to JSON file')
    
    args = parser.parse_args()
    
    # Check if video exists
    if not Path(args.video).exists():
        print(f"❌ Error: Video file not found: {args.video}")
        sys.exit(1)
    
    # Check if config exists
    if not Path(args.config).exists():
        print(f"❌ Error: Configuration file not found: {args.config}")
        sys.exit(1)
    
    # Run test
    tester = BotTester(
        video_path=args.video,
        config_path=args.config,
        start_frame=args.start_frame,
        max_spins=args.max_spins,
        max_detection_failures=args.max_failures,
        frame_skip=args.frame_skip,
        verbose=not args.quiet
    )
    
    results = tester.run()
    tester.print_results(results)
    
    # Save results if requested
    if args.save_results:
        output_path = Path(args.save_results)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✅ Results saved to: {output_path}")


if __name__ == '__main__':
    main()

