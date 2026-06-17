"""
Hermes Desktop Vision — Give your AI agent eyes on Windows.

Pipelines:
  1. Screenshot → EasyOCR → pyautogui  (text-based: icons, labels, buttons with text)
  2. Screenshot → YOLOv8 → pyautogui   (object-based: icons without text, UI elements)

Enables AI agents (Hermes, Claude, GPT, etc.) to see the desktop,
read text on screen, detect objects, and click on UI elements autonomously.

Author: Thoma Lafosse & Gordias (starbottroopers)
Repo: https://github.com/Thomaslafosse85/hermes-desktop-vision
License: MIT
"""

import pyautogui
import easyocr
import os
import time
from typing import Optional, Tuple, List
from dataclasses import dataclass, field

# YOLO (optional — install with: pip install ultralytics opencv-python supervision)
try:
    from ultralytics import YOLO
    import supervision as sv
    import numpy as np
    HAS_YOLO = True
except ImportError:
    HAS_YOLO = False


@dataclass
class DetectedObject:
    """Represents an object detected by YOLO on screen."""
    class_name: str
    confidence: float
    center_x: int
    center_y: int
    width: int
    height: int
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)


@dataclass
class ScreenText:
    """Represents text found on screen."""
    text: str
    confidence: float
    center_x: int
    center_y: int
    bbox: List


class DesktopVision:
    """
    Give your agent eyes on Windows.

    Usage:
        vision = DesktopVision()
        vision.find_and_click("bonjour")
        vision.find_and_double_click("Chrome")
    """

    def __init__(self, languages: list = None, gpu: bool = True):
        """
        Initialize the vision system.

        Args:
            languages: OCR languages (default: ['fr', 'en'])
            gpu: Use GPU acceleration (much faster)
        """
        self.languages = languages or ['fr', 'en']
        self.reader = None
        self.gpu = gpu

    def _ensure_reader(self):
        """Lazy-load the OCR reader (model download on first use)."""
        if self.reader is None:
            self.reader = easyocr.Reader(self.languages, gpu=self.gpu)

    def screenshot(self, path: str = None) -> str:
        """
        Take a screenshot of the entire screen.

        Args:
            path: Save path (default: %TEMP%/hermes_vision_screenshot.png)

        Returns:
            Path to the saved screenshot
        """
        if path is None:
            path = os.path.join(os.environ.get('TEMP', os.path.expanduser('~')), 
                               'hermes_vision_screenshot.png')
        pyautogui.screenshot(path)
        return path

    def show_desktop(self):
        """Minimize all windows to show the desktop."""
        pyautogui.hotkey('win', 'd')
        time.sleep(0.5)

    def scan_screen(self, screenshot_path: str = None) -> List[ScreenText]:
        """
        Scan the screen and return all text found.

        Args:
            screenshot_path: Path to screenshot (takes new one if None)

        Returns:
            List of ScreenText objects with text, confidence, and position
        """
        self._ensure_reader()

        if screenshot_path is None:
            screenshot_path = self.screenshot()

        results = self.reader.readtext(screenshot_path)

        texts = []
        for bbox, text, conf in results:
            xs = [p[0] for p in bbox]
            ys = [p[1] for p in bbox]
            cx = int(sum(xs) / 4)
            cy = int(sum(ys) / 4)
            texts.append(ScreenText(
                text=text,
                confidence=conf,
                center_x=cx,
                center_y=cy,
                bbox=bbox
            ))

        return texts

    def find_text(self, search: str, screenshot_path: str = None,
                  min_confidence: float = 0.3) -> Optional[ScreenText]:
        """
        Find text on screen matching a search string.

        Args:
            search: Text to search for (case-insensitive, partial match)
            screenshot_path: Existing screenshot (takes new one if None)
            min_confidence: Minimum OCR confidence to consider

        Returns:
            ScreenText if found, None otherwise
        """
        texts = self.scan_screen(screenshot_path)

        for st in texts:
            if search.lower() in st.text.lower() and st.confidence >= min_confidence:
                return st

        return None

    def find_all_text(self, search: str, screenshot_path: str = None,
                      min_confidence: float = 0.3) -> List[ScreenText]:
        """Find all occurrences of text on screen."""
        texts = self.scan_screen(screenshot_path)
        return [st for st in texts 
                if search.lower() in st.text.lower() and st.confidence >= min_confidence]

    def click_position(self, x: int, y: int, double: bool = False):
        """Click at a specific position."""
        pyautogui.moveTo(x, y, duration=0.3)
        time.sleep(0.1)
        if double:
            pyautogui.doubleClick()
        else:
            pyautogui.click()

    def find_and_click(self, search: str, double: bool = False,
                       icon_offset_y: int = -45, min_confidence: float = 0.3) -> bool:
        """
        Find text on screen and click on its associated icon.

        This is the main workflow: take a screenshot, find the text label,
        and click on the icon above it (icons are typically above their labels).

        Args:
            search: Text to search for (e.g., "Chrome", "bonjour")
            double: Use double-click instead of single click
            icon_offset_y: Vertical offset from text center to icon (negative = above)
            min_confidence: Minimum OCR confidence

        Returns:
            True if found and clicked, False otherwise
        """
        found = self.find_text(search, min_confidence=min_confidence)

        if found is None:
            return False

        # Icon is typically above the text label
        click_y = found.center_y + icon_offset_y

        self.click_position(found.center_x, click_y, double=double)
        return True

    def find_and_double_click(self, search: str, icon_offset_y: int = -45,
                              min_confidence: float = 0.3) -> bool:
        """Shorthand for find_and_click with double-click."""
        return self.find_and_click(search, double=True, 
                                   icon_offset_y=icon_offset_y,
                                   min_confidence=min_confidence)

    def list_desktop_icons(self) -> List[ScreenText]:
        """
        List all desktop icons by scanning after Win+D.

        Returns:
            List of ScreenText objects found on the desktop
        """
        self.show_desktop()
        path = self.screenshot()
        return self.scan_screen(path)

    def open_desktop_item(self, name: str) -> bool:
        """
        Open an item on the desktop by name.

        Uses Win+D to show desktop, then finds and double-clicks.

        Args:
            name: Partial name of the desktop item

        Returns:
            True if found and opened
        """
        self.show_desktop()
        return self.find_and_double_click(name)

    def open_folder(self, path: str):
        """Open a folder in Windows Explorer."""
        os.system(f'explorer "{path}"')

    def open_app(self, app_name: str):
        """Launch an application by name."""
        os.system(f'start {app_name}')

    def type_text(self, text: str, interval: float = 0.05):
        """Type text at the current cursor position."""
        pyautogui.write(text, interval=interval)

    def press_key(self, key: str):
        """Press a keyboard key."""
        pyautogui.press(key)

    def hotkey(self, *keys):
        """Press a keyboard shortcut (e.g., hotkey('ctrl', 'c'))."""
        pyautogui.hotkey(*keys)

    # ── Object Detection (YOLO) ──────────────────────────────────────────

    def _ensure_yolo(self):
        """Check that YOLO dependencies are installed."""
        if not HAS_YOLO:
            raise ImportError(
                "YOLO support requires: pip install ultralytics opencv-python supervision\n"
                "These are optional — EasyOCR-based methods work without them."
            )

    def detect_objects(self, screenshot_path: str = None,
                       model: str = "yolov8n.pt",
                       classes: List[str] = None,
                       min_confidence: float = 0.3) -> List[DetectedObject]:
        """
        Detect objects on screen using YOLOv8.

        Args:
            screenshot_path: Path to screenshot (takes new one if None)
            model: YOLO model name or path (yolov8n.pt, yolov8s.pt, custom .pt)
            classes: Filter by class names (None = all 80 COCO classes)
            min_confidence: Minimum detection confidence

        Returns:
            List of DetectedObject with class_name, confidence, position, bbox
        """
        self._ensure_yolo()

        if screenshot_path is None:
            screenshot_path = self.screenshot()

        yolo = YOLO(model)
        results = yolo(screenshot_path, verbose=False)[0]

        objects = []
        if results.boxes is not None:
            for box in results.boxes:
                conf = float(box.conf[0])
                if conf < min_confidence:
                    continue

                cls_id = int(box.cls[0])
                cls_name = results.names[cls_id]

                if classes and cls_name not in classes:
                    continue

                x1, y1, x2, y2 = box.xyxy[0].tolist()
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                w = int(x2 - x1)
                h = int(y2 - y1)

                objects.append(DetectedObject(
                    class_name=cls_name,
                    confidence=conf,
                    center_x=cx,
                    center_y=cy,
                    width=w,
                    height=h,
                    bbox=(int(x1), int(y1), int(x2), int(y2))
                ))

        return objects

    def find_object(self, class_name: str, screenshot_path: str = None,
                    model: str = "yolov8n.pt",
                    min_confidence: float = 0.3) -> Optional[DetectedObject]:
        """
        Find a specific object class on screen.

        Args:
            class_name: COCO class name (e.g., 'person', 'laptop', 'cell phone')
            screenshot_path: Existing screenshot
            model: YOLO model
            min_confidence: Minimum detection confidence

        Returns:
            DetectedObject if found, None otherwise
        """
        objects = self.detect_objects(screenshot_path, model,
                                      classes=[class_name],
                                      min_confidence=min_confidence)
        if objects:
            # Return highest confidence match
            return max(objects, key=lambda o: o.confidence)
        return None

    def find_and_click_object(self, class_name: str, double: bool = False,
                              model: str = "yolov8n.pt",
                              min_confidence: float = 0.3) -> bool:
        """
        Find an object by class name and click on it.

        Useful for clicking on non-text UI elements like icons,
        buttons without labels, or any COCO-detectable object.

        Args:
            class_name: COCO class (e.g., 'book', 'cell phone', 'laptop')
            double: Use double-click
            model: YOLO model
            min_confidence: Minimum confidence

        Returns:
            True if found and clicked
        """
        obj = self.find_object(class_name, model=model,
                               min_confidence=min_confidence)
        if obj is None:
            return False

        self.click_position(obj.center_x, obj.center_y, double=double)
        return True

    def annotate_screenshot(self, screenshot_path: str = None,
                            output_path: str = None,
                            model: str = "yolov8n.pt",
                            min_confidence: float = 0.3) -> str:
        """
        Take a screenshot and annotate detected objects with bounding boxes.

        Useful for debugging: see what YOLO sees.

        Args:
            screenshot_path: Input screenshot
            output_path: Where to save annotated image
            model: YOLO model
            min_confidence: Minimum confidence

        Returns:
            Path to the annotated image
        """
        self._ensure_yolo()

        if screenshot_path is None:
            screenshot_path = self.screenshot()

        if output_path is None:
            output_path = screenshot_path.replace('.png', '_annotated.png')

        yolo = YOLO(model)
        results = yolo(screenshot_path, verbose=False)[0]

        if results.boxes is not None:
            detections = sv.Detections.from_ultralytics(results)
            image = np.array(results.orig_img)
            annotator = sv.BoxAnnotator()
            labeler = sv.LabelAnnotator()
            annotated = annotator.annotate(image.copy(), detections)
            annotated = labeler.annotate(annotated, detections)

            import cv2
            cv2.imwrite(output_path, cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))

        return output_path


# ── Demo ──────────────────────────────────────────────────────────────────────

def demo():
    """Demonstrate the desktop vision pipeline."""
    print("=" * 60)
    print(" Hermes Desktop Vision — Demo")
    print("=" * 60)

    vision = DesktopVision()

    # 1. Scan the desktop
    print("\n[1/4] Showing desktop...")
    vision.show_desktop()

    print("[2/4] Scanning screen with EasyOCR (GPU)...")
    texts = vision.scan_screen()
    print(f"      Found {len(texts)} text elements")

    # Show top 10 findings
    print("\n      Top 10 detected texts:")
    for st in sorted(texts, key=lambda t: -t.confidence)[:10]:
        print(f"      [{st.confidence:.2f}] \"{st.text[:50]}\" at ({st.center_x}, {st.center_y})")

    # 3. Find something specific
    print("\n[3/4] Searching for 'Chrome'...")
    found = vision.find_text("Chrome")
    if found:
        print(f"      Found: \"{found.text}\" (conf={found.confidence:.2f})")
        print(f"      Position: ({found.center_x}, {found.center_y})")
    else:
        print("      Not found on this screen")

    # 4. Demonstrate click
    print("\n[4/4] Ready to click!")
    print("      Use vision.find_and_click('target') to click on any UI element.")
    print("\nDone! Your agent can now see and interact with Windows.")


if __name__ == "__main__":
    demo()
