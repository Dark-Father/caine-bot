###
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

class Chess(callbacks.Plugin):
    """Add the help for "@plugin help Chess" here
    This should describe *how* to use this plugin."""
    threaded = True

    def __init__(self, irc):
        self.__parent = super(Combat, self)
        self.__parent.__init__(irc)
        self.channel_lock = {}
        self.players = {}

    def chess(self, irc, msg, args, newgame):
        current_channel = msg.args[0]
        try:
            if current_channel not in self.channel_lock:
                self.channel_lock[current_channel] = True
            else:
                self.channel_lock[current_channel] = True

            if newgame == "newgame":
                if current_channel not in self.channel_lock:
                    self.channel_lock[current_channel] = True
                    self.players[current_channel].clear()
                    irc.reply("New Game Started.")
                else:
                    self.channel_lock[current_channel] = True
                    self.players[current_channel].clear()
                    irc.reply("New Game Started.")

        except KeyError:
            irc.reply("There was an error. Try !chess newgame")


    chess = wrap(chess, [optional('something')])

    def white(self, irc, msg, args, diff):
        current_channel = msg.args[0]
        fancy_outcome = []

        if current_channel not in self.channel_lock:
            irc.error("Game not started. Start with !chess or !chess newgame")

        if self.channel_lock[current_channel] is True:
            for s in range(num):
                if diff:
                    difficulty = diff
                else:
                    difficulty = 7
                die = random.randint(1, 10)

                if die >= difficulty:  # success evaluation
                    success += 1
                    if die == 10:
                        spec += 1
                        fancy_outcome.append(ircutils.mircColor(die, 10))
                    else:
                        fancy_outcome.append(ircutils.mircColor(die, 12))

                elif die == 1:  # math for ones
                    ones += 1
                    fancy_outcome.append(ircutils.mircColor(die, 4))

                else:
                    fancy_outcome.append(ircutils.mircColor(die, 6))

            #the aftermath
            total = success - ones
            if spec > ones:
                spec = spec - ones + total
            else:
                spec = total





        else:
            irc.error("Game not started. Start with !chess or !chess newgame")


    white = wrap(white, [optional('int')])

    def black(self, irc, msg, args, diff):
        current_channel = msg.args[0]
        fancy_outcome = []

        if current_channel not in self.channel_lock:
            irc.reply("Game not started. Start with !chess or !chess newgame")

        for s in range(num):
            if diff:
                difficulty = diff
            else:
                difficulty = 7
            die = random.randint(1, 10)

            if die >= difficulty: #success evaluation
                success += 1
                if die == 10:
                    spec += 1
                    fancy_outcome.append(ircutils.mircColor(die, 10))
                else:
                    fancy_outcome.append(ircutils.mircColor(die, 12))

            elif die == 1: #math for ones
                ones += 1
                fancy_outcome.append(ircutils.mircColor(die, 4))

            else:
                fancy_outcome.append(ircutils.mircColor(die, 6))


        if current_channel not in self.channel_lock:
            irc.reply("Game not started. Start with !chess or !chess newgame")

    black = wrap(black, [optional('int')])




Class = Chess


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
