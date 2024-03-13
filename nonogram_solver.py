from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
import numpy as np
import os
import sys
import time
from utils import *


def solve_nonogram(driver, solve_starting_puzzle):
    # press the "New Puzzle" button to reset timer (and find new puzzle)
    if not solve_starting_puzzle:
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

    return nonogram_grid, n_rows # need n_rows for cache dictionary


# Collect User Input
def user_input():
    # url of puzzle to solve (take the "Progress Permalink:" in the "Share" drop down)
    # this will not be the puzzle solved if the "New Puzzle" button is pressed (see first few lines of solve_nonogram function)
    puzzle_link = input("Input the peramlink of the puzzle: ")

    # If the puzzle is a speical Daily, Weekly, or Monthly puzzle, there is no "New Puzzle" button
    is_special_puzzle = input("\n***\n\nIs this a special Daily, Weekly, or Monthly puzzle? (y/n): ").lower()
    is_special_puzzle = True if is_special_puzzle == 'y' else False

    if not is_special_puzzle:
        # Since the time is already running on the puzzle, the user can choose to reset the time by finding a new puzzle
        solve_starting_puzzle = input("\n***\n\nThe time is already running on the puzzle.\nWant to start by finding a new puzzle so time resets? (y/n): ")
        solve_starting_puzzle = False if solve_starting_puzzle.lower() == 'y' else True

        # number of mazes to solve (iterations in the loop below)
        num_mazes_solve = int(input("\n***\n\nHow many puzzles do you want to solve in a row: "))
    else:
        solve_starting_puzzle = True
        num_mazes_solve = 1
    
    return puzzle_link, is_special_puzzle, solve_starting_puzzle, num_mazes_solve

# The special puzzle page takes a puzzle_id and the size of the puzzle
def specific_puzzle(driver, puzzle_id, size_key):
    size_select = driver.find_element(By.ID, "size")
    options = size_select.find_elements(By.TAG_NAME, "option")
    for option in options:
        if option.get_attribute("value") == str(size_key):
            option.click()
            break

    puzzle_input = driver.find_element(By.NAME, "specid")
    driver.execute_script(f"arguments[0].value = '{puzzle_id}';", puzzle_input)

    # Then we click the "Choose" button
    button = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"][value="   Choose   "]')
    button.click()


if __name__ == "__main__":
    # check if command line arguments were passed
    if len(sys.argv) > 1:
        # if so, the first argument is the puzzle ID
        puzzle_id = sys.argv[1]
        size_key = int(sys.argv[2]) # 5x5 = 0, 10x10 = 1,..., 25x25 = 4
        puzzle_link = 'https://www.puzzle-nonograms.com/specific.php'
        num_mazes_solve = 1
        solve_starting_puzzle = True
        is_special_puzzle = False
    else:
        # Collect User Input
        puzzle_link, is_special_puzzle, solve_starting_puzzle, num_mazes_solve = user_input()
    
    # Check if the cache file exists
    if os.path.exists('solved_puzzles_cache.npy'):
        # Load the cache from the file
        solved_puzzles_cache = np.load('solved_puzzles_cache.npy', allow_pickle=True).item()
    else:
        # Initialize the cache dictionary
        solved_puzzles_cache = {}

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
        if len(sys.argv) == 1:
            if not is_special_puzzle:
                # get the puzzle size and id for the cache
                puzzle_id = driver.find_element(By.ID, "puzzleID").text

                size_info = driver.find_element(By.CSS_SELECTOR, 'div.puzzleInfo p').text[:2]
                size = int(size_info[0]) if size_info.startswith('5') else int(size_info) # could be '5x' or '10','15','20','25
                size_key = int(size/5) - 1      # 5x5 = 0, 10x10 = 1,..., 25x25 = 4
            else:
                puzzle_id = -1
                size_key = -1
        else:
            # Here, we are in the choose specific puzzle page, we need to input the puzzle size and puzzle id
            specific_puzzle(driver, puzzle_id, size_key)

        # check if the puzzle has already been solved (and cached)
        if (puzzle_id,size_key) in solved_puzzles_cache:
            update_website_grid(driver, solved_puzzles_cache[(puzzle_id,size_key)])
        else:
            nonogram_grid, size = solve_nonogram(driver,solve_starting_puzzle)
            update_website_grid(driver, nonogram_grid)
            
            if not is_special_puzzle:
                # Save the solved puzzle to the cache
                solved_puzzles_cache[(puzzle_id,size_key)] = nonogram_grid

        # uncomment if you want to see the puzzle finished before going to next puzzle
        time.sleep(3)

        # click the "New Puzzle" after solving the puzzle
        if solve_starting_puzzle and i < num_mazes_solve - 1:
            new = driver.find_element(By.ID, "btnNew")
            new.click()
    
    # Save the cache to a file
    np.save('solved_puzzles_cache.npy', solved_puzzles_cache)
