#Chess System for Vampire the Masquerade

##Rules:
1. Calculation is Intelligence + Academics. This is a multiple success game.
2. The game runs at diff 7. If you have a speciality or secondary skill, at diff 5. Allowed are Game-Playing and Chess.
3. At 20 successes, the players must begin to declare 'check' for added tension.
4. The game runs until one players has gained 25 successes.

###Commands:

#####!chess
This starts the game of chess in the channel. There can only be one game a channel.<br>
This unlocks the commands: !white and !black for player moves.<br>
The first two players to cast this are locked in as players of this game.<br>
A new game can be started with !chess newgame<br>

#####!white <dice> (diff)
White moves first. The command is !white <dice>. **Example: !white 7.**<br>
If the player has a speciality or game playing. Difficulty can be adjusted manually, by passing a second number.<br>
**Example:** !white 7 5; which sets the difficulty at 5 instead of 7.<br>

#####!black <dice> (diff)
Black moves next. The command is !black <dice>. **Example: !black 7.**<br>
If the player has a speciality or game playing. Difficulty can be adjusted manually, by passing a second number.<br>
**Example:** !black 7 5; which sets the difficulty at 5 instead of 7.<br>

###Game Progress
As the players make their moves, the game maintains the numbers on their behalf. Showing total progress.<br>
It will automatically throw 'check' if the total successes are 20 or more.<br>
At 25 or greater successes, it throws 'Checkmate' to announce the end of the game.<br>
This also clears the current game from the channel and removes the players from the lock list.<br>
Should a new game need be started in the middle of an existing game, it can be reset with !chess newgame<br>



