from itertools import combinations
from selenium.webdriver.common.by import By
from time import sleep


def extract_clues(task_elements):
    clues_list = []

    task_groups = task_elements[0].find_elements(By.CLASS_NAME, "task-group")

    for task_group in task_groups:
        task_cells = task_group.find_elements(By.CLASS_NAME, "task-cell")
        clues = [int(cell.text.strip()) for cell in task_cells if cell.text.strip()]
        clues_list.append(clues)

    return clues_list


def calculate_options(size, clues_list):
    all_options = []

    for clues in clues_list:
        n_groups = len(clues)
        n_empty = size - sum(clues) - (n_groups - 1)

        opts = list(combinations(range(n_groups + n_empty), n_groups))

        options = []

        for opt in opts:
            option = []
            start = opt[0]

            for index in range(len(opt)):
                if index > 0:
                  start = end + opt[index] - opt[index - 1]

                end = start + clues[index]
                option.extend(range(start, end))

            options.append(option)

        all_options.append(options)

    return all_options


def fill_cells(grid, row_options, col_options):
    n_rows, n_columns = grid.shape

    for i in range(n_rows):
        common_indices = set.intersection(*map(set, row_options[i]))
        all_indices = set.union(*map(set, row_options[i]))
        for idx in range(n_columns):
            if idx in common_indices:
                grid[i, idx] = 1
            elif idx not in all_indices:
                grid[i, idx] = -1

    for j in range(n_columns):
        common_indices = set.intersection(*map(set, col_options[j]))
        all_indices = set.union(*map(set, col_options[j]))
        for idx in range(n_rows):
            if idx in common_indices:
                grid[idx, j] = 1
            elif idx not in all_indices:
                grid[idx, j] = -1


def remove_options(grid, row_options, col_options):
    n_rows, n_columns = grid.shape

    for i in range(n_rows):
        for j in range(n_columns):
            if grid[i, j] == -1:
                # remove options which include cells that shouldn't be there
                row_options[i] = [opt for opt in row_options[i] if j not in opt]
                col_options[j] = [opt for opt in col_options[j] if i not in opt]
            if grid[i, j] == 1:
                # remove options which don't include cells that should be there
                row_options[i] = [opt for opt in row_options[i] if j in opt]
                col_options[j] = [opt for opt in col_options[j] if i in opt]


def update_website_grid(driver, nonogram_grid):
    grid = driver.find_element(By.CLASS_NAME, "nonograms-cell-back")
    
    # get list of rows in the grid
    row_elements = grid.find_elements(By.CLASS_NAME, "row")

    for i, row_element in enumerate(row_elements):
        cell_elements = row_element.find_elements(By.CLASS_NAME, "cell")

        for j, cell_element in enumerate(cell_elements):
            # click the cell if it should be filled
            if nonogram_grid[i, j] == 1:
                cell_element.click()

    # press the "done" button to finish
    # done = driver.find_element(By.ID, "btnNew")
    # done.click()

# def update_website_grid(driver, nonogram_grid):
#     grid = driver.find_element(By.CLASS_NAME, "nonograms-cell-back")

#     # Get list of rows in the grid
#     row_elements = grid.find_elements(By.CLASS_NAME, "row")
#     cached_cells = [row.find_elements(By.CLASS_NAME, "cell") for row in row_elements]

#     for i, cell_elements in enumerate(cached_cells):
#         for j, cell_element in enumerate(cell_elements):
#             # If the cell should be filled and is currently "cell-off"
#             if nonogram_grid[i, j] == 1:
#                 # Directly update the class to "cell-on"
#                 driver.execute_script("""var element = arguments[0]; var currentClass = element.getAttribute('class');
#                                         var newClass = currentClass.slice(0, -3) + 'on'; element.setAttribute('class', newClass);""", cell_element)