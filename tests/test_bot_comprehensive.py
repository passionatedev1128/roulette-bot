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
        # Track all processed numbers to prevent duplicates
        self.processed_numbers: set = set()
        self.last_number_frame: Dict[int, int] = {}  # Track last frame each number was processed
        
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
            print(f"Strategy Navigation: {'ENABLED ' if nav_enabled else 'DISABLED'}")
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
            print(f"Templates Loaded: {len(getattr(detector, 'winning_templates', []))}")
            winning_templates = getattr(detector, 'winning_templates', [])
            if winning_templates:
                template_numbers = sorted([t[0] for t in winning_templates])
                print(f"Template Numbers: {template_numbers}")
            print(f"Template Threshold: {getattr(detector, 'winning_template_threshold', 'N/A')}")
            enable_ocr = getattr(detector, 'enable_ocr_fallback', None)
            if enable_ocr is not None:
                print(f"OCR Fallback: {'ENABLED' if enable_ocr else 'DISABLED'}")
                print(f"OCR Confidence Threshold: {getattr(detector, 'ocr_confidence_threshold', 'N/A')}")
        elif hasattr(detector, 'winning_templates'):
            # Handle FrameDetector or other detector types
            print(f"Templates Loaded: {len(getattr(detector, 'winning_templates', []))}")
            winning_templates = getattr(detector, 'winning_templates', [])
            if winning_templates:
                template_numbers = sorted([t[0] for t in winning_templates])
                print(f"Template Numbers: {template_numbers}")
            print(f"Template Threshold: {getattr(detector, 'winning_template_threshold', 'N/A')}")
        print("=" * 80 + "\n")
    
    def check_detection_setup(self) -> bool:
        """Check if detection is properly configured."""
        detector = self.bot.detector
        if not isinstance(detector, ScreenDetector):
            return True
        
        issues = []
        
        # Check templates
        winning_templates = getattr(detector, 'winning_templates', [])
        if len(winning_templates) == 0:
            issues.append("  No winning number templates loaded")
            enable_ocr = getattr(detector, 'enable_ocr_fallback', None)
            if enable_ocr is False:
                issues.append("  OCR fallback is disabled - detection may fail")
        
        # Check screen region
        screen_region = self.detection_config.get('screen_region', [])
        if not screen_region or len(screen_region) != 4:
            issues.append("  Screen region not configured properly")
        
        if issues:
            print("DETECTION SETUP WARNINGS:")
            for issue in issues:
                print(f"  {issue}")
            print()
        
        return len(issues) == 0
    
    def process_spin(self, detection: Dict, frame_number: int) -> bool:
        """
        Process a single spin with correct timing:
        1. Resolve previous pending bet (if any) using current number
        2. Update strategy with bet result
        3. Add current number to bot's result history
        4. Calculate new bet for next spin
        5. Store new bet as pending
        
        Args:
            detection: Detection result
            frame_number: Current frame number
            
        Returns:
            True if spin was processed, False otherwise
        """
        current_number = detection.get('number')
        if current_number is None:
            return False
        
        # Skip if same number was already processed (prevent duplicates)
        # Check if this number was already processed in this test run
        if current_number in self.processed_numbers:
            if self.verbose:
                last_frame = self.last_number_frame.get(current_number, 'unknown')
                print(f"    Skipping duplicate number {current_number} (already processed at frame {last_frame})")
            return False
        
        # Update tracking
        self.last_detected_number = current_number
        self.processed_numbers.add(current_number)
        self.last_number_frame[current_number] = frame_number
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
        
        # STEP 1: Handle pending bet (result of previous bet)
        # This number is the RESULT that resolves the previous bet
        if self.pending_bet:
            bet_type = self.pending_bet['bet_type']
            bet_amount = self.pending_bet['bet_amount']
            previous_gale_step = self.pending_bet.get('gale_step', 0)
            
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
                        print(f"    ZERO - Cycle reset (zero_policy: reset)")
                    # Still need to add result to history and calculate next bet
                    # Continue processing below
                # else: count_as_loss (default)
            
            # Process win/loss
            if won:
                self.stats['wins'] += 1
                self.bot.current_balance += bet_amount
                if self.verbose:
                    print(f"  🎉 WIN! +{bet_amount:.2f} (Balance: {self.bot.current_balance:.2f})")
                
                # Check if cycle ended (first bet in cycle won)
                if previous_gale_step == 0:
                    cycle_ended = True
                    self.stats['cycles_completed'] += 1
                    self.stats['cycles_won'] += 1
            else:
                self.stats['losses'] += 1
                self.bot.current_balance -= bet_amount
                if self.verbose:
                    print(f"   LOSS! -{bet_amount:.2f} (Balance: {self.bot.current_balance:.2f})")
                
                # Check if max gale reached
                if previous_gale_step >= getattr(strategy, 'max_gales', 3):
                    cycle_ended = True
                    self.stats['cycles_completed'] += 1
                    self.stats['cycles_lost'] += 1
                    self.stats['max_gale_reached'] += 1
                    if self.verbose:
                        print(f"    Max gale reached - cycle ended")
            
            # STEP 2: Update strategy with bet result (before adding result to history)
            bet_result_data = {
                'result': 'win' if won else 'loss',
                'bet_amount': bet_amount,
                'balance_after': self.bot.current_balance,
                'cycle_ended': cycle_ended
            }
            
            if hasattr(self.bot, 'strategy_manager') and self.bot.strategy_manager:
                self.bot.strategy_manager.update_after_bet(bet_result_data)
                self.bot.strategy = self.bot.strategy_manager.get_current_strategy()
                strategy = self.bot.strategy_manager.get_current_strategy()
            else:
                self.bot.strategy.update_after_bet(bet_result_data)
                strategy = self.bot.strategy
            
            self.pending_bet = None
        
        # STEP 3: Add current result to bot's history
        # This result is now part of history for calculating the next bet
        self.bot.result_history.append(detection)
        if len(self.bot.result_history) > 100:  # Keep last 100 results
            self.bot.result_history.pop(0)
        
        # Increment bot's spin number (for logging consistency)
        self.bot.spin_number += 1
        
        # Handle zero if needed (strategy-specific handling)
        if is_zero:
            zero_handling = strategy.handle_zero(self.bot.result_history, self.bot.current_balance)
            if self.verbose and zero_handling:
                print(f"  Zero handling: {zero_handling}")
        
        # STEP 4: Calculate new bet for next spin
        # Use the updated strategy state and history
        bet_decision = None
        try:
            if hasattr(self.bot, 'strategy_manager') and self.bot.strategy_manager:
                bet_decision = self.bot.strategy_manager.calculate_bet(
                    self.bot.result_history,
                    self.bot.current_balance,
                    detection
                )
            else:
                bet_decision = strategy.calculate_bet(
                    self.bot.result_history,
                    self.bot.current_balance,
                    detection
                )
            
            if bet_decision:
                self.stats['bets_placed'] += 1
                bet_type = bet_decision.get('bet_type')
                bet_amount = bet_decision.get('bet_amount', 0.0)
                
                # STEP 5: Store as pending bet (to be resolved on next detection)
                self.pending_bet = {
                    'bet_type': bet_type,
                    'bet_amount': bet_amount,
                    'gale_step': bet_decision.get('gale_step', strategy.gale_step),
                    'streak_length': bet_decision.get('streak_length', 0)
                }
                
                # Get updated strategy state
                if hasattr(self.bot, 'strategy_manager') and self.bot.strategy_manager:
                    strategy = self.bot.strategy_manager.get_current_strategy()
                    strategy_name = f" [{self.bot.strategy_manager.current_strategy_name}]"
                else:
                    strategy_name = ""
                
                even_streak = getattr(strategy, 'current_even_streak', 0)
                odd_streak = getattr(strategy, 'current_odd_streak', 0)
                gale_step = strategy.gale_step
                in_cycle = getattr(strategy, 'cycle_active', False)
                
                if self.verbose:
                    print(f"   BET: {bet_type.upper()} - {bet_amount:.2f} (Gale: {gale_step}){strategy_name}")
                    print(f"     Entry streak: {bet_decision.get('streak_length', 0)}")
            else:
                if self.verbose:
                    print(f"   No bet (strategy conditions not met)")
                
                # Update strategy state even if no bet
                if hasattr(self.bot, 'strategy_manager') and self.bot.strategy_manager:
                    strategy = self.bot.strategy_manager.get_current_strategy()
                even_streak = getattr(strategy, 'current_even_streak', 0)
                odd_streak = getattr(strategy, 'current_odd_streak', 0)
                gale_step = strategy.gale_step
                in_cycle = getattr(strategy, 'cycle_active', False)
        
        except Exception as e:
            if self.verbose:
                print(f"   Error calculating bet: {e}")
            import traceback
            traceback.print_exc()
            bet_decision = None
        
        # Store result
        self.results.append({
            'spin': self.stats['total_spins'],
            'frame': frame_number,
            'number': current_number,
            'even_odd': even_odd_str,
            'detection_method': method,
            'confidence': detection.get('confidence', 0),
            'bet_decision': bet_decision,
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
                        print(f"\n Reached maximum spins limit: {self.max_spins}")
                    break
                
                # Check if we've reached the end of video by frame position
                current_frame_pos = int(self.frame_detector.cap.get(cv2.CAP_PROP_POS_FRAMES))
                if current_frame_pos >= total_frames:
                    if self.verbose:
                        print(f"\n End of video reached (frame {current_frame_pos}/{total_frames})")
                    break
                
                # Capture frame - this is the primary way to detect end of video
                frame = self.frame_detector.capture_screen()
                if frame is None:
                    if self.verbose:
                        print(f"\n End of video reached (no more frames available)")
                    break
                
                # Only stop on detection failures if we haven't detected anything yet
                # Once we start detecting, continue until video ends (frame is None)
                if consecutive_failures >= self.max_detection_failures:
                    if self.stats['total_spins'] == 0:
                        # No detections at all - might be wrong region
                        # But still continue processing frames in case detection improves
                        if consecutive_failures >= self.max_detection_failures * 3:
                            if self.verbose:
                                print(f"\n  Too many consecutive detection failures ({consecutive_failures})")
                                print(f"   No numbers detected - check screen_region and templates")
                                print(f"   Continuing to process video but detection may be failing...")
                        # Don't break - continue processing video
                    # If we've detected before, just continue - don't stop on failures
                    # The video will end naturally when frame is None
                
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
                
                # Detect result (pass frame directly to detector)
                detection = self.bot.detector.detect_result(frame)
                
                if detection is None or detection.get('number') is None:
                    consecutive_failures += 1
                    self.stats['detection_failures'] += 1
                    if self.verbose and consecutive_failures % 100 == 0:
                        print(f"  ... {consecutive_failures} consecutive detection failures ...")
                    continue
                
                detected_number = detection.get('number')
                
                # Skip if same number as last detection (number still on screen - normal in video)
                # Also check against all processed numbers to avoid processing duplicates
                if not hasattr(self, 'processed_numbers'):
                    self.processed_numbers = set()
                    self.last_number_frame = {}
                
                if detected_number == self.last_detected_number or detected_number in self.processed_numbers:
                    if self.verbose and detected_number in self.processed_numbers:
                        last_frame = self.last_number_frame.get(detected_number, 'unknown')
                        print(f"    Skipping duplicate number {detected_number} (already processed at frame {last_frame})")
                    continue
                
                # Validate result (only validate when number changes)
                if not self.bot.detector.validate_result(detection):
                    # Validation failed - skip this detection
                    consecutive_failures += 1
                    self.stats['detection_failures'] += 1
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
                print("\n\n  Test stopped by user")
        except Exception as e:
            print(f"\n Error during test: {e}")
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
            print("\n  WARNING: No numbers detected from video!")
            print("   Try:")
            print(f"   1. Adjust start_frame (currently {self.start_frame})")
            print("   2. Check if OCR fallback is enabled in config")
            print("   3. Verify video contains roulette game")
            print("   4. Check screen_region in config matches video")
            print("   5. Verify winning-number templates are loaded")
        
        if stats['bets_placed'] == 0 and stats['total_spins'] > 0:
            print("\n  WARNING: No bets were placed!")
            print("   This might mean:")
            print("   1. Entry conditions not met (streak length too low)")
            print("   2. Strategy is waiting for entry signal")
        
        print()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive bot testing script')
    parser.add_argument('video', type=str, help='Path to video file')
    parser.add_argument('--config', '-c', type=str, default='config/default_config.json',
                       help='Path to configuration file')
    parser.add_argument('--start-frame', '-s', type=int, default=0,
                       help='Frame to start from (default: 0)')
    parser.add_argument('--max-spins', '-m', type=int, default=None,
                       help='Maximum spins to process (default: None = process entire video)')
    parser.add_argument('--max-failures', type=int, default=500,
                       help='Max consecutive detection failures (default: 500)')
    parser.add_argument('--frame-skip', '-f', type=int, default=1,
                       help='Process every Nth frame (default: 1 = all frames)')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Reduce output verbosity')
    parser.add_argument('--save-results', '-o', type=str, default=None,
                       help='Save results to JSON file')
    
    # Filter sys.argv to remove kernel JSON files (Colab/Jupyter issue)
    # These files can appear in sys.argv and cause parsing errors
    # We need to be careful to preserve argument-value pairs
    filtered_argv = []
    argv_list = sys.argv[1:]  # Skip script name
    
    # Flags that expect a value
    flags_needing_value = ['-f', '--frame-skip', '-s', '--start-frame', '-m', '--max-spins', 
                          '--max-failures', '-c', '--config', '-o', '--save-results']
    
    def is_kernel_file(arg):
        """Check if argument is a kernel JSON file."""
        if not arg or not isinstance(arg, str):
            return False
        return (arg.endswith('.json') and 
                ('kernel' in arg or 'runtime' in arg) and
                ('/root/.local/share/jupyter' in arg or 
                 '/tmp' in arg or 
                 arg.startswith('/root')))
    
    i = 0
    while i < len(argv_list):
        arg = argv_list[i]
        
        # Skip kernel files
        if is_kernel_file(arg):
            i += 1
            continue
        
        # Skip empty strings
        if not arg.strip():
            i += 1
            continue
        
        # Check if this is a flag that expects a value
        if arg in flags_needing_value:
            filtered_argv.append(arg)  # Add the flag
            i += 1
            
            # Now find the value for this flag
            # Skip any kernel files that might be in between
            value_found = False
            while i < len(argv_list):
                next_arg = argv_list[i]
                
                # If it's a kernel file, skip it
                if is_kernel_file(next_arg):
                    i += 1
                    continue
                
                # If it's another flag, this flag is missing its value
                if next_arg in flags_needing_value or next_arg.startswith('-'):
                    break
                
                # This looks like a value - add it
                filtered_argv.append(next_arg)
                value_found = True
                i += 1
                break
            
            # If no value found after skipping kernel files, argparse will handle the error
            continue
        
        # Regular argument (not a flag)
        filtered_argv.append(arg)
        i += 1
    
    # If no valid arguments after filtering, use empty list (will show help)
    args = parser.parse_args(filtered_argv if filtered_argv else ['--help'])
    
    # Check if video exists
    if not Path(args.video).exists():
        print(f" Error: Video file not found: {args.video}")
        sys.exit(1)
    
    # Check if config exists
    if not Path(args.config).exists():
        print(f" Error: Configuration file not found: {args.config}")
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
        print(f"\n Results saved to: {output_path}")


if __name__ == '__main__':
    main()

