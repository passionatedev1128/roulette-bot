"""
Implementation Validation Tool
Run this to verify your bot is perfectly configured before running.
"""

import json
import os
import sys
from pathlib import Path
import cv2


class ImplementationValidator:
    """Validates bot implementation step by step."""
    
    def __init__(self, config_path='config/default_config.json'):
        self.config_path = config_path
        self.errors = []
        self.warnings = []
        self.passed = []
    
    def validate_all(self):
        """Run all validation checks."""
        print("=" * 70)
        print("PERFECT BOT IMPLEMENTATION VALIDATOR")
        print("=" * 70)
        print()
        
        checks = [
            ("Project Structure", self.check_project_structure),
            ("Dependencies", self.check_dependencies),
            ("Configuration File", self.check_config_file),
            ("Detection Settings", self.check_detection_settings),
            ("Betting Coordinates", self.check_betting_coordinates),
            ("Templates", self.check_templates),
            ("Strategy Configuration", self.check_strategy),
            ("Risk Management", self.check_risk_management),
            ("Session Management", self.check_session_management),
            ("Logging Setup", self.check_logging),
        ]
        
        for name, check_func in checks:
            print(f"Checking: {name}...")
            try:
                check_func()
            except Exception as e:
                self.errors.append(f"{name}: {str(e)}")
                print(f"   Error: {e}")
            print()
        
        # Print summary
        self.print_summary()
        
        return len(self.errors) == 0
    
    def check_project_structure(self):
        """Check project structure."""
        required_dirs = [
            'backend/app/detection',
            'backend/app/strategy',
            'backend/app/betting',
            'backend/app/logging',
            'config',
            'templates',
            'logs',
            'test_results'
        ]
        
        for dir_path in required_dirs:
            if not os.path.exists(dir_path):
                self.errors.append(f"Missing directory: {dir_path}")
                print(f"   Missing: {dir_path}")
            else:
                print(f"   {dir_path}")
        
        required_files = [
            'main.py',
            'requirements.txt',
            'backend/app/bot.py',
            'backend/app/detection/screen_detector.py',
            'backend/app/strategy/martingale_strategy.py',
            'backend/app/betting/bet_controller.py',
            self.config_path
        ]
        
        for file_path in required_files:
            if not os.path.exists(file_path):
                self.errors.append(f"Missing file: {file_path}")
                print(f"   Missing: {file_path}")
            else:
                print(f"   {file_path}")
    
    def check_dependencies(self):
        """Check Python dependencies."""
        try:
            import cv2
            print("   OpenCV")
        except ImportError:
            self.errors.append("OpenCV not installed")
            print("   OpenCV")
        
        try:
            import numpy
            print("   NumPy")
        except ImportError:
            self.errors.append("NumPy not installed")
            print("   NumPy")
        
        try:
            import pytesseract
            print("   pytesseract")
        except ImportError:
            self.errors.append("pytesseract not installed")
            print("   pytesseract")
        
        try:
            import pyautogui
            print("   pyautogui")
        except ImportError:
            self.errors.append("pyautogui not installed")
            print("   pyautogui")
        
        # Check Tesseract
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            print("   Tesseract OCR accessible")
        except:
            self.warnings.append("Tesseract OCR not found - templates recommended")
            print("   Tesseract OCR not found")
    
    def check_config_file(self):
        """Check configuration file."""
        if not os.path.exists(self.config_path):
            self.errors.append(f"Config file not found: {self.config_path}")
            print(f"   Config file not found")
            return
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            print("   Config file is valid JSON")
        except json.JSONDecodeError as e:
            self.errors.append(f"Config file has JSON syntax error: {e}")
            print(f"   JSON error: {e}")
            return
        
        # Check required sections
        required_sections = ['detection', 'strategy', 'betting', 'risk', 'session']
        for section in required_sections:
            if section not in config:
                self.errors.append(f"Missing config section: {section}")
                print(f"   Missing section: {section}")
            else:
                print(f"   Section present: {section}")
    
    def check_detection_settings(self):
        """Check detection configuration."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
        except:
            return
        
        detection = config.get('detection', {})
        
        # Check screen region
        screen_region = detection.get('screen_region')
        if screen_region is None:
            self.warnings.append("screen_region not set - using full screen (may be slower)")
            print("   screen_region not set")
        elif isinstance(screen_region, list) and len(screen_region) == 4:
            print(f"   screen_region set: {screen_region}")
        else:
            self.errors.append("screen_region invalid format - should be [x, y, width, height]")
            print("   screen_region invalid")
        
        # Check color ranges
        color_ranges = detection.get('color_ranges', {})
        required_colors = ['red', 'black', 'green']
        for color in required_colors:
            if color in color_ranges:
                print(f"   {color} color range configured")
            else:
                self.warnings.append(f"{color} color range not configured")
                print(f"   {color} color range missing")
        
        # Check templates directory
        templates_dir = detection.get('templates_dir', 'templates')
        if os.path.exists(templates_dir):
            print(f"   Templates directory exists: {templates_dir}")
        else:
            self.warnings.append("Templates directory not found - templates recommended")
            print(f"   Templates directory not found")
    
    def check_betting_coordinates(self):
        """Check betting coordinates are set."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
        except:
            return
        
        betting = config.get('betting', {})
        areas = betting.get('betting_areas', {})
        
        # Check red button
        if 'red' in areas and areas['red']:
            red = areas['red']
            if isinstance(red, list) and len(red) >= 2:
                print(f"   Red button coordinates: {red}")
            else:
                self.errors.append("Red button coordinates invalid")
                print("   Red button coordinates invalid")
        else:
            self.errors.append("Red button coordinates not set - CRITICAL")
            print("   Red button coordinates not set")
        
        # Check black button
        if 'black' in areas and areas['black']:
            black = areas['black']
            if isinstance(black, list) and len(black) >= 2:
                print(f"   Black button coordinates: {black}")
            else:
                self.errors.append("Black button coordinates invalid")
                print("   Black button coordinates invalid")
        else:
            self.errors.append("Black button coordinates not set - CRITICAL")
            print("   Black button coordinates not set")
        
        # Check confirm button
        confirm = betting.get('confirm_button')
        if confirm and isinstance(confirm, list) and len(confirm) >= 2:
            print(f"   Confirm button coordinates: {confirm}")
        else:
            self.warnings.append("Confirm button coordinates not set")
            print("   Confirm button coordinates not set")
    
    def check_templates(self):
        """Check number templates."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
        except:
            return
        
        templates_dir = config.get('detection', {}).get('templates_dir', 'templates')
        
        if not os.path.exists(templates_dir):
            self.warnings.append("Templates directory not found")
            print(f"   Templates directory not found: {templates_dir}")
            return
        
        # Check for templates
        template_count = 0
        for i in range(37):
            template_path = os.path.join(templates_dir, f"number_{i}.png")
            if os.path.exists(template_path):
                # Verify it's a valid image
                img = cv2.imread(template_path)
                if img is not None:
                    template_count += 1
                else:
                    self.warnings.append(f"Template number_{i}.png is invalid")
        
        if template_count == 37:
            print(f"   All 37 templates present and valid")
            self.passed.append("All templates created")
        elif template_count > 0:
            self.warnings.append(f"Only {template_count}/37 templates found")
            print(f"   Only {template_count}/37 templates found")
        else:
            self.warnings.append("No templates found - detection will use OCR only")
            print("   No templates found")
    
    def check_strategy(self):
        """Check strategy configuration."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
        except:
            return
        
        strategy = config.get('strategy', {})
        
        # Check strategy type
        strategy_type = strategy.get('type')
        valid_types = ['martingale', 'fibonacci', 'custom']
        if strategy_type in valid_types:
            print(f"   Strategy type: {strategy_type}")
        else:
            self.errors.append(f"Invalid strategy type: {strategy_type}")
            print(f"   Invalid strategy type: {strategy_type}")
        
        # Check base bet
        base_bet = strategy.get('base_bet')
        if base_bet and base_bet > 0:
            print(f"   Base bet: {base_bet}")
            if base_bet < 1.0:
                self.warnings.append("Base bet is very low")
        else:
            self.errors.append("Base bet not set or invalid")
            print("   Base bet invalid")
        
        # Check max gales
        max_gales = strategy.get('max_gales')
        if max_gales and max_gales > 0:
            print(f"   Max gales: {max_gales}")
        else:
            self.errors.append("Max gales not set")
            print("   Max gales not set")
        
        # Check multiplier (for martingale)
        if strategy_type == 'martingale':
            multiplier = strategy.get('multiplier')
            if multiplier and multiplier > 1.0:
                print(f"   Multiplier: {multiplier}")
            else:
                self.warnings.append("Multiplier not set for martingale")
                print("   Multiplier not set")
    
    def check_risk_management(self):
        """Check risk management settings."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
        except:
            return
        
        risk = config.get('risk', {})
        
        # Check initial balance
        initial_balance = risk.get('initial_balance')
        if initial_balance and initial_balance > 0:
            print(f"   Initial balance: {initial_balance}")
        else:
            self.errors.append("Initial balance not set")
            print("   Initial balance not set")
        
        # Check stop loss
        stop_loss = risk.get('stop_loss')
        if stop_loss is not None:
            if stop_loss < initial_balance:
                print(f"   Stop loss: {stop_loss}")
            else:
                self.errors.append(f"Stop loss ({stop_loss}) must be less than initial balance ({initial_balance})")
                print(f"   Stop loss invalid: {stop_loss} >= {initial_balance}")
        else:
            self.errors.append("Stop loss not set - CRITICAL")
            print("   Stop loss not set")
        
        # Check guarantee fund
        guarantee_fund = risk.get('guarantee_fund_percentage')
        if guarantee_fund and 0 <= guarantee_fund <= 100:
            print(f"   Guarantee fund: {guarantee_fund}%")
        else:
            self.warnings.append("Guarantee fund percentage not set")
            print("   Guarantee fund not set")
    
    def check_session_management(self):
        """Check session management settings."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
        except:
            return
        
        session = config.get('session', {})
        
        # Check maintenance interval
        interval = session.get('maintenance_bet_interval')
        if interval and interval > 0:
            minutes = interval / 60
            print(f"   Maintenance interval: {interval}s ({minutes} minutes)")
        else:
            self.warnings.append("Maintenance bet interval not set")
            print("   Maintenance interval not set")
        
        # Check min bet amount
        min_bet = session.get('min_bet_amount')
        if min_bet and min_bet > 0:
            print(f"   Minimum bet: {min_bet}")
        else:
            self.warnings.append("Minimum bet amount not set")
            print("   Minimum bet not set")
    
    def check_logging(self):
        """Check logging configuration."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
        except:
            return
        
        logging_config = config.get('logging', {})
        logs_dir = logging_config.get('logs_dir', 'logs')
        
        # Check logs directory
        if os.path.exists(logs_dir):
            print(f"   Logs directory exists: {logs_dir}")
        else:
            # Try to create it
            try:
                os.makedirs(logs_dir, exist_ok=True)
                print(f"   Logs directory created: {logs_dir}")
            except Exception as e:
                self.errors.append(f"Cannot create logs directory: {e}")
                print(f"   Cannot create logs directory: {e}")
    
    def print_summary(self):
        """Print validation summary."""
        print("=" * 70)
        print("VALIDATION SUMMARY")
        print("=" * 70)
        
        if self.passed:
            print(f"\n Passed Checks: {len(self.passed)}")
            for item in self.passed:
                print(f"   {item}")
        
        if self.warnings:
            print(f"\n Warnings: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"   {warning}")
        
        if self.errors:
            print(f"\n Errors: {len(self.errors)}")
            for error in self.errors:
                print(f"   {error}")
        
        print("\n" + "=" * 70)
        
        if self.errors:
            print(" IMPLEMENTATION NOT READY")
            print("\nFix all errors before running the bot!")
            print("\nCritical errors must be fixed:")
            for error in self.errors:
                if "CRITICAL" in error or "not set" in error.lower():
                    print(f"  - {error}")
        elif self.warnings:
            print(" IMPLEMENTATION READY WITH WARNINGS")
            print("\nBot will work but may not be optimal.")
            print("Consider addressing warnings for best performance.")
        else:
            print(" PERFECT IMPLEMENTATION READY!")
            print("\nAll checks passed. Bot is ready to run.")
        
        print("=" * 70)


def main():
    """Main entry point."""
    config_path = sys.argv[1] if len(sys.argv) > 1 else 'config/default_config.json'
    
    validator = ImplementationValidator(config_path)
    is_valid = validator.validate_all()
    
    sys.exit(0 if is_valid else 1)


if __name__ == '__main__':
    main()

