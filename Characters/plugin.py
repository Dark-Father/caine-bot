# ##
# Copyright (c) 2014, Liam Burke
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
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
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.ircdb as ircdb

import sqlite3
import random
import time


# noinspection PyMethodMayBeStatic,PyUnusedLocal,PyShadowingNames,PyUnboundLocalVariable
class Characters(callbacks.Plugin):
    """Character administration and tracking for Vampire: The Masquerade"""

    def __init__(self, irc):
        #what does this do? I dunno!
        self.__parent = super(Characters, self)
        self.__parent.__init__(irc)

    def startdb(self, irc, msg, args):
        """takes no arguments

        Creates the Database for the first time. If it exists, it will not overwrite it.
        """
        global conn
        try:
            #best practice here. Rather than have the database constantly open, we open it specifically for each command
            conn = sqlite3.connect('characters.db')
            c = conn.cursor()
            c.execute("CREATE TABLE Request(Id INTEGER PRIMARY KEY, Name TEXT, Amount INT)")
            conn.commit()
            irc.reply('Request Log Database Created.')
            c.execute("CREATE TABLE XPlog(Id INTEGER PRIMARY KEY, Name TEXT, Date TEXT, ST TEXT, Amount INT,"
                      " Reason TEXT)")
            conn.commit()
            irc.reply('XP Log Database Created.')
            c.execute("CREATE TABLE Chars(Id INTEGER PRIMARY KEY, Name TEXT unique, BP_Cur INT, "
                      "BP_Max INT, WP_Cur INT, WP_Max INT, XP_Cur INT, XP_Total INT, Description TEXT, Link TEXT, "
                      "Requested_XP INT, Fed_Already INT, Aggravated_Dmg INT, Normal_Dmg INT, NPC INT)")
            conn.commit()
            irc.reply('Character Database Created.')
        except sqlite3.Error:
            #if we pick up an error (i.e the database already exists)
            irc.reply('Error: Database already exists')
            conn.rollback()
        finally:
            #lastly we close the database connection.
            conn.close()
    startdb = wrap(startdb)

    def createchar(self, irc, msg, args, name, bp, wp):
        """<name> <bp> <wp>

        Adds the Character with <name> to the bot, with a maximum <bp> and maximum <wp>
        """
        bp = int(bp)
        wp = int(wp)
        capability = 'characters.createchar'
        #this check isn't really necessary, I was just testing capabilities.

        if capability:
            if not ircdb.checkCapability(msg.prefix, capability):
                irc.errorNoCapability(capability, Raise=True)

        try:
            conn = sqlite3.connect('characters.db')
            conn.text_factory = str
            c = conn.cursor()
            c.execute("INSERT INTO Chars(Name, BP_Cur, Bp_Max, WP_Cur, WP_Max, XP_Cur, XP_Total, Description, Link,"
                      " Requested_XP, "
                      "Fed_Already, Aggravated_Dmg, Normal_Dmg, NPC) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                      (name, bp, bp, wp, wp, 0, 0,
                      'No Description Set', 'No Link Set', 0, 0, 0, 0, 0))
            created = "Added %s with %s bp and %s wp" % (name, bp, wp)
            irc.reply(created)
            conn.commit()

        except sqlite3.IntegrityError:
            # as Name is unique, it throws an integrity error if you try a name that's already in there.
            conn.rollback()
            created = "Error: Character \"%s\" already in database." % name
            created = ircutils.mircColor(created, 4)
            irc.reply(created, private=True)
        finally:
            conn.close()

    createchar = wrap(createchar, ['anything', 'int', 'int'])

    def delchar(self, irc, msg, args, name):
        """<name>

        Removes the Character <name> from the bot.
        """
        try:
            conn = sqlite3.connect('characters.db')
            conn.text_factory = str
            c = conn.cursor()
            # check if that name is even in the bot
            c.execute("SELECT Name FROM Chars WHERE Name = ? COLLATE NOCASE", (name,))
            checkname = c.fetchone()

            if checkname is not None:
                c.execute("DELETE FROM Chars WHERE Name = ? COLLATE NOCASE", (name,))
                conn.commit()
                thereply = "Character %s removed from bot" % name
                irc.reply(thereply)
            else:
                conn.rollback()
                raise sqlite3.Error(name)
        #sqlite doesnt seem to throw an exception if you try to delete something that isn't there.
        except sqlite3.Error as e:
            conn.rollback()
            created = "Error: Character \"%s\" not in database." % e
            created = ircutils.mircColor(created, 4)
            irc.reply(created, private=True)

        finally:
            conn.close()

    delchar = wrap(delchar, ['anything'])

    def setdesc(self, irc, msg, args, description):
        """<description>

        Sets a description for your character
        """
        nicks = msg.nick
        try:
            conn = sqlite3.connect('characters.db')
            conn.text_factory = str
            c = conn.cursor()
            c.execute("SELECT Name FROM Chars WHERE Name = ?", (nicks,))
            checkname = c.fetchone()

            if checkname is not None:
                c.execute("UPDATE Chars SET Description = ? WHERE Name = ?", (description, nicks))
                conn.commit()
                irc.reply("Description Set")

            elif nicks.islower():
                lower = "lower"
                raise NameError(lower)

            else:
                raise NameError(nicks)

        except NameError as e:
            conn.rollback()
            if "lower" in e:
                created = "Error: Your name is lower case. Please capitalise."
                created = ircutils.mircColor(created, 4)
                irc.reply(created)

            else:
                created = "Error: Character \"%s\" not in database." % e
                created = ircutils.mircColor(created, 4)
                irc.reply(created)

        finally:
            conn.close()
    setdesc = wrap(setdesc, ['text'])

    def setlink(self, irc, msg, args, url):
        """<url>

        Sets a link for your character description
        """
        nicks = msg.nick
        try:
            conn = sqlite3.connect('characters.db')
            conn.text_factory = str
            c = conn.cursor()
            c.execute("SELECT Name FROM Chars WHERE Name = ?", (nicks,))
            checkname = c.fetchone()

            if checkname is not None:
                c.execute("UPDATE Chars SET Link = ? WHERE Name = ?", (url, nicks))
                conn.commit()
                irc.reply("Link Set")

            elif nicks.islower():
                lower = "lower"
                raise NameError(lower)

            else:
                raise NameError(nicks)

        except NameError as e:
            conn.rollback()
            if "lower" in e:
                created = "Error: Your name is lower case. Please capitalise."
                created = ircutils.mircColor(created, 4)
                irc.reply(created)

            else:
                created = "Error: Character \"%s\" not in database." % e
                created = ircutils.mircColor(created, 4)
                irc.reply(created)

        finally:
            conn.close()

    setlink = wrap(setlink, ['text'])

    def describe(self, irc, msg, args, name):
        """<name>

        Gets the description of the named character
        """

        name = str(name)
        try:
            conn = sqlite3.connect('characters.db')
            conn.text_factory = str
            c = conn.cursor()
            c.execute("SELECT Name FROM Chars WHERE Name = ? COLLATE NOCASE", (name,))
            checkname = c.fetchone()

            if checkname is not None:
                c.execute("SELECT Name, Description, Link FROM Chars WHERE Name = ? COLLATE NOCASE", (name,))
                desc = c.fetchone()
                created = desc[0] + " " + desc[1]
                created = ircutils.mircColor(created, 6)
                irc.reply(created, prefixNick=False)
                created2nd = "Link: " + desc[2]
                created2nd = ircutils.mircColor(created2nd, 6)
                irc.reply(created2nd, prefixNick=False)

            else:
                raise NameError(name)

        except NameError as e:
            conn.rollback()
            created = "Error: Character \"%s\" not found." % e
            created = ircutils.mircColor(created, 4)
            irc.reply(created)
        finally:
            conn.close()
    describe = wrap(describe, ['anything'])

    def getbp(self, irc, msg, args):
        """takes no arguments
        
        Check your characters BP
        """

        nicks = msg.nick
        sep = '_'
        nicks = nicks.split(sep, 1)[0]

        try:
            conn = sqlite3.connect('characters.db')
            conn.text_factory = str
            c = conn.cursor()
            c.execute("SELECT Name FROM Chars WHERE Name = ?", (nicks,))
            checkname = c.fetchone()

            if checkname is not None:
                c.execute("SELECT BP_Cur, BP_Max FROM Chars WHERE Name = ?", (nicks,))
                bp = c.fetchone()
                bpcur = str(bp[0])
                bpmax = str(bp[1])
                created = "Available Blood (" + bpcur + "/" + bpmax + ")"
                irc.queueMsg(ircmsgs.notice(nicks, created))

            elif nicks.islower():
                lower = "lower"
                raise NameError(lower)

            else:
                raise NameError(nicks)

        except NameError as e:
            conn.rollback()
            if "lower" in e:
                created = "Error: Your name is lower case. Please capitalise."
                created = ircutils.mircColor(created, 4)
                irc.reply(created)

            else:
                created = "Error: Character \"%s\" not in database." % e
                created = ircutils.mircColor(created, 4)
                irc.reply(created)

        finally:
            conn.close()

    getbp = wrap(getbp)

    def bp(self, irc, msg, args, bpnum, reason):
        """(optional number) (optional text)

        Spend 1 BP without any arguments, or as many BP as you define with an optional reason
        """

        nicks = msg.nick
        sep = '_'
        nicks = nicks.split(sep, 1)[0]
        try:
            conn = sqlite3.connect('characters.db')
            conn.text_factory = str
            c = conn.cursor()
            c.execute("SELECT count(*) FROM Chars WHERE Name = ?", (nicks,))
            checkname = c.fetchone()

            if checkname is not None:
                c.execute("SELECT BP_Cur, BP_Max FROM Chars WHERE Name = ?", (nicks,))
                bp = c.fetchone()
                if bpnum is None and bp[0] != 0:
                    bpcur = int(bp[0]) - 1
                    c.execute("UPDATE Chars SET BP_Cur = ? WHERE Name = ?", (bpcur, nicks))
                    conn.commit()
                    bpcur = str(bpcur)
                    bpmax = str(bp[1])
                    created = "Available Blood (" + bpcur + "/" + bpmax + ")"
                    chanreply = "Spent 1 BP"
                    irc.reply(chanreply)
                    irc.queueMsg(ircmsgs.notice(nicks, created))
                elif bpnum <= bp[1] and bpnum <= bp[0] and bpnum is not None:
                    bpcur = int(bp[0]) - bpnum
                    c.execute("UPDATE Chars SET BP_Cur = ? WHERE Name = ?", (bpcur, nicks))
                    conn.commit()
                    bpcur = str(bpcur)
                    bpmax = str(bp[1])
                    created = "Available Blood (" + bpcur + "/" + bpmax + ")"
                    chanreply = "Spent %s BP" % bpnum
                    irc.reply(chanreply)
                    irc.queueMsg(ircmsgs.notice(nicks, created))
                else:
                    irc.reply("You don't enough blood")

            else:
                irc.reply("No such Character")

        finally:
            conn.close()

    bp = wrap(bp, [optional('int'), optional('text')])

    def setbp(self, irc, msg, args, name, newbp):
        """<name> <newbp>

        Set Character <name>'s current bp to <newbp>
        """
        nicks = msg.nick
        try:
            conn = sqlite3.connect('characters.db')
            conn.text_factory = str
            c = conn.cursor()
            c.execute("SELECT Name FROM Chars WHERE Name = ? COLLATE NOCASE", (name,))
            checkname = c.fetchone()

            if checkname is not None:
                c.execute("UPDATE Chars SET BP_Cur = ? WHERE Name = ? COLLATE NOCASE", (newbp, name))
                conn.commit()
                created = "New BP set to %s for %s" % (newbp, name)
                irc.reply(created, private=True)

            else:
                irc.reply("Error: Name not found.")

        finally:
            conn.close()

    setbp = wrap(setbp, ['anything', 'int'])

    def getcharbp(self, irc, msg, args, name):
        """<name>

        Get the Characters bloodpool
        """
        try:
            conn = sqlite3.connect('characters.db')
            conn.text_factory = str
            c = conn.cursor()
            c.execute("SELECT Name FROM Chars WHERE Name = ? COLLATE NOCASE", (name,))
            checkname = c.fetchone()

            if checkname is not None:
                c.execute("SELECT BP_Cur, BP_Max FROM Chars WHERE Name = ? COLLATE NOCASE", (name,))
                bp = c.fetchone()
                bpcur = str(bp[0])
                bpmax = str(bp[1])
                created = "Available Blood for %s (" % name
                created = str(created) + bpcur + "/" + bpmax + ")"
                irc.reply(created, private=True)

        finally:
            conn.close()
    getcharbp = wrap(getcharbp, ['anything'])

    def feed(self, irc, msg, args, num, difficulty):
        """<no. of dice> <difficulty>

        Feed your character in #feed
        """

        nicks = msg.nick
        sep = '_'
        nicks = nicks.split(sep, 1)[0]
        success = ones = total = 0
        fancy_outcome = []

        try:
            conn = sqlite3.connect('characters.db')
            conn.text_factory = str
            c = conn.cursor()
            c.execute("SELECT Name FROM Chars WHERE Name = ?", (nicks,))
            checkname = c.fetchone()

            if checkname is not None:
                for s in range(num):
                    die = random.randint(1, 10)

                    if die >= difficulty:  # success evaluation, no specs when you feed
                        success += 1
                        fancy_outcome.append(ircutils.mircColor(die, 12))

                    elif die == 1:  # math for ones
                        ones += 1
                        fancy_outcome.append(ircutils.mircColor(die, 4))

                    else:
                        fancy_outcome.append(ircutils.mircColor(die, 6))

                total = success - ones

                if success == 0 and ones > 0:
                    total = "BOTCH  >:D"
                    dicepool = 'You fed: %s (%s) %s dice @diff %s' % (" ".join(fancy_outcome), total, str(num),
                                                                      str(difficulty))
                    irc.reply(dicepool, private=True)
                    c.execute("UPDATE Chars SET Fed_Already = 1 WHERE Name = ?", (nicks,))
                    conn.commit()
                elif 0 <= success <= ones:
                    total = "Failure"
                    dicepool = 'You fed: %s (%s) %s dice @diff %s' % (" ".join(fancy_outcome), total, str(num),
                                                                      str(difficulty))
                    irc.reply(dicepool, private=True)
                    c.execute("UPDATE Chars SET Fed_Already = 1 WHERE Name = ?", (nicks,))
                    conn.commit()

                elif total > 0:
                    total = "Gained 3 bp"
                    dicepool = 'You fed: %s (%s) %s dice @diff %s' % (" ".join(fancy_outcome), total, str(num),
                                                                      str(difficulty))
                    irc.reply(dicepool, private=True)
                    c.execute("UPDATE Chars SET Fed_Already = 1 WHERE Name = ?", (nicks,))
                    conn.commit()
                    c.execute("SELECT BP_Cur, BP_Max FROM Chars WHERE Name = ?", (nicks,))
                    bp = c.fetchone()
                    bpcur = int(bp[0])
                    bpmax = int(bp[1])
                    bptest = bpmax - bpcur
                    if bptest <= 3:
                        c.execute("UPDATE Chars SET BP_Cur = ? WHERE Name = ?", (bpmax, nicks))
                        conn.commit()
                    else:
                        bpcur += 3
                        c.execute("UPDATE Chars SET BP_Cur = ? WHERE Name = ?", (bpcur, nicks))
                        conn.commit()
        finally:
            conn.close()
    feed = wrap(feed, ['int', 'int'])

    def getwp(self, irc, msg, args):
        """takes no arguments
        Check your characters WP
        """

        nicks = msg.nick
        sep = '_'
        nicks = nicks.split(sep, 1)[0]

        try:
            conn = sqlite3.connect('characters.db')
            conn.text_factory = str
            c = conn.cursor()
            c.execute("SELECT Name FROM Chars WHERE Name = ?", (nicks,))
            checkname = c.fetchone()

            if checkname is not None:
                c.execute("SELECT WP_Cur, WP_Max FROM Chars WHERE Name = ?", (nicks,))
                wp = c.fetchone()
                wpcur = str(wp[0])
                wpmax = str(wp[1])
                created = "Available Willpower (" + wpcur + "/" + wpmax + ")"
                irc.queueMsg(ircmsgs.notice(nicks, created))
            else:
                irc.reply("Error: Name not found.")

        except sqlite3.Error:
            conn.rollback()
            irc.reply("Error: No such Character")

        finally:
            conn.close()
    getwp = wrap(getwp)

    def wp(self, irc, msg, args, wpnum, reason):
        """(optional number) (optional text)

        Spend 1 WP without any arguments, or as many WP as you define with an optional reason
        """

        nicks = msg.nick
        sep = '_'
        nicks = nicks.split(sep, 1)[0]
        try:
            conn = sqlite3.connect('characters.db')
            conn.text_factory = str
            c = conn.cursor()
            c.execute("SELECT count(*) FROM Chars WHERE Name = ?", (nicks,))
            checkname = c.fetchone()

            if checkname is not None:
                c.execute("SELECT WP_Cur, WP_Max FROM Chars WHERE Name = ?", (nicks,))
                wp = c.fetchone()
                if wpnum is None and wp[0] != 0:
                    wpcur = int(wp[0]) - 1
                    c.execute("UPDATE Chars SET WP_Cur = ? WHERE Name = ?", (wpcur, nicks))
                    conn.commit()
                    wpcur = str(wpcur)
                    wpmax = str(wp[1])
                    created = "Available Willpower (" + wpcur + "/" + wpmax + ")"
                    chanreply = "spent 1 WP"
                    irc.reply(chanreply)
                    irc.queueMsg(ircmsgs.notice(nicks, created))
                elif wpnum <= wp[1] and wpnum <= wp[0] and wpnum is not None:
                    wpcur = int(wp[0]) - wpnum
                    c.execute("UPDATE Chars SET WP_Cur = ? WHERE Name = ?", (wpcur, nicks))
                    conn.commit()
                    wpcur = str(wpcur)
                    wpmax = str(wp[1])
                    created = "Available Willpower (" + wpcur + "/" + wpmax + ")"
                    chanreply = "spent %s WP" % wpnum
                    irc.reply(chanreply)
                    irc.queueMsg(ircmsgs.notice(nicks, created))
                else:
                    irc.reply("You don't have enough willpower")

            else:
                irc.reply("No such Character")

        finally:
            conn.close()

    wp = wrap(wp, [optional('int'), optional('text')])

    def setwp(self, irc, msg, args, name, newwp):
        """<name> <newwp>

        Set Character <name>'s current wp to <newwp>
        """
        nicks = msg.nick
        try:
            conn = sqlite3.connect('characters.db')
            conn.text_factory = str
            c = conn.cursor()
            c.execute("SELECT Name FROM Chars WHERE Name = ? COLLATE NOCASE", (name,))
            checkname = c.fetchone()

            if checkname is not None:
                c.execute("UPDATE Chars SET WP_Cur = ? WHERE Name = ? COLLATE NOCASE", (newwp, name))
                conn.commit()
                created = "New WP set to %s for %s" % (newwp, name)
                irc.reply(created, private=True)

            else:
                irc.reply("Error: Name not found.")

        finally:
            conn.close()

    setwp = wrap(setwp, ['anything', 'int'])

    def getcharwp(self, irc, msg, args, name):
        """<name>

        Get the Characters willpower
        """
        try:
            conn = sqlite3.connect('characters.db')
            conn.text_factory = str
            c = conn.cursor()
            c.execute("SELECT Name FROM Chars WHERE Name = ? COLLATE NOCASE", (name,))
            checkname = c.fetchone()

            if checkname is not None:
                c.execute("SELECT WP_Cur, WP_Max FROM Chars WHERE Name = ? COLLATE NOCASE", (name,))
                wp = c.fetchone()
                wpcur = str(wp[0])
                wpmax = str(wp[1])
                created = "Available Willpower for %s (" % name
                created = str(created) + wpcur + "/" + wpmax + ")"
                irc.reply(created, private=True)

        finally:
            conn.close()
    getcharwp = wrap(getcharwp, ['anything'])

    def getxp(self, irc, msg, args):
        """takes no arguments
        Check your characters XP
        """

        nicks = msg.nick
        sep = '_'
        nicks = nicks.split(sep, 1)[0]

        try:
            conn = sqlite3.connect('characters.db')
            conn.text_factory = str
            c = conn.cursor()
            c.execute("SELECT Name FROM Chars WHERE Name = ?", (nicks,))
            checkname = c.fetchone()

            if checkname is not None:
                c.execute("SELECT XP_Cur, XP_Total FROM Chars WHERE Name = ?", (nicks,))
                xp = c.fetchone()
                xpcur = str(xp[0])
                xpmax = str(xp[1])
                created = "Available Experience (" + xpcur + "/" + xpmax + ")"
                irc.queueMsg(ircmsgs.notice(nicks, created))
            else:
                irc.reply("Error: Name not found.")

        except sqlite3.Error:
            conn.rollback()
            irc.reply("Error: No such Character")

        finally:
            conn.close()
    getxp = wrap(getxp)

    def getcharxp(self, irc, msg, args, name):
        """<name>

        Get the Characters willpower
        """
        try:
            conn = sqlite3.connect('characters.db')
            conn.text_factory = str
            c = conn.cursor()
            c.execute("SELECT Name FROM Chars WHERE Name = ? COLLATE NOCASE", (name,))
            checkname = c.fetchone()

            if checkname is not None:
                c.execute("SELECT XP_Cur, XP_Total FROM Chars WHERE Name = ? COLLATE NOCASE", (name,))
                xp = c.fetchone()
                xpcur = str(xp[0])
                xpmax = str(xp[1])
                created = "Available Experience for %s (" % name
                created = str(created) + xpcur + "/" + xpmax + ")"
                irc.reply(created, private=True)

        finally:
            conn.close()
    getcharxp = wrap(getcharxp, ['anything'])

    def givexp(self, irc, msg, args, name, num):
        """<name> <amount of xp>

        Manually give a Character XP
        """
        try:
            conn = sqlite3.connect('characters.db')
            conn.text_factory = str
            c = conn.cursor()
            c.execute("SELECT Name FROM Chars WHERE Name = ? COLLATE NOCASE", (name,))
            checkname = c.fetchone()

            if checkname is not None:
                c.execute("SELECT XP_Cur, XP_Total FROM Chars WHERE Name = ? COLLATE NOCASE", (name,))
                xp = c.fetchone()
                xpcur = int(xp[0])
                xpmax = int(xp[1])
                xpmax = xpmax + num
                xpcur = xpcur + num
                c.execute("UPDATE Chars SET XP_Cur = ?, XP_Total = ? WHERE Name = ? COLLATE NOCASE", (
                          xpcur, xpmax, name))
                conn.commit()
                created = "%s XP given to %s. (%s/%s)" % (num, name, xpcur, xpmax)
                irc.reply(created, private=True)

        finally:
            conn.close()
    givexp = wrap(givexp, ['anything', 'int'])

    def spendxp(self, irc, msg, args, name, num, reason):
        """<name> <amount of xp> <reason>

        Manually spend a Characters XP
        """

        nicks = msg.nick
        try:
            conn = sqlite3.connect('characters.db')
            conn.text_factory = str
            c = conn.cursor()
            c.execute("SELECT Name FROM Chars WHERE Name = ? COLLATE NOCASE", (name,))
            checkname = c.fetchone()

            if checkname is not None:
                c.execute("SELECT XP_Cur FROM Chars WHERE Name = ? COLLATE NOCASE", (name,))
                xp = c.fetchone()
                xpcur = int(xp[0])
                xpcur = xpcur - num
                if xpcur < 0:
                    irc.reply("Not enough XP to spend!", private=True)
                else:
                    c.execute("UPDATE Chars SET XP_Cur = ? WHERE Name = ? COLLATE NOCASE", (xpcur, name))
                    c.execute("INSERT INTO XPlog(Name, Date, ST, Amount, Reason) VALUES(?, date('now'), ?, ?, ?)",
                              (name, nicks, num, reason))
                    conn.commit()
                    created = "%s XP spent from %s." % (num, name)
                    irc.reply(created, private=True)

        finally:
            conn.close()

    spendxp = wrap(spendxp, ['anything', 'int', 'text'])

    def requestxp(self, irc, msg, args, amount):
        """<amount>

        Request <amount> (1-3) XP for the last week. XP is given out on Mondays.
        """

        nicks = msg.nick
        try:
            conn = sqlite3.connect('characters.db')
            conn.text_factory = str
            c = conn.cursor()
            c.execute("SELECT Name FROM Chars WHERE Name = ?", (nicks,))
            checkname = c.fetchone()
            c.execute("SELECT Name FROM Request WHERE Name = ?", (nicks,))
            reqname = c.fetchone()

            if amount > 3:
                created = "You have requested %s dicks in your eye, you god damn smartass. " \
                          "Pick something below 3." % amount

                irc.queueMsg(ircmsgs.notice(nicks, created))

            elif checkname is not None and reqname is None:
                c.execute("INSERT INTO Request(Name, Amount) VALUES(?, ?)", (nicks, amount))
                conn.commit()
                created = "You have requested %s XP" % amount
                irc.queueMsg(ircmsgs.notice(nicks, created))

            elif checkname is not None and reqname is not None:
                c.execute("UPDATE Request SET Amount = ? WHERE Name = ?", (amount, nicks))
                conn.commit()
                created = "You have requested %s XP" % amount
                irc.queueMsg(ircmsgs.notice(nicks, created))
            else:
                irc.reply("Error: Character name not found")

        finally:
            conn.close()

    requestxp = wrap(requestxp, ['int'])

    def requestlist(self, irc, msg, args):
        """takes no arguments

        Show the Request XP list for this week
        """
        try:
            conn = sqlite3.connect('characters.db')
            c = conn.cursor()
            c.execute("SELECT * FROM Request")
            rows = c.fetchall()

            for row in rows:
                created = "%s requested %s XP" % (row[1], row[2])
                irc.reply(created)

        finally:
            conn.close()

    requestlist = wrap(requestlist)

    def modifylist(self, irc, msg, args, command, name, amount):
        """<command> <name> optional(amount)

        Modify the requestxp list.
        Remove command removes a name from the list.
        Add command adds a name and an amount to the list.
        Change command changes a name already on the list.
        """

        try:
            conn = sqlite3.connect('characters.db')
            conn.text_factory = str
            c = conn.cursor()
            c.execute("SELECT Name FROM Request WHERE Name = ? COLLATE NOCASE", (name,))
            checkname = c.fetchone()
            c.execute("SELECT Name FROM Chars WHERE Name = ? COLLATE NOCASE", (name,))
            secname = c.fetchone()

            if command == 'remove':
                if checkname is not None:
                    c.execute("DELETE FROM Request WHERE Name =? COLLATE NOCASE", (name,))
                    conn.commit()
                    created = "%s removed from requestxp list." % name
                    irc.reply(created, private=True)

                else:
                    irc.reply("Error: Name not found")

            elif command == 'add':
                if checkname is None and secname is not None:
                    c.execute("INSERT INTO Request(Name, Amount) VALUES(?, ?)", (name, amount))
                    conn.commit()
                    created = "%s added with %s XP requested." % (name, amount)
                    irc.reply(created, private=True)

                elif secname is None:
                    irc.reply("Error: Character does not exist")

                else:
                    irc.reply("Error: Name already exists in list. Use change instead.")

            elif command == 'change':
                if checkname is not None:
                    c.execute("UPDATE Request SET Amount = ? WHERE Name = ? COLLATE NOCASE", (amount, name))
                    conn.commit()
                    created = "%s changed to %s XP requested." % (name, amount)
                    irc.reply(created, private=True)

                else:
                    irc.reply("Error: Name not found")
            else:
                irc.reply("Error: Please use commands: remove, add or change")

        finally:
            conn.close()

    modifylist = wrap(modifylist, ['anything', 'anything', optional('int')])

    def approvelist(self, irc, msg, args):
        """takes no arguments

        Approves the XP list for this week.
        """
        try:
            conn = sqlite3.connect('characters.db')
            conn.text_factory = str
            c = conn.cursor()
            c.execute("SELECT * FROM Request")
            rows = c.fetchall()

            for row in rows:
                name = row[1]
                c.execute("SELECT XP_Cur, XP_Total FROM Chars WHERE Name = ?", (name,))
                xp = c.fetchone()
                xpcur = xp[0] + row[2]
                xpmax = xp[1] + row[2]
                c.execute("UPDATE Chars SET XP_Cur = ?, XP_Total = ? WHERE Name = ?", (xpcur, xpmax, name))
                conn.commit()
                created = "Gave %s %s XP" % (name, row[2])
                irc.reply(created, private=True)

        finally:
            c.execute("DROP TABLE Request")
            c.execute("CREATE TABLE Request(Id INTEGER PRIMARY KEY, Name TEXT, Amount INT)")
            conn.commit()
            conn.close()

    approvelist = wrap(approvelist)

    def npc(self, irc, msg, args, name, numset):
        """<name> <1 or 0>

        Sets a characters as an NPC in the bot, preventing blood loss overnight, etc.
        """
        try:
            conn = sqlite3.connect('characters.db')
            conn.text_factory = str
            c = conn.cursor()
            c.execute("SELECT Name FROM Chars WHERE Name = ? COLLATE NOCASE", (name,))
            checkname = c.fetchone()

            if checkname is not None:
                    c.execute("UPDATE Chars SET NPC = ? WHERE Name = ? COLLATE NOCASE", (numset, name))
                    conn.commit()
                    created = "NPC set to %s" % numset
                    irc.reply(created)

        finally:
            conn.close()

    npc = wrap(npc, ['anything', 'int'])

    def nightly(self, irc, msg, args):
        """takes no arguments

        Runs the nightly maintenance.
        """

        try:
            conn = sqlite3.connect('characters.db')
            c = conn.cursor()
            c.execute("SELECT BP_Cur, Name, NPC, BP_Max FROM Chars")
            rows = c.fetchall()

            for row in rows:
                if row[2] == 0:
                    bpcur = row[0] - 1
                    if bpcur < 0:
                        bpcur = 0
                    c.execute("UPDATE Chars SET BP_Cur = ? WHERE Name = ?", (bpcur, row[1]))
                    conn.commit()
                else:
                    bpcur = row[3]
                    c.execute("UPDATE Chars SET BP_Cur = ? WHERE Name = ?", (bpcur, row[1]))
                    conn.commit()

        finally:
            conn.close()

    nightly = wrap(nightly)

    def weekly(self, irc, msg, args):
        """takes no arguments

        Runs the weekly maintenance.
        """

        try:
            conn = sqlite3.connect('characters.db')
            c = conn.cursor()
            c.execute("SELECT WP_Cur, Name, NPC, WP_Max FROM Chars")
            rows = c.fetchall()

            for row in rows:

                wpcur = row[0] + 1
                if wpcur > row[3]:
                    wpcur = row[3]
                c.execute("UPDATE Chars SET WP_Cur = ? WHERE Name = ?", (wpcur, row[1]))
                conn.commit()
        finally:
            conn.close()
    weekly = wrap(weekly)

    def ctest(self, irc, msg, args):
        """Let's see if this works"""
        irc.reply("ctest reporting in")
        c.execute("SELECT * FROM Chars")
        rows = c.fetchall()

        for row in rows:
            irc.reply(row)

    ctest = wrap(ctest)

#    def logtest(self,irc, msg, args):
#        irc.reply("Logtest reporting in")
#        c.execute("SELECT * FROM XPlog")
#
#       rows = c.fetchall()
#
#        for row in rows:
#            irc.reply(row)
#
#   logtest = wrap(logtest)


Class = Characters


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
