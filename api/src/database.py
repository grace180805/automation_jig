from peewee import *


def database():
    return SqliteDatabase('/Users/yozhan/my new/terra_forma_jig.db')


db = database()


class BaseModel(Model):
    class Meta:
        database = db


class LockAndDoorAngle(BaseModel):
    id = PrimaryKeyField()
    device_type = CharField()
    door_closed_angle = IntegerField(null=0)
    door_ajar_angle = IntegerField(null=0)
    door_open_angle = IntegerField(null=0)
    lock_fully_lock_angle = IntegerField(null=0)
    lock_lock_angle = IntegerField(null=0)
    lock_just_lock_angle = IntegerField(null=0)
    lock_just_unlock_angle = IntegerField(null=0)
    lock_unlock_angle = IntegerField(null=0)
    lock_fully_unlock_angle = IntegerField(null=0)


class LockJig(BaseModel):
    id = PrimaryKeyField()
    jig_id = CharField(unique=True)
    lock_type = CharField()
    lock_state = IntegerField(null=0)
    door_state = IntegerField(null=0)
    last_topic = CharField()
    MAC_address = CharField()
    device_type = CharField(default="lock")


class DeviceSupportTopic(BaseModel):
    id = PrimaryKeyField()
    lock_id = CharField(default="default", unique=True)
    angle = IntegerField(null=45)
    hold_time_of_register = FloatField(null=3.0)
    hold_time_of_operation = FloatField(null=2.0)


def initialize_database():
    db = database()
    db.connect()
    db.create_tables([LockJig,
                      ], safe=True)


def add_jig():
    lock = LockJig(jig_id='jig01',
                   lock_type='scan01', lock_state=0,
                   door_state=0, last_topic='lock/close',
                   MAC_address='01:as:2w',
                   device_type='lock')
    lock.save()


if __name__ == '__main__':
    initialize_database()
    # add_jig()
    device_list = []
    # for dev in LockJig.select():
    #     device_list.append(dev.jig_id)
    print(LockJig.select())
