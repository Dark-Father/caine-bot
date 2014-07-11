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
import supybot.conf as conf
import supybot.world as world
import supybot.irclib as irclib
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.registry as registry
import supybot.callbacks as callbacks
#import MySQLdb
#pip install peewee
from peewee import *


class Tracker(callbacks.Plugin):
    """This plugin will register a character in the database.
    Initialize their bloodpool and willpower and track it
    Track Experience and allow them to spend it."""
    threaded = True

    def __init__(self, irc):
        self.__parent = super(Tracker, self)
        self.__parent.__init__(irc)


##############################################################################
################### Tracker: Character Creation ##############################
##############################################################################
    #private function for ops(aka storytellers) this will initialize a record.
    # this inserts the default record into the database
    # autosets the description to "no description set"
    # autosets the generational bloodpool size
    # autosets the willpower
    #example: !newchar David 9 7. Will sent the character name to "David" with Generation 9 (14bp) and 7 willpower
    def newchar(self, irc, msg, args, name, generation, willpower):
        """parameters: <name> <generation> <willpower>
        registers a new character to the database"""
        character = "registered: %s | Generation: %s | Willpower: %s." % (name, generation, willpower)
        irc.reply(character)

    newchar = wrap(newchar, ['admin', 'something', 'int', 'int'])
    
    def activate(self, irc, msg, args, name):
        """Activate a character marked as inactive"""
        pass
    activate = wrap(activate, ['admin', 'something'])
    
    def deactivate(self, irc, msg, args, name):
        """Mark a character as inactive, freezes assets."""
        pass
    deactivate = wrap(deactivate, ['admin', 'something'])    

    #private function for ops(aka storyteller) to delete a character entirely.
    def delchar(self, irc, msg, args, name):
        """parameters: <name>
        removes a character from the database"""
        removed = "has removed character: %s from the database." % name
        irc.reply(removed, action=True)

    delchar = wrap(delchar, ['admin', 'text'])

############################################################################
################### Tracker: Description Section ###########################
############################################################################
    #associate a description to the the irc.nick
    def setdesc(self, irc, msg, args, text):
        """Sets description for your character"""
        pass
    setdesc = wrap(wrap(setdesc, ['text']))

    #set the irc.nick's link association. Generally used to set links to character wiki page or image link
    def setlink(self, irc, msg, args, text):
        """Sets a link for your characeter (generally image or wiki link)"""
        pass
    setlink = wrap(setlink, ['text'])

    #!describe <character> -- returns results by querying mysqldb
    # for character name and its associated description set by !setdesc
    # it should also return its associated URL (still text area) if one exists
    # this will also verify if a character is registered or not and inform the character if they need to contact an ST
    # for assistance in registering their nick
    def describe(self, irc, msg, args, text):
        """Describes a character"""
        pass
    describe = wrap(describe, ['text'])

##########################################################################
################### Tracker: Bloodpool Section ###########################
##########################################################################
    #feeding
    def feed(self, irc, msg, args, hours, diff):
        """Parameters: <hours> <difficulty> (location)
        Feed on the weak and unwilling"""
        pass
    
    feed = wrap(feed, ['int', 'int', optional('text')])
    
    #bloodpool storage
    def getbp(self, irc, msg, args):
        """Obtains character's current bloodpool"""
        pass
    
    getbp = wrap(getbp)
    
    #STORYTELLER FUNCTION
    def forcefeed(self, irc, msg, args, nick, blood):
        """Storyteller Function used to give blood.
        Parameters: <nick> <amount>"""
        pass
    
    forcefeed = wrap(forcefeed, ['admin', 'text', 'int'])
    
    def removebp(self, irc, msg, args, nick, blood):
        """Storyteller Function used to remove blood.
        Parameters: <nick> <amount> (reason)"""
        pass
    removebp = wrap(removebp, ['admin', 'text', 'int'])


##########################################################################
################### Tracker: Willpower Section ###########################
##########################################################################
    def wp(self, irc, msg, args, reason):
        """Spends one willpower point."""
        pass    
    wp = wrap(wp, [optional('text')])
    
    def getwp(self, irc, msg, args):
        """Obtain current willpower amount"""
        pass
    getwp = wrap(getwp)
    
    def forcewp(self, irc, msg, args, nick, willpower):
        """Storyteller Function used to give willpower.
        Parameters: <nick> <amount>"""
        pass
    forcewp = wrap(forcewp, ['admin', 'text', 'int'])

###########################################################################
################### Tracker: Experience Section ###########################
###########################################################################
    def getxp(self, irc, msg, args):
        """Obtains current amount of XP, both available and total gained"""
        pass
    getxp = wrap(getxp)
    
    def requestxp(self, irc, msg, args, amount, reason):
        """Request XP for gameplay
        If called again in the same week, amount is replaced with the new value"""
        pass    
    requestxp = wrap(requestxp, ['int', optional('text')])
    
    def bonusxp(self, irc, msg, args, nick, amount, reason):
        """Storyteller Function used to give bonus XP.
        Parameters: <nick> <amount> (reason)"""
        pass
    bonusxp = wrap(bonusxp, ['admin', 'int', optional('text')])
    
    def listxp(self, irc, msg, args):
        """Storyteller Function to list XP and reasons from all characters that requested"""
        pass
    listxp = wrap(listxp)
    
    def subtractxp(self, irc, msg, args, nick, amount, reason):
        """Storyteller Function to remove XP from a character
        Parameters: <nick> <amount> (reason)"""
        pass
    subtractxp = wrap(subtractxp, ['admin', 'int', optional('text')])
    
    def approveall(self, irc, msg, args):
        """Approves all request XP for characters."""
        pass
    approveall = wrap(approveall, ['admin', 'something'])
    
    def removerequest(self, irc, msg, args, nick, reason):
        """Remove a requested character's experience"""
        pass
    
    removerequest = wrap(removerequest, ['admin', 'something'])















Class = Tracker
