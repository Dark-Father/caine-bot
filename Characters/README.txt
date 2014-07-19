################################################
# Character Administration and Tracking Module #
################################################

This module is for Administrating and Tracking characters in Vampire : The Masquerade. 


@@@@@@@@@@@@
@ !startdb @
@@@@@@@@@@@@

This command creates the Database. Only works if there is not one already. It takes no arguments

Example:

!startdb
<BOT> Database Created.


@@@@@@@@@@@@@@@
@ !createchar @
@@@@@@@@@@@@@@@

This command creates new Characters in the bot. It takes the arguments <name> <bp> <wp>. Name should be letters only. BP and WP, numbers only. If the name you want to use is already in the bot it will give an error.

Example:

!createchar Doug 10 6
<BOT> Added Doug with 10bp and 6 wp


@@@@@@@@@@@@@@
@  !delchar  @
@@@@@@@@@@@@@@

This command deletes a character from the bot. It takes the argument <name>. 

Example:

!delchar Doug
<Bot> Character Doug removed from bot.
