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

from json import load
from urllib2 import urlopen
import time

#ZIP Code is Benton Heights, MI: 49022

class Weather(callbacks.Plugin):
    """Weather Control for the city of Minerva, MI"""

    def __init__(self, irc):
        self.__parent = super(Weather, self)
        self.__parent.__init__(irc)

    def weather(self, irc, msg, args):
        """I don't take kindly to back-talking.
        """
        _URL = "http://api.openweathermap.org/data/2.5/weather?id="
        _CITY_ID = "4985711"
        _KEY = "6aea5fa7d9438052b2403d6a1203dafb"
        _IMP = "&units=imperial"
        _METRIC = "&units=metric"
        #EXAMPLE: http://api.openweathermap.org/data/2.5/forecast/city?id=524901&APPID=1111111111
        _FULL_IMP = _URL + _CITY_ID + "&APPID=" + _KEY + _IMP
        _FULL_MET = _URL + _CITY_ID + "&APPID=" + _KEY + _METRIC

        _FULL2_IMP = urlopen(_FULL_IMP)
        _FULL2_METRIC = urlopen(_FULL_MET)

        #for the good guys, America fuck yea!
        i = load(_FULL2_IMP)
        itemperature = i['main']['temp']
        #temperature_unit = 'F'
        conditions = i['weather'][0]['description']

        #for the Communists out there...
        m = load(_FULL2_METRIC)
        mtemperature = m['main']['temp']

        #shitty weather station says...
        s = "The station reports that the current condition is: {0} with a temperature of {1}{2}({3}{4})"
        report = s.format(
            conditions[0].upper() + conditions[1:].lower(),
            int(round(itemperature)), "F",
            int(round(mtemperature)), "C")
        irc.reply(ircutils.mircColor(report,6))

    weather = wrap(weather)

Class = Weather
