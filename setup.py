import json
import os
from dataclasses import dataclass
from time import sleep
from typing import Any, List

import cv2
from pyautogui import Point, alert, position

from consts import EMPTY_FILE, POSITIONS_FILE
from utils import Screenshotter


@dataclass
class Setup:
    new_game_btn_pos: Point
    top_left_cell_pos: Point
    cell_width: int
    cell_height: int
    deck1_pos: Point
    deck_width_small: int
    deck_width_large: int
    empty_img: Any
    screenshotter: Screenshotter

    def generate_cell_positions(self) -> List[List[Point]]:
        cell_pos = []
        for y in range(11):
            row = []
            cols = 6 + (y if y < 6 else 10 - y)
            row_start = self.top_left_cell_pos.x - (y if y < 6 else 10 - y) * (
                self.cell_width / 2
            )
            for x in range(cols):
                row.append(
                    Point(
                        row_start + self.cell_width * x,
                        self.top_left_cell_pos.y + self.cell_height * y,
                    )
                )
            cell_pos.append(row)
        return cell_pos

    def screenshot(self) -> Any:
        return self.screenshotter.screenshot()

    def to_screenshot_space(self, p: Point) -> Point:
        return self.screenshotter.to_screenshot_space(p)


def perform_setup() -> Setup:
    if os.path.isfile(POSITIONS_FILE):
        with open(POSITIONS_FILE) as f:
            data = json.load(f)
            new_game = Point(*data["new_game"])
            top_left = Point(*data["top_left"])
            width = data["width"]
            height = data["height"]
            deck1 = Point(*data["deck"])
            deck_width_small = data["deck_width_small"]
            deck_width_large = data["deck_width_large"]
    else:
        alert("Hover over new game button")
        new_game = position()

        alert("Hover over top left cell")
        top_left = position()

        alert("Hover over bottom right cell")
        bottom_right = position()

        width = (bottom_right.x - top_left.x) // 5
        height = (bottom_right.y - top_left.y) // 10

        alert("Hover over first element in bottom bar")
        deck1 = position()

        alert("Hover over second element in bottom bar")
        deck2 = position()

        alert("Hover over third element in bottom bar")
        deck3 = position()

        deck_width_small = deck3.x - deck2.x
        deck_width_large = deck2.x - deck1.x

        with open(POSITIONS_FILE, "w") as f:
            json.dump(
                {
                    "new_game": new_game,
                    "top_left": top_left,
                    "width": width,
                    "height": height,
                    "deck": deck1,
                    "deck_width_small": deck_width_small,
                    "deck_width_large": deck_width_large,
                },
                f,
            )

    s = Screenshotter(
        Point(top_left.x - 3 * width, top_left.y - height,),
        Point(top_left.x + 8 * width, top_left.y + 11 * height,),
    )

    if os.path.isfile(EMPTY_FILE):
        empty_img = cv2.imread(EMPTY_FILE)
    else:
        alert("Make sure the board is empty before pressing ok")
        sleep(1)
        empty_img = s.screenshot()
        cv2.imwrite(EMPTY_FILE, empty_img)

    return Setup(
        new_game,
        top_left,
        width,
        height,
        deck1,
        deck_width_small,
        deck_width_large,
        empty_img,
        s,
    )
