# Activity Logger

An AI-powered activity logger that captures screenshots and analyzes user actions using OpenAI's GPT-4 Vision API. Perfect for tracking computer usage patterns, productivity analysis, or creating activity reports.

## Features

- **Automatic Screenshot Capture**: Takes screenshots when you press Enter
- **AI-Powered Analysis**: Uses OpenAI's GPT-4 Vision to analyze and describe actions
- **Activity Logging**: Saves detailed logs with timestamps
- **Low-Level Key Interception**: Captures Enter key presses before system processing
- **Threaded Processing**: Non-blocking screenshot capture and analysis
- **macOS Optimized**: Built specifically for macOS with proper accessibility permissions

## Prerequisites

- **macOS**: This tool is designed for macOS and uses macOS-specific APIs
- **Python 3.8+**: Required for running the application
- **OpenAI API Key**: You'll need an API key from OpenAI to use the AI analysis features
- **Accessibility Permissions**: The app requires accessibility permissions to intercept keyboard events

## Installation

## Setup

### 1. Download activity-logger using pip

```
pip3 install activity_logger
```
Then add your python to your path
```
echo 'export PATH="$HOME/Library/Python/3.14/bin:$PATH"' >> ~/.zshrc

# Restart zsh to apply the changes
exec zsh

# Run the activity-logger command
activity-logger
```
Provide your OpenAI API key as a flag to activity-logger, and you can customize the behavior.

```bash
  activity-logger --api-key sk-...  # Start with specific API key
  activity-logger                    # Start with default settings
  activity-logger --api-key sk-...  # Start with specific API key
  activity-logger --screenshots ~/MyScreenshots  # Custom screenshot folder
  activity-logger --logs ~/MyLogs    # Custom log directory
```

### 2. Grant Accessibility Permissions

1. Open **System Preferences** → **Security & Privacy** → **Privacy**
2. Select **Accessibility** from the left sidebar
3. Click the lock icon and enter your password
4. Add your Terminal application (or the application you're running the script from)
5. Make sure it's checked/enabled

## Usage

### Command Line Usage

After installation, you can run the activity logger with:

```bash
activity-logger
```

### How It Works

1. **Start the application**: Run the command above
2. **View logs**: Check the `logs/` directory for daily activity logs

### Log Files
- **Activity Logs**: Saved to `logs/actions_log_MM-DD-YY.txt`
- **Format**: Each log entry includes timestamp

## File Structure

```
activity_logger/
├── activity_logger.py      # Main application
├── setup.py               # Package setup
├── requirements.txt       # Dependencies
├── README.md             # This file
├── LICENSE               # MIT License
├── MANIFEST.in           # Package manifest
├── logs/                 # Activity logs directory
│   └── actions_log_*.txt # Daily log files
└── ~/Desktop/Screenshots/ # Screenshots (created automatically)
```

## Dependencies

- `pyautogui` - Screenshot capture
- `pynput` - Input monitoring
- `Pillow` - Image processing
- `openai` - AI API integration
- `pyobjc-framework-Quartz` - macOS system integration

## Troubleshooting

### "Could not create event tap!" Error

This means the application doesn't have accessibility permissions:

1. Go to System Preferences → Security & Privacy → Privacy → Accessibility
2. Add your Terminal/Python application
3. Make sure it's enabled
4. Restart the application

### OpenAI API Errors

- Verify your API key is set correctly: `echo $OPENAI_API_KEY`
- Check you have sufficient API credits
- Ensure you have access to the GPT-4 Vision API

### Performance Issues

- The app uses threading to avoid blocking
- Screenshots and AI analysis run in background threads
- If experiencing lag, consider reducing `max_tokens` in the API call

## Privacy & Security

- Screenshots are saved locally to your Desktop
- AI analysis is sent to OpenAI (review their privacy policy)
- No data is sent to third parties except OpenAI
- You can delete screenshots and logs at any time

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Make sure you're running on macOS with proper permissions