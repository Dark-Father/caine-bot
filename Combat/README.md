###############
#Combat Plugin#
###############

The Combat plugin for Caine on Elysia-online.org. Track, manage and execute combat.


################################
#Initiative and Starting Combat#
################################

So first we concentrate on inits rolls, tracking those inits, displaying those inits, and managing combat rounds. 
Then we have a few functions for starting combat that automatically creates a new round in the room, and summons an ST.
-------------
Combat Management:

Using "!combat start", opens a combat tracker with round 1. 
Characters then cast !inits to add themselves to the round.
Using !newround generates a new rounds, clears existing inits list and players must cast !inits to join the newround.
There is no "turn" management to allow for players that depart in the middle of the round, that is controlled out of character.
To end the !combat, Caine looks for: !combat end.

Full Example:
!combat start
[IRC] <Caine> Combat Round started. Round 1. Declare !inits to join combat. Declare!bp spends now.

David: !inits 5
[IRC] <Caine> David rolled: 7

To add an NPC:
ST: !inits 3 villain
[IRC] <Caine> Villain rolled: 9

Once everyone has joined, the "manager" casts !showinits and Caine gives back a looped reply of all characters in round. Starting from lowest to highest.
ST: !showinits
[IRC] <Caine> David: 7
[IRC] <Caine> Villain: 9


Once the round is completed, the Storyteller casts !newround. This clears the current round, displays the new round number
and players must once again cast !inits to join the new round of combat

ST: !newround
[IRC] <Caine> New Round Started. Round 2. Declare !inits to join combat. Declare !bp spends now.

Once combat has completed, the ST clears the current combat list with !combat end. It also displays the total number of rounds fought.
!combat end
[IRC] <Caine> Combat has ended. Total rounds: 2

-------------

!inits <Dexterity+wits> [Alternative Name]
* Use [Alternative Name] to add NPCs to the inititative list.

Example:
!inits 6 Mage #1

[IRC] <Caine> Mage #1 Inits : 12


-----------

!showinits

Example:
!showinits

[IRC] <Caine> Mage #1 Inits : 12
[IRC] <Caine> Kevin Inits   : 8
[IRC] <Caine> David Inits   : 6


-------------

!newround

Example
!newround

[IRC] <Caine> New Round Started. Join: !inits. Declare !bp spends now.
