from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

# Minesweeper levels
EASY = [8, 10, 40] # rows, cols, pixel length of single square edge
MEDIUM = [14, 18, 30]
HARD = [20, 24, 25]

# Square values
UNKNOWN = -1
MINE = -2


def click_square(canvas, row, col, square_size, left_click):
  X_OFFSET = -1 * (col / 2 * square_size) + 10
  Y_OFFSET = -1 * (row / 2 * square_size) + 10
  action = webdriver.common.action_chains.ActionChains(driver)
  action.move_to_element_with_offset(canvas, X_OFFSET + col * square_size, Y_OFFSET + row * square_size)
  if left_click:
    action.click()
  else:
    action.context_click()
  action.perform()


def step(canvas, row, col, square_size):
   click_square(canvas, row, col, square_size, True)


def mark_mine(canvas, row, col, square_size):
   click_square(canvas, row, col, square_size, False)


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
time.sleep(5)
canvas = driver.find_element(By.TAG_NAME, "canvas")
[rows, cols, square_size] = find_size(canvas.get_attribute("height"), canvas.get_attribute("width"))
print(f"Aha, I'm playing with {rows} rows and {cols} cols")
field = [ [UNKNOWN] * cols for i in range(rows) ]
mark_mine(canvas, rows - 1, cols - 1, square_size)

time.sleep(10)