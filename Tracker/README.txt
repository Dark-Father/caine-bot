Plugin to remember character descriptions, bloodpool, willpower and eXPerience by inserting them into a mysql database.
This is for future possible web-based management.
------------------------------------
To begin, an admin (generally storyteller) must register the new player.
This generates the necessary tables for the new player and inserts the base values.
!newchar <desired IRC Nick> <generation> <willpower>

Example: !newchar David 9 7
[IRC] BOT has registered a new player: David
[IRC] BOT has set Generation at 9 (bloodpool 14), with Willpower: 7

A character can be declared inactive from the database by an admin (ST).
This can be used for players that disappear or go on vacation for an extended period of time.
This freezes their BP, WP and XP, disabling any alterations to it by Caine's hand.
!deactivate <IRC NICK>

Example: !deactivate David
[IRC] BOT has deactivated the character: David.

A player can resume a character by having an ST re-activate them with !activate

Example: !activate David
[IRC] BOT has activated the character: David.

Lastly, a character can be purged from the database by !delchar.
Example: !delchar David
[IRC] BOT has purged the character: David.


------------------------------------
To set the Character's description:
!setdesc
Example: !setdesc writes sexy python code.

It can also set links to wiki or image links, they will be returned with !describe:
!setlink <url>
Example: !setlink http://placekitten.com/g/200/300

To recall description and links:
!describe <character>

Example:
[IRC] David writes sexy python code
[IRC] Link: http://placekitten.com/g/200/300

------------------------------------
To recall bloodpool
!getbp
[IRC] David has a 7/14 blood remaining

To feed, players will need to occasionally hunt for blood using the !feed command.
!feed <hours> <difficulty> <domain or hunting grounds>
Example: !feed 3 7 Marshall Park
[IRC] David has hunted for 3 hours and gained 4 BP by hunting.

Characters will often need to spend blood to activate various disciplines and powers.
This is accomplished by !bp.
!bp <num> (optional text)

Example: !bp 1 Potence
[IRC] David spent 1 bp.

Storytellers can give blood to players by passing a !forcefeed command.
This is too allow for emergency feeding and any other means.
!forcefeed <IRC NICK> <bp> (reason)

Example: !forcefeed David 4 
[IRC] David has been given 4 bp. Total bp is now: 11/14

Storytellers can remove blood for various reasons by using !removebp
Example: !removebp David 4
[IRC] Removed 4 bp from David. Total bp is now: 7/14

------------------------------------
To recall willpower
!getwp
[IRC] David has 7/7 willpower remaining

To spend willpower, this only spends 1 at a time due to how the rules work.
This also needs to be tracked separately during spending as they come back only 1 a week.
!wp
Example: !wp
[IRC] Willpower spent.

Storytellers can give back willpower through In-Character actions or
    if a player mistakenly spends willpower by !forcewill
!forcewill <IRC NICK> <willpower> (reason)
Example: !forcewill David 3
[IRC] David has restored 3 willpower.

------------------------------------
To recall eXPerience
!getxp
[IRC] David has spent 19 of 21 XP.

To gain experience, players are asked to request it weekly.
This maxes at 3 for heavy interaction, 2 for moderate, 1 for you logged in and had a casual scene.
!requestxp {1,2,3} (reason)
Example: !requestxp 3
[IRC] David has requested 3 XP for the week.

Character spend XP by purchasing increases in various fields of their sheet.
Storytellers manage that spending by !spendxp
!spendxp <IRC NICK> <XP Spent> (optional text)
Example: !spendxp David 4 increasing Brawl
[IRC] David spent 4 XP

Storytellers can give bonus XP with !bonusxp
!bonusxp <IRC NICK> <XP> (reason)
Example: !bonusxp David 5
[IRC] David was awarded with 5 bonus XP.

Storytellers can also penalize or if for some reason need to subtract XP from a player
!subtractxp <IRC NICK> <XP> (reason)
Example: !subtractxp David 5
[IRC] David has had 5 XP subtracted.

Storytellers can view all requestxp with !listxp. If there was a reason with the requestxp, it is displayed.
Example: !listxp
[IRC] David has requested 3 XP for the week. Reason: "I played a lot this week, ran an event."
[IRC] Joe has requested 2 XP for the week. Reason: <none>
[IRC] Jamie has requested 1 XP for the week. Reason: "I barely got a chance to play, had a casual scene or two."

Storytellers can approved all XP requests with !approveall
Example: !approveall
[IRC] All character XP requests approved successfully.

Storytellers can remove a request with !removerequest
Example: !removerequest David
[IRC] David's request for XP 3 has been removed.
------------------------------------


