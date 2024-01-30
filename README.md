# Nonogram Solver

## Overview

I have played the Nonograms app on my iphone for quite some time. After my final exams one semester, I found there was an online version (which probably predated the iphone app), at https://www.puzzle-nonograms.com/, and decided to find a way to automate the puzzles.

## Features

- **Selenium:** Uses Selenium for web automation and to interact with the puzzles on the website.
- **Algorithm:** Implements an algorithm to solve nonogram puzzles.

## Requirements

- Python 3
- Selenium
- ChromeDriver
- NumPy
- Potentially other dependecies

## Algorithm

The algorithm I developed to solve the nonogram puzzles (calculate_options, fill_cells, remove_options in utils.py) was inspired by Hennie de Harder through this article: https://towardsdatascience.com/solving-nonograms-with-120-lines-of-code-a7c6e0f627e4. The article also gives an overview on how the puzzle is formatted, if that is something you need to see.

Hennie explains there are three general steps in the process.
- Calculate every option each row and column could be filled according to their corresponding clues.
- Fill the cells that you know must be filled (the intersection of all the options for that row / column)
- Remove options based on step 2

In step 2, I also "unfilled" (put an X) cells I knew must be unfilled (the cell doesn't appear in the union of all the options for that row / column).
I solved the puzzle using a NumPy array. After solving the puzzle, I use Selenium to access the cell elements on the website and click the cells that should be filled. Visually, the puzzle will always appear to be solved top to bottom. An optimization that could be implemented is to fill the cells as the puzzle is being solved (though I don't think it would do much).
  
Currently, I don't plan on adding more to this program... but who knows.

## Use the program

To use the program, go to the nonograms website linked above.
- Find the puzzle you want to solve
- Press the "Share" button under the puzzle
- Copy the "Progress Permalink" and paste it into the specified arguement in the "solve_nonogram" function in "nonogram_solver.py"

The puzzle you chose will be the starting point. The code starts the "solving process" by getting a new puzzle (it will be the same dimension as the selected puzzle) so that the timer will restart. If you want to solve the puzzle you chose, comment out the specified lines in "solve_nonogram," but make sure to uncomment out the lines specified in "__main__" if you want to solve multiple puzzles in a row. Finally, of course, run the program using "python3 nonogram_solver.py" in terminal.
