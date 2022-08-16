import sys
import copy
import game_reader
import game_input
import random

# global variable to hold all possible solutions that are
# going to be calculated by the multisquare algorythm
possible_sols = []

# solves the game, by now, with the single square method
# this method checks the surrounding tiles of a numbered square,
# placing mines in all unknown tiles if all of them must be
# mines and popping them if all flags have already been placed
# returns 1 if it has been able to solve the game, 0 if it got
# stuck and -1 if it lost the game on a random starting click
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
    ret = -1
    while ret != 0:
        im = game_reader.get_game_screenshot()
        if im:
            board = game_reader.read_board(im)
        # pop a random tile until it reveals a 0,
        # which means a large area has been revealed
        ret = click_random_tile()
        # we lost while random clicking
        if ret == -3:
            print("Bad luck, lost on a random starting click :(")
            return -1

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
                                    tile[0], tile[1],
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
                                    tile[0], tile[1],
                                    right_click=False   # this pops tiles
                                )
                                updated = True
                                bigUpdating = True


                # when there are no mines left, we pop all unopened cells
                if board[i][j] == -1 and mines_left == 0:
                    game_input.click_cell(
                        game_reader.get_window_position(),
                        i, j,
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
        return 1
    else:
        print("Dead end encountered...")
        return 0

# for now, this takes the board already screenshot, expecting to
# be called from basic_solve only if it gets stuck
def multisquare_solve(board):
    # get all border tiles
    border_tiles = get_border_tiles(board)

    # now we get all the possible mine combinations of border_tiles
    global possible_sols
    possible_sols = []
    generate_solutions_rec(board, border_tiles, {})

# recursive function to generate all possible valid combinations for the 
# list of tiles border_tiles, where current_mines is a dictionary that matches
# tiles from border_tiles to boolean values if there is or isnt a mine
# on the solution path we are currently exploring, so that when all of
# border_tiles are on current mines recursion ends
def generate_solutions_rec(board, border_tiles, current_mines):
    # check if the solution is valid so far 
    # this is the board updated with the combination we have so far
    virtual_board = generate_virtual_board(board, current_mines)
    if not valid_board(virtual_board):
        # we dont add nothing to the possible_sols list, ending recursion
        return
    
    # base case, we have as many tiles decided with/without mine
    # as tiles we had on the border originally, we found a solution
    if len(current_mines) == len(border_tiles):
        global possible_sols
        possible_sols.append(current_mines)
        return
    
    # otherwise, we split in two smaller recursive settings:
    # one when next undecided tile has a mine and one when it doesnt

    # the first tile that has not been decided yet in current_mines
    next_tile = border_tiles[len(current_mines)]

    # next_tile has a mine, we continue the recursion
    current_mines_1 = current_mines.copy()
    current_mines_1[next_tile] = True
    generate_solutions_rec(board, border_tiles, current_mines_1)
        
    # next_tile has NO mine, we continue the recursion
    current_mines_2 = current_mines.copy()
    current_mines_2[next_tile] = False
    generate_solutions_rec(board, border_tiles, current_mines_2)

# generates the hypothetical board that would be the result of modifying
# the existing board with the guessses present on the current_mines dict
def generate_virtual_board(board, current_mines):
    virtual_board = copy.deepcopy(board)

    # update every tile on the virtual board with the mine information
    # present on current_mines (if there is/isnt a mine on those tiles)
    for tile in current_mines:
        if current_mines[tile] == True:
            # place a flag there
            virtual_board[tile[0]][tile[1]] == -2
        else:
            # no mine on this tile
            # the easiest way to label the tile as "no mine" is to
            # put a 0 so that the valid_board function doesnt check its
            # correction (even though we dont now the tile's content)
            virtual_board[tile[0]][tile[1]] == 0

    return virtual_board

# checks if the given board is in a valid game state
def valid_board(board):
    # go through every tile
    for i in range(game_reader.num_cols):
        for j in range(game_reader.num_rows):
            if board[i][j] > 0:     # we only check numbered tiles
                mines_placed = get_flagged_around(board, i, j)
                unknown_tiles = get_unflagged_around(board, i, j)
                # there are more mines that should be, error
                if mines_placed > board[i][j]:
                    return False
                # there are less possible mines that should be, error
                if mines_placed + unknown_tiles < board[i][j]:
                    return False

    return True

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

# returns the number of opened tiles around the one given its coordinates
def get_opened_around(board, row, col):
    opened = 0

    for tile in get_all_surrounding_tiles(row, col):
        opened += (board[tile[0]][tile[1]] >= 0)
    
    return opened
    
# returns a list of tuples (row, col) of tiles that are considered border,
# that is, that are unopened and have at least one opened tile around them
def get_border_tiles(board):
    border_tiles = []

    for i in range(game_reader.num_cols):
        for j in range(game_reader.num_rows):
            # unknown tile with at least one opened tile around them
            if board[i][j] == -1 and get_opened_around(board, i, j) > 0:
                border_tiles.append((i, j))

    return border_tiles

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
    
    #basic_solve()
    possible_sols = []
    border_tiles = [(1, 1), (2, 2), (3, 3)]
    generate_solutions_rec(0, border_tiles, {})
    print(possible_sols)
    print(len(possible_sols))