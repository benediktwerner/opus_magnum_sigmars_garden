from time import sleep

import cv2
from pyautogui import Point

from consts import Board, Element
from setup import Setup
from utils import mouseDown, mouseUp, moveTo

DECK = [0, "l", "s", "s", "s", "l", "l", "s", "s", "s", "s", "s"]


def detect_board(setup: Setup, click_delay: float, show_detection: bool) -> Board:
    cells = setup.generate_cell_positions()
    board: Board = [[None] * len(row) for row in cells]

    params = cv2.SimpleBlobDetector_Params()
    params.minThreshold = 10
    params.maxThreshold = 200
    params.filterByArea = True
    params.minArea = 100
    params.filterByCircularity = False
    params.filterByConvexity = False
    params.filterByInertia = False
    detector = cv2.SimpleBlobDetector_create(params)

    clean = setup.screenshot()
    deck_x = setup.deck1_pos.x

    for element, d in enumerate(DECK, start=1):
        if d == "l":
            deck_x += setup.deck_width_large
        elif d == "s":
            deck_x += setup.deck_width_small
        moveTo(Point(deck_x, setup.deck1_pos.y))
        mouseDown()
        sleep(click_delay)
        hover = setup.screenshot()
        mouseUp()

        diff = cv2.absdiff(clean, hover)
        keypoints = detector.detect(diff)

        for kp in keypoints:
            min_d = float("inf")
            min_p = None
            for y, row in enumerate(cells):
                for x, c in enumerate(row):
                    c = setup.to_screenshot_space(c)
                    dist = (kp.pt[0] - c.x) ** 2 + (kp.pt[1] - c.y) ** 2
                    if dist < min_d:
                        min_d = dist
                        min_p = (x, y)
            assert min_p is not None
            board[min_p[1]][min_p[0]] = Element.from_int(element)

    diff = cv2.absdiff(clean, setup.empty_img)
    # txt = []

    for y, row in enumerate(cells):
        for x, c in enumerate(row):
            if board[y][x] is not None:
                continue
            c = setup.to_screenshot_space(c)
            x1 = int(c.x - setup.cell_width / 4)
            y1 = int(c.y - setup.cell_height / 4)
            x2 = int(c.x + setup.cell_width / 4)
            y2 = int(c.y + setup.cell_height / 4)
            val = sum(cv2.mean(diff[y1:y2, x1:x2]))

            cx1 = int(c.x - setup.cell_width / 8)
            cy1 = int(c.y - setup.cell_height / 8)
            cx2 = int(c.x + setup.cell_width / 8)
            cy2 = int(c.y + setup.cell_height / 8)
            delta = (
                sum(cv2.mean(clean[cy1:cy2, cx1:cx2]))
                - sum(cv2.mean(setup.empty_img[cy1:cy2, cx1:cx2]))
            )

            # nothing ~0-10 (small screenshot/calibration noise)
            # Use center-cell `delta` sign in ambiguous ranges:
            # positive -> LIGHT (cell got brighter), negative -> DARK.

            if val < 12:
                continue
            elif val < 30:
                board[y][x] = Element.LIGHT if delta >= 0 else Element.DARK
            elif val < 3 * 23:
                board[y][x] = Element.DARK if delta < 0 else Element.LIGHT
            elif val < 3 * 50:
                board[y][x] = Element.LIGHT if delta >= 0 else Element.DARK
            else:
                board[y][x] = Element.DARK if delta < 0 else Element.LIGHT

            # diff = cv2.rectangle(diff, (x1, y1), (x2, y2), 255)
            # txt.append((val, (c.x, c.y)))

    # for val, cord in txt:
    #     x, y = cord
    #     diff = cv2.putText(diff, f"{val:.2f}", (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))

    # cv2.imshow("x", diff)
    # cv2.waitKey()

    # show detected values
    if show_detection:
        for rowc, rowv in zip(cells, board):
            for c, v in zip(rowc, rowv):
                if v is None:
                    continue
                c = setup.to_screenshot_space(c)
                name = str(v)
                if name == "QUICKSILVER":
                    name = "QS"
                clean = cv2.putText(
                    clean,
                    name,
                    (int(c.x), int(c.y)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 0),
                    2
                )
        cv2.imshow("Detected board (press any key to continue)", clean)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        exit(3)

    # with open(BOARD_FILE, "w") as f:
    #     json.dump(board, f)

    return board
