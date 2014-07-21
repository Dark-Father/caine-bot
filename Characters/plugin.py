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
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import sqlite3



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

        try:
            conn = sqlite3.connect('characters.db')
            conn.text_factory = str
            c = conn.cursor()
            c.execute("INSERT INTO Chars(Name, BP_Cur, Bp_Max, WP_Cur, WP_Max, XP_Cur, XP_Total, Description, Link,"
                      " Requested_XP, "
                      "Fed_Already, Aggravated_Dmg, Normal_Dmg, NPC) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (name,
                                                                                                 bp, bp, wp, wp, 0, 0,
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

    def describe(self, irc, msg, args, name):
        """<name>

        Gets the description of the named character
        """

        name = str(name)
        try:
            conn = sqlite3.connect('characters.db')
            conn.text_factory = str
            c = conn.cursor()
            c.execute("SELECT Name, Description FROM Chars WHERE Name = ?", (name,))
            desc = c.fetchone()
            created = desc[0] + " " + desc[1]
            created = ircutils.mircColor(created,6)
            irc.reply(created, prefixNick=False)

        except sqlite3.Error:
            conn.rollback()
            irc.reply("Error: Name not found.")

        finally:
            conn.close()



    describe = wrap(describe, ['anything'])

    def ctest(self, irc, msg, args):
        """Let's see if this works"""
        irc.reply("ctest reporting in")
        c.execute("SELECT * FROM Chars")
        rows = c.fetchall()

        for row in rows:
            irc.reply(row)


    ctest = wrap(ctest)

    def secondtest(self, irc, msg, args):
        """no arguments
        """
        irc.reply("secondtest reporting in")
        try:
            conn = sqlite3.connect('characters.db')
            conn.text_factory = str
            c = conn.cursor()
            c.execute("SELECT Name FROM Chars")
            rows = c.fetchall()
        finally:
            conn.close

        for row in rows:
            str(row)
            irc.reply(row[0])


Class = Characters


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
