import pyautogui
import win32gui

# constant declaration, could be moved somewhere else
game_window_title = "Minesweeper"
square_size = 16

# this could be modified to include presets for 
# preexisting difficulty settings
num_rows = 9
num_cols = 9

# this two are used to get the upper left corner of the 
# first square in the game, ignoring user interface
vertical_ui_size = 55
horizontal_ui_size = 12

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
        for j in range(num_cols):
            # crops the part of the image from this cell 
            crop_box = (currentX, currentY,
                currentX + square_size,
                currentY + square_size)
            square = im.crop(crop_box)

            #filename = "imgs/sq_" + str(i) + "_" + str(j) + ".png"
            #square.save(filename)

            # TODO: get number from each cropped square

            currentX += square_size
        
        currentY += square_size
        currentX = horizontal_ui_size

    return board

im = get_game_screenshot()
if im:
    im.show()
    #im.save("testimage.png")
    board = read_board(im)

