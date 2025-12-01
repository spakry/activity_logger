#!/usr/bin/env python3
"""
Setup script for creating the Activity Logger macOS application bundle
Run: python setup_app.py py2app
"""

from setuptools import setup
import os

APP = ['activity_logger/app.py']
APP_NAME = 'Logger'

DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'strip': True,
    'packages': [
        'rumps',
        'keyring',
        'mss',
        'pynput',
        'PIL',
        'openai',
        'pydantic',
        'httpx',
        'torch',
        'transformers',
        'accelerate',
        'bitsandbytes',
        'sentencepiece',
        'timm',
        'Quartz',
        'AppKit',
        'Foundation',
        'Cocoa',
        'keyring.backends.macOS',
        'activity_logger',
    ],
    'includes': [
        'activity_logger.core',
        'activity_logger.local_model',
        'activity_logger.app',
        'activity_logger.settings',
        'activity_logger.login_item',
        'activity_logger.prompts',
    ],
    'excludes': [
        'pydoc',
        'doctest',
        'unittest',
        'difflib',
        'inspect',
        'sqlite3',
        'pip',
        'setuptools',
        'wheel',
        'pkg_resources',
        'distutils',
        'backports',
        'backports.tarfile',
    ],
    'resources': [
        os.path.join('resources', 'wood.icns'),
    ],
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleIdentifier': 'com.activitylogger.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleGetInfoString': 'AI-powered activity logger',
        'CFBundleExecutable': APP_NAME,
        'CFBundleIconFile': 'wood.icns',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.13',
        'LSApplicationCategoryType': 'public.app-category.utilities',
        'LSUIElement': True,
        'NSAccessibilityUsageDescription': 'Activity Logger needs accessibility access to monitor keyboard events for screenshot capture when you press Enter.',
        'NSScreenCaptureUsageDescription': 'Activity Logger captures screenshots to analyze your activities and create activity logs.',
    },
}

setup(
    name=APP_NAME,
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
