Character Management Plugin

# Player Commands

## Description:

###!setdesc
Sets the character's descriptive description.

###!setlink
Sets the character's descriptive link. Generally a picture or profile page.

###!setlastname
Sets the character's descriptive last name.

###!setstats
Sets the character's descriptive stats.

###!describe <name>
Describes a character if they have set the above, otherwise a default message is shown.


## Blood Pool:

###!getbp
Gets character current blood pool.

###!bp (num)
If passed as blank only one blood is spent. If passed with a number, more can be spent.

###!feed <pool> <diff>
Character hunting rolls. It is a predetermined pool with a set difficulty.

###!efeed (num)
If the character sends it as blank, it tells them the available e-blood available, total spent and total in general.
If passed with a number, it'll check if the player has enough available to spend and will automatically add blood to their current pool.
It recovers all spends after 30 days.

##Willpower:

###!getwp
Gets character current willpower

###!wp
Must be spend 1 at a time even when multiples are needed in order to easily record spending.


##Experience

###!getxp
Gets the characters current XP available, total XP spent, and XP request for the week if one was made.

###!requestxp <num>
Weekly Experience Request Controls


##Damage

###!getdmg
Gets player's current damage total along with dice penalty modifier.

###!heal <num> <type (norm|agg)>
Heals the character removing blood and damage accordingly.


