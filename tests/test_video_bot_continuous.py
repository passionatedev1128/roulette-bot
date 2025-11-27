"""
Test Bot with Video - Continuous Processing with Mouse Movement and Betting
Runs the bot continuously processing video, making betting decisions, and moving mouse.
"""

import os
import sys
import argparse
import time
from pathlib import Path

from backend.app.bot import RouletteBot
from backend.app.config_loader import ConfigLoader


def main():
    """Run bot with video in continuous mode."""
    parser = argparse.ArgumentParser(
        description='Test bot with video - continuous processing with mouse movement and betting',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test mode (no real bets, mouse movement only)
  python test_video_bot_continuous.py --test
  
  # Production mode (real bets - WARNING!)
  python test_video_bot_continuous.py
  
  # Custom config
  python test_video_bot_continuous.py --config config/my_config.json --test
        """
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config/default_config.json',
        help='Path to config file (default: config/default_config.json)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run in test mode (no real bets, just mouse movement)'
    )
    parser.add_argument(
        '--video',
        type=str,
        default=None,
        help='Path to video file (overrides BOT_VIDEO_PATH and auto-detection)'
    )
    
    args = parser.parse_args()
    
    # Get video path
    video_path = args.video
    if not video_path:
        video_path = os.environ.get('BOT_VIDEO_PATH')
    if not video_path:
        # Check for common video file names
        project_root = Path(__file__).parent
        common_video_names = ['roleta_brazileria.mp4', 'roulette_video.mp4', 'test_video.mp4']
        for video_name in common_video_names:
            potential_path = project_root / video_name
            if potential_path.exists():
                video_path = str(potential_path)
                print(f" Auto-detected video file: {video_path}")
                break
    
    if not video_path or not Path(video_path).exists():
        print(" Error: Video file not found!")
        print("   Please:")
        print("   - Place 'roleta_brazileria.mp4' in project root")
        print("   - Set BOT_VIDEO_PATH environment variable")
        print("   - Or use --video /path/to/video.mp4")
        sys.exit(1)
    
    # Set video path for bot
    os.environ['BOT_VIDEO_PATH'] = video_path
    
    # Config path
    config_path = args.config
    if not Path(config_path).exists():
        print(f" Error: Config file not found: {config_path}")
        sys.exit(1)
    
    # Load config to show settings
    config = ConfigLoader.load_config(config_path)
    strategy_config = config.get('strategy', {})
    
    test_mode = args.test
    
    # Get detection region info
    detection_config = config.get('detection', {})
    screen_region = detection_config.get('screen_region')
    
    print("=" * 80)
    print("ROULETTE BOT - CONTINUOUS MODE")
    print("=" * 80)
    print(f"Video: {video_path} (for reference/processing)")
    print(f"Config: {config_path}")
    print(f"Mode: {'TEST (no real bets)' if test_mode else 'PRODUCTION (real bets)'}")
    print(f"Strategy: {strategy_config.get('type', 'unknown')}")
    print(f"Base Bet: R$ {strategy_config.get('base_bet', 10.0):.2f}")
    print(f"Max Gales: {strategy_config.get('max_gales', 6)}")
    print(f"Frame Skip: {config.get('detection', {}).get('frame_skip_interval', 10)}")
    print()
    print("DETECTION SETTINGS:")
    if screen_region:
        x, y, w, h = screen_region
        print(f"   Winning numbers: Desktop screen capture")
        print(f"    Region: ({x}, {y}) - {w}x{h} pixels")
        print(f"    Location: Top-left at ({x}, {y})")
    else:
        print(f"    screen_region not configured - using full screen")
    print("=" * 80)
    print()
    
    if test_mode:
        print("  TEST MODE: Bot will:")
        print("   - Detect winning numbers from DESKTOP (screen capture)")
        print("   - Process video continuously (for reference)")
        print("   - Make betting decisions based on strategy")
        print("   - Move mouse to betting positions")
        print("   -  NOT place real bets (test mode)")
    else:
        print("  PRODUCTION MODE: Bot will:")
        print("   - Detect winning numbers from DESKTOP (screen capture)")
        print("   - Process video continuously (for reference)")
        print("   - Make betting decisions based on strategy")
        print("   - Move mouse to betting positions")
        print("   -  PLACE REAL BETS (uses real money!)")
        print()
        print("Make sure:")
        print("   1. Game window is visible on desktop")
        print("   2. Winning number region is visible (use show_detection_region.py to check)")
        print("   3. You're using a test account with minimum bets")
        print("   4. You can stop with Ctrl+C")
    
    print()
    if screen_region:
        print(" Tip: Run 'python show_detection_region.py' to visualize the detection region")
        print()
    response = input("Continue? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        sys.exit(0)
    
    print()
    print("Starting bot...")
    print("Press Ctrl+C to stop")
    print("-" * 80)
    print()
    print("📌 IMPORTANT: Bot will detect winning numbers from DESKTOP screen capture")
    print("   Make sure the game window is visible and positioned correctly!")
    print()
    
    try:
        # Initialize bot (uses ScreenDetector by default - detects from desktop)
        bot = RouletteBot(config_path, test_mode=test_mode)
        
        # Bot uses ScreenDetector which captures from desktop
        # Video is not used for detection, only for reference/processing
        print(f" Bot initialized with ScreenDetector")
        print(f" Winning numbers will be detected from desktop region: {screen_region}")
        print()
        
        # Run bot (this will process continuously, detecting from desktop)
        bot.run()
        
    except KeyboardInterrupt:
        print("\n\n" + "=" * 80)
        print("Bot stopped by user (Ctrl+C)")
        print("=" * 80)
    except Exception as e:
        print(f"\n\n Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

