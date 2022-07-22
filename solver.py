from __future__ import annotations

from typing import Any, Iterator, List, Optional, Set, Tuple

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


class BoardState:
    def __init__(self, board: Board):
        self.board = board
        self.accessible: Set[Coord] = set()
        self.counts = [0 for _ in range(len(Element) + 1)]
        self.metal_level = Element.LEAD

        for row in board:
            for v in row:
                if v:
                    self.counts[v] += 1

        for y, row in enumerate(board):
            for x, v in enumerate(row):
                if v is None:
                    continue
                if self.is_accessible(x, y):
                    self.accessible.add((x, y))

    @property
    def solved(self) -> bool:
        return not self.accessible

    def __getitem__(self, index: Coord) -> Optional[Element]:
        x, y = index
        return self.board[y][x]

    def __setitem__(self, index: Coord, value: Optional[Element]) -> None:
        x, y = index
        self.board[y][x] = value

    def is_accessible(self, x: int, y: int) -> bool:
        c = 0
        for n in NEIGHBORS[y][x]:
            if n is None or self[n] is None:
                c += 1
                if c == 3:
                    break
            else:
                c = 0
        else:
            for n in NEIGHBORS[y][x][:2]:
                if n is None or self[n] is None:
                    c += 1
                    if c == 3:
                        break
                else:
                    c = 0
            else:
                return False
        return True

    def hash(self) -> int:
        h = 0
        for row in self.board:
            for c in row:
                if c is None:
                    h |= 1
                h <<= 1
        return h

    def salts_solvable(self) -> bool:
        return (
            sum(self.counts[e] % 2 for e in Element.basics())
            <= self.counts[Element.SALT]
        )

    def possible_moves(self) -> Iterator[Tuple[Coord, ...]]:
        pos = list(self.accessible)

        for i, c in enumerate(pos):
            typ = self[c]
            assert typ is not None

            if typ.is_metal:
                if self.metal_level != typ:
                    continue

                if typ == Element.GOLD:
                    yield (c,)
                    continue

            for nc in pos[i + 1 :]:
                ntyp = self[nc]
                assert ntyp is not None
                if typ.compatible(ntyp):
                    if ntyp.is_metal and ntyp != self.metal_level:
                        continue
                    yield (c, nc)

    def apply_temorary(self, move: Tuple[Coord, ...]) -> MoveUndoer:
        news = set()
        undo_moves: List[Tuple[Coord, Element]] = []
        metal_level = self.metal_level

        for c in move:
            typ = self[c]
            assert typ is not None
            undo_moves.append((c, typ))
            self[c] = None
            self.accessible.remove(c)
            self.counts[typ] -= 1
            if typ.is_metal:
                self.metal_level = self.metal_level.nxt()

        for x, y in move:
            for n in NEIGHBORS[y][x]:
                if (
                    n is not None
                    and n not in self.accessible
                    and self[n]
                    and self.is_accessible(*n)
                ):
                    news.add(n)

        self.accessible |= news

        return MoveUndoer(self, undo_moves, metal_level, news)


class MoveUndoer:
    def __init__(
        self,
        board_state: BoardState,
        undo_moves: List[Tuple[Coord, Element]],
        metal_level: Element,
        news: Set[Coord],
    ):
        self.board_state = board_state
        self.undo_moves = undo_moves
        self.metal_level = metal_level
        self.news = news

    def __enter__(self) -> MoveUndoer:
        return self

    def __exit__(self, *args: Any) -> None:
        self.board_state.metal_level = self.metal_level
        self.board_state.accessible -= self.news

        for c, typ in self.undo_moves:
            self.board_state[c] = typ
            self.board_state.counts[typ] += 1
            self.board_state.accessible.add(c)


class Solver:
    def __init__(self, board: Board):
        self.board = BoardState(board)
        self.timeout = 50_000
        self.seen: Set[int] = set()

    def solve(self) -> Optional[List[Coord]]:
        self.timeout -= 1
        if self.timeout < 0:
            raise TimeoutException()

        if not self.board.salts_solvable():
            return None

        for move in self.board.possible_moves():
            with self.board.apply_temorary(move):
                h = self.board.hash()
                if h in self.seen:
                    continue
                self.seen.add(h)

                if self.board.solved:
                    return [*move]

                result = self.solve()
                if result:
                    result.extend(move)
                    return result

        return None


class TimeoutException(Exception):
    pass
