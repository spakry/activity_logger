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

### Option 1: Install from Source

1. Clone the repository:

```bash
git clone https://github.com/yourusername/activity_logger.git
cd activity_logger
```

2. Install the package:

```bash
pip install -e .
```

### Option 2: Install Dependencies Manually

1. Install required packages:

```bash
pip install -r requirements.txt
```

## Setup

### 1. Set OpenAI API Key

Set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or add it to your shell profile (`.bashrc`, `.zshrc`, etc.):

```bash
echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
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

Or if installed manually:

```bash
python activity_logger.py
```

### How It Works

1. **Start the application**: Run the command above
2. **Press Enter**: Whenever you press Enter in any application, the logger will:
   - Capture a screenshot
   - Send it to OpenAI's GPT-4 Vision API for analysis
   - Log the AI's description of your action
   - Save the screenshot to your Desktop/Screenshots folder
3. **View logs**: Check the `logs/` directory for daily activity logs

### Log Files

- **Screenshots**: Saved to `~/Desktop/Screenshots/`
- **Activity Logs**: Saved to `logs/actions_log_MM-DD-YY.txt`
- **Format**: Each log entry includes timestamp and AI-generated description

## Configuration

### Customizing AI Analysis

Edit the prompt in `activity_logger.py` around line 74-79 to customize how the AI analyzes screenshots:

```python
"text": (
    "Analyze this screenshot and describe the high-level action being performed "
    "answer briefly in one concise sentence. Focus on what text was entered, what button is about "
    "to be pressed, or what action is being taken. Provide context on"
    "where the action is performed, what the action is."
),
```

### Changing Log Directory

Modify the `log_dir` parameter in the `log_response()` function calls to save logs to a different location.

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
2. Open an issue on GitHub
3. Make sure you're running on macOS with proper permissions

## Roadmap

- [ ] Support for other operating systems
- [ ] Configurable hotkeys (not just Enter)
- [ ] Web dashboard for viewing logs
- [ ] Export logs to various formats
- [ ] Screenshot compression options
- [ ] Offline mode with local AI models
