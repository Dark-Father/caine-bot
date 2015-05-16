from peewee import *
import datetime

db = MySQLDatabase('cainitebot', host="192.168.1.6", user='cainitebot', passwd='cainitebot')


class BaseModel(Model):
    class Meta:
        database = db


class Character(BaseModel):
    id = PrimaryKeyField()
    name = CharField(unique=True)
    created = DateField(default=datetime.date.today())
    bp = IntegerField(default=0)
    bp_cur = IntegerField(default=0)
    ebp = IntegerField(default=0)
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


class XPlog(BaseModel):
    id = ForeignKeyField(Character)
    name = CharField(default='')
    date = DateField(default=datetime.date.today())
    st = CharField(default='')
    amount = IntegerField(default=0)
    reason = TextField(default='')


class Botch(BaseModel):
    id = ForeignKeyField(Character)
    name = CharField(default='')
    date = DateTimeField(default=datetime.datetime.now)
    command = TextField(default='')


##############################
# Database Model Controls
##############################
# db.connect()
# db.drop_tables([XPlog], cascade=True)
# db.drop_tables([Character], cascade=True)
XPlog.drop_table()
Botch.drop_table()
Character.drop_table()

Character.create_table()
XPlog.create_table()
Botch.create_table()

# test data


def create(name, bp, wp):

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

#create some data
create(name="Abel", bp="1", wp="1")
create(name="Caine", bp=99, wp=99)
create(name="Mike", bp=12, wp=12)
create(name="Gabe", bp=13, wp=7)
create(name="Lucifer", bp=15, wp=10)