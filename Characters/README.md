# Character Administration and Tracking Module 

This module is for Administrating and Tracking characters in Vampire : The Masquerade. 

###!startdb 

This command creates the Database. Only works if there is not one already. It takes no arguments.

Example:

!startdb
**[BOT]** Database Created.


###!createchar 

This command creates new Characters in the bot. It takes the arguments <name> <bp> <wp>. Name should be letters only. BP and WP, numbers only. If the name you want to use is already in the bot it will give an error.

Example:

!createchar Doug 10 6
**[BOT]** Added Doug with 10 B{ and 6 WP


###!delchar  

This command deletes a character from the bot. It takes the argument <name>. 

Example:

!delchar Doug
**[BOT]** Character Doug removed from bot.


###!setdesc

This command allows a player to set the description for their Character.

Example:

!setdesc is a large man with rippling and sexy muscles. (app6)
**[BOT] Description Set.


###!setlink

This command allows a player to set a link in the description for their Character.

Example:

!setlink http://tinyurl.com/ABC
**[BOT] Link Set.


###!describe

This command describes the named Character in the channel or PM.

Example:

!describe Doug   
**[BOT]** Doug is a large man with rippling and sexy muscles. (app6)  
**[BOT]** http://tinyurl.com/ABC


###!getbp

This command shows the user his Characters current bloodpool. Returns the message in a private notice.

Example:

!getbp
**[BOT]** Available Blood (20/20)


!feed

Feeding


!bp

Spends bp


!getcharbp

gets bp of a character for STs


!setbp

sets bp of a character by sts



!getwp

gets wp for player


!wp

Spend a wp


!getcharwp
gets wp of a character for sts


!setwp

sets wp of a character for sts


!getxp

gets xp for a player


!requestxp

request xp


!givexp

gives xp from an st

!spendxp

st spend xp

!requestlist

show current weeks requested xp

!approvexp

approve the XP list

!modify request

st modify an xp request

!getdmg

get a players damage level

!giveagg

give agg damage

!givenorm

give normal damage

!npc

set character to NPC
