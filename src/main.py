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
from copy import deepcopy

MINESWEEPER_LEVELS = {
    # (height, width): [rows, cols, pixel length of square edge]
    (360, 400): [8, 10, 40],  # EASY
    (420, 540): [14, 18, 30],  # MEDIUM
    (500, 600): [20, 24, 25],  # HARD
}

# Square values
UNKNOWN = -1
MINE = -2
UNKNOWN_BUT_NOT_MINE = -3
# 0 for blank space and n >= 1 means that's the number showing on the square


def identify_square_by_color(pixel):
    COLOR_RANGES = [
        {"red": (215, 229), "green": (184, 194), "blue": (153, 159), "type": 0},
        {"red": (225, 236), "green": (202, 209), "blue": (179, 183), "type": 0},
        {"red": (169, 171), "green": (214, 216), "blue": (80, 82), "type": UNKNOWN},
        {"red": (161, 163), "green": (208, 210), "blue": (72, 74), "type": UNKNOWN},
        {"red": (230, 240), "green": (51, 54), "blue": (6, 8), "type": MINE},
        {"red": (25, 31), "green": (117, 121), "blue": (207, 211), "type": 1},  # blue 1
        {"red": (56, 58), "green": (141, 143), "blue": (59, 61), "type": 2},  # green 2
        {"red": (210, 212), "green": (46, 49), "blue": (46, 49), "type": 3},  # red 3
        {
            "red": (122, 132),
            "green": (30, 43),
            "blue": (161, 163),
            "type": 4,
        },  # purple 4
        {
            "red": (250, 253),
            "green": (148, 150),
            "blue": (17, 21),
            "type": 5,
        },  # orange 5
    ]
    red = pixel[0]
    green = pixel[1]
    blue = pixel[2]
    for r in COLOR_RANGES:
        if (
            red >= r["red"][0]
            and red <= r["red"][1]
            and green >= r["green"][0]
            and green <= r["green"][1]
            and blue >= r["blue"][0]
            and blue <= r["blue"][1]
        ):
            return r["type"]
    raise KeyError("Couldn't identify color for ", pixel)


def click_square(canvas, row, col, left_click):
    X_OFFSET = -1 * (cols / 2 * square_size) + 10
    Y_OFFSET = -1 * (rows / 2 * square_size) + 10
    action = webdriver.common.action_chains.ActionChains(driver)
    action.move_to_element_with_offset(
        canvas, X_OFFSET + col * square_size, Y_OFFSET + row * square_size
    )
    if left_click:
        action.click()
    else:
        action.context_click()
    action.perform()


def count_perimeter(field, row, col, square_type):
    count = 0
    row_min = max(0, row - 1)
    col_min = max(0, col - 1)
    row_max = min(row + 2, rows)
    col_max = min(col + 2, cols)
    for i in range(row_min, row_max):
        for j in range(col_min, col_max):
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
def check_combination_logic(field, row, col):
    mine_count = field[row][col]
    print(f"eliminate permutations for {row}, {col}: ({mine_count})")
    mines_in_unknowns = mine_count - count_perimeter(field, row, col, MINE)
    row_min = max(0, row - 1)
    col_min = max(0, col - 1)
    row_max = min(row + 2, rows)
    col_max = min(col + 2, cols)
    # Array containing i,j coordinates of all unknowns in the perimeter
    unknown_array = []
    for i in range(row_min, row_max):
        for j in range(col_min, col_max):
            if field[i][j] == UNKNOWN:
                unknown_array.append((i, j))
    print("unknown array ", unknown_array)
    try:
        possible_combinations = list(
            itertools.combinations(unknown_array, mines_in_unknowns)
        )
    except ValueError:
        print("Logic crapped out again!!")
        print_field()
        sys.exit(1)
    print(len(possible_combinations), " possible combinations ", possible_combinations)
    if len(possible_combinations) <= 1:
        return
    valid_combinations = []
    for comb in possible_combinations:
        print(comb)
        # Mock up a field with that combination of mines
        hypothetical_field = deepcopy(field)
        for square in comb:
            hypothetical_field[square[0]][square[1]] = MINE
        for i in range(row_min, row_max):
            for j in range(col_min, col_max):
                if hypothetical_field[i][j] == UNKNOWN:
                    hypothetical_field[i][j] = 0  # Assert 0 for temp computation sake
        # Test that all squares in perimeter are compatible w/that field
        illogical_combo = False
        for i in range(row_min, row_max):
            for j in range(col_min, col_max):
                if i == row and j == col:
                    continue
                if field[i][j] >= 0 and not perimeter_makes_sense(
                    hypothetical_field, i, j
                ):
                    print(f"configuration is illogical for {i}, {j}")
                    illogical_combo = True
        if not illogical_combo:
            valid_combinations.append(comb)
    print("valid combinations: ", valid_combinations)
    # If there's the same mine in all valid_combinations, then it must be a mine
    # If there's a mine missing in all valid_combinations, it must be safe

    # Verdict for each unknown (could_be_mine, could_be_not_mine)
    unknown_verdict = [[False, False] for i in range(len(unknown_array))]
    print(unknown_verdict)
    idx = 0
    for unknown in unknown_array:
        for comb in valid_combinations:
            if unknown in comb:
                # Unknown is in a valid mine comb so could be mine
                unknown_verdict[idx][0] = True
            else:
                unknown_verdict[idx][1] = True
        idx += 1
    for i in range(len(unknown_array)):
        if not unknown_verdict[i][0] and not unknown_verdict[i][1]:
            raise ValueError("Logic contridiction for " + unknown_array[i])
        if not unknown_verdict[i][0]:
            step(canvas, unknown_array[i][0], unknown_array[i][1])
            print("Logic concluded no mine at " + str(unknown_array[i]))
        if not unknown_verdict[i][1]:
            mark_mine(canvas, unknown_array[i][0], unknown_array[i][1])
            print("Logic concluded mine at " + str(unknown_array[i]))


# Precondition: field[row][col] > 0
def mark_perimeter(row, col):
    global field_dirty
    mine_count = field[row][col]
    mines_found = count_perimeter(field, row, col, MINE)
    unknowns_found = count_perimeter(field, row, col, UNKNOWN)
    row_min = max(0, row - 1)
    col_min = max(0, col - 1)
    row_max = min(row + 2, rows)
    col_max = min(col + 2, cols)
    if mine_count == unknowns_found + mines_found:
        # All the unknowns are mines, mark them
        for i in range(row_min, row_max):
            for j in range(col_min, col_max):
                if field[i][j] == UNKNOWN:
                    mark_mine(canvas, i, j)
                    mines_found += 1
                    field_dirty = True
    if mines_found == mine_count:
        # All the mines are already marked, simulate chord click
        for i in range(row_min, row_max):
            for j in range(col_min, col_max):
                if field[i][j] == UNKNOWN:
                    step(canvas, i, j)
                    field_dirty = True
    if count_perimeter(field, row, col, UNKNOWN) > 0:
        check_combination_logic(field, row, col)


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
        print(f"Couldn't match color while checking mine at {row}, {col}")
        pass
    try:
        return identify_square_by_color(
            pixels[(col + 0.5) * square_size + 1, (row + 0.5) * square_size]
        )
    except KeyError as e:
        print(f"UNKNOWN COLOR at {row}, {col} HELLLLLPPPPPP", e)
        for x in range(col * square_size, (col + 1) * square_size):
            for y in range(row * square_size, (row + 1) * square_size):
                pass
                # print(f"{x}, {y}: {pixels[x,y]}")


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
            print("%2s" % (val), end="")
        print()


def board_solved():
    for i in range(0, rows):
        for j in range(0, cols):
            if field[i][j] == UNKNOWN:
                return False
    return True


def read_field():
    print("\nreading field")
    time.sleep(0.85)  # Wait for animation to end
    png = canvas.screenshot_as_png
    canvas.screenshot("temp.png")  # temporarily for debugging
    image = Image.open(BytesIO(png))
    pixels = image.load()
    # Sync field to the latest on screen
    for row in range(0, rows):
        for col in range(0, cols):
            if field[row][col] in (UNKNOWN, UNKNOWN_BUT_NOT_MINE):
                field[row][col] = read_square(pixels, row, col)


def interpret_field():
    for row in range(0, rows):
        for col in range(0, cols):
            if field[row][col] > 0 and borders_unknown_square(field, row, col):
                mark_perimeter(row, col)


def step(canvas, row, col):
    click_square(canvas, row, col, True)
    print(f"Stepped on square at {row}, {col}")
    field[row][col] = UNKNOWN_BUT_NOT_MINE


def mark_mine(canvas, row, col):
    click_square(canvas, row, col, False)
    print(f"Marked mine at {row}, {col}")
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
[rows, cols, square_size] = find_size(
    canvas.get_attribute("height"), canvas.get_attribute("width")
)
print(f"Aha, I'm playing with {rows} rows and {cols} cols")
field = [[UNKNOWN] * cols for i in range(rows)]
field_dirty = False
# Start with random guess at 0, 0
step(canvas, 0, 0)
while True:
    field_dirty = False
    read_field()
    interpret_field()
    if board_solved():
        print("OMG IT WORKED!!!!!!")
        sys.exit(0)
    if not field_dirty:
        print("HELP I'M STUCK!!!")
        print_field()
        time.sleep(5)
        sys.exit(1)
