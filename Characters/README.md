# Character Administration and Tracking Module 

This module is for Administrating and Tracking characters in Vampire : The Masquerade. 

###!startdb 

This command creates the Database. Only works if there is not one already. It takes no arguments.

######Example:

!startdb
<br>[BOT] Database Created.


###!createchar 

This command creates new Characters in the bot. It takes the arguments <name> <bp> <wp>. Name should be letters only. BP and WP, numbers only. If the name you want to use is already in the bot it will give an error.

###### Example:

!createchar Doug 10 6
<br>[BOT] Added Doug with 10bp and 6 wp


###!delchar  

This command deletes a character from the bot. It takes the argument <name>. 

######Example:

!delchar Doug
<br>[BOT] Character Doug removed from bot.


###!setdesc

This command allows a player to set the description for their Character.

######Example:

!setdesc is a large man with rippling and sexy muscles. (app6)
<br>[BOT] Description Set.


###!setlink

This command allows a player to set a link in the description for their Character.

######Example:

!setlink http://tinyurl.com/ABC
<br>[BOT] Link Set.


###!describe

This command describes the named Character in the channel or PM.

######Example:

!describe Doug
<br>[BOT] Doug is a large man with rippling and sexy muscles. (app6)
<br>[BOT] http://tinyurl.com/ABC


###!getbp

This command checks a Characters bloodpool.

######Example:

!getbp
<br>[BOT] Available Blood (20/20)


###!feed

This command hunts for the character, in order to gain blood.

#####Example:

!feed 3 5
<br>[BOT] You fed: 4 6 4 (Gained 3 bp) 3 dice @diff 5


###!bp

This command spends BP for the named character. It works both without a number (defaults to 1 bp) as well as with a number and a reason (both optional)

#####Example:

!bp 3 Cel 3
<br>[BOT] Spent 3 BP


###!getcharbp

This command is ST only, and returns a named Characters current bloodpool.

#####Example:

!getcharbp Doug
<br>[BOT] Available Blood for Doug (17/20)


###!setbp

This command is ST only, and sets a named Characters current bloodpool.

#####Example:

!setbp Doug 20
<br>[BOT] New BP set to 20 for Doug


###!getwp

This command checks a characters willpower.

#####Example:

!getwp
<br>[BOT] Available Willpower (8/8)


###!wp

This command spends willpower for a character. May be used alone (default to 1 wp) or with an optional number and reason

#####Example:

!wp 1 resist derangement
<br>[BOT] Doug: Spent 1 WP
<br>[BOT] Available Willpower (7/8)


###!getcharwp

This command gets the named Characters current willpower.

#####Example:

!getcharwp Doug
<br>[BOT] Available willpower for Doug (7/7)


###!setwp

This command sets the named characters current willpower.

#####Example:

!setwp Doug 5
<br>[Bot] New wp set to 5 for Doug


###!getxp

This command checks a characters current and total experience points.

#####Example:

!getxp
<br>[Bot] Available Experience (6/30)


###!requestxp

This command puts in a request for weekly experience.

#####Example:

!requestxp 3
<br>[Bot] You have requested 3 XP.


###!givexp

This command allows an ST to manually give XP to a character.

#####Example:

!givexp Doug 3
<br>[Bot] 3 XP given to Doug.


###!spendxp

This command allows an ST to spend a characters XP.

#####Example:

!spendxp Doug 3 Athletics 1
<br>[Bot] 3 XP spent from Doug.


###!requestlist

This command shows an ST the current weeks requestxp list.

#####Example:

!requestlist
<br>[Bot] Doug requested 3 XP
<br>[Bot] Bill requested 3 XP


###!modifylist

This command allows an ST to modify the requestxp list. They can either ADD, REMOVE or CHANGE the list.

#####Example:

!modifylist add Ken 3
<br>[Bot] Ken added with 3 XP requested


###!approvelist

This command approves the requestxp list, giving out XP.

#####Example:

!approvelist
<br>[Bot] Doug given 3 XP
<br>[Bot] Bill given 3 XP
<br>[Bot] Ken given 3 XP


###!dmg

This command shows a characters current damage levels.

#####Example:

!dmg
<br>[Bot] 3 agg / 3 norm * CRIPPLED -5 Dice Pool Penalty


###!heal

This command spends blood to heal a characters damage.

#####Example:

!heal 1 agg
<br>[Bot] 1 agg healed for 5 bp.
<br>[Bot] 2 agg / 3 norm * MAULED -2 Dice Pool Penalty


###!givedmg

This command allows an ST to give damage to a character.

#####Example:

!givedmg Doug 1 agg
<br>[Bot] Doug given 1 agg damage.


###!npc

This command allows an ST to set a character as an NPC, removing their need to feed. 1 sets the character as an NPC, 0 sets them as a normal character.

#####Example:

!npc Doug 1
<br>[Bot] NPC set to 1


###!nightly

This command subtracts BP nightly, and should be scheduled to run every 24 hours.


###!weekly

This command adds WP weekly, and should be scheduled to run every 7 days.
