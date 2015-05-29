###
# Copyright (c) 2015, David Rickman
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
# this list of conditions, and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions, and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# * Neither the name of the author of this software nor the name of
# contributors to this software may be used to endorse or promote products
# derived from this software without specific prior written consent.
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
from random import randint

################################
# Database Connection
################################
db = MySQLDatabase('cainitebot', host="192.168.1.6", user='cainitebot', passwd='cainitebot')


class BaseModel(Model):
    class Meta:
        database = db


class Character(BaseModel):
    name = CharField(unique=True)
    created = DateField(default=datetime.date.today())
    bp = IntegerField(default=0)
    bp_cur = IntegerField(default=0)
    ebp = IntegerField(default=0)
    ebp_cur = IntegerField(default=0)
    wp = IntegerField(default=0)
    wp_cur = IntegerField(default=0)
    xp_cur = IntegerField(default=0)
    xp_spent = IntegerField(default=0)
    xp_total = IntegerField(default=0)
    xp_req = IntegerField(default=0)
    fed_already = DateField(default='0000-00-00')
    desc = CharField(default='Looks like you need a description. Set one before you go in-character.')
    link = CharField(default='')
    lastname = CharField(default='')
    stats = CharField(default='')
    dmg_norm = IntegerField(default=0)
    dmg_agg = IntegerField(default=0)
    isnpc = BooleanField(default=False)

    class Meta:
        order_by = ('name',)


class Botch(BaseModel):
    name = ForeignKeyField(Character,
                           db_column='name',
                           to_field='name',
                           related_name='botches')
    date = DateTimeField(default=datetime.datetime.now)
    command = TextField(default='None Declared')


class Willpower(BaseModel):
    name = ForeignKeyField(Character,
                           db_column='name',
                           to_field='name',
                           related_name='willpower')
    date = DateTimeField(default=datetime.datetime.today())


class Emergency(BaseModel):
    name = ForeignKeyField(Character,
                           db_column='name',
                           to_field='name',
                           related_name='efeed')
    date = DateTimeField(default=datetime.datetime.today())
    amount = IntegerField(default=0)


class XPlog(BaseModel):
    name = ForeignKeyField(Character,
                           db_column='name',
                           to_field='name',
                           related_name='spends')
    date = DateField(default=datetime.date.today())
    st = CharField(default='')
    amount = IntegerField(default=0)
    reason = TextField(default='')

##############################
# Database Controls
##############################
# db.connect()
# db.drop_tables([XPlog], cascade=True)
# db.drop_tables([Character], cascade=True)
XPlog.drop_table()
Botch.drop_table()
Willpower.drop_table(fail_silently=True)
Emergency.drop_table(fail_silently=True)
Character.drop_table()

Character.create_table()
XPlog.create_table()
Botch.create_table()
Willpower.create_table()
Emergency.create_table()

# test data


def createchar(name, bp, wp):
    try:
        with db.atomic():
            Character.get_or_create(
                name=name,
                bp=int(bp),
                bp_cur=int(bp),
                wp=int(wp),
                wp_cur=int(wp),
                created=datetime.date.today())
    finally:
        pass


def botches(character):
    try:
        with db.atomic():
            Botch.create(
                character=character,
            )
    finally:
        pass

# create some data
createchar(name="Abel", bp=1, wp=1)
createchar(name="Cain", bp=99, wp=99)
createchar(name="Mike", bp=12, wp=12)
createchar(name="Gabe", bp=13, wp=7)
createchar(name="Lucifer", bp=15, wp=10)

# # botches(name="Lucifer")
# botches(character='Cain')



################################
# The BOT
################################
class Management(callbacks.Plugin):
    """This is the full character management system for Cainite.org"""
    threaded = True

    def __init__(self, irc):
        self.__parent = super(Management, self)
        self.__parent.__init__(irc)

    ##########################################
    # Character Creation Controls
    ##########################################

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
        except IntegrityError:
            created = ircutils.mircColor("Character {0} already in database.".format(name), 4)
            irc.reply(created, private=True)
        except DoesNotExist:
            created = "Error connecting to database."
            irc.reply(created, private=True)

    createchar = wrap(createchar, ['anything', 'int', 'int'])

    def delchar(self, irc, msg, args, name):
        """Removes the Character from the bot."""

        try:
            with db.atomic():
                fetch = Character.get(Character.name == name)
                fetch.delete_instance(recursive=True)
                message = "Character {0} removed from database.".format(name)
                irc.reply(message)
        except DoesNotExist:
            created = ircutils.mircColor("Error: Character {0} does not exist in database.".format(name), 4)
            irc.reply(created, private=True)


    delchar = wrap(delchar, ['anything'])

    # Create Update Character Functions to increase blood and willpower pools.

    #########################################
    # Character Description Controls
    #########################################

    def setdesc(self, irc, msg, args, description):
        """<description>
        Sets a description for your character
        """
        nick = str.capitalize(msg.nick)
        try:
            with db.atomic():
                if len(description) > 255:
                    irc.reply("Description is too long. Maximum length is 255 characters.")
                else:
                    Character.update(desc=description).where(Character.name == nick).execute()
                    irc.reply("Description set.")
        finally:
            pass

    setdesc = wrap(setdesc, ['text'])

    def setlastname(self, irc, msg, args, lastname):
        """<name>
        Set your characters last name for your description, so people don't have to look it up.
        """
        nick = str.capitalize(msg.nick)
        try:
            with db.atomic():
                Character.update(lastname=lastname).where(Character.name == nick).execute()
            irc.reply("Lastname set.")
        except Character.DoesNotExist:
            irc.reply("Character does not exist.", private=True)

    setlastname = wrap(setlastname, ['anything'])

    def setlink(self, irc, msg, args, url):
        """<url>
        Sets a link for your character description
        """
        nick = str.capitalize(msg.nick)

        try:
            with db.atomic():
                Character.update(link=url).where(Character.name == nick).execute()
            irc.reply("Your link has been set.")
        except Character.DoesNotExist:
            irc.reply("Character does not exist.", private=True)

    setlink = wrap(setlink, ['text'])

    def setstats(self, irc, msg, args, stats):
        """<stats>
        Set your characters stats i.e App2|Cha2
        """
        nick = str.capitalize(msg.nick)

        try:
            with db.atomic():
                Character.update(stats=stats).where(Character.name == nick).execute()
            irc.reply("Your stats have been updated.")

        except Character.DoesNotExist:
            irc.reply("Character does not exist.", private=True)

    setstats = wrap(setstats, ['text'])

    def describe(self, irc, msg, args, name):
        """<name>
        Gets the description of the a character
        """
        try:
            with db.atomic():
                q = Character.get(Character.name == name)
            message = "{0} {1} {2}".format(q.name, q.lastname, q.desc)
            message = ircutils.mircColor(message, 8)
            irc.reply(message, prefixNick=False, private=True)
            if q.link or q.stats:
                message2 = 'Link: {0} || Stats: {1}'.format(q.link, q.stats)
                message2 = ircutils.mircColor(message2, 8)
                irc.reply(message2, prefixNick=False, private=True)
        except Character.DoesNotExist:
            irc.reply("Character does not exist.", private=True)

    describe = wrap(describe, ['anything'])

    ##########################################
    # Blood Pool Controls
    ##########################################

    def getbp(self, irc, msg, args):
        nick = str.capitalize(msg.nick)
        try:
            with db.atomic():
                q = Character.get(Character.name == nick)
                message = "Character Blood Pool: {0}/{1}".format(str(q.bp_cur), str(q.bp))
            irc.reply(message, prefixNick=False, private=True)
        except Character.DoesNotExist:
            irc.reply("Character Not Found.", private=True)

    getbp = wrap(getbp)

    def bp(self, irc, msg, args, bpnum, reason):
        nick = str.capitalize(msg.nick)
        currentChannel, bot = msg.args[0], 'CAINE'

        if currentChannel == bot:
            irc.reply("You must be in a channel")
        else:
            if not bpnum:
                bpnum = 1

            try:
                with db.atomic():
                    q = Character.get(Character.name == nick)
                    if bpnum >= q.bp_cur:
                        irc.reply(ircutils.mircColor("Not enough blood available."), prefixNick=False, private=True)
                    else:
                        bpnew = q.bp_cur - bpnum
                        Character.update(bp_cur=bpnew).where(Character.name == nick).execute()
                        q = Character.select().where(Character.name == nick).get()
                        message = ircutils.mircColor("Blood spent. Blood Remaining: {0}/{1}".format(
                            str(q.bp_cur), str(q.bp)), 4)
                        irc.reply(message, prefixNick=False, private=True)
            except Character.DoesNotExist:
                irc.reply("Character Not Found.", private=True)

    bp = wrap(bp, [optional('int'), optional('text')])

    def setbp(self, irc, msg, args, name, newbp):
        try:
            with db.atomic():
                q = Character.get(Character.name == name)
                if newbp > q.bp:
                    newbp = q.bp
                Character.update(bp_cur=newbp).where(Character.name == name).execute()
            irc.reply("Blood pool set.")
        except Character.DoesNotExist:
            irc.reply("Character Not Found.", private=True)

    setbp = wrap(setbp, ['anything', 'int'])

    def getcharbp(self, irc, msg, args, name):
        name = str.capitalize(name)
        try:
            with db.atomic():
                q = Character.get(Character.name == name)
                message = "Character Blood Pool: " + str(q.bp_cur) + '/' + str(q.bp)
            irc.reply(message, prefixNick=False, private=True)
        except Character.DoesNotExist:
            irc.reply("Character Not Found.", private=True)

    getcharbp = wrap(getcharbp, ['anything'])

    ##########################################
    # Feeding Controls
    ##########################################

    # Need to add check for feeding to check for botch
    # if botch:
    # Cannot feed until botch is resolved.

    def feed(self, irc, msg, args, num, difficulty, extra):
        """<no. of dice> <difficulty> <additional information>
        See: http://cainite.org/the-game/feeding/ for any questions.
        """
        name = str.capitalize(msg.nick)
        success = ones = 0
        fancy_outcome = []

        try:

            for s in range(num):
                die = randint(1, 10)
                if die >= difficulty:  # success evaluation, no specs when you feed
                    success += 1
                    fancy_outcome.append(ircutils.mircColor(die, 12))
                elif die == 1:  # maths for ones
                    ones += 1
                    fancy_outcome.append(ircutils.mircColor(die, 4))
                else:
                    fancy_outcome.append(ircutils.mircColor(die, 6))

            total = success - ones

            if success == 0 and ones > 0:
                if extra:
                    command = 'feeding: base(' + str(num) + ') at difficulty(' + str(difficulty) + ') - ' + extra
                else:
                    command = 'feeding: base(' + str(num) + ') at difficulty(' + str(difficulty) + ')'

                with db.atomic():
                    Botch.create(name=name, command=command)
                    Character.update(fed_already=datetime.date.today()).where(Character.name == name).execute()
                total = "BOTCH  >:D"
                dicepool = 'You fed: {0} ({1}) {2} dice @diff {3}'.format(" ".join(fancy_outcome), total,
                                                                          str(num),
                                                                          str(difficulty))
                irc.reply(dicepool, private=True)

            elif 0 <= success <= ones:
                with db.atomic():
                    Character.get(Character.name == name)
                    Character.update(fed_already=datetime.date.today()).where(Character.name == name).execute()
                total = "Failure"
                dicepool = 'You fed: {0} ({1}) {2} dice @diff {3}'.format(" ".join(fancy_outcome), total,
                                                                          str(num),
                                                                          str(difficulty))
                irc.reply(dicepool, private=True)

            elif total == 1:
                with db.atomic():
                    q = Character.get(Character.name == name)
                    bpcur, bpmax = int(q.bp_cur), int(q.bp)
                    bptest = bpmax - bpcur
                    if bptest <= 3:
                        Character.update(fed_already=datetime.date.today(),
                                         bp_cur=bpmax).where(Character.name == name).execute()
                    else:
                        bpcur += 3
                        Character.update(fed_already=datetime.date.today(),
                                         bp_cur=bpcur).where(Character.name == name).execute()
                    total = "Gained 3 bp"
                    dicepool = 'You fed: {0} ({1}) {2} dice @diff {3}'.format(" ".join(fancy_outcome), total,
                                                                              str(num),
                                                                              str(difficulty))
                irc.reply(dicepool, private=True)

            elif total >= 3:
                with db.atomic():
                    q = Character.get(Character.name == name)
                    bpcur, bpmax = int(q.bp_cur), int(q.bp)
                    bptest = bpmax - bpcur
                    if bptest <= 6:
                        Character.update(fed_already=datetime.date.today(),
                                         bp_cur=bpmax).where(Character.name == name).execute()
                    else:
                        bpcur += 6
                        Character.update(fed_already=datetime.date.today(),
                                         bp_cur=bpcur).where(Character.name == name).execute()
                    total = "Gained 6 bp"
                    dicepool = 'You fed: {0} ({1}) {2} dice @diff {3}'.format(" ".join(fancy_outcome), total,
                                                                              str(num),
                                                                              str(difficulty))
                    irc.reply(dicepool, private=True)

        except DoesNotExist:
            irc.reply("Character not found.", prefixNick=False)
        except IntegrityError:
            irc.reply("Character not found.", prefixNick=False)

    feed = wrap(feed, ['int', 'int', optional('text')])

    ##############
    # CREATE E_FEED FUNCTION
    #
    #
    # #########################################

    ##########################################
    # Willpower Controls
    ##########################################

    def getwp(self, irc, msg, args):
        nick = str.capitalize(msg.nick)
        try:
            with db.atomic():
                q = Character.get(Character.name == nick)
                message = "Character Willpower: {0}/{1}".format(str(q.wp_cur), str(q.wp))
            irc.reply(message, prefixNick=False, private=True)
        except Character.DoesNotExist:
            irc.reply("Character Not Found.", private=True)

    getwp = wrap(getwp)

    # Should record willpower spends into a new database. One-to-Many relationship to character name.
    # Nightly job should query this and only free spends that are older than 7 days.

    def wp(self, irc, msg, args, wpnum, reason):
        """<number if more than one> <reason>
        """
        nick = str.capitalize(msg.nick)
        currentChannel, bot = msg.args[0], 'CAINE'

        if currentChannel == bot:
            irc.reply("You must be in a channel")
        else:
            if not wpnum:
                wpnum = 1
            try:
                with db.atomic():
                    q = Character.get(Character.name == nick)
                    if wpnum >= q.wp_cur:
                        irc.reply(ircutils.mircColor("Not enough willpower available."), prefixNick=False, private=True)
                    else:
                        wpnew = q.wp_cur - wpnum
                        Character.update(wp_cur=wpnew).where(Character.name == nick).execute()
                        q = Character.select().where(Character.name == nick).get()
                        message = ircutils.mircColor("Willpower spent. Willpower Remaining: ".format(
                            str(q.wp_cur), str(q.wp)), 12)
                        irc.reply(message, prefixNick=False, private=True)
            except Character.DoesNotExist:
                irc.reply("Character Not Found.", private=True)

    wp = wrap(wp, [optional('int'), optional('text')])

    def setwp(self, irc, msg, args, name, newwp):
        """<name> <new willpower>
        if above max will set to max
        """
        try:
            with db.atomic():
                q = Character.get(Character.name == name)
                if newwp > q.wp:
                    newwp = q.wp
                Character.update(wp_cur=newwp).where(Character.name == name).execute()
            irc.reply("Willpower pool set.")
        except Character.DoesNotExist:
            irc.reply("Character Not Found.", private=True)

    setwp = wrap(setwp, ['anything', 'int'])

    def getcharwp(self, irc, msg, args, name):
        """<name>
        gets player's current willpower totals
        """
        name = str.capitalize(name)
        try:
            with db.atomic():
                q = Character.get(Character.name == name)
                message = "Character Willpower Pool: {0}/{1}".format(str(q.wp_cur), str(q.wp))
            irc.reply(message, prefixNick=False, private=True)
        except Character.DoesNotExist:
            irc.reply("Character Not Found.", private=True)

    getcharwp = wrap(getcharwp, ['anything'])

    ##########################################
    # Experience Controls
    ##########################################

    def getxp(self, irc, msg, args):
        nick = str.capitalize(msg.nick)
        try:
            with db.atomic():
                q = Character.get(Character.name == nick)
                message = "Current Experience: {0} | Total Experience: {1} | Requested Experience: {2}".format(
                    str(q.xp_cur), str(q.xp_total), str(q.xp_req))
            irc.reply(message, prefixNick=False, private=True)
        except Character.DoesNotExist:
            irc.reply("Character Not Found.", private=True)

    getxp = wrap(getxp)

    def getcharxp(self, irc, msg, args, name):
        """<name>
        gets current player's XP totals
        """
        nick = str.capitalize(name)
        try:
            with db.atomic():
                q = Character.get(Character.name == nick)
                message = "{0}: Current Experience: {1} | Total Experience: {2} | Requested Experience: {3}".format(
                    q.name, str(q.xp_cur), str(q.xp_total), str(q.xp_req))
            irc.reply(message, prefixNick=False, private=True)
        except Character.DoesNotExist:
            irc.reply("Character Not Found.", private=True)

    getcharxp = wrap(getcharxp, ['anything'])

    def givexp(self, irc, msg, args, name, num):
        """<name> <num>
        """
        nick = str.capitalize(name)

        try:
            with db.atomic():
                q = Character.get(Character.name == nick)
                bonus = q.xp_cur + num
                Character.update(xp_cur=bonus).where(Character.name == nick).execute()
                message = "Character {0} awarded {1} experience.".format(str(q.name), str(num))
            irc.reply(message)
        except Character.DoesNotExist:
            irc.reply("Character Not Found.", private=True)

    givexp = wrap(givexp, ['anything', 'int'])

    def spendxp(self, irc, msg, args, name, xpnum, reason):
        """<name> <num> <reason>
        """
        name = str.capitalize(name)
        st = str.capitalize(msg.nick)

        try:
            with db.atomic():
                q = Character.get(Character.name == name)
                if xpnum > q.xp_cur:
                    irc.reply(ircutils.mircColor("Not enough experience available."), prefixNick=False, private=True)
                else:
                    newCurrent, newSpent, newTotal = q.xp_cur - xpnum, q.xp_spent + xpnum, q.xp_total + xpnum
                    Character.update(xp_cur=newCurrent, xp_spent=newSpent, xp_total=newTotal).where(
                        Character.name == name).execute()
                    XPlog.create(
                        name=name,
                        st=st,
                        amount=xpnum,
                        reason=reason)
                    irc.reply("Experience successfully spent.")
        except Character.DoesNotExist:
            irc.reply("Character Not Found.", private=True)

    spendxp = wrap(spendxp, ['anything', 'int', 'text'])

    def requestxp(self, irc, msg, args, amount):
        """<num>
        See: http://cainite.org/the-game/experience/ for more help.
        """
        name = str.capitalize(msg.nick)

        try:
            with db.atomic():
                if amount < 1 or amount > 3:
                    irc.reply("You must request between 1 and 3 experience.")
                else:
                    Character.update(xp_req=amount).where(Character.name == name).execute()
                    message = "Requested {0} experience for the week.".format(str(amount))
                    irc.reply(message, private=True)
        except Character.DoesNotExist:
            irc.reply("Character Not Found.", private=True)

    requestxp = wrap(requestxp, ['int'])

    def requestlist(self, irc, msg, args):
        """requests returns of all those that submitted XP requests for the week.
        """
        try:
            with db.atomic():
                for request in Character.select():
                    if request.xp_req > 0:
                        message = '{0} requested {1} experience for the week.'.format(request.name, str(request.xp_req))
                        irc.reply(message)
        except Character.DoesNotExist:
            irc.reply("Error with database.", private=True)

    requestlist = wrap(requestlist)

    def modifylist(self, irc, msg, args, command, name, amount):
        """<command (remove|add|change)> <name> <amount (used for add|change)>
        """
        name = str.capitalize(name)
        try:
            with db.atomic():
                if command == 'remove':
                    Character.update(xp_req=0).where(Character.name == name).execute()
                    created = "{0} removed from requestxp list.".format(name)
                    irc.reply(created, private=True)
                elif command == 'add':
                    Character.update(xp_req=amount).where(Character.name == name).execute()
                    created = "{0} added with {1} XP requested.".format(name, str(amount))
                    irc.reply(created, private=True)
                elif command == 'change':
                    Character.update(xp_req=amount).where(Character.name == name).execute()
                    created = "{0} changed to {1} XP requested.".format(name, str(amount))
                    irc.reply(created, private=True)
                else:
                    irc.reply("Error: Please use commands: remove, add or change")
        except Character.DoesNotExist:
            irc.reply("Character Not Found.", private=True)

    modifylist = wrap(modifylist, ['anything', 'anything', optional('int')])

    def approvelist(self, irc, msg, args):
        try:
            with db.atomic():
                for request in Character.select():
                    if request.xp_req > 0:
                        add = request.xp_req + request.xp_cur
                        Character.update(xp_cur=add, xp_req=0).where(Character.name == request.name).execute()
            irc.reply("Experience List updated.")
        except Character.DoesNotExist:
            irc.reply("Error with database..", private=True)

    approvelist = wrap(approvelist)

    def charlog(self, irc, msg, args, name):
        name = str.capitalize(name)
        name = Character.get(Character.name == name)
        try:
            with db.atomic():
                for spend in name.spends:
                    message = "Storyteller: {0} | Date: {1} | Reason: {2}".format(
                        name.name, spend.st, spend.date, spend.reason)
                    irc.reply(message)
        except XPlog.DoesNotExist:
            irc.reply("No Log Found.", private=True)

    charlog = wrap(charlog, ['admin', 'anything'])

    ##########################################
    # Damage Controls
    ##########################################

    def _damage(self, name):
        try:
            with db.atomic():
                q = Character.get(Character.name == name)
                agg, norm = q.dmg_agg, q.dmg_norm
                response = name + " " + str(agg) + " Agg | " + str(norm) + " Norm"
                if agg + norm == 0:
                    response += " * UNDAMAGED"
                elif agg + norm == 1:
                    response += " * BRUISED (0 Dice Penalty)"
                elif agg + norm == 2:
                    response += " * HURT (-1 Dice Penalty)"
                elif agg + norm == 3:
                    response += " * INJURED (-1 Dice Penalty)"
                elif agg + norm == 4:
                    response += " * WOUNDED (-2 Dice Penalty)"
                elif agg + norm == 5:
                    response += " * MAULED (-2 Dice Penalty)"
                elif agg + norm == 6:
                    response += " * CRIPPLED (-5 Dice Penalty)"
                elif agg + norm == 7:
                    response += " * INCAPACITATED"
                elif norm == 8:
                    response += " * TORPORED"
                elif agg == 8:
                    response += " * FINAL DEATH"
            return response

        except DoesNotExist:
            response = "Character Not Found."
            return response

    def getdmg(self, irc, msg, args):
        """check your current damage
        """
        name = str.capitalize(msg.nick)
        try:
            response = self._damage(name)
            irc.reply(response, private=True)
        finally:
            pass

    getdmg = wrap(getdmg)

    def getchardmg(self, irc, msg, args, name):
        """<name>
        check a player's current damage
        """
        try:
            response = self._damage(name)
            irc.reply(response)
        finally:
            pass

    getchardmg = wrap(getchardmg, ['anything'])

    def givedmg(self, irc, msg, args, name, amount, dmgtype):
        """<name> <amount> <type>
        Give players damage. Use agg or norm for type.
        """
        try:
            with db.atomic():
                q = Character.get(Character.name == name)
                if dmgtype.lower() == 'norm':
                    dmg = q.dmg_norm + amount
                    Character.update(dmg_norm=dmg).where(Character.name == name).execute()
                elif dmgtype.lower() == 'agg':
                    dmg = q.dmg_agg + amount
                    Character.update(dmg_agg=dmg).where(Character.name == name).execute()
                else:
                    irc.reply("Damage command incorrectly entered.")
        finally:
            pass

        response = self._damage(name)
        irc.reply(response, private=True)

    givedmg = wrap(givedmg, ['anything', 'int', 'anything'])

    def heal(self, irc, msg, args, amount, dmgtype):
        """<amount> <damage type (norm|agg)>
        """
        name = str.capitalize(msg.nick)
        currentChannel = msg.args[0]
        bot = '#stchambers'

        if currentChannel != bot:
            irc.reply("You must be in in #stchambers to heal.")
        else:
            try:
                with db.atomic():
                    q = Character.get(Character.name == name)
                    if q.dmg_agg or q.dmg_norm <= 0:
                        Character.update(dmg_norm=0, dmg_agg=0).where(Character.name == name).execute()
                        irc.reply("You have no damage to heal.")
                    else:
                        if dmgtype.lower() is 'norm' or 'agg':
                            if dmgtype.lower() == 'norm':
                                newbp = q.bp_cur - amount
                                if newbp > 0:
                                    Character.update(bp_cur=newbp, dmg_norm=Character.dmg_norm-amount).where(
                                        Character.name == name).execute()
                                    created = "{0} {1} damage healed for {2} blood.".format(amount, dmgtype, amount)
                                    irc.reply(created)
                                else:
                                    irc.reply("Not enough blood available to heal", private=True)
                            elif dmgtype.lower() == 'agg':
                                amountbp = amount * 5
                                newbp = q.bp_cur - amountbp
                                if newbp > 0:
                                    Character.update(bp_cur=newbp, dmg_agg=Character.dmg_agg-amount).where(
                                        Character.name == name).execute()
                                    created = "{0} {1} damage healed for {2} blood.".format(amount, dmgtype, amountbp)
                                    irc.reply(created)
                                else:
                                    irc.reply("Not enough blood available to heal", private=True)
                        else:
                            irc.reply("Damage command entered incorrectly.")
            except DoesNotExist:
                irc.reply("Character Not Found.", private=True)

    heal = wrap(heal, ['int', 'anything'])

    ##########################################
    # Storyteller Controls
    ##########################################

    def npc(self, irc, msg, args, name, npc):
        name = str.capitalize(name)
        try:
            with db.atomic():
                if npc is 1:
                    Character.update(isnpc=True).where(Character.name == name).execute()
                    irc.reply("Character has been set as NPC.")
                elif npc is 0:
                    Character.update(isnpc=False).where(Character.name == name).execute()
                    irc.reply("Character has been set as PC.")
        except DoesNotExist:
            irc.reply("Character Not Found.", private=True)

    npc = wrap(npc, ['anything', 'int'])

    def nightly(self, irc, msg, args):
        try:
            with db.atomic():
                Character.update(bp_cur=Character.bp_cur - 1).where(Character.isnpc == 0).execute()

                #willpower regen

                #efeed regen

        finally:
            pass

    nightly = wrap(nightly)

    # def weekly(self, irc, msg, args):
    #
    # weekly = wrap(weekly)

Class = Management


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
