from itertools import chain
from typing import List, Optional, Set

from consts import Board, Coord, Element


def generate_neighbors() -> List[List[List[Optional[Coord]]]]:
    DIMENSIONS = [6, 7, 8, 9, 10, 11, 10, 9, 8, 7, 6]

    def in_range(x: int, y: int) -> Optional[Coord]:
        if 0 <= y < len(DIMENSIONS) and 0 <= x < DIMENSIONS[y]:
            return x, y
        return None

    neighbors = []

    for y, width in enumerate(DIMENSIONS):
        rr: List[List[Optional[Coord]]] = []
        for x in range(width):
            ns: List[Optional[Coord]] = []
            ns.append(in_range(x - 1, y))
            ns.append(in_range(x - 1 if y < 6 else x, y - 1))
            ns.append(in_range(x if y < 6 else x + 1, y - 1))
            ns.append(in_range(x + 1, y))
            ns.append(in_range(x + 1 if y < 5 else x, y + 1))
            ns.append(in_range(x if y < 5 else x - 1, y + 1))
            rr.append(ns)
        neighbors.append(rr)

    return neighbors


NEIGHBORS = generate_neighbors()


class Solver:
    def __init__(self, board: Board):
        self.board = board
        self.possible: Set[Coord] = set()
        self.counts = [0 for _ in range(len(Element) + 1)]
        self.metal_level = Element.LEAD
        self.timeout = 1_000_000

        for row in board:
            for v in row:
                if v:
                    self.counts[v] += 1

        for y, row in enumerate(board):
            for x, v in enumerate(row):
                if v is None:
                    continue
                if self.is_accessible(x, y):
                    self.possible.add((x, y))

    def is_accessible(self, x: int, y: int) -> bool:
        c = 0
        for n in NEIGHBORS[y][x]:
            if n is None or self.board[n[1]][n[0]] is None:
                c += 1
                if c == 3:
                    break
            else:
                c = 0
        else:
            for n in NEIGHBORS[y][x][:2]:
                if n is None or self.board[n[1]][n[0]] is None:
                    c += 1
                    if c == 3:
                        break
                else:
                    c = 0
            else:
                return False
        return True

    def solve(self) -> Optional[List[Coord]]:
        self.timeout -= 1
        if self.timeout < 0:
            return None

        if (
            sum(self.counts[e] % 2 for e in Element.basics())
            > self.counts[Element.SALT]
        ):
            return None

        pos = list(self.possible)
        for i, (x, y) in enumerate(pos):
            typ = self.board[y][x]
            assert typ is not None
            if typ.is_metal:
                if self.metal_level != typ:
                    continue

                if typ == Element.GOLD:
                    self.board[y][x] = None
                    self.possible.remove((x, y))
                    news = set()
                    for n in NEIGHBORS[y][x]:
                        if (
                            n is not None
                            and n not in self.possible
                            and self.board[n[1]][n[0]]
                            and self.is_accessible(*n)
                        ):
                            news.add(n)
                    self.possible |= news
                    if not self.possible:
                        return [(x, y)]
                    result = self.solve()
                    if result:
                        result.append((x, y))
                        return result
                    self.possible -= news
                    self.board[y][x] = typ
                    self.possible.add((x, y))
                    continue

                self.metal_level = self.metal_level.nxt()

            for nx, ny in pos[i + 1 :]:
                ntyp = self.board[ny][nx]
                assert ntyp is not None
                if typ.compatible(ntyp):
                    if ntyp.is_metal:
                        if ntyp != self.metal_level:
                            continue
                        self.metal_level = self.metal_level.nxt()
                    self.board[y][x] = None
                    self.board[ny][nx] = None
                    self.possible.remove((x, y))
                    self.possible.remove((nx, ny))
                    news = set()
                    for n in chain(NEIGHBORS[y][x], NEIGHBORS[ny][nx]):
                        if (
                            n is not None
                            and n not in self.possible
                            and self.board[n[1]][n[0]]
                            and self.is_accessible(*n)
                        ):
                            news.add(n)
                    self.possible |= news
                    if not self.possible:
                        return [(x, y), (nx, ny)]
                    self.counts[typ] -= 1
                    self.counts[ntyp] -= 1
                    result = self.solve()
                    if result:
                        result.append((x, y))
                        result.append((nx, ny))
                        return result
                    self.possible -= news
                    self.counts[typ] += 1
                    self.counts[ntyp] += 1
                    self.board[y][x] = typ
                    self.board[ny][nx] = ntyp
                    self.possible.add((x, y))
                    self.possible.add((nx, ny))

                    if ntyp.is_metal:
                        self.metal_level = self.metal_level.prev()

            if typ.is_metal:
                self.metal_level = self.metal_level.prev()

        return None
