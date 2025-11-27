"""
Test Mouse Positions During Video Processing
Tests if the bot moves mouse to correct positions when betting during video processing.
"""

import cv2
import sys
import time
import pyautogui
from pathlib import Path
from typing import Optional, Dict
import argparse

from backend.app.detection.frame_detector import FrameDetector
from backend.app.config_loader import ConfigLoader
from backend.app.strategy.even_odd_strategy import EvenOddStrategy
from backend.app.betting.bet_controller import BetController


class MousePositionTester:
    """Test mouse positions during video processing."""
    
    def __init__(self, config_path: str, video_path: str, move_mouse: bool = False):
        """
        Initialize tester.
        
        Args:
            config_path: Path to config file
            video_path: Path to video file
            move_mouse: If True, actually moves mouse. If False, only shows coordinates.
        """
        self.config = ConfigLoader.load_config(config_path)
        self.video_path = video_path
        self.move_mouse = move_mouse
        
        # Initialize components
        self.detector = FrameDetector(self.config, video_path, start_frame=0)
        self.strategy = EvenOddStrategy(self.config.get('strategy', {}))
        self.bet_controller = BetController(self.config)
        
        # Statistics
        self.total_frames = 0
        self.detections = 0
        self.bet_decisions = 0
        self.mouse_movements = []
        
        print("=" * 80)
        print("MOUSE POSITION TESTER - VIDEO MODE")
        print("=" * 80)
        print(f"Video: {video_path}")
        print(f"Config: {config_path}")
        print(f"Mouse Movement: {'ENABLED (will move mouse)' if move_mouse else 'DISABLED (coordinates only)'}")
        print("=" * 80)
        print()
        
        if move_mouse:
            print("  WARNING: Mouse will actually move!")
            print("   Make sure:")
            print("   1. Game window is visible")
            print("   2. You're using a test account")
            print("   3. You can stop with Ctrl+C")
            print()
            response = input("Continue? (yes/no): ").strip().lower()
            if response != 'yes':
                print("Cancelled.")
                sys.exit(0)
            print()
    
    def get_bet_coordinates(self, bet_type: str) -> Optional[tuple]:
        """Get coordinates for bet type."""
        coords = self.bet_controller.find_betting_area(bet_type)
        return coords
    
    def show_mouse_position(self, x: int, y: int, bet_type: str, bet_amount: float):
        """Show where mouse would move (or actually move it)."""
        print(f"   Mouse Position: ({x}, {y})")
        print(f"   Bet Type: {bet_type}")
        print(f"   Bet Amount: {bet_amount:.2f}")
        
        if self.move_mouse:
            try:
                # Move mouse to position (slowly so you can see it)
                pyautogui.moveTo(x, y, duration=0.5)
                print(f"   Mouse moved to ({x}, {y})")
                time.sleep(0.5)  # Pause so you can see
                # Don't actually click - just show movement
            except Exception as e:
                print(f"   Error moving mouse: {e}")
        else:
            print(f"  [SIMULATION MODE - Mouse not moved]")
        
        # Store for summary
        self.mouse_movements.append({
            'x': x,
            'y': y,
            'bet_type': bet_type,
            'bet_amount': bet_amount
        })
    
    def process_video(self, max_frames: Optional[int] = None, frame_skip: int = 30):
        """Process video and show mouse positions for betting decisions."""
        print("\n" + "=" * 80)
        print("PROCESSING VIDEO")
        print("=" * 80)
        print(f"Frame skip: {frame_skip} (process every {frame_skip}th frame)")
        if max_frames:
            print(f"Max frames: {max_frames}")
        print()
        
        frame_count = 0
        result_history = []
        
        try:
            while True:
                # Capture frame
                frame = self.detector.capture_screen()
                if frame is None:
                    print("\nEnd of video reached.")
                    break
                
                frame_count += 1
                
                # Skip frames
                if frame_count % frame_skip != 0:
                    continue
                
                self.total_frames += 1
                
                # Detect result
                detection = self.detector.detect_result(frame)
                
                if detection.get('number') is not None:
                    self.detections += 1
                    number = detection.get('number')
                    color = detection.get('color', 'N/A')
                    confidence = detection.get('confidence', 0)
                    
                    # Get frame number
                    frame_num = self.detector.get_current_frame_number()
                    
                    print(f"\n[Frame {frame_num}] Detected: {number} ({color}) [Confidence: {confidence:.2f}]")
                    
                    # Add to history
                    result_history.append({
                        'number': number,
                        'color': color,
                        'even_odd': 'even' if number % 2 == 0 and number != 0 else 'odd' if number != 0 else None
                    })
                    
                    # Calculate bet decision
                    try:
                        bet_decision = self.strategy.calculate_bet(
                            result_history,
                            self.strategy.current_balance,
                            detection
                        )
                        
                        if bet_decision:
                            self.bet_decisions += 1
                            bet_type = bet_decision.get('bet_type')
                            bet_amount = bet_decision.get('bet_amount', 0.0)
                            
                            print(f"   Bet Decision: {bet_type} - {bet_amount:.2f}")
                            
                            # Get coordinates
                            coords = self.get_bet_coordinates(bet_type)
                            
                            if coords:
                                x, y = coords
                                self.show_mouse_position(x, y, bet_type, bet_amount)
                            else:
                                print(f"   Coordinates not found for {bet_type}")
                                print(f"    Check config: betting.betting_areas.{bet_type}")
                        else:
                            print(f"   No bet decision (strategy conditions not met)")
                            # Show strategy state
                            even_streak = self.strategy.current_even_streak
                            odd_streak = self.strategy.current_odd_streak
                            cycle_active = self.strategy.cycle_active
                            print(f"    Even streak: {even_streak}, Odd streak: {odd_streak}, Cycle: {cycle_active}")
                    
                    except Exception as e:
                        print(f"   Error calculating bet: {e}")
                        import traceback
                        traceback.print_exc()
                
                # Check max frames
                if max_frames and self.total_frames >= max_frames:
                    print(f"\nReached max frames limit ({max_frames}).")
                    break
                
                # Small delay
                time.sleep(0.1)
        
        except KeyboardInterrupt:
            print("\n\nStopped by user (Ctrl+C)")
        
        finally:
            self.print_summary()
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total frames processed: {self.total_frames}")
        print(f"Successful detections: {self.detections}")
        print(f"Bet decisions made: {self.bet_decisions}")
        print(f"Mouse movements: {len(self.mouse_movements)}")
        print()
        
        if self.mouse_movements:
            print("Mouse Movement Details:")
            print("-" * 80)
            for i, move in enumerate(self.mouse_movements, 1):
                print(f"{i}. {move['bet_type']:10s}  ({move['x']:4d}, {move['y']:4d}) - R$ {move['bet_amount']:.2f}")
            print()
            
            # Show unique positions
            unique_positions = {}
            for move in self.mouse_movements:
                key = (move['x'], move['y'])
                if key not in unique_positions:
                    unique_positions[key] = []
                unique_positions[key].append(move['bet_type'])
            
            print("Unique Mouse Positions:")
            print("-" * 80)
            for (x, y), bet_types in unique_positions.items():
                print(f"  ({x:4d}, {y:4d}): {', '.join(set(bet_types))}")
            print()
        
        print("=" * 80)
        print("\nNext steps:")
        print("  1. Verify coordinates match your game's betting buttons")
        print("  2. If coordinates are wrong, update config/default_config.json")
        print("  3. Run with --move-mouse to test actual mouse movement")
        print("  4. Use test_betting.py to test individual bet types")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Test mouse positions during video processing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test coordinates only (no mouse movement)
  python test_mouse_positions_video.py roleta_brazileria.mp4
  
  # Test with actual mouse movement
  python test_mouse_positions_video.py roleta_brazileria.mp4 --move-mouse
  
  # Test with custom config
  python test_mouse_positions_video.py roleta_brazileria.mp4 --config config/my_config.json
  
  # Limit to 50 frames
  python test_mouse_positions_video.py roleta_brazileria.mp4 --max-frames 50
        """
    )
    
    parser.add_argument(
        'video',
        type=str,
        help='Path to video file'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config/default_config.json',
        help='Path to config file (default: config/default_config.json)'
    )
    parser.add_argument(
        '--move-mouse',
        action='store_true',
        help='Actually move mouse (default: simulation only)'
    )
    parser.add_argument(
        '--max-frames',
        type=int,
        default=None,
        help='Maximum frames to process (default: unlimited)'
    )
    parser.add_argument(
        '--frame-skip',
        type=int,
        default=30,
        help='Process every Nth frame (default: 30)'
    )
    
    args = parser.parse_args()
    
    # Check if video exists
    if not Path(args.video).exists():
        print(f"Error: Video file not found: {args.video}")
        sys.exit(1)
    
    # Check if config exists
    if not Path(args.config).exists():
        print(f"Error: Config file not found: {args.config}")
        sys.exit(1)
    
    # Create tester
    tester = MousePositionTester(
        args.config,
        args.video,
        move_mouse=args.move_mouse
    )
    
    # Process video
    tester.process_video(
        max_frames=args.max_frames,
        frame_skip=args.frame_skip
    )


if __name__ == '__main__':
    main()

