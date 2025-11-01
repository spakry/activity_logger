#!/usr/bin/env python3
"""
GUI Application for Activity Logger
Menu bar interface for managing the activity logger
"""

import rumps
import threading
from .core import ActivityLogger
from .settings import Settings
from .login_item import LoginItemManager
import traceback

APP_NAME = "Logger"
class ActivityLoggerApp(rumps.App):
    """Main menu bar application for Logger"""
    
    def __init__(self):
        super().__init__("Logger", icon="/Users/michaelkim/src/activity_logger/resources/wood.icns", template=True, quit_button=None)
        self.logger = None
        self.logger_thread = None
        self.is_running = False
        self.settings = Settings()
        self.login_item_manager = LoginItemManager()

        # Setup menu items
        self.setup_menu()
        
    def _on_logger_status_change(self, status, message):
        """Callback for logger status updates"""
        # This can be used for more sophisticated status updates
        # For now, we keep it simple
        print(f"Logger status: {status} - {message}")
        
    def setup_menu(self):
        self.menu = [
            rumps.MenuItem("Start Logging"),    # handled by decorator
            None,
            rumps.MenuItem("Preferences..."),
            rumps.MenuItem("View Logs"),
            None,
            rumps.MenuItem("Quit"),             # single Quit item only
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
                on_status_change=self._on_logger_status_change,
                capture_mode="focused_window",
            )

            # Preflight Screen Recording permission for focused-window mode
            if getattr(self.logger, 'capture_mode', '') == 'focused_window':
                try:
                    probe = self.logger.capture_focused_window()
                except Exception:
                    probe = None
                if probe is None:
                    import subprocess
                    rumps.alert(
                        title="Screen Recording Required",
                        message=(
                            "Logger needs Screen Recording permission to capture the focused window.\n\n"
                            "Click 'Open Settings' and enable your Python/menubar app in Screen Recording."
                        ),
                        ok_button="Open Settings",
                    )
                    subprocess.run([
                        'open',
                        'x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenCapture'
                    ])
            
                try:
                    self.logger_thread = threading.Thread(target=self.logger.start, daemon=True)
                    self.logger_thread.start()
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    rumps.alert(
                        title="An unexpected error occurred",
                        message=f"An unexpected error occurred: {e} Please kindly email this error to the developer."
                    )

            self.is_running = True
            self.menu["Start Logging"].title = "Stop Logging"
            rumps.notification(
                title= APP_NAME,
                subtitle="Started",
                message="Logging has begun"
            )
            
        except ValueError as e:
            rumps.alert(
                title="Configuration Error",
                message=f"{str(e)}\n\nPlease set your OpenAI API key in Preferences."
            )
        except RuntimeError as e:
            print("Permission error: ", e)
        # Handle permission error with UI
            import subprocess
            rumps.alert(
                title="Permission Required",
                message="Logger needs Accessibility permission to monitor keyboard events.\n\nClick 'Grant Permission' to open System Settings.",
                ok_button="Grant Permission"
            )
            # Open System Preferences to Accessibility pane
            subprocess.run([
                'open', 
                'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'
            ])
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
            title= APP_NAME,
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
    app = ActivityLoggerApp()
    try:
        app.run()
    except Exception as e:
        print(f"\nUnexpected error occurred: {e}")
        traceback.print_exc()
    finally:
        if app:
            app.quit_app(None)



if __name__ == "__main__":
    main()
