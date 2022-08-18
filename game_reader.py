import pyautogui
import win32gui
import game_input
import termcolor
import os

os.system('color')

# constant declaration, could be moved somewhere else
game_window_title = "Minesweeper"
square_size = 16

# the middle pixel for each square, which will be 
# used to identify the number on each tile using color
middle_pixel_pos = (square_size/2 - 1, square_size/2 - 1)

# in case of the numbers that dont paint the middle pixel,
# we will use this second pixel to get its color
aux_pixel_pos = (7, 3)

# this could be modified to include presets for 
# preexisting difficulty settings
num_rows = 16
num_cols = 16
num_mines = 40

# this two are used to get the upper left corner of the 
# first square in the game, ignoring user interface
vertical_ui_size = 55
horizontal_ui_size = 12

# the position of the minesweeper window, which will be
# updated after every call to get_game_screenshot
global window_position

# all of the colors to identify tiles via individual pixels
WHITE = (255, 255, 255) # on the upper left corner for unclicked tiles
                        # also on the middle pixel for bombed mines
LIGHT_GREY = (192, 192, 192)    # background color
BLUE = (0, 0, 255)              # for the number 1
GREEN = (0, 128, 0)             # for the number 2
RED = (255, 0, 0)               # for the number 3
DARK_BLUE = (0, 0, 128)         # for the number 4
DARK_RED = (128, 0, 0)          # for the number 5
GREEN_BLUE = (0, 128, 128)      # for the number 6
BLACK = (0, 0, 0)               # for the number 7
GREY = (123, 123, 123)          # for the number 8

# returns the screenshot of the game window
def get_game_screenshot():
    # get minesweeper window 
    gamewnd = win32gui.FindWindow(None, game_window_title)
    if gamewnd:
        # take the window to the foreground 
        win32gui.SetForegroundWindow(gamewnd)
        x, y, x1, y1 = win32gui.GetClientRect(gamewnd)
        x, y = win32gui.ClientToScreen(gamewnd, (x, y))
        x1, y1 = win32gui.ClientToScreen(gamewnd, (x1 - x, y1 - y))

        # save the position of the window
        global window_position 
        window_position = (x, y)

        # get screenshot of desired area
        im = pyautogui.screenshot(region=(x, y, x1, y1))
        return im
    else:
        # error control should be implemented someday (?)
        print('Window not found!')

# reads the current state of the board from the given screenshot
def read_board(im):
    # the board is a two-dimensional array whose elements are the number
    # of mines surrounding each cell, -1 if it is unknown
    # or -2 if a flag has been already placed there
    board = []

    # the region from the upper left square will start here
    currentX = horizontal_ui_size
    currentY = vertical_ui_size

    # go through all cells 
    for i in range(num_rows):
        board.append([])

        for j in range(num_cols):
            # crops the part of the image from this cell 
            crop_box = (currentX, currentY,
                currentX + square_size,
                currentY + square_size)
            square = im.crop(crop_box)

            #filename = "imgs/sq_" + str(i) + "_" + str(j) + ".png"
            #square.save(filename)

            # get number from each cropped square
            num_mines = get_number_from_region(square)
            board[i].append(num_mines)

            currentX += square_size
        
        currentY += square_size
        currentX = horizontal_ui_size

    return board

# reads the pixels in a region to determine the number that is being shown
# returns the number of mines surrounding the region (0 to 8), 
# -1 if cell situation is unknown (unclicked and unmarked), 
# -2 if cell is unclicked but has been flagged as mine, and
# -3 if cells contains a mine that has been exploded (game over)
def get_number_from_region(region):
    # first of all, get the upper left pixel. if it is white,
    # the square has not been clicked yet, so it can be 
    # either unknown or have a flag placed
    pixel1 = region.getpixel((0,0))
    middle_pixel = region.getpixel(middle_pixel_pos)

    if pixel1 == WHITE:
        # now we differentiate between unknown and flags        
        if middle_pixel == LIGHT_GREY:
            # unknown number of mines and no flag
            return -1
        else:
            # a flag has been placed here
            return -2
    else:
        # differentiate between possible number tiles
        if middle_pixel == LIGHT_GREY:
            # this can mean no mines (empty square), but also 2 or 7,
            # as these numbers arent drawn on the middle pixel, so we
            # check another pixel that should be colored in these cases
            aux_pixel = region.getpixel(aux_pixel_pos)
            if aux_pixel == GREEN:
                # 2 mines nearby
                return 2
            elif aux_pixel == BLACK:
                # 7 mines nearby
                return 7
            else:
                # 0 mines nearby, empty square
                return 0
        elif middle_pixel == BLUE:
            # 1 mine nearby
            return 1
        elif middle_pixel == RED:
            # 3 mines nearby
            return 3
        elif middle_pixel == DARK_BLUE:
            # 4 mines nearby
            return 4
        elif middle_pixel == DARK_RED:
            # 5 mines nearby
            return 5
        elif middle_pixel == GREEN_BLUE:
            # 6 mines nearby
            return 6
        elif middle_pixel == GREY:
            # 8 mines nearby
            return 8
        elif middle_pixel == WHITE:
            # exploded mine (game over)
            return -3

    print("Error: unidentified region")
    return -1

# sets the values of the grid according to the specified difficulty,
# which is set on argv[1]:
# b: beginner, i: intermediate, e: expert, c: custom
# in the case of custom difficulty we expect 3 extra arguments:
# num_rows, num_cols and num_mines of the custom game, in that order
# default values for the windows xp minesweeper are used
def load_difficulty(argv):
    global num_rows, num_cols, num_mines

    if not argv: 
        # if no argument is specified we use the values set above
        return
    elif argv[1] == 'b':    # beginner
        num_rows = 9
        num_cols = 9
        num_mines = 10
    elif argv[1] == 'i':    # intermediate
        num_rows = 16
        num_cols = 16
        num_mines = 40
    elif argv[1] == 'e':    # expert
        num_rows = 16
        num_cols = 30
        num_mines = 99
    elif argv[1] == 'c' and len(argv) > 4: # custom
        num_rows = int(argv[2])
        num_cols = int(argv[3])
        num_mines = int(argv[4])

# auxiliary function to see the board more clearly
def print_board(board):
    for i in range(num_rows):
        for j in range(num_cols):
            print_cell(board[i][j])
        
        print("\n", end='')

def get_window_position():
    return window_position

# prints the number of mines on a cell in a clear way.
# for 1-5 mines we use colors similar to the ones in game 
# for visibility, and 6-8 should not happen very often
def print_cell(content):
    if content == -1:   # unknown
        print(" u ", end='')
    elif content == -2: # flag
        print(" f ", end='')
    elif content == -3: # exploded mine
        print(" m ", end='')
    elif content == 0:  # empty
        print("   ", end='')
    elif content == 1:  # 1 mines
        print(termcolor.colored(" 1 ", 'cyan'), end='')
    elif content == 2:  # 2 mines
        print(termcolor.colored(" 2 ", 'green'), end='')
    elif content == 3:  # 3 mines
        print(termcolor.colored(" 3 ", 'red'), end='')
    elif content == 4:  # 4 mines
        print(termcolor.colored(" 4 ", 'blue'), end='')
    elif content == 5:  # 5 mines
        print(termcolor.colored(" 5 ", 'magenta'), end='')
    elif content == 6:  # 6 mines
        print(termcolor.colored(" 6 ", 'yellow'), end='')
    elif content == 7:  # 7 mines
        print(termcolor.colored(" 7 ", 'yellow'), end='')
    elif content == 8:  # 8 mines
        print(termcolor.colored(" 3 ", 'yellow'), end='')

if __name__ == "__main__":     
    im = get_game_screenshot()
    if im:
        #im.show()
        #im.save("testimage.png")
        board = read_board(im)
        print_board(board)

        # left click on a square
        game_input.click_cell(window_position, 6, 2)
        # right click on another one
        game_input.click_cell(window_position, 4, 4, True)

        # print the board again
        im = get_game_screenshot()
        board = read_board(im)
        print("\n")
        print_board(board)

