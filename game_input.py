import pyautogui
import game_reader

# clicks on one of the game's cells, given its column and row
# window_position is a tuple containing the position of the game window
# the click is right if specified, otherwise is a left click 
def click_cell(window_position, col, row, right_click=False):
    # position of the upper left cell
    initial_cell_x = window_position[0] + game_reader.horizontal_ui_size
    initial_cell_y = window_position[1] + game_reader.vertical_ui_size

    # now we go to the center of the desired cell
    cell_pos_x = initial_cell_x + (col * game_reader.square_size) + game_reader.middle_pixel_pos[0]
    cell_pos_y = initial_cell_y + (row * game_reader.square_size) + game_reader.middle_pixel_pos[1]

    # execute the click on this position
    if right_click:
        pyautogui.click(cell_pos_x, cell_pos_y, button='right')
    else:
        pyautogui.click(cell_pos_x, cell_pos_y, button='left')

    return
