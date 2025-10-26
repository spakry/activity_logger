#!/usr/bin/env python3
"""
Setup script for activity_logger package
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Activity Logger - AI-powered screenshot analysis and activity tracking"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="activity-logger",
    version="1.0.0",
    author="Michael Kim",
    author_email="mjunyeopkim@gmail.com",
    description="AI-powered activity logger that captures screenshots and analyzes user actions",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/spakry/activity_logger",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Desktop Environment :: Screen Savers",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "activity-logger=activity_logger.cli:main",
            "activity-logger-gui=activity_logger.app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "activity_logger": ["*.txt", "logs/*.txt"],
    },
    keywords="screenshot, activity, logging, ai, openai, automation, monitoring",
    project_urls={
        "Bug Reports": "https://github.com/spakry/activity_logger/issues",
        "Source": "https://github.com/spakry/activity_logger",
    },
)
