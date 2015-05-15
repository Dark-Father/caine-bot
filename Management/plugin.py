###
# Copyright (c) 2015, David Rickman
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
from peewee import *
from datetime import date


db = MySQLDatabase('cainitebot', host="192.168.1.6", user='cainitebot', passwd='cainitebot')

class BaseModel(Model):
    class Meta:
        database = db

class Character(BaseModel):
    id = PrimaryKeyField()
    name = TextField(default='', unique=True)
    created = DateField()
    bp = IntegerField()
    bp_cur = IntegerField()
    ebp = IntegerField()
    wp = IntegerField()
    wp_cur = IntegerField()
    xp_cur = IntegerField()
    xp_spent = IntegerField()
    xp_total = IntegerField()
    xp_req = IntegerField()
    fed_already = DateField()
    desc = TextField(default='Looks like you need a description. Set one before you go in-character.')
    link = TextField(default='')
    lastname = TextField(default='')
    stats = TextField(default='')
    dmg_norm = IntegerField()
    dmg_agg = IntegerField()
    isnpc = BooleanField()


class XPlog(BaseModel):
    id = ForeignKeyField(Character)
    name = TextField(default='')
    date = DateField()
    st = TextField(default='')
    amount = IntegerField()
    reason = TextField(default='')

db.connect()

# db.drop_tables([XPlog], cascade=True)
# db.drop_tables([Character], cascade=True)
db.create_table(Character)
db.create_table(XPlog)

# abel = Character(name="Abel", created=date(2015, 5, 15), bp=1, bp_cur=1, ebp=1, wp=1, wp_cur=1, xp_cur=1, xp_spent=1,
#                  xp_total=1, xp_req=3, fed_already=date(2015, 5, 15), desc="First Son", link="http://abel.org",
#                  lastname="Abel", stats="Murdered", dmg_norm=1, dmg_agg=1, isnpc=False)
# abel.save()
# caine = Character(name="Caine", created=date(2015, 5, 15), bp=1000, bp_cur=1000, ebp=1000, wp=1000, wp_cur=1000,
#                   xp_cur=1000, xp_spent=1000, xp_total=1000, xp_req=3, fed_already=date(2015, 5, 15),
#                   desc="Dark Father", link="http://caine.org", lastname="Nod", stats="All of them", dmg_norm=1,
#                   dmg_agg=1, isnpc=False)
# caine.save()





# SUPYBOT CODE AFTER HERE
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
        bp, wp = int(bp), int(wp)
        #capability = 'characters.createchar'
        #this check isn't really necessary, I was just testing capabilities.
        # if capability:
        #     if not ircdb.checkCapability(msg.prefix, capability):
        #         irc.errorNoCapability(capability, Raise=True)
        try:
            with database.transaction():
                # Attempt to create the user. If the username is taken, due to the
                # unique constraint, the database will raise an IntegrityError.
                pass

            user = User.create(
                name=name,
                bp=bp,
                wp=wp,
                created=datetime.datetime.now()
            )
            # mark the user as being 'authenticated' by setting the session vars
            auth_user(user)
            return redirect(url_for('homepage'))

        except IntegrityError:
            flash('That username is already taken')


        try:
            arg = Character.
            # fields = ()
            self.dbmgr.query(arg)
            created = "Added %s with %s bp and %s wp" % (name, bp, wp)
            irc.reply(created)

        except sqlite3.IntegrityError:
            # as Name is unique, it throws an integrity error if you try a name that's already in there.
            self.dbmgr.rollback()
            created = ircutils.mircColor("Error: Character \"%s\" already in database." % name, 4)
            irc.reply(created, private=True)






Class = Management


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
