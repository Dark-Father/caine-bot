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

    def combat(self, irc, msg, args, powered):
        """Start combat with: !combat start 
        End combat with: !combat end"""
        if powered = "start":
            irc.reply("Combat Started")
        elif powered = "end":
            irc.reply("Combat Ended")
        else:
            irc.error("Start or end combat with: !combat start|end")
    
    def inits(self, irc, msg, args, inits, reason):
        """Adds player to combat roster"""
        rolled = str(random.randrange(1, 11)) #python counts from 0
        inits += rolled
    
    def showinits(self, irc, msg, args):
        """Lists the current combat roster"""
        pass
    
    def newround(self, irc, msg, args):
        """Clears roster of all characters. Players will need to rejoin with !inits"""
        pass
    
    






Class = Combat


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
