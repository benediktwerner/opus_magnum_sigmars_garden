from typing import Any

import cv2
import numpy as np
import pyautogui
import win32api
import win32con
from pyautogui import Point


def safety_check() -> None:
    x, y = win32api.GetCursorPos()
    if x < 100 and y < 100:
        print("Mouse moved to top left corner. Aborting.")
        exit(2)


def mouseDown() -> None:
    safety_check()
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)


def mouseUp() -> None:
    safety_check()
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


def moveTo(p: Point) -> None:
    safety_check()
    win32api.SetCursorPos((int(p.x), int(p.y)))


class Screenshotter:
    def __init__(self, top_left: Point, bottom_right: Point):
        self.top_left = top_left
        self.bottom_right = bottom_right

    def screenshot(self) -> Any:
        width = self.bottom_right.x - self.top_left.x
        height = self.bottom_right.y - self.top_left.y
        region = (self.top_left.x, self.top_left.y, width, height)
        return cv2.cvtColor(
            np.array(pyautogui.screenshot(None, region)), cv2.COLOR_RGB2BGR
        )

    def to_screenshot_space(self, p: Point) -> Point:
        return Point(p.x - self.top_left.x, p.y - self.top_left.y)
