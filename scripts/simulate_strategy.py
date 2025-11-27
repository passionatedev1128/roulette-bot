"""
Strategy Simulation Script
Test the bot's strategy logic using video frames instead of live screen capture.
"""

import sys
import time
import argparse
from pathlib import Path
from typing import Optional

from backend.app.config_loader import ConfigLoader
from backend.app.bot import RouletteBot
from backend.app.detection.frame_detector import FrameDetector


def simulate_strategy(
    video_path: str,
    config_path: str = 'config/default_config.json',
    max_spins: Optional[int] = None,
    delay_between_spins: float = 0.5,
    verbose: bool = True
):
    """
    Simulate bot strategy using video frames.
    
    Args:
        video_path: Path to video file
        config_path: Path to configuration file
        max_spins: Maximum number of spins to process (None = unlimited)
        delay_between_spins: Delay between processing spins (seconds)
        verbose: Print detailed output
    """
    # Load configuration
    if verbose:
        print(f"Loading configuration from {config_path}...")
    config = ConfigLoader.load_config(config_path)
    
    # Initialize bot
    if verbose:
        print("Initializing bot in test mode...")
    bot = RouletteBot(config_path, test_mode=True)
    
    # Replace detector with frame detector
    if verbose:
        print(f"Loading video: {video_path}")
    frame_detector = FrameDetector(config, video_path)
    bot.detector = frame_detector
    
    # Statistics
    total_spins = 0
    successful_detections = 0
    bets_placed = 0
    wins = 0
    losses = 0
    
    try:
        if verbose:
            print("\n" + "=" * 60)
            print("STRATEGY SIMULATION STARTED")
            print("=" * 60)
            print(f"Video: {video_path}")
            print(f"Strategy: {bot.strategy.strategy_type}")
            print(f"Base bet: {config.get('strategy', {}).get('base_bet', 10.0)}")
            print(f"Max spins: {max_spins or 'unlimited'}")
            print("-" * 60 + "\n")
        
        last_detected_number = None
        consecutive_no_detection = 0
        
        while True:
            # Check max spins limit
            if max_spins and total_spins >= max_spins:
                if verbose:
                    print(f"\nReached maximum spins limit: {max_spins}")
                break
            
            # Capture frame
            frame = frame_detector.capture_screen()
            if frame is None:
                if verbose:
                    print("\nEnd of video reached.")
                break
            
            # Detect result
            detection = bot.detector.detect_result(frame)
            
            if detection is None or detection.get('number') is None:
                consecutive_no_detection += 1
                if consecutive_no_detection > 10 and verbose:
                    print(".", end="", flush=True)  # Progress indicator
                time.sleep(0.1)  # Short delay when no detection
                continue
            
            # Reset consecutive no-detection counter
            consecutive_no_detection = 0
            
            # Check if this is a new result (avoid processing same result multiple times)
            current_number = detection.get('number')
            if current_number == last_detected_number:
                time.sleep(0.1)
                continue
            
            last_detected_number = current_number
            total_spins += 1
            successful_detections += 1
            
            if verbose:
                print(f"\n[Spin {total_spins}] Detected: {current_number} ({detection.get('color', 'N/A')})")
                print(f"  Method: {detection.get('method', 'N/A')}, Confidence: {detection.get('confidence', 0):.2f}")
            
            # Process spin (applies strategy)
            try:
                spin_result = bot.process_spin(detection)
                
                # Check if bet was placed
                bet_decision = spin_result.get('bet_decision')
                if bet_decision:
                    bets_placed += 1
                    bet_type = bet_decision.get('bet_type')
                    bet_amount = bet_decision.get('bet_amount', 0.0)
                    gale_step = bot.strategy.gale_step
                    
                    if verbose:
                        print(f"   Bet decision: {bet_type} - {bet_amount} (Gale step: {gale_step})")
                    
                    # Simulate win/loss (for testing purposes)
                    # In real scenario, you'd wait for next result to determine outcome
                    # For simulation, you can manually determine or use a simple rule
                    # Here we'll just log that a bet was placed
                    if verbose:
                        print(f"   Bet placed (simulated - no actual bet in test mode)")
                else:
                    if verbose:
                        print(f"   No bet decision (strategy conditions not met)")
                
                # Wait before next detection
                time.sleep(delay_between_spins)
                
            except Exception as e:
                if verbose:
                    print(f"   Error processing spin: {e}")
                continue
            
            # Check stop conditions
            if bot.check_stop_conditions():
                if verbose:
                    print("\nStop conditions met (stop loss or max gale reached)")
                break
        
        # Final statistics
        if verbose:
            print("\n" + "=" * 60)
            print("SIMULATION SUMMARY")
            print("=" * 60)
            print(f"Total spins processed: {total_spins}")
            print(f"Successful detections: {successful_detections}")
            print(f"Bets placed: {bets_placed}")
            print(f"Current balance: {bot.current_balance:.2f}")
            print(f"Gale step: {bot.strategy.gale_step}")
            print(f"Result history length: {len(bot.result_history)}")
            print("=" * 60)
        
        # Export logs
        if verbose:
            print("\nLogs saved to logs/ directory")
            stats = bot.logger.get_statistics()
            if stats:
                print(f"Statistics: {stats}")
    
    except KeyboardInterrupt:
        if verbose:
            print("\n\nSimulation stopped by user")
    except Exception as e:
        print(f"\nError during simulation: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        frame_detector.release()
        if verbose:
            print("\nSimulation completed.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Simulate bot strategy using video file')
    parser.add_argument(
        'video',
        type=str,
        help='Path to video file'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config/default_config.json',
        help='Path to configuration file (default: config/default_config.json)'
    )
    parser.add_argument(
        '--max-spins',
        type=int,
        default=None,
        help='Maximum number of spins to process (default: unlimited)'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=0.5,
        help='Delay between processing spins in seconds (default: 0.5)'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Reduce output verbosity'
    )
    
    args = parser.parse_args()
    
    # Check if video exists
    video_path = Path(args.video)
    if not video_path.exists():
        print(f"Error: Video file not found: {video_path}")
        sys.exit(1)
    
    # Check if config exists
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Configuration file not found: {config_path}")
        sys.exit(1)
    
    # Run simulation
    simulate_strategy(
        str(video_path),
        str(config_path),
        args.max_spins,
        args.delay,
        verbose=not args.quiet
    )


if __name__ == '__main__':
    main()

