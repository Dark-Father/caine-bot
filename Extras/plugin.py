# ##
# Copyright (c) 2014, David Rickman
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


class Extras(callbacks.Plugin):
    """Extra commands to make life easier and better for players and Storytellers.
    https://github.com/freedomischaos/caine-bot/blob/master/Extras/README.txt"""
    threaded = True

    def __init__(self, irc):
        #pass
        self.__parent = super(Extras, self)
        self.__parent.__init__(irc)

    def stfree(self, irc, msg, args):
        """takes no arguments
        Checks #stchambers to see if occupied."""
        channel = "#stchambers"
        diff = []

        users = list(irc.state.channels[channel].users)
        st = list(irc.state.channels[channel].ops)
        diff = list(set(users) - set(st))

        if not st:
            abbra = "There are no Storytellers logged in. Try again later."
            irc.reply(abbra)
        elif diff:
            abbra = "Chambers is " + ircutils.mircColor("BUSY", 4) + ". Occupied by: " + ircutils.bold(", ".join(diff))
            irc.reply(abbra)
        else:
            abbra = "Chambers is " + ircutils.mircColor("OPEN", 3) + ". Join #stchambers now!"
            irc.reply(abbra)

    stfree = wrap(stfree)


Class = Extras


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
