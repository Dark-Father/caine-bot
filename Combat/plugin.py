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
import random

class Combat(callbacks.Plugin):
    """This plugin manages combat for Vampire the Masquerade system.
    It is called with !combat start. This also pings #stchambers with a message that combat has started in #channel.
    It logs players that cast !inits to join the current round. This is redone with !newround.
    Combat ends with !combat end"""
    threaded = True
    
    
    def __init__(self, irc):
        self.__parent = super(Combat, self)
        self.__parent.__init__(irc)
        self.powered = "end"
        self.channel_lock = False
        self.roundlist = {}

    def combat(self, irc, msg, args, powered):
        """Start combat with: !combat start 
        End combat with: !combat end"""
        if self.channel_lock == True:
            irc.error("Combat is already started. Join combat with !inits <dex+wits>", Raise=True)
        elif powered == "start":
            self.powered = "start"
            self.channel_lock = True
            irc.reply("Combat Started")
        elif powered == "end":
            self.powered = "end"
            self.channel_lock = False
            irc.reply("Combat Ended")
        else:
            irc.error("Start or end combat with: !combat start|end", Raise=True)
    combat = wrap(combat, [optional('text')])
    
    def inits(self, irc, msg, args, inits, NPC):
        """Roll to join combat. Use !inits <dex+wits>.
        To add NPCs, cast: !inits <value> (NPC)."""
        if self.powered == "start":
            rolled = inits + random.randint(1, 10)

            #check to see if NPC was passed.
            if not NPC:
                character = msg.nick
            else:
                character = NPC

            self.roundlist[character] = rolled

            joined = str(character) + " rolled a: " + str(rolled)
            irc.reply(joined)
            #irc.reply(character)
            #irc.reply(rolled)
        else:
            irc.reply("Combat is not started. Start combat with: !combat start")
    inits = wrap(inits, ['int', optional('text')])
    
    def showinits(self, irc, msg, args):
        """Lists the current combat roster"""
        irc.reply(self.roundlist)
    showinits = wrap(showinits)

    def newround(self, irc, msg, args):
        """Clears roster of all characters. Players will need to rejoin with !inits"""
        pass
    newround = wrap(newround)
    






Class = Combat


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
