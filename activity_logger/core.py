import threading
import mss
from pynput import keyboard, mouse
import datetime
import os
import base64
from openai import OpenAI
import io
import base64
from PIL import Image

## todo find way to prevent lag on pressing enter. 

from Quartz import (
    CGEventTapCreate,
    kCGSessionEventTap,
    kCGHeadInsertEventTap,
    kCGEventKeyDown,
    CGEventMaskBit,
    kCGEventFlagMaskCommand,
    CFRunLoopAddSource,
    CGEventTapEnable,
    CFRunLoopGetCurrent,
    kCFRunLoopCommonModes,
    CFMachPortCreateRunLoopSource,
    CFRunLoopRun,
    CGEventGetIntegerValueField,
    kCGKeyboardEventKeycode
)


def encode_image_from_pil(image):
    buffer = io.BytesIO()        # create an in-memory binary stream
    image.save(buffer, format="PNG")  # write the image as PNG into the buffer
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


class ActivityLogger:
    """
    AI-powered activity logger that captures screenshots and analyzes user actions.
    """
    
    def __init__(self, api_key=None, screenshot_folder=None, log_dir="logs"):
        """
        Initialize the Activity Logger.
        
        Args:
            api_key (str): OpenAI API key. If None, uses OPENAI_API_KEY env var.
            screenshot_folder (str): Folder to save screenshots. Defaults to ~/Desktop/Screenshots
            log_dir (str): Directory to save activity logs. Defaults to 'logs'
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.log_dir = log_dir
        
        # Setup screenshot folder
        if screenshot_folder is None:
            screenshot_folder = os.path.expanduser("~/Desktop/Screenshots")
        self.screenshot_folder = screenshot_folder
        os.makedirs(self.screenshot_folder, exist_ok=True)
        
        # Initialize counters and storage
        self.file_num = 0
        self.saved_files = []
        
        # Keycode for Return/Enter key on Mac
        self.ENTER_KEYCODE = 36
        self.event_tap = None
        
        # Initialize MSS for screenshot capture
        self.mss_instance = mss.mss()
        
        # Setup logging directory
        os.makedirs(self.log_dir, exist_ok=True)
    
    def encode_image(self, image_path):
        """Encode image to base64 for API"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_screenshot_then_log(self, image):
        """Send an in-memory screenshot to ChatGPT for analysis"""
        try:
            base64_image = encode_image_from_pil(image)

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # or "gpt-4o"
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    "Analyze this screenshot and describe the high-level action being performed "
                                    "answer briefly in one concise sentence. Focus on what text was entered, what button is about "
                                    "to be pressed, or what action is being taken. Provide context on"
                                    "where the action is performed, what the action is."
                                ),
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=150,
            )
            chosen_response_content = response.choices[0].message.content 
            self.log_response(chosen_response_content)

            return response.choices[0].message.content

        except Exception as e:
            print(f"Error analyzing screenshot: {e}")
            return "Error analyzing screenshot"
    
    def capture_screenshot(self):
        """Capture and save a screenshot using mss"""
        # Capture screenshot using mss (faster than pyautogui)
        screenshot_data = self.mss_instance.grab(self.mss_instance.monitors[0])
        
        # Convert mss screenshot to PIL Image
        screenshot = Image.frombytes("RGB", screenshot_data.size, screenshot_data.bgra, "raw", "BGRX")
        
        return screenshot
    
    def log_response(self, response_content):
        """Log the AI response to a daily log file"""
        date_str = datetime.datetime.now().strftime("%m-%d-%y")   # CHANGED
        log_filename = f"actions_log_{date_str}.txt"              # CHANGED
        actions_log = os.path.join(self.log_dir, log_filename)          # CHANGED
        
        with open(actions_log, "a") as f:  # same logic, still append
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {response_content}\n")                  # CHANGED
            print(f"[Wrote to] {actions_log}")
            print(f"[Wrote log] {response_content}")
        return response_content     
    
    def keyboard_event_callback(self, proxy, event_type, event, refcon):
        """This runs BEFORE the system processes the key"""
        if event_type == kCGEventKeyDown:
            keycode = CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode)
            
            if keycode == self.ENTER_KEYCODE:
                screenshot = self.capture_screenshot()
                threading.Thread(target=self.save_screenshot, args=(screenshot,), daemon=True).start()
                threading.Thread(target=self.analyze_screenshot_then_log, args=(screenshot,), daemon=True).start()

                if self.event_tap:
                    CGEventTapEnable(self.event_tap, True)
        
        # Return the event to let it continue to the system
        return event
    
    def save_screenshot(self, screenshot):
        """Save screenshot to file"""
        file_path = os.path.join(self.screenshot_folder, f"screenshot_{self.file_num}.png")
        self.file_num += 1 
        screenshot.save(file_path)
        self.saved_files.append(file_path)
        print(f'screenshot saved to {file_path}')
    
    def start(self):
        """Start the activity logger"""
        # Create event tap
        event_mask = CGEventMaskBit(kCGEventKeyDown)
        self.event_tap = CGEventTapCreate(
            kCGSessionEventTap,
            kCGHeadInsertEventTap,
            0,  # Active flag
            event_mask,
            self.keyboard_event_callback,
            None
        )

        if not self.event_tap:
            raise RuntimeError(
                "Could not create event tap! "
                "Make sure the application has Accessibility permissions."
            )

        # Add to run loop
        run_loop_source = CFMachPortCreateRunLoopSource(None, self.event_tap, 0)
        CFRunLoopAddSource(CFRunLoopGetCurrent(), run_loop_source, kCFRunLoopCommonModes)

        print("Low-level keyboard hook active!")
        print("Press Enter to capture screenshot BEFORE system processes it")
        print("Press Ctrl+C to stop\n")

        try:
            CFRunLoopRun()
        except KeyboardInterrupt:
            print("\nStopped.")
    
    def stop(self):
        """Stop the activity logger"""
        if self.event_tap:
            CGEventTapEnable(self.event_tap, False)


def main():
    """Main entry point for the activity logger"""
    try:
        logger = ActivityLogger()
        logger.start()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return 1
    except RuntimeError as e:
        print(f"Permission Error: {e}")
        print("Please grant Accessibility permissions in System Preferences.")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
