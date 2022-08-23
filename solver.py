import sys
import copy
import game_reader
import game_input
import random

# global variable to hold all possible solutions that are
# going to be calculated by the multisquare algorythm
possible_sols = []

# when there are less that LOW_TILES_THRESHOLD unknown tiles left,
# the multisquare algorythm will calculate the mine combinations on
# all remaining tiles instead of just the border tiles, as cost
# now is feasible. Ideally, this threshold shouldn exist and the 
# recursion should be applied on all tiles in order to solve the
# highest amount of boards possible, but cost is exponential to
# the number of tiles we want to calculate combinations of
LOW_TILES_THRESHOLD = 20

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
        if not bigUpdating:     # last loop did nothing
            # differentiate between game won and getting stuck
            mines_left = recompute_mines_left(board)
            if mines_left > 0:
                # when this algorythm gets stuck, we use the multisquare solver
                im = game_reader.get_game_screenshot()
                if im:
                    board = game_reader.read_board(im)

                print("Using multisquare solver")
                ret = multisquare_solve(board)
                if ret == 0:
                    print("multisquare did nothing")
                    break
                elif ret == -1:
                    # we lost on an undeterministic guess, exit solver
                    return 0
            else:
                break

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
        # we may still need to pop some tiles we know are clean
        pop_all_unknowns(board)
        print("Game won!")
        return 1
    else:
        print("Dead end encountered...")
        return 0

# advanced (and slower) method to be used when the singlesquare solver gets stuck.
# this method divides all border tiles into independent regions and generates all
# possible solutions for these regions, popping tiles that are always empty on all
# solutions and flagging the ones that are always mines, and if no tile matches any
# of this criteria it will pop the one with the highest (estimated) probability
# of being safe, which might lead to a game over.
# returns 1 if the solver made progress, -1 if it caused a gameover and 0 otherwise
def multisquare_solve(board):
    # to check if this method was able to progress on the game or if we are stuck
    did_something = False
    working_on_all_tiles = False

    unknown_tiles = get_unknown_tiles(board)

    # if there are less unknown tiles that a certain optimization threshold,
    # we calculate the combinations on all the remaining tiles instead of just
    # the border ones, and thus we dont separate them in border_groups.
    # While this second option is better (as it would allow us to solve any
    # deterministic board -that can be solved without guessing-), its cost
    # is extremely high so we cant apply it until the late game
    if len(unknown_tiles) > LOW_TILES_THRESHOLD:
        # get all border tiles
        border_tiles = get_border_tiles(board)
        # divide border_tiles in equivalency groups so all mine
        # combinations can be considered separatedly (which is faster)
        border_groups = generate_border_groups(border_tiles)
        print(border_groups)
    else:
        # no grouping tiles for the late game method
        print("Using late game optimization")
        border_groups = [unknown_tiles]
        working_on_all_tiles = True

    # this is the highest probability of a tile NOT having a mine out of all
    # tiles in border_groups, which will be popped only if we cannot make
    # any deterministic/certain move. Note that these probabilities are only an
    # estimate if we are only calculations on a limited set of border tiles, as
    # we are not taking into account all of the possible combinations across all
    # the board with the exact ammount of mines left so combinations on a single
    # border group may not be equally likely, but the estimation should be enough
    best_prob = 0
    best_tile = (-1, -1)

    # each group is treated on its own
    for group in border_groups:
        # now we get all the possible mine combinations of this group
        global possible_sols    # here is where these combinations are stored
        possible_sols = []  
        generate_solutions_rec(board, group, {}, working_on_all_tiles)

        # now we check for each border tile if it was a mine or empty
        # in all obtained solutions, in which case we flag / pop it
        for tile in group:
            times_mine = 0
            times_empty = 0

            for sol in possible_sols:
                # mine there
                if sol[tile] == True:
                    times_mine += 1
                else:   # empty space there
                    times_empty += 1

            if times_empty == 0:
                # we can 100% confirm there is a mine here!
                game_input.click_cell(
                    game_reader.get_window_position(),
                    tile[0], tile[1],
                    right_click=True    # this flags tiles
                )
                did_something = True
            elif times_mine == 0:
                # we can 100% confirm this space is empty!
                game_input.click_cell(
                    game_reader.get_window_position(),
                    tile[0], tile[1],
                    right_click=False    # this pops tiles
                )
                did_something = True
            elif not did_something:
                # only continue calculating probabilities if no move could be made
                prob = times_empty / (times_empty + times_mine)
                if prob > best_prob:
                    best_prob = prob
                    best_tile = tile

    # if no deterministic move could be made, we have to guess
    if not did_something:
        print("Guessing at tile " + str(best_tile) + " with success probability: " + str(best_prob))
        game_input.click_cell(
            game_reader.get_window_position(),
            best_tile[0], best_tile[1],
            right_click=False   # this pops tiles
        )
        did_something = True

        # we have to check for a game over
        im = game_reader.get_game_screenshot()
        if im:
            board = game_reader.read_board(im)

        if board[best_tile[0]][best_tile[1]] == -3: # we lost
            print("GAMEOVER: Guess failed")
            return -1

    # we return now to the basic algorythm, with hopes that the new state of
    # the board doesnt get it stuck. if that happens, that algorythm will 
    # call the multisquare method again
    if did_something:
        return 1
    else:
        return 0

# recursive function to generate all possible valid combinations for the 
# list of tiles border_tiles, where current_mines is a dictionary that matches
# tiles from border_tiles to boolean values if there is or isnt a mine
# on the solution path we are currently exploring, so that when all of
# border_tiles are on current mines recursion ends.
# If working_on_all_tiles is True, the recursion is being applied on all
# of the remaining unknown tiles, so the number of mines on the hypothetical
# solution must be exactly the number of mines of the game
def generate_solutions_rec(board, border_tiles, current_mines, working_on_all_tiles):
    # check if the solution is valid so far 
    # this is the board updated with the combination we have so far
    virtual_board = generate_virtual_board(board, current_mines)
    if not valid_board(virtual_board):
        # we dont add nothing to the possible_sols list, ending recursion
        return
    
    # base case, we have as many tiles decided with/without mine
    # as tiles we had on the border originally, we found a solution
    if len(current_mines) == len(border_tiles):
        # but if we are making the recursion on all tiles for the late game
        # we have to make sure that the virtual board has all mines flagged
        # (as it wont have unknown tiles anymore)
        if working_on_all_tiles and recompute_mines_left(virtual_board) != 0:
            return  # unvalid solution, we dont add it
        global possible_sols
        possible_sols.append(current_mines)
        return
    
    # otherwise, we split in two smaller recursive settings:
    # one when next undecided tile has a mine and one when it doesnt

    # the first tile that has not been decided yet in current_mines
    next_tile = border_tiles[len(current_mines)]

    # next_tile has a mine, we continue the recursion
    current_mines_1 = copy.deepcopy(current_mines)
    current_mines_1[next_tile] = True
    generate_solutions_rec(board, border_tiles, current_mines_1, working_on_all_tiles)
        
    # next_tile has NO mine, we continue the recursion
    current_mines_2 = copy.deepcopy(current_mines)
    current_mines_2[next_tile] = False
    generate_solutions_rec(board, border_tiles, current_mines_2, working_on_all_tiles)

# generates the hypothetical board that would be the result of modifying
# the existing board with the guessses present on the current_mines dict
def generate_virtual_board(board, current_mines):
    virtual_board = copy.deepcopy(board)

    # update every tile on the virtual board with the mine information
    # present on current_mines (if there is/isnt a mine on those tiles)
    for tile in current_mines:
        if current_mines[tile] == True:
            # place a flag there
            virtual_board[tile[0]][tile[1]] = -2
        else:
            # no mine on this tile
            # the easiest way to label the tile as "no mine" is to
            # put a 0 so that the valid_board function doesnt check its
            # correction (even though we dont now the tile's content)
            virtual_board[tile[0]][tile[1]] = 0

    return virtual_board

# checks if the given board is in a valid game state
def valid_board(board):
    virtual_flags = 0
    # go through every tile
    for i in range(game_reader.num_rows):
        for j in range(game_reader.num_cols):
            if board[i][j] > 0:     # we only check numbered tiles
                mines_placed = get_flagged_around(board, i, j)
                unknown_tiles = get_unflagged_around(board, i, j)
                # there are more mines that should be, error
                if mines_placed > board[i][j]:
                    return False
                # there are less possible mines that should be, error
                if mines_placed + unknown_tiles < board[i][j]:
                    return False
            elif board[i][j] == -2: 
                # we keep track of how many mines we have detected
                virtual_flags += 1

    # we discard virtual boards if they have more mines flagged that the
    # total mines the board should have. however, virtual_flags could be
    # strictly less that the total number of mines as the board we are validating
    # could still have unknown tiles (because not every unclicked tile is 
    # on the border_tiles list of tiles we are calculating combinations)
    if virtual_flags > game_reader.num_mines:
        return False

    return True

# divides border_tiles in groups of tiles that are independent, that is,
# whose tiles are at distance 1, so that the multisquare algorythm
# can be applied on each of these groups independently for speed
def generate_border_groups(border_tiles):
    border_groups = []

    tiles_to_add = copy.deepcopy(border_tiles)

    # the outer loop creates all groups
    while len(tiles_to_add) > 0:
        group = [tiles_to_add.pop()]    # get an element from the list

        updating_group = True
        # in this loop we add all elements belonging to this group
        # we may have to go through every tile in case a tile belongs
        # to the group only after another tile has been added later
        while updating_group:   # loop this until no more tiles are added
            updating_group = False
            for tile in tiles_to_add:
                # add all tiles within distance 1
                if belongs_to_group(tile, group):
                    tiles_to_add.remove(tile)
                    group.append(tile)
                    updating_group = True

        border_groups.append(group)

    return border_groups

# checks if the given tile belongs in the given equivalence group.
# this happen if the tile is at distance 1 or less (in both 
# coordinates) of any other tile in the group
def belongs_to_group(tile, group):
    for group_tile in group:
        # the tile will be on the group if its within distance 1
        # of one of the tiles already on the group
        if abs(tile[0] - group_tile[0]) <= 1 and \
            abs(tile[1] - group_tile[1]) <= 1:
            return True

    return False

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

    for i in range(game_reader.num_rows):
        for j in range(game_reader.num_cols):
            # unknown tile with at least one opened tile around them
            if board[i][j] == -1 and get_opened_around(board, i, j) > 0:
                border_tiles.append((i, j))

    return border_tiles

# returns a list of tuples (row, col) of tiles that are unknown
def get_unknown_tiles(board):
    unknown_tiles = []

    for i in range(game_reader.num_rows):
        for j in range(game_reader.num_cols):
            if board[i][j] == -1:
                unknown_tiles.append((i, j))

    return unknown_tiles

# pops all unknown tiles (only to be called if we know they arent mines)
def pop_all_unknowns(board):
    for i in range(game_reader.num_rows):
        for j in range(game_reader.num_cols):
            if board[i][j] == -1:
                game_input.click_cell(
                        game_reader.get_window_position(),
                        i, j,
                        right_click=False   # this pops tiles
                    )
    
    return
                
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
        game_reader.load_difficulty(sys.argv)
    
    basic_solve()