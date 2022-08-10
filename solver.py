import sys
import game_reader
import game_input
import random

# solves the game, by now, with the single square method
# this method checks the surrounding tiles of a numbered square,
# placing mines in all unknown tiles if all of them must be
# mines and popping them if all flags have already been placed
def basic_solve():
    gameOver = False    
    mines_left = game_reader.num_mines

    # we use two updates: one for the smaller loop to see if 
    # working with a specific tile has caused any changes and a
    # new screenshot is needed and another for the bigger loop to
    # see if we are still making any progress or if we are stuck
    updated = True
    bigUpdating = True

    # we start popping a random unknown tile
    im = game_reader.get_game_screenshot()
    if im:
        board = game_reader.read_board(im)

    ret = -1
    while ret != 0:
        # pop a random tile until it reveals a 0,
        # which means a large area has been revealed
        ret = click_random_tile()

    while not gameOver:
        if not bigUpdating:
            break
        else:
            im = game_reader.get_game_screenshot()
            if im:
                board = game_reader.read_board(im)
                bigUpdating = False

        # go through each tile
        for i in range(game_reader.num_rows):
            for j in range(game_reader.num_cols):
                if updated:
                    im = game_reader.get_game_screenshot()
                if im:
                    board = game_reader.read_board(im)
                    updated = False

                if board[i][j] > 0:     # case of a numbered square
                    unflagged = get_unflagged_around(board, i, j)
                    flagged = get_flagged_around(board, i, j)

                    # if the number of unflagged mines is the number
                    # of unopened mines around our tile
                    if unflagged + flagged == board[i][j]:
                        # all unflagged are mines
                        # flag all unflagged squares around
                        for tile in get_all_surrounding_tiles(i, j):
                            if board[tile[0]][tile[1]] == -1:   # only unknown
                                game_input.click_cell(
                                    game_reader.get_window_position(),
                                    tile[0],
                                    tile[1],
                                    right_click=True    # this flags tiles
                                )
                                mines_left -= 1
                                updated = True
                                bigUpdating = True
                        
                    # if we have already flagged all mines around us
                    if flagged == board[i][j]:
                        # pop all unflagged tiles
                        for tile in get_all_surrounding_tiles(i, j):
                            if board[tile[0]][tile[1]] == -1:   # only unknown
                                game_input.click_cell(
                                    game_reader.get_window_position(),
                                    tile[0],
                                    tile[1],
                                    right_click=False   # this pops tiles
                                )
                                updated = True
                                bigUpdating = True


                # when there are no mines left, we pop all unopened cells
                if board[i][j] == -1 and mines_left == 0:
                    game_input.click_cell(
                        game_reader.get_window_position(),
                        i,
                        j,
                        right_click=False   # this pops tiles
                    )
                    updated = True
                    bigUpdating = True

    # end while

    # we have to check how many mines are left because clicking the last
    # unmined square makes the game automatically flag all remaining mines
    # so we cannot trust our previous count of mines left
    mines_left = recompute_mines_left(board)

    # win / stuck conditions
    if mines_left == 0:
        print("Game won!")
    else:
        print("Dead end encountered...")


# left clicks (pops) on a random tile in the game and
# returns the number underneath said tile
def click_random_tile():
    row = random.randrange(game_reader.num_rows)
    col = random.randrange(game_reader.num_cols)

    game_input.click_cell(
        game_reader.get_window_position(),
        row,
        col,
        right_click=False   # this pops tiles
    )

    im = game_reader.get_game_screenshot()
    if im:
        board = game_reader.read_board(im)

    return board[row][col]

# get a list of all tiles surrounding the one with given coordinates,
# taking into acount corners and edges of the game grid
# return is a list of tuples (row, column) integers
def get_all_surrounding_tiles(row, col):
    tiles = []

    if row > 0 and col > 0:
        # up and to the left
        tiles.append((row-1,col-1))
    if row > 0:
        # straight up
        tiles.append((row-1,col))
    if row > 0 and col < game_reader.num_cols-1:
        # up and to the right
        tiles.append((row-1,col+1))
    if col > 0:
        # straight left
        tiles.append((row,col-1))
    if col < game_reader.num_cols-1:
        # straight right
        tiles.append((row,col+1))
    if row < game_reader.num_rows-1 and col > 0:
        # down and to the left
        tiles.append((row+1,col-1))
    if row < game_reader.num_rows-1:
        # straight down
        tiles.append((row+1,col))
    if row < game_reader.num_rows-1 and col < game_reader.num_cols-1:
        tiles.append((row+1,col+1))

    return tiles

# returns the number of unkwnown tiles around the one given its coordinates
def get_unflagged_around(board, row, col):
    unflagged = 0

    for tile in get_all_surrounding_tiles(row, col):
        unflagged += (board[tile[0]][tile[1]] == -1)
    
    return unflagged

# returns the number of flag tiles around the one given its coordinates
def get_flagged_around(board, row, col):
    flagged = 0

    for tile in get_all_surrounding_tiles(row, col):
        flagged += (board[tile[0]][tile[1]] == -2)
    
    return flagged
    
# calculates the number of mines left as the starting number
# minus all the flags that have been placed on the grid
def recompute_mines_left(board):
    mines_left = game_reader.num_mines

    for i in range(game_reader.num_rows):
        for j in range(game_reader.num_cols):
            mines_left -= (board[i][j] == -2)

    return mines_left

if __name__ == "__main__":
    # difficulty can be specified through command line
    if len(sys.argv) > 1:
        game_reader.load_difficulty(sys.argv[1])
    
    basic_solve()