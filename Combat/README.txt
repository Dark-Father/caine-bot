###############
#Combat Plugin#
###############

The Combat plugin for Caine on Elysia-online.org. Track, manage and execute combat.


################################
#Initiative and Starting Combat#
################################

So first we concentrate on inits rolls, tracking those inits, displaying those inits, and managing combat rounds. Then we have a few functions for starting combat that automatically creates a new round in the room, and summons an ST.

!inits <Dexterity+wits> <Optional Reason>

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