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
    """
    Convert a PIL Image object (e.g., pyautogui.screenshot()) 
    into a base64-encoded PNG string for the API.
    """
    buffer = io.BytesIO()        # create an in-memory binary stream
    image.save(buffer, format="PNG")  # write the image as PNG into the buffer
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create a folder for screenshots
screenshot_folder = os.path.expanduser("~/Desktop/Screenshots")
os.makedirs(screenshot_folder, exist_ok=True)
file_num = 0 
saved_files = []

# Store actions log
actions_log = os.path.join(screenshot_folder, "actions_log.txt")

# Keycode for Return/Enter key on Mac
ENTER_KEYCODE = 36

def encode_image(image_path):
    """Encode image to base64 for API"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_screenshot_then_log(image):
    """Send an in-memory screenshot to ChatGPT for analysis"""
    try:
        base64_image = encode_image_from_pil(image)

        response = client.chat.completions.create(
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
        log_response(chosen_response_content)

        return response.choices[0].message.content

    except Exception as e:
        print(f"Error analyzing screenshot: {e}")
        return "Error analyzing screenshot"

# Initialize MSS for screenshot capture
mss_instance = mss.mss()

def capture_screenshot():
    """Capture and save a screenshot using mss"""
    # Capture screenshot using mss (faster than pyautogui)
    screenshot_data = mss_instance.grab(mss_instance.monitors[0])
    
    # Convert mss screenshot to PIL Image
    screenshot = Image.frombytes("RGB", screenshot_data.size, screenshot_data.bgra, "raw", "BGRX")
    
    return screenshot

def log_response(response_content, log_dir='logs'):
    date_str = datetime.datetime.now().strftime("%m-%d-%y")   # CHANGED
    log_filename = f"actions_log_{date_str}.txt"              # CHANGED
    actions_log = os.path.join(log_dir, log_filename)          # CHANGED
    os.makedirs(log_dir, exist_ok=True)
    
    with open(actions_log, "a") as f:  # same logic, still append
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {response_content}\n")                  # CHANGED
        print(f"[Wrote to] {actions_log}")
        print(f"[Wrote log] {response_content}")
    return response_content     

def keyboard_event_callback(proxy, event_type, event, refcon):
    global event_tap  # ADD THIS LINE

    """This runs BEFORE the system processes the key"""
    if event_type == kCGEventKeyDown:
        keycode = CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode)
        

        if keycode == ENTER_KEYCODE:
        
            screenshot = capture_screenshot()
            threading.Thread(target=save_screenshot, args=(screenshot,), daemon=True).start()
            threading.Thread(target=analyze_screenshot_then_log, args=(screenshot,), daemon=True).start()

            if event_tap:
                CGEventTapEnable(event_tap, True)
    
    # Return the event to let it continue to the system
    return event
def save_screenshot(screenshot):
    global file_num
    file_path = os.path.join(screenshot_folder, f"screenshot_{file_num}.png")
    file_num += 1 
    screenshot.save(file_path)
    saved_files.append(file_path)
    print(f'screenshot saved to {file_path}')

# Create event tap
event_mask = CGEventMaskBit(kCGEventKeyDown)
event_tap = CGEventTapCreate(
    kCGSessionEventTap,
    kCGHeadInsertEventTap,
    0,  # Active flag
    event_mask,
    keyboard_event_callback,
    None
)

if not event_tap:
    print("ERROR: Could not create event tap!")
    print("Make sure Terminal has Accessibility permissions.")
    exit(1)

# Add to run loop
run_loop_source = CFMachPortCreateRunLoopSource(None, event_tap, 0)
CFRunLoopAddSource(CFRunLoopGetCurrent(), run_loop_source, kCFRunLoopCommonModes)

print("Low-level keyboard hook active!")
print("Press Enter to capture screenshot BEFORE system processes it")
print("Press Ctrl+C to stop\n")

try:
    CFRunLoopRun()
except KeyboardInterrupt:
    print("\nStopped.")