from __future__ import annotations

from enum import IntEnum
from typing import List, Optional, Tuple

import numpy as np

POSITIONS_FILE = "positions.json"
EMPTY_FILE = "empty.png"


class Element(IntEnum):
    SALT = 1
    WATER = 2
    FIRE = 3
    WIND = 4
    EARTH = 5
    QUICKSIVER = 6
    LEAD = 7
    TIN = 8
    IRON = 9
    COPPER = 10
    SILVER = 11
    GOLD = 12
    LIGHT = 13
    DARK = 14

    def compatible(self, other: Element) -> bool:
        if self == Element.SALT:
            return other <= Element.EARTH
        if Element.WATER <= self <= Element.EARTH:
            return other == Element.SALT or self == other
        if self == Element.QUICKSIVER:
            return Element.LEAD <= other < Element.GOLD
        if Element.LEAD <= self < Element.GOLD:
            return other == Element.QUICKSIVER
        if self == Element.DARK:
            return other == Element.LIGHT
        if self == Element.LIGHT:
            return other == Element.DARK
        return False

    def prev(self) -> Element:
        return Element.from_int(self - 1)

    def nxt(self) -> Element:
        return Element.from_int(self + 1)

    @property
    def is_metal(self) -> bool:
        return Element.LEAD <= self <= Element.GOLD

    @staticmethod
    def basics() -> Tuple[Element, Element, Element, Element]:
        return (Element.WATER, Element.FIRE, Element.WIND, Element.EARTH)

    @staticmethod
    def from_int(x: int) -> Element:
        return ELE_LIST[x - 1]


ELE_LIST = tuple(Element)

Coord = Tuple[int, int]
Board = List[List[Optional[Element]]]
