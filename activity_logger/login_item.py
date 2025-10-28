#!/usr/bin/env python3
"""
Login Item Management for macOS
Handles auto-start on login functionality
"""

from AppKit import NSWorkspace, NSURL


class LoginItemManager:
    """Manages auto-start on login for the application"""
    
    def __init__(self, app_path=None):
        """
        Initialize the Login Item Manager.
        
        Args:
            app_path (str): Path to the .app bundle. If None, attempts to auto-detect.
        """
        self.app_path = app_path or self._get_app_path()
        
    def _get_app_path(self):
        """Attempt to auto-detect the app path"""
        import sys
        import os
        
        # If running from within the app bundle
        if '.app/Contents/MacOS' in sys.executable:
            # Extract the app path
            app_path = sys.executable
            while '/Contents/MacOS' not in os.path.dirname(app_path):
                app_path = os.path.dirname(app_path)
            return os.path.dirname(app_path)
        
        # For development/testing - return the expected installed path
        return '/Applications/Activity Logger.app'
    
    def is_enabled(self):
        """Check if the app is set to start at login"""
        try:
            # Get all login items
            ws = NSWorkspace.sharedWorkspace()
            login_items = ws.runningApplications()
            
            # Check if our app is in login items by checking LaunchAgents
            # For a proper implementation, we'd check LSSharedFileList
            # This is a simplified version
            login_services = []
            
            # Try to check via Launch Services
            try:
                from LaunchServices import LSCopyApplicationURLsForBundleIdentifier
                import objc
                
                # Check if app is registered
                bundle_id = "com.activitylogger.app"
                urls = LSCopyApplicationURLsForBundleIdentifier(bundle_id, None)
                
                if urls and len(urls) > 0:
                    # App exists, now check login items
                    return self._check_login_items_via_plist()
                    
            except ImportError:
                # Fallback to checking plist files
                return self._check_login_items_via_plist()
                
            return False
        except Exception as e:
            print(f"Error checking login items: {e}")
            return False
    
    def _check_login_items_via_plist(self):
        """Check login items by examining plist files"""
        import os
        from plistlib import load as load_plist
        
        login_items_path = os.path.expanduser(
            "~/Library/Application Support/com.apple.sharedfilelist/com.apple.LSSharedFileList.LoginItems.sfl"
        )
        
        if not os.path.exists(login_items_path):
            return False
            
        try:
            with open(login_items_path, 'rb') as f:
                plist_data = load_plist(f)
                
            # Search for our app in the login items
            items = plist_data.get('items', [])
            for item in items:
                name = item.get('Name', '')
                if 'Activity Logger' in name:
                    return True
                    
        except Exception as e:
            print(f"Error reading login items: {e}")
            
        return False
    
    def enable(self):
        """Enable auto-start on login"""
        import subprocess
        import os
        
        if not os.path.exists(self.app_path):
            print(f"Error: App not found at {self.app_path}")
            return False
            
        try:
            # Use `open` command to add to login items via Launch Services
            # This is the simplest approach
            cmd = [
                'osascript',
                '-e',
                f'tell application "System Events" to make login item at end with properties {{path:"{self.app_path}", hidden:false}}'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("Auto-start on login enabled")
                return True
            else:
                print(f"Error enabling login item: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error enabling login item: {e}")
            return False
    
    def disable(self):
        """Disable auto-start on login"""
        import subprocess
        
        try:
            # Use osascript to remove from login items
            cmd = [
                'osascript',
                '-e',
                f'tell application "System Events" to delete login item "Activity Logger"'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("Auto-start on login disabled")
                return True
            else:
                print(f"Error disabling login item: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error disabling login item: {e}")
            return False


def main():
    """Test the login item manager"""
    print("Testing Login Item Manager...")
    
    manager = LoginItemManager()
    
    # Check current status
    is_enabled = manager.is_enabled()
    print(f"Auto-start currently enabled: {is_enabled}")
    
    # The actual enable/disable operations require the app to be installed
    # Uncomment to test:
    # manager.enable()
    # manager.disable()


if __name__ == "__main__":
    main()
