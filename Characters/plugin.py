# ##
# Copyright (c) 2014, Liam Burke, David Rickman
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
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


class DatabaseManager(object):
    def __init__(self, db):
        self.conn = sqlite3.connect(db, timeout=5)
        # self.conn.execute('')
        # self.conn.commit()
        self.conn.text_factory = str
        self.c = self.conn.cursor()

    def query(self, arg):
        if arg:
            self.c.execute(arg)
            self.conn.commit()
            return True
        else:
            return "There was a problem."

    def checkname(self, name):
        self.c.execute("SELECT Name FROM Chars WHERE Name = ? COLLATE NOCASE", (name,))
        checkname = self.c.fetchone()
        return checkname

    def reqname(self, name):
        self.c.execute("SELECT Amount FROM Request WHERE Name = ?", (name,))
        reqname = self.c.fetchone()
        return reqname

    def readone(self, arg):
        read = self.c.execute(arg)
        read = read.fetchone()
        return read

    def fetchall(self, arg):
        read = self.c.execute(arg)
        read = read.fetchall()
        return read

    def rollback(self):
        self.conn.rollback()

    def __del__(self):
        self.conn.close()


class Characters(callbacks.Plugin):
    """Character administration and tracking for Vampire: The Masquerade"""

    def __init__(self, irc):
        self.__parent = super(Characters, self)
        self.__parent.__init__(irc)
        self.dbmgr = DatabaseManager('characters.db')

    def startdb(self, irc, msg, args):
        """takes no arguments

        Creates the Database for the first time. If it exists, it will not overwrite it.
        """
        try:
            import os
            data = os.stat('characters.db').st_size
            if data < 1:
                arg = '''CREATE TABLE Request(Id INTEGER PRIMARY KEY, Name TEXT, Amount INT)'''
                create = self.dbmgr.query(arg)
                if create is True:
                    irc.reply('Request Log Database Created.')
                arg = '''CREATE TABLE XPlog(Id INTEGER PRIMARY KEY, Name TEXT,
                          Date TEXT, ST TEXT, Amount INT, Reason TEXT)'''
                create = self.dbmgr.query(arg)
                if create is True:
                    irc.reply('XP Log Database Created.')
                arg = '''CREATE TABLE Chars(Id INTEGER PRIMARY KEY, Name TEXT unique, BP_Cur INT, BP_Max INT,
                            WP_Cur INT, WP_Max INT, XP_Cur INT, XP_Total INT, Description TEXT,
                            Link TEXT, Requested_XP INT, Fed_Already INT,
                            Aggravated_Dmg INT, Normal_Dmg INT, NPC INT, Lastname TEXT, Stats TEXT)'''
                create = self.dbmgr.query(arg)
                if create is True:
                    irc.reply('Character Database Created.')
            else:
                raise sqlite3.Error
        except sqlite3.Error:
            #if we pick up an error (i.e the database already exists)
            irc.reply('Error: Database already exists')
            self.dbmgr.rollback()

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
            arg = '''INSERT INTO Chars(Name, BP_Cur, BP_Max, WP_Cur, WP_Max, XP_Cur, XP_Total, Description, Link,
                        Requested_XP, Fed_Already, Aggravated_Dmg, Normal_Dmg, NPC, Lastname, Stats)
                        VALUES("{0}", "{1}", "{1}", "{2}", "{2}", 0, 0, 'No Description', 'No Link',
                        0, 0, 0, 0, 0, '', 'No Stats Set')'''.format(name, bp, wp)
            # fields = ()
            self.dbmgr.query(arg)
            created = "Added %s with %s bp and %s wp" % (name, bp, wp)
            irc.reply(created)

        except sqlite3.IntegrityError:
            # as Name is unique, it throws an integrity error if you try a name that's already in there.
            self.dbmgr.rollback()
            created = ircutils.mircColor("Error: Character \"%s\" already in database." % name, 4)
            irc.reply(created, private=True)

    createchar = wrap(createchar, ['anything', 'int', 'int'])

    def delchar(self, irc, msg, args, name):
        """<name>

        Removes the Character <name> from the bot.
        """
        try:
            checkname = self.dbmgr.checkname(name)

            if checkname:
                arg = '''DELETE FROM Chars WHERE Name = "{0}" COLLATE NOCASE'''.format(name)
                self.dbmgr.query(arg, name)
                response = "Character %s removed from bot" % name
                irc.reply(response)
            else:
                self.dbmgr.rollback()
                raise sqlite3.Error(name)
        #sqlite doesnt seem to throw an exception if you try to delete something that isn't there.
        except sqlite3.Error as e:
            self.dbmgr.rollback()
            created = ircutils.mircColor("Error: Character \"%s\" not in database." % e, 4)
            irc.reply(created, private=True)

    delchar = wrap(delchar, ['anything'])

    def setdesc(self, irc, msg, args, description):
        """<description>

        Sets a description for your character
        """
        nicks = str.capitalize(msg.nick)
        try:
            checkname = self.dbmgr.checkname(nicks)

            if checkname:
                arg = '''UPDATE Chars SET Description = "{0}" WHERE Name = "{1}"'''.format(description, nicks)
                self.dbmgr.query(arg)
                irc.reply("Description Set")
            else:
                raise NameError(nicks)

        except NameError as e:
            self.dbmgr.rollback()
            created = ircutils.mircColor("Error: Character \"%s\" not in database." % e, 4)
            irc.reply(created)

    setdesc = wrap(setdesc, ['text'])

    def setlink(self, irc, msg, args, url):
        """<url>

        Sets a link for your character description
        """
        nicks = str.capitalize(msg.nick)
        try:
            checkname = self.dbmgr.checkname(nicks)

            if checkname:
                arg = '''UPDATE Chars SET Link = "{0}" WHERE Name = "{1}"'''.format(url, nicks)
                self.dbmgr.query(arg)
                irc.reply("Link Set")
            else:
                raise NameError(nicks)

        except NameError as e:
            self.dbmgr.rollback()
            created = ircutils.mircColor("Error: Character \"%s\" not in database." % e, 4)
            irc.reply(created)

    setlink = wrap(setlink, ['text'])

    def setlastname(self, irc, msg, args, name):
        """<name>

        Set your characters last name for your description, so people don't have to look it up.
        """
        nicks = str.capitalize(msg.nick)
        try:
            checkname = self.dbmgr.checkname(nicks)

            if checkname:
                arg = '''UPDATE Chars SET Lastname = "{0}" WHERE Name = "{1}"'''.format(name, nicks)
                self.dbmgr.query(arg)
                irc.reply("Last name set.")
            else:
                raise NameError(nicks)

        except NameError as e:
            self.dbmgr.rollback()
            created = ircutils.mircColor("Error: Character \"%s\" not in database." % e, 4)
            irc.reply(created)

    setlastname = wrap(setlastname, ['anything'])

    def setstats(self, irc, msg, args, stats):
        """<stats>

        Set your characters stats i.e App2|Cha2
        """
        nicks = str.capitalize(msg.nick)
        try:
            conn = sqlite3.connect('characters.db')
            conn.text_factory = str
            c = conn.cursor()
            checkname = self.dbmgr.checkname(nicks)

            if checkname:
                arg = '''UPDATE Chars SET Stats = "{0}" WHERE Name = "{1}"'''.format(stats, nicks)
                self.dbmgr.query(arg)
                irc.reply("Character stats set.")
            else:
                raise NameError(nicks)

        except NameError as e:
            self.dbmgr.rollback()
            created = ircutils.mircColor("Error: Character \"%s\" not in database." % e, 4)
            irc.reply(created)

    setstats = wrap(setstats, ['text'])

    def describe(self, irc, msg, args, name):
        """<name>

        Gets the description of the named character
        """

        nicks = str.capitalize(name)
        try:
            checkname = self.dbmgr.checkname(nicks)

            if checkname:
                arg = '''SELECT Name, Description, Link, Lastname, Stats
                          FROM Chars WHERE Name = "{0}" COLLATE NOCASE'''.format(name)
                desc = self.dbmgr.readone(arg)
                if desc[3] is not None:
                    created = desc[0] + " " + desc[3] + " " + desc[1]
                else:
                    created = desc[0] + " " + desc[1]
                created = ircutils.mircColor(created, 6)
                irc.reply(created, prefixNick=False)
                stats = desc[4]
                if stats is None:
                    stats = "No Stats Set."
                created2nd = "Link: " + desc[2] + " * " + "Stats: " + stats
                created2nd = ircutils.mircColor(created2nd, 6)
                irc.reply(created2nd, prefixNick=False)

            else:
                raise NameError(name)

        except NameError as e:
            self.dbmgr.rollback()
            created = ircutils.mircColor("Error: Character \"%s\" not found." % e, 4)
            irc.reply(created)

    describe = wrap(describe, ['anything'])

    def getbp(self, irc, msg, args):
        """takes no arguments
        
        Check your characters BP
        """

        nicks = str.capitalize(msg.nick)
        sep = '_'
        nicks = nicks.split(sep, 1)[0]

        try:
            checkname = self.dbmgr.checkname(nicks)

            if checkname:
                arg = '''SELECT BP_Cur, BP_Max FROM Chars WHERE Name = "{0}"'''.format(nicks)
                bp = self.dbmgr.readone(arg)
                bpcur = str(bp[0])
                bpmax = str(bp[1])
                created = "Available Blood (" + bpcur + "/" + bpmax + ")"
                irc.queueMsg(ircmsgs.notice(nicks, created))
            else:
                nicks = msg.nick
                raise NameError(nicks)

        except NameError as e:
            self.dbmgr.rollback()
            created = ircutils.mircColor("Error: Character \"%s\" not in database." % e, 4)
            irc.reply(created)

    getbp = wrap(getbp)

    def bp(self, irc, msg, args, bpnum, reason):
        """(optional number) (optional text)

        Spend 1 BP without any arguments, or as many BP as you define with an optional reason
        """

        nicks = msg.nick
        sep = '_'
        nicks = nicks.split(sep, 1)[0]
        try:
            checkname = self.dbmgr.checkname(nicks)

            if checkname:
                arg = '''SELECT BP_Cur, BP_Max FROM Chars WHERE Name = "{0}"'''.format(nicks)
                bp = self.dbmgr.readone(arg)
                if bpnum is None and bp[0] != 0:
                    bpcur = int(bp[0]) - 1
                    arg = '''UPDATE Chars SET BP_Cur = "{0}" WHERE Name = "{1}"'''.format(bpcur, nicks)
                    self.dbmgr.query(arg)
                    bpcur, bpmax = str(bpcur), str(bp[1])
                    created = "Available Blood (" + bpcur + "/" + bpmax + ")"
                    response = "Spent 1 BP"
                    irc.reply(response)
                    irc.queueMsg(ircmsgs.notice(nicks, created))
                elif bpnum <= bp[1] and bpnum <= bp[0] and bpnum is not None:
                    bpcur = int(bp[0]) - bpnum
                    arg = '''UPDATE Chars SET BP_Cur = "{0}" WHERE Name = "{1}"'''.format(bpcur, nicks)
                    self.dbmgr.query(arg)
                    bpcur, bpmax = str(bpcur), str(bp[1])
                    created = "Available Blood (" + bpcur + "/" + bpmax + ")"
                    response = "Spent %s BP" % bpnum
                    irc.reply(response)
                    irc.queueMsg(ircmsgs.notice(nicks, created))
                else:
                    irc.reply("You don't enough blood")

            else:
                nicks = msg.nick
                raise NameError(nicks)

        except NameError as e:
            self.dbmgr.rollback()
            created = ircutils.mircColor("Error: Character \"%s\" not in database." % e, 4)
            irc.reply(created)

    bp = wrap(bp, [optional('int'), optional('text')])

    def setbp(self, irc, msg, args, name, newbp):
        """<name> <newbp>

        Set Character <name>'s current bp to <newbp>
        """
        try:
            checkname = self.dbmgr.checkname(name)

            if checkname:
                arg = '''UPDATE Chars SET BP_Cur = "{0}" WHERE Name = "{1}" COLLATE NOCASE '''.format(newbp, name)
                self.dbmgr.query(arg)
                created = "New BP set to %s for %s" % (newbp, name)
                irc.reply(created, private=True)
            else:
                raise NameError(name)

        except NameError as e:
            self.dbmgr.rollback()
            created = ircutils.mircColor("Error: Character \"%s\" not in database." % e, 4)
            irc.reply(created)

    setbp = wrap(setbp, ['anything', 'int'])

    def getcharbp(self, irc, msg, args, name):
        """<name>

        Get the Characters bloodpool
        """
        try:
            checkname = self.dbmgr.checkname(name)

            if checkname:
                arg = '''SELECT BP_Cur, BP_Max FROM Chars WHERE Name = "{0}" COLLATE NOCASE'''.format(name)
                bp = self.dbmgr.readone(arg)
                bpcur, bpmax = str(bp[0]), str(bp[1])
                created = "Available Blood for %s (" % name
                created = str(created) + bpcur + "/" + bpmax + ")"
                irc.reply(created, private=True)
            else:
                raise NameError(name)

        except NameError as e:
            self.dbmgr.rollback()
            created = ircutils.mircColor("Error: Character \"%s\" not in database." % e, 4)
            irc.reply(created)

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
            checkname = self.dbmgr.checkname(nicks)

            if checkname:
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
                    arg = '''UPDATE Chars SET Fed_Already = 1 WHERE Name = "{0}"'''.format(nicks)
                    self.dbmgr.query(arg)
                elif 0 <= success <= ones:
                    total = "Failure"
                    dicepool = 'You fed: %s (%s) %s dice @diff %s' % (" ".join(fancy_outcome), total, str(num),
                                                                      str(difficulty))
                    irc.reply(dicepool, private=True)
                    arg = '''UPDATE Chars SET Fed_Already = 1 WHERE Name = "{0}"'''.format(nicks)
                    self.dbmgr.query(arg)

                elif total == 1:
                    total = "Gained 3 bp"
                    dicepool = 'You fed: %s (%s) %s dice @diff %s' % (" ".join(fancy_outcome), total, str(num),
                                                                      str(difficulty))
                    irc.reply(dicepool, private=True)
                    arg = '''UPDATE Chars SET Fed_Already = 1 WHERE Name = "{0}"'''.format(nicks)
                    self.dbmgr.query(arg)
                    arg = '''SELECT BP_Cur, BP_Max FROM Chars WHERE Name = "{0}"'''.format(nicks)
                    bp = self.dbmgr.readone(arg)
                    bpcur, bpmax = int(bp[0]),  int(bp[1])
                    bptest = bpmax - bpcur
                    if bptest <= 3:
                        arg = '''UPDATE Chars SET BP_Cur = "{0}" WHERE Name = "{1}"'''.format(bpmax, nicks)
                        self.dbmgr.query(arg)
                    else:
                        bpcur += 3
                        arg = '''UPDATE Chars SET BP_Cur = "{0}" WHERE Name = "{1}"'''.format(bpcur, nicks)
                        self.dbmgr.query(arg)

                elif total > 1:
                    total = "Gained 6 bp"
                    dicepool = 'You fed: %s (%s) %s dice @diff %s' % (" ".join(fancy_outcome), total, str(num),
                                                                      str(difficulty))
                    irc.reply(dicepool, private=True)
                    arg = '''UPDATE Chars SET Fed_Already = 1 WHERE Name = "{0}"'''.format(nicks)
                    self.dbmgr.query(arg)
                    arg = '''SELECT BP_Cur, BP_Max FROM Chars WHERE Name = "{0}"'''.format(nicks)
                    bp = self.dbmgr.readone(arg)
                    bpcur, bpmax = int(bp[0]), int(bp[1])
                    bptest = bpmax - bpcur
                    if bptest <= 6:
                        arg = '''UPDATE Chars SET BP_Cur = "{0}" WHERE Name = "{1}"'''.format(bpmax, nicks)
                        self.dbmgr.query(arg)
                    else:
                        bpcur += 6
                        arg = '''UPDATE Chars SET BP_Cur = "{0}" WHERE Name = "{1}"'''.format(bpcur, nicks)
                        self.dbmgr.query(arg)
            else:
                nicks = msg.nick
                raise NameError(nicks)

        except NameError as e:
            self.dbmgr.rollback()
            created = ircutils.mircColor("Error: Character \"%s\" not in database." % e, 4)
            irc.reply(created)

    feed = wrap(feed, ['int', 'int'])

    def getwp(self, irc, msg, args):
        """takes no arguments
        Check your characters WP
        """

        nicks = msg.nick
        sep = '_'
        nicks = nicks.split(sep, 1)[0]

        try:
            checkname = self.dbmgr.checkname(nicks)

            if checkname:
                arg = '''SELECT WP_Cur, WP_Max FROM Chars WHERE Name = "{0}"'''.format(nicks)
                wp = self.dbmgr.readone(arg)
                wpcur, wpmax = str(wp[0]), str(wp[1])
                created = "Available Willpower (" + wpcur + "/" + wpmax + ")"
                irc.queueMsg(ircmsgs.notice(nicks, created))
            else:
                nicks = msg.nick
                raise NameError(nicks)

        except NameError as e:
            self.dbmgr.rollback()
            created = ircutils.mircColor("Error: Character \"%s\" not in database." % e, 4)
            irc.reply(created)

    getwp = wrap(getwp)

    def wp(self, irc, msg, args, wpnum, reason):
        """(optional number) (optional text)

        Spend 1 WP without any arguments, or as many WP as you define with an optional reason
        """

        nicks = msg.nick
        sep = '_'
        nicks = nicks.split(sep, 1)[0]
        try:
            checkname = self.dbmgr.checkname(nicks)

            if checkname:
                arg = '''SELECT WP_Cur, WP_Max FROM Chars WHERE Name = "{0}"'''.format(nicks)
                wp = self.dbmgr.readone(arg)
                if wpnum is None and wp[0] != 0:
                    wpcur = int(wp[0]) - 1
                    arg = '''UPDATE Chars SET WP_Cur = "{0}" WHERE Name = "{1}"'''.format(wpcur, nicks)
                    self.dbmgr.query(arg)
                    wpcur, wpmax = str(wpcur), str(wp[1])
                    created = "Available Willpower (" + wpcur + "/" + wpmax + ")"
                    chanreply = "Spent 1 WP"
                    irc.reply(chanreply)
                    irc.queueMsg(ircmsgs.notice(nicks, created))
                elif wpnum <= wp[1] and wpnum <= wp[0] and wpnum is not None:
                    wpcur = int(wp[0]) - wpnum
                    arg = '''UPDATE Chars SET WP_Cur = "{0}" WHERE Name = "{1}"'''.format(wpcur, nicks)
                    self.dbmgr.query(arg)
                    wpcur, wpmax = str(wpcur), str(wp[1])
                    created = "Available Willpower (" + wpcur + "/" + wpmax + ")"
                    chanreply = "Spent %s WP" % wpnum
                    irc.reply(chanreply)
                    irc.queueMsg(ircmsgs.notice(nicks, created))
                else:
                    irc.reply("You don't have enough willpower")
            else:
                nicks = msg.nick
                raise NameError(nicks)

        except NameError as e:
            self.dbmgr.rollback()
            created = ircutils.mircColor("Error: Character \"%s\" not in database." % e, 4)
            irc.reply(created)

    wp = wrap(wp, [optional('int'), optional('text')])

    def setwp(self, irc, msg, args, name, newwp):
        """<name> <newwp>

        Set Character <name>'s current wp to <newwp>
        """
        try:
            checkname = self.dbmgr.checkname(name)

            if checkname:
                arg = '''UPDATE Chars SET WP_Cur = "{0}" WHERE Name = "{1}" COLLATE NOCASE'''.format(newwp, name)
                self.dbmgr.query(arg)
                created = "New WP set to %s for %s" % (newwp, name)
                irc.reply(created, private=True)
            else:
                raise NameError(name)

        except NameError as e:
            self.dbmgr.rollback()
            created = ircutils.mircColor("Error: Character \"%s\" not in database." % e, 4)
            irc.reply(created)

    setwp = wrap(setwp, ['anything', 'int'])

    def getcharwp(self, irc, msg, args, name):
        """<name>

        Get the Characters willpower
        """
        try:
            checkname = self.dbmgr.checkname(name)

            if checkname:
                arg = '''SELECT WP_Cur, WP_Max FROM Chars WHERE Name = "{0}" COLLATE NOCASE'''.format(name)
                wp = self.dbmgr.readone(arg)
                wpcur, wpmax = str(wp[0]), str(wp[1])
                created = "Available Willpower for %s (" % name
                created = str(created) + wpcur + "/" + wpmax + ")"
                irc.reply(created, private=True)
            else:
                raise NameError(name)

        except NameError as e:
            self.dbmgr.rollback()
            created = ircutils.mircColor("Error: Character \"%s\" not in database." % e, 4)
            irc.reply(created)

    getcharwp = wrap(getcharwp, ['anything'])

    def getxp(self, irc, msg, args):
        """takes no arguments
        Check your characters XP
        """

        nicks = msg.nick
        sep = '_'
        nicks = nicks.split(sep, 1)[0]

        try:
            checkname = self.dbmgr.checkname(nicks)
            reqname = self.dbmgr.reqname(nicks)

            if checkname:
                arg = '''SELECT XP_Cur, XP_Total FROM Chars WHERE Name = "{0}"'''.format(nicks)
                xp = self.dbmgr.readone(arg)
                xpcur, xpmax = str(xp[0]), str(xp[1])
                if reqname:
                    request = str(reqname[0])
                    created = "Available Experience (" + xpcur + "/" + xpmax + ")" + \
                              " - Requested " + request + "XP for the week."
                else:
                    created = "Available Experience (" + xpcur + "/" + xpmax + ")"

                irc.queueMsg(ircmsgs.notice(nicks, created))
            else:
                raise NameError(nicks)

        except NameError as e:
            self.dbmgr.rollback()
            created = ircutils.mircColor("Error: Character \"%s\" not in database." % e, 4)
            irc.reply(created)

    getxp = wrap(getxp)

    def getcharxp(self, irc, msg, args, name):
        """<name>

        Get the Characters willpower
        """
        try:
            checkname = self.dbmgr.checkname(name)

            if checkname:
                arg = '''SELECT XP_Cur, XP_Total FROM Chars WHERE Name = "{0}" COLLATE NOCASE'''.format(name)
                xp = self.dbmgr.readone(arg)
                xpcur, xpmax = str(xp[0]), str(xp[1])
                created = "Available Experience for %s (" % name
                created = str(created) + xpcur + "/" + xpmax + ")"
                irc.reply(created, private=True)
            else:
                raise NameError(name)

        except NameError as e:
            self.dbmgr.rollback()
            created = ircutils.mircColor("Error: Character \"%s\" not in database." % e, 4)
            irc.reply(created)

    getcharxp = wrap(getcharxp, ['anything'])

    def givexp(self, irc, msg, args, name, num):
        """<name> <amount of xp>

        Manually give a Character XP
        """
        try:
            checkname = self.dbmgr.checkname(name)

            if checkname:
                arg = '''SELECT XP_Cur, XP_Total FROM Chars WHERE Name = "{0}" COLLATE NOCASE'''.format(name)
                xp = self.dbmgr.readone(arg)
                xpcur, xpmax = int(xp[0]), int(xp[1])
                xpmax, xpcur = xpmax + num, xpcur + num
                arg = '''UPDATE Chars SET XP_Cur = "{0}", XP_Total = "{1}" WHERE Name = "{2}" COLLATE NOCASE'''.format(
                    xpcur, xpmax, name)
                self.dbmgr.query(arg)
                created = "%s XP given to %s. (%s/%s)" % (num, name, xpcur, xpmax)
                irc.reply(created, private=True)
            else:
                raise NameError(name)

        except NameError as e:
            self.dbmgr.rollback()
            created = ircutils.mircColor("Error: Character \"%s\" not in database." % e, 4)
            irc.reply(created)

    givexp = wrap(givexp, ['anything', 'int'])

    def spendxp(self, irc, msg, args, name, num, reason):
        """<name> <amount of xp> <reason>

        Manually spend a Characters XP
        """
        try:
            checkname = self.dbmgr.checkname(name)

            if checkname:
                arg = '''SELECT XP_Cur FROM Chars WHERE Name = "{0}" COLLATE NOCASE'''.format(name)
                xp = self.dbmgr.readone(arg)
                xpcur = int(xp[0])
                xpcur = xpcur - num
                if xpcur < 0:
                    irc.reply("Not enough XP to spend!", private=True)
                else:
                    arg = '''UPDATE Chars SET XP_Cur = "{0}" WHERE Name = "{1}" COLLATE NOCASE'''.format(xpcur, name)
                    self.dbmgr.query(arg)
                    arg = '''INSERT INTO XPlog(Name, Date, ST, Amount, Reason)
                              VALUES("{0}", date('now'), "{1}", "{2}", "{3}")'''.format(name, nicks, num, reason)
                    self.dbmgr.query(arg)
                    created = "%s XP spent from %s." % (num, name)
                    irc.reply(created, private=True)
            else:
                raise NameError(name)

        except NameError as e:
            self.dbmgr.rollback()
            created = ircutils.mircColor("Error: Character \"%s\" not in database." % e, 4)
            irc.reply(created)

    spendxp = wrap(spendxp, ['anything', 'int', 'text'])

    def requestxp(self, irc, msg, args, amount):
        """<amount>

        Request <amount> (1-3) XP for the last week. XP is given out on Mondays.
        """

        nicks = msg.nick
        try:
            checkname = self.dbmgr.checkname(nicks)
            reqname = self.dbmgr.reqname(nicks)

            if 3 < amount < 1:
                created = "You have requested %s dicks in your eye, you god damn smartass. " \
                          "Pick something below 3." % amount
                irc.queueMsg(ircmsgs.notice(nicks, created))

            elif checkname and not reqname:
                arg = '''INSERT INTO Request(Name, Amount) VALUES("{0}", "{1}")'''.format(nicks, amount)
                self.dbmgr.query(arg)
                created = "You have requested %s XP" % amount
                irc.queueMsg(ircmsgs.notice(nicks, created))

            elif checkname and reqname:
                arg = '''UPDATE Request SET Amount = "{0}" WHERE Name = "{1}"'''.format(amount, nicks)
                self.dbmgr.query(arg)
                created = "You have requested %s XP" % amount
                irc.queueMsg(ircmsgs.notice(nicks, created))
            else:
                raise NameError(nicks)

        except NameError as e:
            self.dbmgr.rollback()
            created = ircutils.mircColor("Error: Character \"%s\" not in database." % e, 4)
            irc.reply(created)

    requestxp = wrap(requestxp, ['int'])

    def requestlist(self, irc, msg, args):
        """takes no arguments

        Show the Request XP list for this week
        """
        try:
            arg = '''SELECT * FROM Request'''
            rows = self.dbmgr.fetchall(arg)

            for row in rows:
                created = "%s requested %s XP" % (row[1], row[2])
                irc.reply(created, prefixNick=False)

        finally:
            pass

    requestlist = wrap(requestlist)

    def modifylist(self, irc, msg, args, command, name, amount):
        """<command> <name> <optional(amount)>

        Modify the requestxp list.
        Remove command removes a name from the list.
        Add command adds a name and an amount to the list.
        Change command changes a name already on the list.
        """
        try:
            checkname = self.dbmgr.checkname(name)
            reqname = self.dbmgr.readone(name)

            if command == 'remove':
                if checkname and reqname:
                    arg = '''DELETE FROM Request WHERE Name = "{0}" COLLATE NOCASE'''.format(name)
                    self.dbmgr.query(arg)
                    created = "%s removed from requestxp list." % name
                    irc.reply(created, private=True)
                else:
                    raise NameError(name)

            elif command == 'add':
                if checkname and not reqname:
                    arg = '''INSERT INTO Request(Name, Amount) VALUES("{0}", "{1}")'''.format(name, amount)
                    self.dbmgr.query(arg)
                    created = "%s added with %s XP requested." % (name, amount)
                    irc.reply(created, private=True)
                else:
                    irc.reply("Error: Name already exists in list. Use change instead.")

            elif command == 'change':
                if checkname and reqname:
                    arg = '''UPDATE Request SET Amount = "{0}" WHERE Name = "{1}" COLLATE NOCASE'''.format(amount, name)
                    self.dbmgr.query(arg)
                    created = "%s changed to %s XP requested." % (name, amount)
                    irc.reply(created, private=True)

                else:
                    raise NameError(name)
            else:
                irc.reply("Error: Please use commands: remove, add or change")

        except NameError as e:
            self.dbmgr.rollback()
            created = ircutils.mircColor("Error: Character \"%s\" not found in table." % e, 4)
            irc.reply(created)

    modifylist = wrap(modifylist, ['anything', 'anything', optional('int')])

    def approvelist(self, irc, msg, args):
        """takes no arguments

        Approves the XP list for this week.
        """
        try:

            arg = '''SELECT * FROM Request'''
            rows = self.dbmgr.fetchall(arg)

            for row in rows:
                name = row[1]
                arg = '''SELECT XP_Cur, XP_Total FROM Chars WHERE Name = "{0}"'''.format(name)
                xp = self.dbmgr.readone(arg)
                xpcur, xpmax = xp[0] + row[2], xp[1] + row[2]
                arg = '''UPDATE Chars SET XP_Cur = "{0}", XP_Total = "{1}" WHERE Name = "{2}"'''.format\
                    (xpcur, xpmax, name)
                self.dbmgr.query(arg)
                created = "Gave %s %s XP" % (name, row[2])
                irc.reply(created, private=True)

        finally:
            arg = '''DROP TABLE Request'''
            self.dbmgr.query(arg)
            arg = '''CREATE TABLE Request(Id INTEGER PRIMARY KEY, Name TEXT, Amount INT)'''
            self.dbmgr.query(arg)

    approvelist = wrap(approvelist)

    def _damage(self, name):
        try:
            check_name = self.dbmgr.checkname(name)

            if check_name:
                arg = '''SELECT Aggravated_dmg, Normal_dmg FROM Chars WHERE Name = "{0}"'''.format(name)
                dmg = self.dbmgr.readone(arg)
                agg, norm = dmg[0], dmg[1]
                response = name + " " + str(agg) + " Agg | " + str(norm) + " Norm"
                if agg + norm == 0:
                    response += " * UNDAMAGED"
                elif agg + norm == 1:
                    response += " * BRUISED (0 Dice Penalty)"
                elif agg + norm == 2:
                    response += " * HURT (-1 Dice Penalty)"
                elif agg + norm == 3:
                    response += " * INJURED (-1 Dice Penalty)"
                elif agg + norm == 4:
                    response += " * WOUNDED (-2 Dice Penalty)"
                elif agg + norm == 5:
                    response += " * MAULED (-2 Dice Penalty)"
                elif agg + norm == 6:
                    response += " * CRIPPLED (-5 Dice Penalty)"
                elif agg + norm == 7:
                    response += " * INCAPACITATED"
                elif norm == 8:
                    response += " * TORPORED"
                elif agg == 8:
                    response += " * FINAL DEATH"

                return response
            else:
                raise NameError(name)

        except NameError as e:
            self.dbmgr.rollback()
            response = ircutils.mircColor("Error: Character \"%s\" not in database." % e, 4)
            return response

    def getdmg(self, irc, msg, args):
        """takes no arguments

        check your current damage
        """
        name = msg.nick
        try:
            response = self._damage(name)
            irc.reply(response)
        finally:
            pass

    getdmg = wrap(getdmg)

    def dmgcheck(self, irc, msg, args, name):
        """takes <name> argument -
        check a players current damage
        """
        try:
            response = self._damage(name)
            irc.reply(response)
        except NameError:
            pass

    dmgcheck = wrap(dmgcheck, ['anything'])

    def givedmg(self, irc, msg, args, name, amount, dmgtype):
        """<name> <amount> <type>

        Give players damage. Use agg or norm for type.
        """
        try:
            checkname = self.dbmgr.checkname(name)

            if checkname:
                arg = '''SELECT Aggravated_Dmg, Normal_Dmg FROM Chars WHERE Name = "{0}" COLLATE NOCASE'''.format(name)
                dmg = self.dbmgr.readone(arg)
                combinedmg = dmg[0] + dmg[1] + amount

                if dmgtype.lower() == "agg" and combinedmg > 7:
                    arg = '''UPDATE Chars SET Aggravated_Dmg = 8 WHERE Name = "{0}" COLLATE NOCASE'''.format(name)
                    self.dbmgr.query(arg)
                    created = "%s %s given to %s. %s has met FINAL DEATH!" % (amount, dmgtype, name, name)
                    irc.reply(created)

                elif dmgtype.lower() == "norm" and combinedmg == 7:
                    newamount = amount + dmg[1]
                    arg = '''UPDATE Chars SET Normal_Dmg = "{0}" WHERE Name = "{1}" COLLATE NOCASE'''.format(
                        newamount, name)
                    self.dbmgr.query(arg)
                    created = "%s %s given to %s. %s has been INCAPACITATED!" % (amount, dmgtype, name, name)
                    irc.reply(created)

                elif dmgtype.lower() == "norm" and combinedmg > 7:
                    newamount = amount + dmg[1]
                    arg = '''UPDATE Chars SET Normal_Dmg = "{0}" WHERE Name = "{1}" COLLATE NOCASE'''(newamount, name)
                    self.dbmgr.query(arg)
                    created = "%s %s given to %s. %s has been TORPRED!" % (amount, dmgtype, name, name)
                    irc.reply(created)

                elif dmgtype.lower() == "agg":
                    newamount = amount + dmg[0]
                    arg = '''UPDATE Chars SET Aggravated_Dmg = "{0}" WHERE Name = "{1}" COLLATE NOCASE'''.format(
                        newamount, name)
                    self.dbmgr.query(arg)
                    created = "%s %s given to %s." % (amount, dmgtype, name)
                    irc.reply(created)

                elif dmgtype.lower() == "norm":
                    newamount = amount + dmg[1]
                    arg = '''UPDATE Chars SET Normal_Dmg = "{0}" WHERE Name = "{1}" COLLATE NOCASE'''.format(
                        newamount, name)
                    self.dbmgr.query(arg)
                    created = "%s %s given to %s." % (amount, dmgtype, name)
                    irc.reply(created)
                else:
                    raise NameError("Error: You must use !givedmg <value> <agg|norm>")

                ## give new values after setting them...
                try:
                    response = self._damage(name)
                    irc.queueMsg(ircmsgs.privmsg(name, response))
                finally:
                    pass

        except NameError as error:
            self.dbmgr.rollback()
            irc.reply(error)

    givedmg = wrap(givedmg, ['anything', 'int', 'anything'])

    def heal(self, irc, msg, args, amount, dmgtype):
        """<amount> <type>

        Heal <amount> of <type> damage. Make sure you have enough BP.
        """
        nicks = msg.nick
        try:
            checkname = self.dbmgr.checkname(nicks)

            if checkname:
                arg = '''SELECT BP_Cur, Aggravated_Dmg, Normal_Dmg FROM Chars WHERE Name = "{0}"'''.format(nicks)
                info = self.dbmgr.readone(arg)
                #first check what type of damage it is
                if dmgtype.lower() == "agg":
                    #do they have enough bp? it's 5bp per agg healed
                    amountbp = amount * 5
                    newbp = info[0] - amountbp
                    if newbp >= 0:
                        toheal = info[1] - amount
                        # if we heal too much
                        if toheal < 0:
                            raise ArithmeticError("You don't have that much damage to heal.")

                        arg = '''UPDATE Chars SET Aggravated_Dmg = "{0}", BP_Cur = "{1}" WHERE Name = "{2}"'''.format(
                            toheal, newbp, nicks)
                        self.dbmgr.query(arg)
                        created = "%s %s damage healed for %s BP." % (amount, dmgtype, amountbp)
                        irc.reply(created)

                    else:
                        raise ArithmeticError("You do not have enough BP!")

                elif dmgtype.lower() == "norm":
                    newbp = info[0] - amount
                    if newbp >= 0:
                        toheal = info[2] - amount

                        if toheal < 0:
                            raise ArithmeticError("You don't have that much damage to heal.")

                        arg = '''UPDATE Chars SET Normal_Dmg = "{0}", BP_Cur = "{1}" WHERE Name = "{2}"'''.format(
                            toheal, newbp, nicks)
                        self.dbmgr.query(arg)
                        created = "%s %s damage healed for %s BP" % (amount, dmgtype, amount)
                        irc.reply(created)

                    else:
                        raise ArithmeticError("You do not have enough BP!")

        except ArithmeticError as error:
            irc.reply(error)

    heal = wrap(heal, ['int', 'anything'])

    def npc(self, irc, msg, args, name, numset):
        """<name> <1 or 0>

        Sets a characters as an NPC in the bot, preventing blood loss overnight, etc.
        """
        try:
            checkname = self.dbmgr.checkname(name)

            if checkname:
                arg = '''UPDATE Chars SET NPC = "{0}" WHERE Name = "{1}" COLLATE NOCASE'''.format(numset, name)
                self.dbmgr.query(arg)
                created = "NPC set to %s" % numset
                irc.reply(created)
            else:
                raise NameError(name)

        except NameError as e:
            self.dbmgr.rollback()
            response = ircutils.mircColor("Error: Character \"%s\" not in database." % e, 4)
            return response

    npc = wrap(npc, ['anything', 'int'])

    def nightly(self, irc, msg, args):
        """takes no arguments

        Runs the nightly maintenance.
        """

        try:
            arg = '''SELECT BP_Cur, Name, NPC, BP_Max FROM Chars'''
            rows = self.dbmgr.fetchall(arg)

            for row in rows:
                if row[2] == 0:
                    bpcur = row[0] - 1
                    if bpcur < 0:
                        bpcur = 0
                    arg = '''UPDATE Chars SET BP_Cur = "{0}" WHERE Name = "{1}"'''.format(bpcur, row[1])
                else:
                    bpcur = row[3]
                    arg = '''UPDATE Chars SET BP_Cur = "{0}" WHERE Name = "{1}"'''.format(bpcur, row[1])

                self.dbmgr.query(arg)

        finally:
            pass

    nightly = wrap(nightly)

    def weekly(self, irc, msg, args):
        """takes no arguments

        Runs the weekly maintenance.
        """

        try:
            arg = '''SELECT WP_Cur, Name, NPC, WP_Max FROM Chars'''
            rows = self.dbmgr.fetchall(arg)

            for row in rows:
                wpcur = row[0] + 1
                if wpcur > row[3]:
                    wpcur = row[3]
                arg = '''UPDATE Chars SET WP_Cur = "{0}" WHERE Name = "{1}"'''.format(wpcur, row[1])
                self.dbmgr.query(arg)
        finally:
            pass

    weekly = wrap(weekly)

    def charlog(self, irc, msg, args, name):
        """takes the <name> argument

        Gives a log of characters XP spends
        """

        try:

            arg = '''SELECT Date, ST, Amount, Reason FROM XPlog WHERE Name = "{0}" COLLATE NOCASE'''.format(name)
            logdata = self.dbmgr.fetchall(arg)

            if logdata:
                reply = ('Date', 'ST Name', 'XP Spent', 'Reason')
                irc.reply(reply, prefixNick=False)

                for row in logdata:
                    irc.reply(row, prefixNick=False)
            else:
                raise NameError(name)

        except NameError as error:
            self.dbmgr.rollback()
            response = ircutils.mircColor("Error: Character \"%s\" not in database." % error, 4)
            return irc.reply(response, prefixNick=False)

    charlog = wrap(charlog, ['admin', 'anything'])

    # def ctest(self, irc, msg, args):
    #     """Let's see if this works"""
    #     irc.reply("ctest reporting in")
    #     conn = sqlite3.connect('characters.db')
    #     c = conn.cursor()
    #     c.execute("SELECT * FROM Chars")
    #     rows = c.fetchall()
    #
    #     for row in rows:
    #         irc.reply(row)
    #
    # ctest = wrap(ctest)
    #
    # def logtest(self, irc, msg, args):
    #     conn = sqlite3.connect('characters.db')
    #     c = conn.cursor()
    #     c.execute("SELECT * FROM XPlog")
    #
    #     rows = c.fetchall()
    #
    #     for row in rows:
    #         irc.reply(row)
    #
    # logtest = wrap(logtest)

Class = Characters