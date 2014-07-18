###
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
conn = sqlite3.connect('characters.db')
c = conn.cursor()


class Characters(callbacks.Plugin):
    """Character administration and tracking for Vampire: The Masquerade"""


    def __init__(self, irc):
        #what does this do? I dunno!
        self.__parent = super(Characters, self)
        self.__parent.__init__(irc)

    def startdb(self, irc, msg, args):
        # Here we initialise the database table. Integer Primary Key makes the Id automatically increment. Then we set
        # up BP, WP, XP, Descriptions, a link, how much xp they requested, if they have already fed that day, and damage
        #  tracking. Exciting!
        c.execute("CREATE TABLE IF NOT EXISTS Chars(Id INTEGER PRIMARY KEY, Name TEXT, BP_Cur INT, "
                  "BP_Max INT, WP_Cur INT, WP_Max INT, XP_Cur INT, XP_Total INT, Description TEXT, Link TEXT, "
                  "Requested_XP INT, Fed_Already INT, Aggravated_Dmg INT, Normal_Dmg INT)")
        irc.reply('Database Created.')
    startdb = wrap(startdb)

    def createchar(self, irc, msg, args, name, bp, wp):
        """<name> <bp> <wp>

        """
        bp = int(bp)
        wp = int(wp)
        name = str(name)
        irc.reply('what what')
        created = "Added %s, with %s bp and %s wp" % (name, str(bp), str(wp))
        irc.reply(created)
    createchar = wrap(createchar, ['text', 'int', 'int'])

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
