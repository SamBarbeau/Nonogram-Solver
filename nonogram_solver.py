from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
import numpy as np
import time
from utils import *


def solve_nonogram(driver):
    # url of puzzle to solve
    driver.get('https://www.puzzle-nonograms.com/?pl=f3bcb9ebdada43e1e59b2078c0cbe1eb65a03ad17f95f')

    # # press the "New Puzzle" button to reset timer (and find new puzzle)
    # # uncomment if
    new = driver.find_element(By.ID, "btnNew")
    new.click()

    # set "robot" value to "1" to switch to ROBOTS Hall of Fame
    robot_input = driver.find_element(By.ID, "robot")
    driver.execute_script("arguments[0].value = '1';", robot_input)

    # trying to cheat
    timer_button = driver.find_element(By.ID, "btnPause")
    timer_button.click()

    """finished set up - start solving"""

    # extract clues from taskTop and taskLeft
    task_top_elements = driver.find_elements(By.ID, "taskTop")
    task_left_elements = driver.find_elements(By.ID, "taskLeft")

    task_top_clues = extract_clues(task_top_elements)
    task_left_clues = extract_clues(task_left_elements)

    # print(f"top clues:    {task_top_clues}")
    # print(f"left clues:   {task_left_clues}")

    # initialize nonogram grid
    n_rows = len(task_left_clues)
    n_columns = len(task_top_clues)

    nonogram_grid = np.zeros((n_rows, n_columns), dtype=int)

    # step 1: calculate all options for every row and column
    col_options = calculate_options(n_rows, task_top_clues)
    row_options = calculate_options(n_columns, task_left_clues)

    # print(f"col_options:   {col_options}")
    # print(f"row_options:   {row_options}")

    while not np.all((nonogram_grid == 1) | (nonogram_grid == -1)):
        # step 2: fill cells based on common indices in options
        fill_cells(nonogram_grid, row_options, col_options)

        # step 3: remove options based on filled or unfilled (1 or -1) cells
        remove_options(nonogram_grid, row_options, col_options)

    return nonogram_grid



if __name__ == "__main__":
    # input this before anything opens up
    num_mazes_solve = int(input("Input the number of mazes you want to solve: "))

    # chromedriver executable
    chromedriver_path = '/Users/sambarbeau/Documents/code/python/nonogram solver/driver/chromedriver'

    # chrome profile
    # chrome_profile_path = '/Users/sambarbeau/Library/Application Support/Google/Chrome/Profile 9'

    chrome_options = Options()
    # chrome_options.add_argument(f'--user-data-dir={chrome_profile_path}') # so selenium will open the chrome profile I want it to
    # chrome_options.add_argument('--profile-directory=Sam (Spam)')
    chrome_options.add_experimental_option("detach", True) # so the window will stay open after the program ends

    # set up the WebDriver
    driver = webdriver.Chrome(service = Service(chromedriver_path), options = chrome_options)


    for i in range(num_mazes_solve):
        nonogram_grid = solve_nonogram(driver)
        update_website_grid(driver, nonogram_grid)

        # time.sleep(3)

        # new = driver.find_element(By.ID, "btnNew")
        # new.click()
        input("-- press enter to close --")