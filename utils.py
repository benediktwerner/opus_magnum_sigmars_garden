from collections import defaultdict
from typing import Any, DefaultDict, Optional

import cv2
import numpy as np
import pyautogui
import win32api
import win32con
from pyautogui import Point

from consts import Board, Element


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


def is_invalid_board(board: Board) -> Optional[str]:
    counts: DefaultDict[Element, int] = defaultdict(int)
    for row in board:
        for e in row:
            if e is not None:
                counts[e] += 1

    max_count = {
        Element.SALT: 4,
        Element.AIR: 8,
        Element.FIRE: 8,
        Element.WATER: 8,
        Element.EARTH: 8,
        Element.QUICKSILVER: 5,
        Element.LEAD: 1,
        Element.TIN: 1,
        Element.IRON: 1,
        Element.COPPER: 1,
        Element.SILVER: 1,
        Element.GOLD: 1,
        Element.LIGHT: 4,
        Element.DARK: 4,
    }

    for e, c in max_count.items():
        if counts[e] > c:
            return f"Too many {e} elements. Found {counts[e]}, expected at most {c}."

    has = counts[Element.GOLD]
    total = 0
    for i in range(Element.GOLD - 1, Element.QUICKSILVER, -1):
        e = Element.from_int(i)
        if counts[e]:
            if not has:
                return f"Has {e} but not {e.nxt()}."
            total += 1
        else:
            has = False

    if counts[Element.QUICKSILVER] != total:
        return f"Has {counts[Element.QUICKSILVER]} quicksilver but {total} metals which require it."

    if counts[Element.DARK] != counts[Element.LIGHT]:
        return f"Has {counts[Element.DARK]} dark elements but {counts[Element.LIGHT]} light elements."

    required_salt = sum(counts[e] % 2 for e in Element.basics())
    if required_salt > counts[Element.SALT]:
        return f"Requires at least {required_salt} salt but only has {counts[Element.SALT]}."

    if (counts[Element.SALT] - required_salt) % 2 != 0:
        return f"Salt and element counts are incompatible."

    return None
