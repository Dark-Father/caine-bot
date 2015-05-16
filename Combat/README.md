#Combat Plugin#

The Combat plugin for Caine on Cainite.org. Track, manage and execute combat.

#Combat Management Quick Overview:

Using **!combat start**, opens a combat tracker with round 1. 
Characters then cast **!inits** (or **!inits X NPC**) to add themselves or NPCs to the round.
Using **!newround** generates a new rounds, clears existing inits list and players must cast **!inits** to join the newround.
Once everyone has joined, cast **!showinits** to retrieve the list. It also displays the characters that haven't joined but are in the channel.
There is no "turn" management to allow for players that depart in the middle of the round, or drop, or whatever that is controlled out of character.
To end the !combat, Caine looks for: **!combat end**.

###Full Example:**

<br> **Storyteller/Manager:** !combat start
<br>[BOT] <Caine> Combat Round started. Round 1. Declare !inits to join combat. Declare !bp spends now.
<br> **David:** !inits 5
<br>[BOT] <Caine> David rolled: 7
<br> **Jamie:** !inits 5
<br>[BOT] <Caine> Jamie rolled: 9
<br> **Storyteller/Manager:** !inits 7 NPC
<br>[BOT] <Caine> NPC rolled: 17
<br> **Storyteller/Manager:** !showinits
<br>[BOT] <Caine> #################
<br>[BOT] <Caine>  NPC: 17
<br>[BOT] <Caine>  Jamie: 9
<br>[BOT] <Caine>  David: 7
<br>[BOT] <Caine> #################
<br> **Everyone takes their turns. Everyone flees. So no new round of combat**
<br> **Storyteller/Manager:** !combat end
<br>[BOT] <Caine> Combat Ended. Total number of rounds: 1

###To start combat:
!combat start

This will create a lock on the current channel, initialize the nested dictionary for the round list and set the round_count to 1.

**Example:**
<br> **Storyteller/Manager:** !combat start
<br>[BOT] <Caine> Combat Round started. Round 1. Declare !inits to join combat. Declare !bp spends now.

###To join the current combat:

To join combat once it has been started, the players and Storytellers will join with !inits <dex+wits>

**Example:**
<br> **David:** !inits 5
<br>[BOT] <Caine> David rolled: 7

###To add an NPC:

Should an NPC need to join combat, it's added with !inits <dex+wits> [NPC NAME]. This name can have spaces or characters without an issue.
However, the pound sign should be avoided as most IRC clients will translate that into a channel name link.

**Example**
**ST:** !inits 3 NPC
<br>[BOT] <Caine> NPC rolled: 9

###To view the initiative list:
Once everyone has joined, the manager of combat can cast !showinits. This can be cast multiple times if players jostle around and it is automatically updated accordingly.
The manager is going to direct turns as there is no turn management.

**Example:**
<br> **Storyteller/Manager:** !showinits
<br>[BOT] <Caine> ################
<br>[BOT] <Caine>  NPC: 17
<br>[BOT] <Caine>  Jamie: 9
<br>[BOT] <Caine>  David: 7
<br>[BOT] <Caine> ################

###To start a new round:

Once the round is completed, the "manager" casts !newround. This clears the current round, displays the new round number
and players must once again cast !inits to join the new round of combat.

**ST:** !newround
<br>[BOT] <Caine> New Round Started. Round 2. Declare !inits to join combat. Declare !bp spends now.

###To end combat:
Once combat has completed, the ST clears the current combat list with !combat end. It also displays the total number of rounds fought.

**!combat end**
<br>[BOT] <Caine> Combat has ended. Total rounds: 2
