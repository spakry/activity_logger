#!/usr/bin/env python3
"""
Settings Management for Activity Logger
Handles secure storage of API key and user preferences
"""

import os
import json
import keyring
from pathlib import Path


class Settings:
    """Manages application settings with secure storage"""
    
    # Service name for keychain
    KEYCHAIN_SERVICE = "com.activitylogger.api"
    
    # Default settings
    DEFAULT_SCREENSHOT_FOLDER = os.path.expanduser("~/Desktop/Screenshots")
    DEFAULT_LOG_DIR = "logs"
    
    def __init__(self):
        """Initialize settings"""
        self.settings_file = Path.home() / ".activity_logger" / "settings.json"
        self._ensure_settings_dir()
        
    def _ensure_settings_dir(self):
        """Create settings directory if it doesn't exist"""
        self.settings_file.parent.mkdir(parents=True, exist_ok=True)
        
    # API Key Management (Keychain)
    
    def get_api_key(self):
        """Retrieve API key from Keychain"""
        try:
            api_key = keyring.get_password(self.KEYCHAIN_SERVICE, "api_key")
            if api_key:
                print("api_key: ", api_key)
                return api_key
        except Exception as e:
            print(f"Error retrieving API key: {e}")
        return None
        
    def set_api_key(self, api_key):
        """Store API key in Keychain"""
        try:
            if api_key:
                keyring.set_password(self.KEYCHAIN_SERVICE, "api_key", api_key)
                return True
            else:
                # Delete if None/empty
                self.delete_api_key()
                return True
        except Exception as e:
            print(f"Error storing API key: {e}")
            return False
            
    def delete_api_key(self):
        """Delete API key from Keychain"""
        try:
            keyring.delete_password(self.KEYCHAIN_SERVICE, "api_key")
        except keyring.errors.PasswordDeleteError:
            # Password doesn't exist, that's fine
            pass
        except Exception as e:
            print(f"Error deleting API key: {e}")
            
    def has_api_key(self):
        """Check if API key is stored"""
        return self.get_api_key() is not None
    
    # User Preferences (JSON file)
    
    def get_preferences(self):
        """Load user preferences from file"""
        if not self.settings_file.exists():
            return self._get_default_preferences()
            
        try:
            with open(self.settings_file, 'r') as f:
                prefs = json.load(f)
                # Ensure all keys exist (for migration)
                defaults = self._get_default_preferences()
                defaults.update(prefs)
                return defaults
        except Exception as e:
            print(f"Error loading preferences: {e}")
            return self._get_default_preferences()
            
    def _get_default_preferences(self):
        """Get default preference values"""
        return {
            "screenshot_folder": self.DEFAULT_SCREENSHOT_FOLDER,
            "log_dir": self.DEFAULT_LOG_DIR,
            "auto_start": False,
            "minimize_to_tray": True
        }
        
    def set_preferences(self, preferences):
        """Save user preferences to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(preferences, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving preferences: {e}")
            return False
            
    def update_preference(self, key, value):
        """Update a single preference"""
        prefs = self.get_preferences()
        prefs[key] = value
        return self.set_preferences(prefs)
        
    def get(self, key, default=None):
        """Get a preference value"""
        prefs = self.get_preferences()
        return prefs.get(key, default)
        
    def set(self, key, value):
        """Set a preference value"""
        return self.update_preference(key, value)
    
    # Convenience methods for specific settings
    
    def get_screenshot_folder(self):
        """Get screenshot folder path"""
        folder = self.get("screenshot_folder", self.DEFAULT_SCREENSHOT_FOLDER)
        os.makedirs(folder, exist_ok=True)
        return folder
        
    def set_screenshot_folder(self, folder):
        """Set screenshot folder path"""
        return self.set("screenshot_folder", folder)
        
    def get_log_dir(self):
        """Get log directory path"""
        log_dir = self.get("log_dir", self.DEFAULT_LOG_DIR)
        os.makedirs(log_dir, exist_ok=True)
        return log_dir
        
    def set_log_dir(self, log_dir):
        """Set log directory path"""
        return self.set("log_dir", log_dir)
        
    def get_auto_start(self):
        """Get auto-start preference"""
        return self.get("auto_start", False)
        
    def set_auto_start(self, value):
        """Set auto-start preference"""
        return self.set("auto_start", bool(value))
        
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        try:
            # Delete Keychain entry
            self.delete_api_key()
            
            # Reset preferences
            self.set_preferences(self._get_default_preferences())
            
            return True
        except Exception as e:
            print(f"Error resetting settings: {e}")
            return False
