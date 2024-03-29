from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from PIL import Image
from io import BytesIO
from math import ceil
import time
import sys
import itertools

DEBUG = True

MINESWEEPER_LEVELS = {
    # (height, width): [rows, cols, pixel length of square edge]
    (360, 400): [8, 10, 40],  # EASY
    (420, 540): [14, 18, 30],  # MEDIUM
    (500, 600): [20, 24, 25],  # HARD
}

# Square values
# 0 for blank space and n >= 1 means that's the number showing on the square
UNKNOWN = -1
MINE = -2
# For right after I step on square b/c it's def not a mine but haven't read field yet
UNKNOWN_BUT_NOT_MINE = -3


def identify_square_by_color(pixel):
    COLOR_RANGES = [
        {"R": (215, 229), "G": (184, 194), "B": (153, 159), "type": 0},
        {"R": (225, 236), "G": (202, 209), "B": (179, 183), "type": 0},
        {"R": (169, 171), "G": (213, 216), "B": (80, 82), "type": UNKNOWN},
        {"R": (161, 163), "G": (208, 210), "B": (72, 74), "type": UNKNOWN},
        {"R": (230, 240), "G": (51, 54), "B": (6, 8), "type": MINE},
        {"R": (25, 31), "G": (117, 121), "B": (207, 211), "type": 1},  # blue 1
        {"R": (56, 58), "G": (141, 143), "B": (59, 61), "type": 2},  # green 2
        {"R": (210, 212), "G": (46, 51), "B": (46, 50), "type": 3},  # red 3
        {"R": (122, 132), "G": (30, 43), "B": (161, 163), "type": 4},  # purple 4
        {"R": (250, 253), "G": (148, 150), "B": (17, 21), "type": 5},  # orange 5
        {"R": (108, 110), "G": (170, 172), "B": (162, 164), "type": 6},  # cyan 6
    ]
    red = pixel[0]
    green = pixel[1]
    blue = pixel[2]
    for r in COLOR_RANGES:
        if (
            red >= r["R"][0]
            and red <= r["R"][1]
            and green >= r["G"][0]
            and green <= r["G"][1]
            and blue >= r["B"][0]
            and blue <= r["B"][1]
        ):
            return r["type"]
    raise KeyError("Couldn't identify color for ", pixel)


def printd(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


def click_square(canvas, row, col, left_click):
    global web_action
    X_OFFSET = -1 * (cols / 2 * square_size) + 10
    Y_OFFSET = -1 * (rows / 2 * square_size) + 10
    web_action.move_to_element_with_offset(
        canvas, X_OFFSET + col * square_size, Y_OFFSET + row * square_size
    )
    if left_click:
        web_action.click().perform()
    else:
        web_action.context_click().perform()


def row_perimeter(row):
    row_min = max(0, row - 1)
    row_max = min(row + 2, rows)
    return range(row_min, row_max)


def col_perimeter(col):
    col_min = max(0, col - 1)
    col_max = min(col + 2, cols)
    return range(col_min, col_max)


def count_perimeter(field, row, col, square_type):
    count = 0
    for i in row_perimeter(row):
        for j in col_perimeter(col):
            if i == row and j == col:
                continue
            if field[i][j] == square_type:
                count += 1
    return count


def borders_unknown_square(field, row, col):
    unknowns = count_perimeter(field, row, col, UNKNOWN)
    return unknowns > 0


def perimeter_makes_sense(hypothetical_field, row, col):
    mine_count = hypothetical_field[row][col]
    if mine_count < 0:
        return True
    mines_found = count_perimeter(hypothetical_field, row, col, MINE)
    unknowns_found = count_perimeter(hypothetical_field, row, col, UNKNOWN)
    # Neither too many nor too few mines in the perimeter for given square
    return mines_found <= mine_count and unknowns_found + mines_found >= mine_count


# Precondition: There is at least one unknown in the perimeter of row, col
# Returns whether a change was made
def check_combination_logic(field, row, col):
    mine_count = field[row][col]
    printd(f"check valid combinations for {row}, {col}: ({mine_count})")
    mines_in_unknowns = mine_count - count_perimeter(field, row, col, MINE)
    # Array containing i,j coordinates of all unknowns in the perimeter
    unknown_array = []
    for i in row_perimeter(row):
        for j in col_perimeter(col):
            if field[i][j] == UNKNOWN:
                unknown_array.append((i, j))
    possible_combinations = list(
        itertools.combinations(unknown_array, mines_in_unknowns)
    )
    if len(possible_combinations) <= 1:  # For some reason, 1 is a degenerate empty list
        return False
    valid_combinations = []
    for comb in possible_combinations:
        # Mock up a field with that combination of mines
        hypothetical_field = [row[:] for row in field]
        for square in comb:
            hypothetical_field[square[0]][square[1]] = MINE
        for i in row_perimeter(row):
            for j in col_perimeter(col):
                if hypothetical_field[i][j] == UNKNOWN:
                    hypothetical_field[i][j] = UNKNOWN_BUT_NOT_MINE
        # Test that all squares in perimeter are compatible w/that field
        logical_combo = True
        for i in row_perimeter(row):
            for j in col_perimeter(col):
                if i == row and j == col:
                    continue
                if field[i][j] >= 0 and not perimeter_makes_sense(
                    hypothetical_field, i, j
                ):
                    logical_combo = False
        if logical_combo:
            valid_combinations.append(comb)

    # If there's the same mine in all valid_combinations, then it must be a mine
    # If there's a potential mine missing in all valid_combinations, it must be safe
    made_change = False
    unknown_verdict = [
        {"could_be_mine": False, "could_be_not_mine": False}
        for i in range(len(unknown_array))
    ]
    # Figure out which unknowns are conclusively mine or not mine
    for i in range(len(unknown_array)):
        for comb in valid_combinations:
            if unknown_array[i] in comb:
                unknown_verdict[i]["could_be_mine"] = True
            else:
                unknown_verdict[i]["could_be_not_mine"] = True
    # Act on the verdicts to step or mark mine
    for i in range(len(unknown_array)):
        if not unknown_verdict[i]["could_be_mine"]:
            step(canvas, unknown_array[i][0], unknown_array[i][1])
            made_change = True
            printd("Logic concluded no mine at " + str(unknown_array[i]))
        if not unknown_verdict[i]["could_be_not_mine"]:
            mark_mine(canvas, unknown_array[i][0], unknown_array[i][1])
            made_change = True
            printd("Logic concluded mine at " + str(unknown_array[i]))
    return made_change


# Precondition: field[row][col] > 0 and at least one square in perimeter is UNKNOWN
# Return whether or not any square was changed after running this
def mark_perimeter(row, col):
    made_change = False
    mine_count = field[row][col]
    mines_found = count_perimeter(field, row, col, MINE)
    unknowns_found = count_perimeter(field, row, col, UNKNOWN)
    if mine_count == unknowns_found + mines_found:
        # All the unknowns are mines, mark them
        for i in row_perimeter(row):
            for j in col_perimeter(col):
                if field[i][j] == UNKNOWN:
                    mark_mine(canvas, i, j)
                    mines_found += 1
                    made_change = True
    if mines_found == mine_count:
        # All the mines are already marked, simulate chord click
        for i in row_perimeter(row):
            for j in col_perimeter(col):
                if field[i][j] == UNKNOWN:
                    step(canvas, i, j)
                    made_change = True
    if count_perimeter(field, row, col, UNKNOWN) > 0:
        made_change = made_change or check_combination_logic(field, row, col)
    return made_change


def read_square(pixels, row, col):
    try:
        if (
            identify_square_by_color(
                pixels[
                    ceil((col + 0.25) * square_size), ceil((row + 0.25) * square_size)
                ]
            )
            == MINE
        ):
            # Center of mine square looks unknown, check the upper left area for mine color
            return MINE
    except KeyError:
        printd(f"Couldn't match color while checking mine at {row}, {col}")
        pass
    return identify_square_by_color(
        pixels[(col + 0.5) * square_size + 1, (row + 0.5) * square_size]
    )


def print_field():
    for i in range(0, rows):
        for j in range(0, cols):
            val = field[i][j]
            if val == UNKNOWN:
                val = "?"
            elif val == MINE:
                val = "M"
            else:
                val = str(val)
            printd("%2s" % (val), end="")
        printd()


def board_solved():
    for i in range(0, rows):
        for j in range(0, cols):
            if field[i][j] == UNKNOWN:
                return False
    return True


def read_field():
    printd("\nreading field")
    time.sleep(0.5)  # Wait for animation to end
    png = canvas.screenshot_as_png
    if DEBUG:
        canvas.screenshot("temp.png")
    image = Image.open(BytesIO(png))
    pixels = image.load()
    time.sleep(0.15)
    png2 = canvas.screenshot_as_png
    if DEBUG:
        canvas.screenshot("temp2.png")
    image2 = Image.open(BytesIO(png2))
    pixels2 = image2.load()
    # Sync field to the latest on screen
    for row in range(0, rows):
        for col in range(0, cols):
            if field[row][col] in (UNKNOWN, UNKNOWN_BUT_NOT_MINE):
                try:
                    printd(f"Reading from image for {row}, {col}")
                    field[row][col] = read_square(pixels, row, col)
                except KeyError:
                    printd(f"Reading from image2 for {row}, {col}")
                    field[row][col] = read_square(pixels2, row, col)


# Returns true if a change was made to field, otherwise false
def interpret_field():
    field_dirty = False
    while True:
        made_change = False
        for row in range(0, rows):
            for col in range(0, cols):
                if field[row][col] > 0 and borders_unknown_square(field, row, col):
                    if mark_perimeter(row, col):
                        made_change = True
                        printd(f"{row}, {col} made change in interpret_field")
                        field_dirty = True
        if not made_change:
            break
    return field_dirty


def step(canvas, row, col):
    click_square(canvas, row, col, True)
    printd(f"Stepped on square at {row}, {col}")
    field[row][col] = UNKNOWN_BUT_NOT_MINE


def mark_mine(canvas, row, col):
    click_square(canvas, row, col, False)
    printd(f"Marked mine at {row}, {col}")
    field[row][col] = MINE


def find_size(height, width):
    try:
        return MINESWEEPER_LEVELS[(int(height), int(width))]
    except KeyError:
        raise AssertionError(
            f"Canvas height {height} or width {width} is invalid, cannot continue"
        )


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://www.google.com/search?q=minesweeper")
time.sleep(5)  # Pause so I can manually hit Play and create board
canvas = driver.find_element(By.TAG_NAME, "canvas")
web_action = webdriver.common.action_chains.ActionChains(driver)
[rows, cols, square_size] = find_size(
    canvas.get_attribute("height"), canvas.get_attribute("width")
)
printd(f"Aha, I'm playing with {rows} rows and {cols} cols")
field = [[UNKNOWN] * cols for i in range(rows)]
# Start with random guess at 0, 0
step(canvas, 0, 0)
while True:
    read_field()
    field_dirty = interpret_field()
    if board_solved():
        printd("OMG IT WORKED!!!!!!")
        time.sleep(5)
        sys.exit(0)
    if not field_dirty:
        printd("HELP I'M STUCK!!!")
        print_field()
        time.sleep(5)
        sys.exit(1)
