from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
import numpy as np
import time
from utils import *


def solve_nonogram(driver, solve_starting_puzzle):
    # press the "New Puzzle" button to reset timer (and find new puzzle)
    if solve_starting_puzzle:
        new = driver.find_element(By.ID, "btnNew")
        new.click()

    # set "robot" value to "1" to switch to ROBOTS Hall of Fame
    robot_input = driver.find_element(By.ID, "robot")
    driver.execute_script("arguments[0].value = '1';", robot_input)

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
    # url of puzzle to solve (take the "Progress Permalink:" in the "Share" drop down)
    # this will not be the puzzle solved if the "New Puzzle" button is pressed (see first few lines of solve_nonogram function)
    puzzle_link = input("Input the peramlink of the puzzle: ")

    # If the puzzle is a speical Daily, Weekly, or Monthly puzzle, there is no "New Puzzle" button
    is_special_puzzle = input("\n***\n\nIs this a special Daily, Weekly, or Monthly puzzle? (y/n): ").lower()

    if is_special_puzzle == 'n':
        # Since the time is already running on the puzzle, the user can choose to reset the time by finding a new puzzle
        solve_starting_puzzle = input("\n***\n\nThe time is already running on the puzzle.\nWant to start by finding a new puzzle so time resets? (y/n): ")
        solve_starting_puzzle = True if solve_starting_puzzle.lower() == 'y' else False

        # number of mazes to solve (iterations in the loop below)
        num_mazes_solve = int(input("\n***\n\nHow many puzzles do you want to solve in a row: "))
    else:
        solve_starting_puzzle = False
        num_mazes_solve = 1

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

    driver.get(puzzle_link)

    for i in range(num_mazes_solve):
        nonogram_grid = solve_nonogram(driver,solve_starting_puzzle)
        update_website_grid(driver, nonogram_grid)

        # uncomment if you want to see the puzzle finished before going to next puzzle
        time.sleep(3)

        # click the "New Puzzle" after solving the puzzle
        if not solve_starting_puzzle and i < num_mazes_solve - 1:
            new = driver.find_element(By.ID, "btnNew")
            new.click()

    # this is to keep the browser from closing after completing (doens't always close -- may depend on device?)
    # input("-- press enter to close --")
