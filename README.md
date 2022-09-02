# minesweeperbot
bot that plays windows xp minesweeper
## Requirements
First of all, you need the Minesweeper game itself. I used the one avaliable at http://www.minesweeper.info/downloads/WinmineXP.html, and in general any version of the original Windows XP's Minesweeper should work perfectly. Any other versions of Minesweeper will probably require editing the code for board recognition.
As for Python, i used version 3.10.6, and any other versions are untested. You will need the packages pyautogui, pywin32 (which includes win32gui, the one used here), termcolor and Pillow

## Usage
There are multiple constants declared on game_reader.py you will have to modify if you are using a different version of the game. If you are using the same version as I am, just open the game and execute the program with:

python3 solver.py \<difficulty\>

Here, \<difficulty\> can be b (begginer), i (intermediate), e (expert) or c (custom), and has to be set according to the one you are playing the game on. In the case of custom difficulty three more arguments are expected: num_rows, num_cols and num_mines of the custom game, in that order.

## How it works
### Game input / output
As their names imply, the **game_reader.py** and **game_input.py** files are dedicated to game interaction. **game_input** simply clicks specific tiles using pyautogui, taking control of the mouse. **game_reader** takes a screenshot of the game and turns it into a 2-dimensional array representing the current state of the board. The recognition of the type of each cell is made reading specific pixels and comparing them to the values of each type of cell (numerical, empty, unknwon, flagged or clicked mine). This part is arbitrary as the pixels and colors we use are meant to work specifically with our version of the game, so all this code is not expected to work with other versions of Minesweeper.

### The solver itself
In order to play the game we use two different algorythms, one simpler than the other. The basic one, or **singlesquare**, goes through every numbered cell in the game and counts the number of flagged and unknown tiles around them. If the number of the cell is equal to the number of flagged cells, then it pops the rest of unknown tiles arund it, as they cannot be mines. If the number of flagged plus the number of unflagged is equal to the number of the cell, then all of them are tiles, so it flags all the unflagged ones.

This algorythm is used at the start of the game, and is good enough to win some games in the begginer and intermediate difficulty. However, if this method gets stuck we call the **multisquare** solver, which is more powerful but can also be incredibly slow. In the multisquare method, we take all the "border" tiles (unknown tiles adjacent to a numbered tile), divide them in groups where what happens on a group doesn't affect the other, and then calculate all viable solutions for mines on these border groups. If there are tiles that are never a mine in any solution, we pop them, and if there are always a mine, we flag them. So far all moves have been deterministic, and we had no chance of losing in any of them. However, if we get stuck at this point we need to make a guess, so we pop the tile with the lowest (estimated) chance of containing a mine, according to all of the possible solutions we have enumerated. 

While this algorythm has a much greater win rate that just the singlesquare one, it's complexity increases exponentially with the number of border tiles, which can be seen specially on the expert difficulty. So what the solver does is use the singlesquare method by default, resort to multisquare if it gets stuck, and then return to singlesquare. 
