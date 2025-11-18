#!/bin/bash
# Run the activity logger from CLI using the bundled Python

cd /Users/michaelkim/src/activity_logger

# Use the Python from the bundled app which has all dependencies
PYTHON_BIN="/Users/michaelkim/src/activity_logger/dist/Logger.app/Contents/MacOS/python"

if [ ! -f "$PYTHON_BIN" ]; then
    echo "Error: Python binary not found at $PYTHON_BIN"
    echo "Please build the app first or install dependencies:"
    echo "  pip3 install -e ."
    exit 1
fi

# Run the CLI module
export PYTHONPATH="/Users/michaelkim/src/activity_logger:$PYTHONPATH"
"$PYTHON_BIN" -m activity_logger.cli "$@"


