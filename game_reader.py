import pyautogui
import win32gui

# constant declaration, could be moved somewhere else
game_window_title = "Minesweeper"

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


im = get_game_screenshot()
if im:
    im.show()