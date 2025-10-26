"""
Activity Logger - AI-powered screenshot analysis and activity tracking

A tool that captures screenshots and uses OpenAI's GPT-4 Vision API to analyze
and log user actions for productivity tracking and analysis.
"""

__version__ = "1.0.0"
__author__ = "Michael Kim"
__email__ = "your.email@example.com"

from .core import ActivityLogger
from .app import ActivityLoggerApp
from .settings import Settings

__all__ = ["ActivityLogger", "ActivityLoggerApp", "Settings"]
