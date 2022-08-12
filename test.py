import solver
import game_input
import game_reader

REPETITIONS = 500   # number of valid games to play

# test program
# this plays a certain number of games on a fixed difficulty
# and counts wins and losses (times the solver got stuck).
# games lost when clicking on a random mine at the 
# beggining are not counted as losing is not the solver's fault
if __name__ == "__main__":
    # difficulty setting
    game_reader.load_difficulty("i")

    wins = 0
    valid_games = 0
    while valid_games < REPETITIONS:
        game_input.new_game()
        ret = solver.basic_solve()

        if ret == 1:    # game won
            print(str(valid_games) + ": WIN")
            wins += 1
            valid_games += 1
        elif ret == 0:  # game lost (got stuck)
            print(str(valid_games) + ": STUCK")
            valid_games += 1
        # if game was lost on a random click valid_games is not increased

    # show results
    print("TEST FINISHED. RESULTS: ")
    print("Wins: " + str(wins))
    print("Losses: " + str(REPETITIONS - wins))

    print("Win rate: " + str(wins/REPETITIONS))