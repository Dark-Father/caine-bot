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
To end the !combat loop, Caine looks for !combat end to exit the loop.

Full Example:
!combat start
[IRC] <Caine> Combat Round started. Round 1. Declare !inits to join combat.

David: !inits 5
[IRC] <Caine> David rolled initative: 7

An Storyteller (op) can add an additional text to the end of their liner to add NPCs easily to the combat list
ST: !inits 3 villian
[IRC] <Caine> Villian rolled initative: 9

Once everyone has joined, the Storyteller casts !showinits and Caine gives back a looped reply of all characters in round.
ST: !showinits
[IRC] <Caine> Villian: 9
[IRC] <Caine> David: 7

Once the round is completed, the Storyteller casts !newround. This clears the current round, displays the new round number
and players must once again cast !inits to join the new round of combat

ST: !newround
[IRC] <Caine> New Round Started. Round 2. Declare !inits to join combat.

Once combat has completed, the ST clears the current combat list with !combat end. It also displays the total number of rounds fought.
!combat end
[IRC] <Caine> Combat has ended. Total rounds: 2

-------------

!inits <Dexterity+wits> [Alternative Name]
* Only Storytellers can use [Alternative Name] to change their name in inits list.

Example:
!inits 6 Mage #1

[IRC] <Caine> Mage #1 Inits : 12


-----------

!showinits

Example:
!showinits

[IRC] <Caine> Mage #2 Inits : 12
[IRC] <Caine> Kevin Inits   : 8
[IRC] <Caine> David Inits   : 6


-------------

!newround

Example
!newround

[IRC] <Caine> New Round Started. Declare BP spends and roll new inits!
