from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from PIL import Image
from io import BytesIO
from math import ceil
import time

# Minesweeper levels
EASY = [8, 10, 40] # rows, cols, pixel length of single square edge
MEDIUM = [14, 18, 30]
HARD = [20, 24, 25]

# Square values
UNKNOWN = -1
MINE = -2
# 0 for blank space and n >= 1 means that's the number showing on the square

COLOR_CODES = {
  (229, 194, 159, 255): 0,
  (215, 184, 153, 255): 0,
  (236, 209, 183, 255): 0, # non-mine pixel (when checking mine pixel)
  (225, 202, 179, 255): 0, # non-mine pixel (when checking mine pixel)
  (170, 215, 81, 255): UNKNOWN,
  (162, 209, 73, 255): UNKNOWN,
  (135, 175, 58, 255): -10, #edge border color
  (242, 54, 7, 255): MINE,
  (230, 51, 7, 255): MINE,
  (25, 118, 210, 255): 1, # blue 1
  (56, 142, 60, 255): 2, # green 2
  (211, 47, 47, 255): 3, # red 3 
  (123, 31, 162, 255): 4, # purple 4
}

def click_square(canvas, row, col, left_click):
  print(square_size)
  X_OFFSET = -1 * (cols / 2 * square_size) + 10
  Y_OFFSET = -1 * (rows / 2 * square_size) + 10
  action = webdriver.common.action_chains.ActionChains(driver)
  action.move_to_element_with_offset(canvas, X_OFFSET + col * square_size, Y_OFFSET + row * square_size)
  if left_click:
    action.click()
  else:
    action.context_click()
  action.perform()


def borders_unknown_square(row, col):
  row_min = row - 1 if row > 0 else 0
  col_min = col - 1 if col > 0 else 0
  row_max = row + 2 if row < rows - 1 else row + 1
  col_max = col + 2 if col < cols - 1 else col + 1
  for i in range(row_min, row_max):
    for j in range(col_min, col_max):
      if field[i][j] == UNKNOWN:
        return True
  return False


def mark_perimeter(row, col):
  #print(f"mark_perimeter for {row}, {col}")
  mine_count = field[row][col]
  mines_found = 0
  unknown_found = 0
  row_min = row - 1 if row > 0 else 0
  col_min = col - 1 if col > 0 else 0
  row_max = row + 2 if row < rows - 1 else row + 1
  col_max = col + 2 if col < cols - 1 else col + 1
  for i in range(row_min, row_max):
    for j in range(col_min, col_max):
      if field[i][j] == MINE: 
        mines_found += 1
      elif field[i][j] == UNKNOWN:
        unknown_found += 1
  if mines_found == mine_count:
    # All the mines are already marked, simulate chord click
    for i in range(row_min, row_max):
      for j in range(col_min, col_max):
        if field[i][j] == UNKNOWN:
          step(canvas, i, j)
          field_dirty = True
  if mine_count == unknown_found + mines_found:
    # All the unknowns are mines, mark them
    for i in range(row_min, row_max):
      for j in range(col_min, col_max):
        if field[i][j] == UNKNOWN:
          mark_mine(canvas, i, j)
          field_dirty = True


def read_square(pixels, row, col):
  try:
    if COLOR_CODES[pixels[ceil((col + 0.25) * square_size), ceil((row + 0.25) * square_size)]] == MINE:
      # Center of mine square looks unknown, check the upper left area for mine color
      return MINE
    else:
      return COLOR_CODES[pixels[(col + 0.5) * square_size + 1, (row + 0.5) * square_size]]
  except KeyError as e: 
    print(f"UNKNOWN COLOR at {row}, {col} HELLLLLPPPPPP", e)
    for x in range(col * square_size, (col + 1) * square_size):
      for y in range(row * square_size, (row + 1) * square_size):
        print(f"{x}, {y}: {pixels[x,y]}")


def read_field():
  time.sleep(1) # Wait for animation to end
  png = canvas.screenshot_as_png
  canvas.screenshot('temp.png')
  image = Image.open(BytesIO(png))
  pixels = image.load()
  # Sync field to the latest on screen
  for i in range(0, rows):
    for j in range(0, cols):
      if field[i][j] == UNKNOWN:
        field[i][j] = read_square(pixels, i, j)
  for i in range(0, rows):
    for j in range(0, cols):
      print("%2d" % (field[i][j]), end="")
    print()


def interpret_field():
  for row in range(0, rows):
    for col in range(0, cols):
      if field[row][col] > 0 and borders_unknown_square(row, col):
        mark_perimeter(row, col)


def step(canvas, row, col):
   click_square(canvas, row, col, True)
   print(f"Stepped on square at {row}, {col}")


def mark_mine(canvas, row, col):
   click_square(canvas, row, col, False)
   print(f"Marked mine at {row}, {col}")
   field[row][col] = MINE


def find_size(height, width):
  if height == "360" and width == "400":
    return EASY
  if height == "420" and width == "540":
    return MEDIUM 
  if height == "500" and width == "600":
    return HARD
  raise AssertionError(f"Canvas height {height} or width {width} is invalid, cannot continue")
    

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://www.google.com/search?q=minesweeper")
time.sleep(5) # Pause so I can manually hit Play and create board
canvas = driver.find_element(By.TAG_NAME, "canvas")
[rows, cols, square_size] = find_size(canvas.get_attribute("height"), canvas.get_attribute("width"))
print(f"Aha, I'm playing with {rows} rows and {cols} cols")
field = [ [UNKNOWN] * cols for i in range(rows) ]
#mark_mine(canvas, 0, 0)
step(canvas, 0, 0)
while True:
  read_field()
  field_dirty = False
  interpret_field()
  if not field_dirty:
    print("HELP I'M STUCK!!!")
