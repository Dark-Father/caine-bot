###
# Copyright (c) 2015, David Rickman
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
# this list of conditions, and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions, and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# * Neither the name of the author of this software nor the name of
# contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
from peewee import *
import datetime
from models import db, Character, XPlog, Botch


class Management(callbacks.Plugin):
    """This is the full character management system for Cainite.org"""
    threaded = True

    def __init__(self, irc):
        self.__parent = super(Management, self)
        self.__parent.__init__(irc)

    def createchar(self, irc, msg, args, name, bp, wp):
        """<name> <bp> <wp>
        Adds the Character with <name> to the bot, with a maximum <bp> and maximum <wp>
        """
        try:
            with db.atomic():
                Character.get_or_create(
                    name=name,
                    bp=int(bp),
                    bp_cur=int(bp),
                    wp=int(wp),
                    wp_cur=int(wp),
                    created=datetime.date.today())
                created = "Added %s with %s bp and %s wp" % (name, bp, wp)
                irc.reply(created)
        except IntegrityError or DoesNotExist:
            created = ircutils.mircColor("Error: Character {0} already in database.".format(name), 4)
            irc.reply(created, private=True)

    createchar = wrap(createchar, ['anything', 'int', 'int'])

    def delchar(self, irc, msg, args, name):
        """Removes the Character <name> from the bot."""

        try:
            with db.atomic():
                fetch = Character.get(Character.name == name)
                fetch.delete_instance(recursive=True)
                message = "Character {0} removed from database.".format(name)
                irc.reply(message)
        except DoesNotExist:
            created = ircutils.mircColor("Error: Character {0} does not exist in database.".format(name), 4)
            irc.reply(created, private=True)


    delchar = wrap(delchar, ['anything'])

#########################################
# Character Description Controls
#########################################
    def setdesc(self, irc, msg, args, description):
        """<description>
        Sets a description for your character
        """
        nick = str.capitalize(msg.nick)

        try:
            with db.atomic():
                q = Character.update(desc=description).where(Character.name == nick)
                q.execute()
                irc.reply("Description set.")
        finally:
            pass

    setdesc = wrap(setdesc, ['text'])

    def setlastname(self, irc, msg, args, lastname):
        """<name>
        Set your characters last name for your description, so people don't have to look it up.
        """
        nick = str.capitalize(msg.nick)
        try:
            with db.atomic():
                q = Character.update(lastname=lastname).where(Character.name == nick)
                q.execute()
            irc.reply("Lastname set.")
        finally:
            pass

    setlastname = wrap(setlastname, ['anything'])

    def setlink(self, irc, msg, args, url):
        """<url>
        Sets a link for your character description
        """
        nick = str.capitalize(msg.nick)

        try:
            with db.atomic():
                q = Character.update(link=url).where(Character.name == nick)
                q.execute()
            irc.reply("Your link has been set.")
        finally:
            pass

    setlink = wrap(setlink, ['text'])

    def setstats(self, irc, msg, args, stats):
        """<stats>
        Set your characters stats i.e App2|Cha2
        """
        nick = str.capitalize(msg.nick)

        try:
            with db.atomic():
                q = Character.update(stats=stats).where(Character.name == nick)
                q.execute()
            irc.reply("Your stats have been updated.")

        finally:
            pass

    setstats = wrap(setstats, ['text'])

    def describe(self, irc, msg, args, name):
        """<name>
        Gets the description of the a character
        """
        try:
            with db.atomic():
                q = Character.select().where(Character.name == name).get()
            message = q.name + ' ' + q.lastname + ' ' + q.desc
            message = ircutils.mircColor(message, 8)
            irc.reply(message, prefixNick=False, private=True)
            if q.link or q.stats:
                message2 = 'Link: ' + q.link + ' || ' + 'Stats: ' + q.stats
                message2 = ircutils.mircColor(message2, 8)
                irc.reply(message2, prefixNick=False, private=True)
        except DoesNotExist:
            irc.reply("Character does not exist.", private=True)

    describe = wrap(describe, ['anything'])

##########################################
# Blood Pool Controls
##########################################

    def getbp(self, irc, msg, args):
        nick = str.capitalize(msg.nick)
        try:
            with db.atomic():
                q = Character.select().where(Character.name == nick).get()
                message = "Character Blood Pool: " + str(q.bp_cur) + '/' + str(q.bp)
            irc.reply(message, prefixNick=False, private=True)
        except DoesNotExist:
            irc.reply("Character Not Found.", private=True)

    getbp = wrap(getbp)

    def bp(self, irc, msg, args, bpnum, reason):
        nick = str.capitalize(msg.nick)
        try:
            with db.atomic():
                q = Character.select().where(Character.name == nick).get()
                if bpnum >= q.bp_cur:
                    irc.reply(ircutils.mircColor("Not enough blood available."), prefixNick=False, private=True)
                else:
                    bpnew = q.bp_cur - bpnum
                    q = Character.update(bp_cur=bpnew).where(Character.name == nick)
                    q.execute()
                    q = Character.select().where(Character.name == nick).get()
                    message = ircutils.mircColor("Blood Remaining: " + str(q.bp_cur) + '/' + str(q.bp), 4)
                    irc.reply("Blood spent. " + message, prefixNick=False, private=True)
        except DoesNotExist:
            irc.reply("Character Not Found.", private=True)

    bp = wrap(bp, [optional('int'), optional('text')])

    def setbp(self, irc, msg, args, name, newbp):
        try:
            with db.atomic():
                q = Character.select().where(Character.name == name).get()
                if newbp > q.bp:
                    newbp = q.bp
                q = Character.update(bp_cur=newbp).where(Character.name == name)
                q.execute()
            irc.reply("Blood pool set.")
        except DoesNotExist:
            irc.reply("Character Not Found.", private=True)

    setbp = wrap(setbp, ['anything', 'int'])

    def getcharbp(self, irc, msg, args, name):
        try:
            with db.atomic():
                q = Character.select().where(Character.name == name).get()
                message = "Character Blood Pool: " + str(q.bp_cur) + '/' + str(q.bp)
            irc.reply(message, prefixNick=False, private=True)
        except DoesNotExist:
            irc.reply("Character Not Found.", private=True)

    getcharbp = wrap(getcharbp, ['anything'])

# #########################################
#
#     def feed(self, irc, msg, args, num, difficulty):
#         """<no. of dice> <difficulty>
#         Feed your character in #feed
#         """
#
#         nicks = msg.nick
#         sep = '_'
#         nicks = nicks.split(sep, 1)[0]
#         success = ones = total = 0
#         fancy_outcome = []
#
#         try:
#             checkname = self.dbmgr.checkname(nicks)
#
#             if checkname:
#                 for s in range(num):
#                     die = random.randint(1, 10)
#
#                     if die >= difficulty:  # success evaluation, no specs when you feed
#                         success += 1
#                         fancy_outcome.append(ircutils.mircColor(die, 12))
#
#                     elif die == 1:  # math for ones
#                         ones += 1
#                         fancy_outcome.append(ircutils.mircColor(die, 4))
#
#                     else:
#                         fancy_outcome.append(ircutils.mircColor(die, 6))
#
#                 total = success - ones
#
#                 if success == 0 and ones > 0:
#                     total = "BOTCH  >:D"
#                     dicepool = 'You fed: %s (%s) %s dice @diff %s' % (" ".join(fancy_outcome), total, str(num),
#                                                                       str(difficulty))
#                     irc.reply(dicepool, private=True)
#                     arg = '''UPDATE Chars SET Fed_Already = 1 WHERE Name = "{0}"'''.format(nicks)
#                     self.dbmgr.query(arg)
#                 elif 0 <= success <= ones:
#                     total = "Failure"
#                     dicepool = 'You fed: %s (%s) %s dice @diff %s' % (" ".join(fancy_outcome), total, str(num),
#                                                                       str(difficulty))
#                     irc.reply(dicepool, private=True)
#                     arg = '''UPDATE Chars SET Fed_Already = 1 WHERE Name = "{0}"'''.format(nicks)
#                     self.dbmgr.query(arg)
#
#                 elif total == 1:
#                     total = "Gained 3 bp"
#                     dicepool = 'You fed: %s (%s) %s dice @diff %s' % (" ".join(fancy_outcome), total, str(num),
#                                                                       str(difficulty))
#                     irc.reply(dicepool, private=True)
#                     arg = '''UPDATE Chars SET Fed_Already = 1 WHERE Name = "{0}"'''.format(nicks)
#                     self.dbmgr.query(arg)
#                     arg = '''SELECT BP_Cur, BP_Max FROM Chars WHERE Name = "{0}"'''.format(nicks)
#                     bp = self.dbmgr.readone(arg)
#                     bpcur, bpmax = int(bp[0]),  int(bp[1])
#                     bptest = bpmax - bpcur
#                     if bptest <= 3:
#                         arg = '''UPDATE Chars SET BP_Cur = "{0}" WHERE Name = "{1}"'''.format(bpmax, nicks)
#                         self.dbmgr.query(arg)
#                     else:
#                         bpcur += 3
#                         arg = '''UPDATE Chars SET BP_Cur = "{0}" WHERE Name = "{1}"'''.format(bpcur, nicks)
#                         self.dbmgr.query(arg)
#
#                 elif total > 1:
#                     total = "Gained 6 bp"
#                     dicepool = 'You fed: %s (%s) %s dice @diff %s' % (" ".join(fancy_outcome), total, str(num),
#                                                                       str(difficulty))
#                     irc.reply(dicepool, private=True)
#                     arg = '''UPDATE Chars SET Fed_Already = 1 WHERE Name = "{0}"'''.format(nicks)
#                     self.dbmgr.query(arg)
#                     arg = '''SELECT BP_Cur, BP_Max FROM Chars WHERE Name = "{0}"'''.format(nicks)
#                     bp = self.dbmgr.readone(arg)
#                     bpcur, bpmax = int(bp[0]), int(bp[1])
#                     bptest = bpmax - bpcur
#                     if bptest <= 6:
#                         arg = '''UPDATE Chars SET BP_Cur = "{0}" WHERE Name = "{1}"'''.format(bpmax, nicks)
#                         self.dbmgr.query(arg)
#                     else:
#                         bpcur += 6
#                         arg = '''UPDATE Chars SET BP_Cur = "{0}" WHERE Name = "{1}"'''.format(bpcur, nicks)
#                         self.dbmgr.query(arg)
#             else:
#                 nicks = msg.nick
#                 raise NameError(nicks)
#
#         except NameError as e:
#             self.dbmgr.rollback()
#             created = ircutils.mircColor("Error: Character \"%s\" not in database." % e, 4)
#             irc.reply(created)
#
#     feed = wrap(feed, ['int', 'int'])
#
##############
# CREATE E_FEED FUNCTION
#
#
# #########################################
#
#     def getwp(self, irc, msg, args):
#
#     getwp = wrap(getwp)
#
#     def wp(self, irc, msg, args, wpnum, reason):
#
#     wp = wrap(wp, [optional('int'), optional('text')])
#
#     def setwp(self, irc, msg, args, name, newwp):
#
#     setwp = wrap(setwp, ['anything', 'int'])
#
#     def getcharwp(self, irc, msg, args, name):
#
#     getcharwp = wrap(getcharwp, ['anything'])
#
#
# #########################################
#
#     def getxp(self, irc, msg, args):
#
#     getxp = wrap(getxp)
#
#
#     def getcharxp(self, irc, msg, args, name):
#
#     getcharxp = wrap(getcharxp, ['anything'])
#
#
#     def givexp(self, irc, msg, args, name, num):
#
#     givexp = wrap(givexp, ['anything', 'int'])
#
#     def spendxp(self, irc, msg, args, name, num, reason):
#
#     spendxp = wrap(spendxp, ['anything', 'int', 'text'])
#
#     def requestxp(self, irc, msg, args, amount):
#
#     requestxp = wrap(requestxp, ['int'])
#
#
#     def requestlist(self, irc, msg, args):
#
#     requestlist = wrap(requestlist)
#
#
#     def modifylist(self, irc, msg, args, command, name, amount):
#
#     modifylist = wrap(modifylist, ['anything', 'anything', optional('int')])
#
#
#     def approvelist(self, irc, msg, args):
#
#     approvelist = wrap(approvelist)
#
#     def charlog(self, irc, msg, args, name):
#
#     charlog = wrap(charlog, ['admin', 'anything'])
#
#
# #########################################
#
#    def _damage(self, name):
#         try:
#             check_name = self.dbmgr.checkname(name)
#
#             if check_name:
#                 arg = '''SELECT Aggravated_dmg, Normal_dmg FROM Chars WHERE Name = "{0}"'''.format(name)
#                 dmg = self.dbmgr.readone(arg)
#                 agg, norm = dmg[0], dmg[1]
#                 response = name + " " + str(agg) + " Agg | " + str(norm) + " Norm"
#                 if agg + norm == 0:
#                     response += " * UNDAMAGED"
#                 elif agg + norm == 1:
#                     response += " * BRUISED (0 Dice Penalty)"
#                 elif agg + norm == 2:
#                     response += " * HURT (-1 Dice Penalty)"
#                 elif agg + norm == 3:
#                     response += " * INJURED (-1 Dice Penalty)"
#                 elif agg + norm == 4:
#                     response += " * WOUNDED (-2 Dice Penalty)"
#                 elif agg + norm == 5:
#                     response += " * MAULED (-2 Dice Penalty)"
#                 elif agg + norm == 6:
#                     response += " * CRIPPLED (-5 Dice Penalty)"
#                 elif agg + norm == 7:
#                     response += " * INCAPACITATED"
#                 elif norm == 8:
#                     response += " * TORPORED"
#                 elif agg == 8:
#                     response += " * FINAL DEATH"
#
#                 return response
#             else:
#                 raise NameError(nicks)
#
#         except NameError as e:
#             self.dbmgr.rollback()
#             response = ircutils.mircColor("Error: Character \"%s\" not in database." % e, 4)
#             return response
#
#
#
#     def getdmg(self, irc, msg, args):
#
#     getdmg = wrap(getdmg)
#
#
#     def getchardmg(self, irc, msg, args, name):
#
#     getchardmg = wrap(dmgcheck, ['anything'])
#
#
#     def givedmg(self, irc, msg, args, name, amount, dmgtype):
#
#     givedmg = wrap(givedmg, ['anything', 'int', 'anything'])
#
#
#     def heal(self, irc, msg, args, amount, dmgtype):
#
#     heal = wrap(heal, ['int', 'anything'])
#
#
# #########################################
#
#
#     def npc(self, irc, msg, args, name, numset):
#
#
#     npc = wrap(npc, ['anything', 'int'])
#
#
#     def nightly(self, irc, msg, args):
#
#     nightly = wrap(nightly)
#
#
#     def weekly(self, irc, msg, args):
#
#     weekly = wrap(weekly)
#
#
#
#
#
#
#
Class = Management


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
