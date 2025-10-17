#!/usr/bin/env python3
"""
Command-line interface for Activity Logger
"""

import argparse
import sys
import os
from .core import ActivityLogger


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="AI-powered activity logger that captures screenshots and analyzes user actions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  activity-logger                    # Start with default settings
  activity-logger --api-key sk-...  # Start with specific API key
  activity-logger --screenshots ~/MyScreenshots  # Custom screenshot folder
  activity-logger --logs ~/MyLogs    # Custom log directory

Requirements:
  - OpenAI API key (set OPENAI_API_KEY env var or use --api-key)
  - macOS with Accessibility permissions granted
        """
    )
    
    parser.add_argument(
        "--api-key",
        help="OpenAI API key (default: uses OPENAI_API_KEY environment variable)"
    )
    
    parser.add_argument(
        "--screenshots",
        help="Directory to save screenshots (default: ~/Desktop/Screenshots)"
    )
    
    parser.add_argument(
        "--logs",
        help="Directory to save activity logs (default: logs)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="activity-logger 1.0.0"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize the logger
        logger = ActivityLogger(
            api_key=args.api_key,
            screenshot_folder=args.screenshots,
            log_dir=args.logs or "logs"
        )
        
        print("Starting Activity Logger...")
        print(f"Screenshots will be saved to: {logger.screenshot_folder}")
        print(f"Activity logs will be saved to: {logger.log_dir}")
        print()
        
        # Start the logger
        logger.start()
        
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print()
        print("Please set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        print("  # OR")
        print("  activity-logger --api-key your-api-key-here")
        return 1
        
    except RuntimeError as e:
        print(f"Permission Error: {e}")
        print()
        print("To fix this:")
        print("1. Open System Preferences → Security & Privacy → Privacy")
        print("2. Select 'Accessibility' from the left sidebar")
        print("3. Click the lock icon and enter your password")
        print("4. Add your Terminal application")
        print("5. Make sure it's checked/enabled")
        print("6. Restart this application")
        return 1
        
    except KeyboardInterrupt:
        print("\nActivity Logger stopped by user.")
        return 0
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
