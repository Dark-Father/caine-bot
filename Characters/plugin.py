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
        try:
            #best practice here. Rather than have the database constantly open, we open it specifically for each command
            conn = sqlite3.connect('characters.db')
            c = conn.cursor()
            c.execute("CREATE TABLE Chars(Id INTEGER PRIMARY KEY, Name TEXT unique, BP_Cur INT, "
                      "BP_Max INT, WP_Cur INT, WP_Max INT, XP_Cur INT, XP_Total INT, Description TEXT, Link TEXT, "
                      "Requested_XP INT, Fed_Already INT, Aggravated_Dmg INT, Normal_Dmg INT, NPC INT)")
            conn.commit()
            irc.reply('Database Created.')
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

        irc.reply(ircdb.isCapability(capability))
        irc.reply(ircdb.checkCapability(msg.prefix, capability))

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
            # as Name is unique, it throws an integrity error if you try a name thats already in there.
            conn.rollback()
            irc.reply("Error: Name already taken")
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
            name = str(name)
            # check if that name is even in the bot
            c.execute("SELECT Name FROM Chars WHERE Name = ?", (name,))
            checkname = c.fetchall()

            if len(checkname) != 0:
                c.execute("DELETE FROM Chars WHERE Name = ?", (name,))
                conn.commit()
                thereply = "Character %s removed from bot" % name
                irc.reply(thereply)
            else:
                raise sqlite3.Error(name)
        #sqlite doesnt seem to throw an exception if you try to delete something that isn't there.
        except sqlite3.Error as e:
            conn.rollback()
            created = "Error: %s not found." % e
            irc.reply(created)

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
            checkname = c.fetchall()

            if len(checkname) != 0:
                c.execute("UPDATE Chars SET Description = ? WHERE Name = ?", (description, nicks))
                conn.commit()
                irc.reply("Description Set")
            else:
                irc.reply("No such Character")

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
            checkname = c.fetchall()

            if len(checkname) != 0:
                c.execute("UPDATE Chars SET Link = ? WHERE Name = ?", (url, nicks))
                conn.commit()
                irc.reply("Link Set")
            else:
                irc.reply("No such Character")

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
            c.execute("SELECT Name, Description, Link FROM Chars WHERE Name = ?", (name,))
            desc = c.fetchone()
            created = desc[0] + " " + desc[1]
            created = ircutils.mircColor(created, 6)
            irc.reply(created, prefixNick=False)
            created2nd = "Link: " + desc[2]
            created2nd = ircutils.mircColor(created2nd, 6)
            irc.reply(created2nd, prefixNick=False)

        except sqlite3.Error:
            conn.rollback()
            irc.reply("Error: Name not found.")
        finally:
            conn.close()
    describe = wrap(describe, ['anything'])

    def getbp(self,irc, msg, args):
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
            else:
                irc.reply("Error: Name not found.")

        except sqlite3.Error:
            conn.rollback()
            irc.reply("Error: No such Character")

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
                    chanreply = "spent 1 BP"
                    irc.reply(chanreply)
                    irc.queueMsg(ircmsgs.notice(nicks, created))
                elif bpnum <= bp[1] and bpnum <= bp[0] and bpnum is not None:
                    bpcur = int(bp[0]) - bpnum
                    c.execute("UPDATE Chars SET BP_Cur = ? WHERE Name = ?", (bpcur, nicks))
                    conn.commit()
                    bpcur = str(bpcur)
                    bpmax = str(bp[1])
                    created = "Available Blood (" + bpcur + "/" + bpmax + ")"
                    chanreply = "spent %s BP" % bpnum
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
            c.execute("SELECT Name FROM Chars WHERE Name = ?", (name,))
            checkname = c.fetchone()

            if checkname is not None:
                 c.execute("UPDATE Chars SET BP_Cur = ? WHERE Name = ?", (newbp, name))
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
            c.execute("SELECT Name FROM Chars WHERE Name = ?", (name,))
            checkname = c.fetchone()

            if checkname is not None:
                c.execute("SELECT BP_Cur, BP_Max FROM Chars WHERE Name = ?", (name,))
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
                        fancy_outcome.append(ircutils.mircColor(die,12))

                    elif die == 1:  # math for ones
                        ones += 1
                        fancy_outcome.append(ircutils.mircColor(die,4))

                    else:
                        fancy_outcome.append(ircutils.mircColor(die,6))

                total = success - ones

                if success == 0 and ones > 0:
                    total = "BOTCH  >:D"
                    dicepool = 'fed: %s (%s) %s dice @diff %s' % (" ".join(fancy_outcome), total, str(num),
                                                                  str(difficulty))
                    irc.reply(dicepool, private=True)
                    c.execute("UPDATE Chars SET Fed_Already = 1 WHERE Name = ?", (nicks,))
                    conn.commit()
                elif 0 <= success <= ones:
                    total = "Failure"
                    dicepool = 'fed: %s (%s) %s dice @diff %s' % (" ".join(fancy_outcome), total, str(num),
                                                                  str(difficulty))
                    irc.reply(dicepool, private=True)
                    c.execute("UPDATE Chars SET Fed_Already = 1 WHERE Name = ?", (nicks,))
                    conn.commit()

                elif total > 0:
                    total = "Gained 3 bp"
                    dicepool = 'fed: %s (%s) %s dice @diff %s' % (" ".join(fancy_outcome), total, str(num),
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
                        bpcur = bpcur + 3
                        c.execute("UPDATE Chars SET BP_Cur = ? WHERE Name = ?", (bpcur, nicks))
                        conn.commit()




        finally:
            conn.close()
    feed = wrap(feed, ['int', 'int'])

    def getwp(self,irc, msg, args):
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
            c.execute("SELECT Name FROM Chars WHERE Name = ?", (name,))
            checkname = c.fetchone()

            if checkname is not None:
                 c.execute("UPDATE Chars SET WP_Cur = ? WHERE Name = ?", (newwp, name))
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
            c.execute("SELECT Name FROM Chars WHERE Name = ?", (name,))
            checkname = c.fetchone()

            if checkname is not None:
                c.execute("SELECT WP_Cur, WP_Max FROM Chars WHERE Name = ?", (name,))
                wp = c.fetchone()
                wpcur = str(wp[0])
                wpmax = str(wp[1])
                created = "Available Willpower for %s (" % name
                created = str(created) + wpcur + "/" + wpmax + ")"
                irc.reply(created, private=True)

        finally:
            conn.close()
    getcharwp = wrap(getcharwp, ['anything'])

    def getxp(self,irc, msg, args):
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
            c.execute("SELECT Name FROM Chars WHERE Name = ?", (name,))
            checkname = c.fetchone()

            if checkname is not None:
                c.execute("SELECT XP_Cur, XP_Total FROM Chars WHERE Name = ?", (name,))
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
            c.execute("SELECT Name FROM Chars WHERE Name = ?", (name,))
            checkname = c.fetchone()

            if checkname is not None:
                c.execute("SELECT XP_Cur, XP_Total FROM Chars WHERE Name = ?", (name,))
                xp = c.fetchone()
                xpcur = int(xp[0])
                xpmax = int(xp[1])
                xpmax = xpmax + num
                xpcur = xpcur + num
                c.execute("UPDATE Chars SET XP_Cur = ?, XP_Total = ? WHERE Name = ?", (xpcur, xpmax, name))
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
            c.execute("SELECT Name FROM Chars WHERE Name = ?", (name,))
            checkname = c.fetchone()

            if checkname is not None:
                c.execute("SELECT XP_Cur FROM Chars WHERE Name = ?", (name,))
                xp = c.fetchone()
                xpcur = int(xp[0])
                xpcur = xpcur - num
                if xpcur < 0:
                    irc.reply("Not enough XP to spend!", private=True)
                else:
                    c.execute("UPDATE Chars SET XP_Cur = ? WHERE Name = ?", (xpcur, name))
                    # date = time.strftime("%x")
                    # log = "%s - %s XP - %s - %s" % (name, num, reason, date)
                    # gotta decide how best to create an xp spend log
                    conn.commit()
                    created = "%s XP spent from %s." % (num, name)
                    irc.reply(created, private=True)

        finally:
            conn.close()
    spendxp = wrap(spendxp, ['anything', 'int', 'text'])

    def ctest(self, irc, msg, args):
        """Let's see if this works"""
        irc.reply("ctest reporting in")
        c.execute("SELECT * FROM Chars")
        rows = c.fetchall()

        for row in rows:
            irc.reply(row)


    ctest = wrap(ctest)


Class = Characters


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
