#!/usr/bin/env python3
"""
GUI Application for Activity Logger
Menu bar interface for managing the activity logger
"""

import rumps
import threading
from .core import ActivityLogger
from .settings import Settings


class ActivityLoggerApp(rumps.App):
    """Main menu bar application for Activity Logger"""
    
    def __init__(self):
        super().__init__("Activity Logger", icon="📝", template=True)
        self.logger = None
        self.logger_thread = None
        self.is_running = False
        self.settings = Settings()
        
        # Setup menu items
        self.setup_menu()
        
    def _on_logger_status_change(self, status, message):
        """Callback for logger status updates"""
        # This can be used for more sophisticated status updates
        # For now, we keep it simple
        print(f"Logger status: {status} - {message}")
        
    def setup_menu(self):
        """Initialize the menu items"""
        self.menu = [
            rumps.MenuItem("Start Logging", callback=self.start_stop_logging),
            None,  # Separator
            rumps.MenuItem("Preferences...", callback=self.show_preferences),
            rumps.MenuItem("View Logs", callback=self.view_logs),
            None,  # Separator
            rumps.MenuItem("Quit", callback=self.quit_app)
        ]
        
    @rumps.clicked("Start Logging")
    def start_stop_logging(self, sender):
        """Start or stop the activity logger"""
        if not self.is_running:
            self.start_logging()
        else:
            self.stop_logging()
            
    def start_logging(self):
        """Start the activity logger"""
        try:
            # Get API key from settings (Keychain)
            api_key = self.settings.get_api_key()
            
            if not api_key:
                rumps.alert(
                    title="API Key Required",
                    message="Please set your OpenAI API key in Preferences.",
                    ok="Open Preferences"
                )
                self.show_preferences(None)
                return
            
            # Initialize the logger with API key and settings
            self.logger = ActivityLogger(
                api_key=api_key,
                screenshot_folder=self.settings.get_screenshot_folder(),
                log_dir=self.settings.get_log_dir(),
                on_status_change=self._on_logger_status_change
            )
            
            # Start logger in a background thread
            self.logger_thread = threading.Thread(target=self.logger.start, daemon=True)
            self.logger_thread.start()
            
            self.is_running = True
            self.menu["Start Logging"].title = "Stop Logging"
            rumps.notification(
                title="Activity Logger",
                subtitle="Started",
                message="Logging has begun"
            )
            
        except ValueError as e:
            rumps.alert(
                title="Configuration Error",
                message=f"{str(e)}\n\nPlease set your OpenAI API key in Preferences."
            )
        except RuntimeError as e:
            rumps.alert(
                title="Permission Error",
                message=f"{str(e)}\n\nPlease grant Accessibility permissions in System Preferences."
            )
        except Exception as e:
            rumps.alert(title="Error", message=f"Failed to start logger: {str(e)}")
            
    def stop_logging(self):
        """Stop the activity logger"""
        if self.logger:
            # Stop the logger (thread-safe)
            self.logger.stop()
            self.logger = None
            
        # Update UI
        self.is_running = False
        self.menu["Start Logging"].title = "Start Logging"
        
        rumps.notification(
            title="Activity Logger",
            subtitle="Stopped",
            message="Logging has stopped"
        )
        
    @rumps.clicked("Preferences...")
    def show_preferences(self, sender):
        """Show preferences window (placeholder for now)"""
        rumps.alert(
            title="Preferences",
            message="Preferences window coming soon!\n\nFor now, set your API key:\nexport OPENAI_API_KEY='your-key'"
        )
        
    @rumps.clicked("View Logs")
    def view_logs(self, sender):
        """Open the logs directory"""
        import subprocess
        
        log_dir = self.settings.get_log_dir()
        import os
        if os.path.exists(log_dir):
            subprocess.run(["open", log_dir])
        else:
            rumps.alert(title="No Logs", message="Log directory not found.")
            
    @rumps.clicked("Quit")
    def quit_app(self, sender):
        """Quit the application"""
        if self.is_running:
            self.stop_logging()
        rumps.quit_application()


def main():
    """Launch the menu bar application"""
    ActivityLoggerApp().run()


if __name__ == "__main__":
    main()
