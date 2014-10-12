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
import random


class Extras(callbacks.Plugin):
    """Extra commands to make life easier and better for players and Storytellers.
    https://github.com/freedomischaos/caine-bot/blob/master/Extras/README.txt"""
    threaded = True

    def __init__(self, irc):
        #pass
        self.__parent = super(Extras, self)
        self.__parent.__init__(irc)
        self.snack = {}
        self.megan = 0

    def stfree(self, irc, msg, args):
        """takes no arguments
        Checks #stchambers to see if occupied."""
        channel = "#stchambers"
        bot = str.capitalize(irc.nick)
        storytellers = [x.capitalize() for x in list(irc.state.channels[channel].ops)]
        diff = list(set([x.lower() for x in list(irc.state.channels[channel].users)]) -
                    set([x.lower() for x in list(irc.state.channels[channel].ops)]))
        diff = [x.capitalize() for x in diff]
        if bot in diff:
            diff.pop(diff.index(bot))
        if bot in storytellers:
            storytellers.pop(storytellers.index(bot))

        diff = [ircutils.mircColor(x, 4) for x in diff]

        if diff:
            abbra = "Chambers is " + ircutils.mircColor("BUSY", 4) + ". Occupied by: " + ircutils.bold(", ".join(diff))
            irc.reply(abbra)
        elif not storytellers:
            abbra = "There are no Storytellers logged in. Try again later."
            irc.reply(abbra)
        elif not diff:
            abbra = "Chambers is " + ircutils.mircColor("OPEN", 3) + ". Join #stchambers now!"
            irc.reply(abbra)
    stfree = wrap(stfree)

    def treat(self, irc, msg, args):
        currentChannel = msg.args[0]
        only_channel = "#ooc"
        nick = msg.nick

        if currentChannel == only_channel:
            if nick not in self.snack:
                self.snack[nick] = 0

            if self.snack[nick] < random.randint(1, 1000):
                self.snack[nick] += 1
                irc.reply("You fed a treat to %s. You've fed %s treats to Caine."
                          % (irc.nick, self.snack[nick]))
            else:
                irc.reply("Caine has risen from torpor and devoured you as a treat.")
                self.snack[nick] = 0
        else:
            irc.error("Command only available in #ooc.", Raise=True)
    treat = wrap(treat)

    def sacrifice(self, irc, msg, args, megan):
        currentChannel = msg.args[0]
        only_channel = "#ooc"

        try:
            if currentChannel == only_channel:
                die = random.randint(1, 100)
                if msg.nick == "Isabel" or msg.nick == "Megan":
                    self.megan += 1
                    silly_megan = "Megan slips and falls into the sacrifice instead, " \
                                  "sacrificing herself to herself. Standard Megan move. " \
                                  "Megan has been sacrificed %s times." % self.megan
                    irc.reply(silly_megan, prefixNick=False)
                elif megan != "Megan":
                    irc.reply("Caine prefers Megan only.", prefixNick=False)
                elif megan == "Megan":
                    self.megan += 1
                    irc.reply("Megan has been sacrificed to appeased Caine. Megan has been sacrificed %s times."
                              % self.megan, prefixNick=False)
                elif not megan:
                    if die < 90:
                        irc.reply("%s sacrifices themselves to %s."
                                  % (msg.nick, irc.nick), prefixNick=False)
                    else:
                        irc.reply("%s rejects your pathetic attempts to appease him, %s."
                                  % (irc.nick, msg.nick), prefixNick=False)
            else:
                irc.error("Command only available in #ooc.", Raise=True)
        except KeyError:
            pass
    sacrifice = wrap(sacrifice, [optional('text')])
Class = Extras


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
