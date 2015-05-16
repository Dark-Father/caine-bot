###
# Copyright (c) 2015, David Rickman
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
# this list of conditions, and the following disclaimer.
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
from peewee import *
import datetime


db = MySQLDatabase('cainitebot', host="192.168.1.6", user='cainitebot', passwd='cainitebot')


class BaseModel(Model):
    class Meta:
        database = db


class Character(BaseModel):
    id = PrimaryKeyField()
    name = CharField(unique=True)
    created = DateField()
    bp = IntegerField(default=0)
    bp_cur = IntegerField(default=0)
    ebp = IntegerField(default=0)
    wp = IntegerField(default=0)
    wp_cur = IntegerField(default=0)
    xp_cur = IntegerField(default=0)
    xp_spent = IntegerField(default=0)
    xp_total = IntegerField(default=0)
    xp_req = IntegerField(default=0)
    fed_already = DateField()
    desc = CharField(default='Looks like you need a description. Set one before you go in-character.')
    link = CharField(default='')
    lastname = CharField(default='')
    stats = CharField(default='')
    dmg_norm = IntegerField(default=0)
    dmg_agg = IntegerField(default=0)
    isnpc = BooleanField(default=False)


class XPlog(BaseModel):
    id = ForeignKeyField(Character)
    name = TextField(default='')
    date = DateField(default=datetime.date.today())
    st = TextField(default='')
    amount = IntegerField(default=0)
    reason = TextField(default='')


##############################
# Database Model Controls
##############################
# db.connect()
# db.drop_tables([XPlog], cascade=True)
# db.drop_tables([Character], cascade=True)
XPlog.drop_table()
Character.drop_table()
Character.create_table()
XPlog.create_table()


##############################
# SUPYBOT CODE AFTER HERE
##############################
class Management(callbacks.Plugin):
    """This is the full character management system for Cainite.org"""
    threaded = True

    def __init__(self, irc):
        self.__parent = super(Management, self)
        self.__parent.__init__(irc)

    def createchar(self, irc, msg, args, name, bp, wp):
        """<name> <bp> <wp>
        Adds the Character with <name> to the bot, with a maximum <bp> and maximum <wp>
        """
        try:
            with db.atomic():
                Character.get_or_create(
                    name=name,
                    bp=int(bp),
                    bp_cur=int(bp),
                    wp=int(wp),
                    wp_cur=int(wp),
                    created=datetime.date.today())
                created = "Added %s with %s bp and %s wp" % (name, bp, wp)
                irc.reply(created)
        except IntegrityError or DoesNotExist:
            created = ircutils.mircColor("Error: Character \"%s\" already in database." % name, 4)
            irc.reply(created, private=True)

    createchar = wrap(createchar, ['anything', 'int', 'int'])

    def delchar(self, irc, msg, args, name):
        """Removes the Character <name> from the bot."""


Class = Management


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
