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
import signal
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
from Quartz import (
    CGWindowListCopyWindowInfo,
    kCGWindowListOptionOnScreenOnly,
    kCGWindowListExcludeDesktopElements,
    kCGNullWindowID,
)
from Quartz import (
    CGWindowListCreateImage,
    kCGWindowListOptionIncludingWindow,
    kCGWindowImageBoundsIgnoreFraming,
    CGRectInfinite,
    CGImageGetWidth,
    CGImageGetHeight,
    CGImageGetDataProvider,
    CGDataProviderCopyData,
)
from AppKit import NSWorkspace
from .prompts import build_activity_prompt


def encode_image_from_pil(image):
    buffer = io.BytesIO()        # create an in-memory binary stream
    image.save(buffer, format="PNG")  # write the image as PNG into the buffer
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


class ActivityLogger:
    """
    AI-powered activity logger that captures screenshots and analyzes user actions.
    """
    
    def __init__(self, api_key=None, screenshot_folder=None, log_dir="logs", on_status_change=None, capture_mode="full_display"):
        """
        Initialize the Activity Logger.
        
        Args:
            api_key (str): OpenAI API key. If None, uses OPENAI_API_KEY env var.
            screenshot_folder (str): Folder to save screenshots. Defaults to ~/Desktop/Screenshots
            log_dir (str): Directory to save activity logs. Defaults to 'logs'
            on_status_change (callable): Optional callback function(status, message) for status updates
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
        
        # Keycode for Return/Enter key on Mac
        self.ENTER_KEYCODE = 36
        self.event_tap = None
        
        # Capture mode: "full_display" or "focused_window"
        self.capture_mode = capture_mode if capture_mode in ("full_display", "focused_window") else "full_display"

        # Initialize MSS for screenshot capture
        self.mss_instance = mss.mss()
        
        # Setup logging directory
        os.makedirs(self.log_dir, exist_ok=True)
        
        # GUI integration
        self.on_status_change = on_status_change
        self._running = False
        self._should_stop = False
        self._run_loop_thread = None
    
    def encode_image(self, image_path):
        """Encode image to base64 for API"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def get_frontmost_window_info(self):
        """Return info for the currently focused (frontmost) window.

        Returns dict with keys: window_id, bounds (x, y, width, height), app_name, window_title, pid.
        Returns None if it cannot be determined.
        """
        try:
            workspace = NSWorkspace.sharedWorkspace()
            app = workspace.frontmostApplication()
            if app is None:
                return None
            pid = int(app.processIdentifier())
            app_name = str(app.localizedName()) if app.localizedName() else ""

            options = kCGWindowListOptionOnScreenOnly | kCGWindowListExcludeDesktopElements
            window_list = CGWindowListCopyWindowInfo(options, kCGNullWindowID) or []

            # Windows are front-to-back ordered; pick the first for this PID with layer 0
            front_windows = []
            for w in window_list:
                try:
                    owner_pid = int(w.get('kCGWindowOwnerPID', -1))
                    if owner_pid != pid:
                        continue
                    layer = int(w.get('kCGWindowLayer', 0))
                    if layer != 0:
                        continue
                    bounds = w.get('kCGWindowBounds') or {}
                    width = int(bounds.get('Width', 0))
                    height = int(bounds.get('Height', 0))
                    if width <= 2 or height <= 2:
                        continue
                    alpha = float(w.get('kCGWindowAlpha', 1.0))
                    if alpha <= 0.01:
                        continue
                    front_windows.append(w)
                except Exception:
                    continue

            if not front_windows:
                return None

            w = front_windows[0]
            bounds = w.get('kCGWindowBounds') or {}
            x = int(bounds.get('X', 0))
            y = int(bounds.get('Y', 0))
            width = int(bounds.get('Width', 0))
            height = int(bounds.get('Height', 0))
            window_id = int(w.get('kCGWindowNumber')) if w.get('kCGWindowNumber') is not None else None
            window_title = w.get('kCGWindowName') or ""
            owner_name = w.get('kCGWindowOwnerName') or app_name

            return {
                'window_id': window_id,
                'bounds': (x, y, width, height),
                'app_name': owner_name,
                'window_title': window_title,
                'pid': pid,
            }
        except Exception as e:
            print(f"Failed to get frontmost window info: {e}")
            return None
    
    def analyze_screenshot_then_log(self, image):
        """Send an in-memory screenshot to ChatGPT for analysis"""
        try:
            base64_image = encode_image_from_pil(image)
            info = self.get_frontmost_window_info()
            prompt_text = build_activity_prompt(
                (info.get('app_name') if info else None),
                (info.get('window_title') if info else None),
            )

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # or "gpt-4o"
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt_text,
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
    
    def capture_focused_window(self):
        """Capture only the currently focused window as a PIL Image.

        Returns PIL Image on success, or None on failure (e.g., no focused window
        or missing Screen Recording permission).
        """
        info = self.get_frontmost_window_info()
        if not info or not info.get('window_id'):
            return None

        window_id = info['window_id']
        try:
            image_ref = CGWindowListCreateImage(
                CGRectInfinite,  # ignored when IncludingWindow is used
                kCGWindowListOptionIncludingWindow,
                window_id,
                kCGWindowImageBoundsIgnoreFraming,
            )
            if not image_ref:
                # Likely missing Screen Recording permission, or window cannot be imaged
                return None

            width = int(CGImageGetWidth(image_ref))
            height = int(CGImageGetHeight(image_ref))
            if width == 0 or height == 0:
                return None

            provider = CGImageGetDataProvider(image_ref)
            data = CGDataProviderCopyData(provider)
            if data is None:
                return None
            raw = bytes(data)

            # Convert from BGRA to RGBA for PIL
            image = Image.frombuffer(
                "RGBA",
                (width, height),
                raw,
                "raw",
                "BGRA",
                0,
                1,
            )
            return image
        except Exception as e:
            print(f"Failed to capture focused window: {e}")
            return None
    
    def capture_screenshot(self):
        """Capture a screenshot per capture_mode with safe fallback to full display."""
        if self.capture_mode == "focused_window":
            img = self.capture_focused_window()
            if img is not None:
                return img
            print("Focused window capture failed; falling back to full-display screenshot.")

        # Full display capture via mss
        screenshot_data = self.mss_instance.grab(self.mss_instance.monitors[0])
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
        
        # Notify GUI of new log entry if callback is set
        if self.on_status_change:
            self.on_status_change("logged", response_content)
            
        return response_content     
    
    def keyboard_event_callback(self, proxy, event_type, event, refcon):
        """This runs BEFORE the system processes the key"""
        if event_type == kCGEventKeyDown:
            keycode = CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode)
            
            if keycode == self.ENTER_KEYCODE:
                print('enter pressed')
                screenshot = self.capture_screenshot()
                threading.Thread(target=self.save_screenshot, args=(screenshot,), daemon=True).start()
                threading.Thread(target=self.analyze_screenshot_then_log, args=(screenshot,), daemon=True).start()
    
                if self.event_tap:
                    CGEventTapEnable(self.event_tap, True)
        
        # Return the event to let it continue to the system
        return event
    
    def save_screenshot(self, screenshot):
        """Save screenshot to file; keep only 5 screenshots, deleting from right side of reverse-sorted list."""
        file_path = os.path.join(self.screenshot_folder, f"screenshot_{self.file_num}.png")
        self.file_num += 1
        screenshot.save(file_path)
        print(f'screenshot saved to {file_path}')

        # --- New logic: reverse sort by modification time ---
        screenshots = sorted(
            [os.path.join(self.screenshot_folder, f) for f in os.listdir(self.screenshot_folder)
             if f.lower().endswith('.png')],
            key=os.path.getmtime,
            reverse=True   # newest first
        )

        while len(screenshots) > 5:
            oldest = screenshots.pop()
            try:
                os.remove(oldest)
                print(f'deleted screenshot: {oldest}')
            except Exception as e:
                print(f'failed to delete {oldest}: {e}')
                break
    
    def is_running(self):
        """Check if the logger is currently running"""
        return self._running
        
    def start(self):
        """Start the activity logger"""
        if self._running:
            return
            
        self._should_stop = False
        
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

        # Notify GUI that we're starting
        if self.on_status_change:
            self.on_status_change("starting", "Activity logger starting...")
        
        self._running = True
        print("Low-level keyboard hook active!")
        print("Press Enter to capture screenshot BEFORE system processes it")
        print("Press Ctrl+C to stop\n")

        try:
            CFRunLoopRun()
        except KeyboardInterrupt:
            print("\nStopped.")
        finally:
            self._cleanup()
    
    def _cleanup(self):
        """Clean up resources"""
        if self.event_tap:
            CGEventTapEnable(self.event_tap, False)
            self.event_tap = None
        
        self._running = False
        
        # Notify GUI that we've stopped
        if self.on_status_change:
            self.on_status_change("stopped", "Activity logger stopped.")
    
    def stop(self):
        """Stop the activity logger (thread-safe)"""
        if not self._running:
            return
            
        self._should_stop = True
        
        # Stop the CFRunLoop
        from Quartz import CFRunLoopStop
        CFRunLoopStop(CFRunLoopGetCurrent())
        
        self._cleanup()

def _sigint_handler(_signum, _frame):                 # ✅ ADDED
    if logger:
        logger.stop()


def main():
    """Main entry point for the activity logger"""
    try:
        global logger
        logger = ActivityLogger()
        signal.signal(signal.SIGINT, _sigint_handler) 
        t = threading.Thread(target=logger.start, daemon=True)
        t.start()
        try:
            t.join()
        except KeyboardInterrupt:
            _sigint_handler(None, None)
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
