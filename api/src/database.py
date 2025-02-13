import os

from peewee import *


def database():
    return SqliteDatabase(os.getcwd() + '/new_jig.db')


db = database()


class BaseModel(Model):
    class Meta:
        database = db


class Jig(BaseModel):
    id = PrimaryKeyField()
    jig_id = CharField(unique=True)
    model = CharField()
    lock_state = IntegerField(null=0)
    door_state = IntegerField(null=0)
    jig_state = IntegerField(null=0)
    last_topic = CharField()
    MAC_address = CharField()
    device_type = CharField(default="lock")


class DeviceSupportTopic(BaseModel):
    id = PrimaryKeyField()
    model = CharField()
    device_type = CharField()
    support_topic = CharField()


class LockAndDoorSteps(BaseModel):
    id = PrimaryKeyField()
    model = CharField()
    door_closed_steps = IntegerField(null=0)
    door_ajar_steps = IntegerField(null=0)
    door_open_steps = IntegerField(null=0)
    lock_fully_lock_steps = IntegerField(null=0)
    lock_lock_steps = IntegerField(null=0)
    lock_just_lock_steps = IntegerField(null=0)
    lock_just_unlock_steps = IntegerField(null=0)
    lock_unlock_steps = IntegerField(null=0)
    lock_fully_unlock_steps = IntegerField(null=0)


def initialize_database():
    db.connect()
    db.create_tables([LockAndDoorSteps, Jig, DeviceSupportTopic], safe=True)


def add_jig(jig_id, model, MAC_address):
    jig = Jig(jig_id=jig_id,
              model=model,
              lock_state='0',
              door_state='0',
              jig_state='0',
              last_topic='lock/close',
              MAC_address=MAC_address,
              device_type='lock')
    jig.save()


def add_support_topic(model, support_topic_value):
    add_topic = DeviceSupportTopic(model=model,
                                   device_type='lock',
                                   support_topic=support_topic_value)
    add_topic.save()


def add_steps(model, door_closed_steps, door_ajar_steps, door_open_steps, lock_fully_lock_steps
              , lock_lock_steps, lock_just_lock_steps, lock_just_unlock_steps, lock_unlock_steps
              , lock_fully_unlock_steps):
    steps = LockAndDoorSteps(model=model,
                             door_closed_steps=door_closed_steps,
                             door_ajar_steps=door_ajar_steps,
                             door_open_steps=door_open_steps,
                             lock_fully_lock_steps=lock_fully_lock_steps,
                             lock_lock_steps=lock_lock_steps,
                             lock_just_lock_steps=lock_just_lock_steps,
                             lock_just_unlock_steps=lock_just_unlock_steps,
                             lock_unlock_steps=lock_unlock_steps,
                             lock_fully_unlock_steps=lock_fully_unlock_steps)
    steps.save()


if __name__ == '__main__':
    initialize_database()
    # add_support_topic('terra_scan01', 'lock/open')
    add_jig('jig01', 'forma_scan01', '1b:3e:ee:we:e3')
    add_steps('forma_scan01', '4000', '4350', '4800', '5273', '4950', '4688', '3504', '3559', '3328')

    for jig in Jig.select():
        print(jig.jig_id, jig.model, jig.lock_state)

    for steps in LockAndDoorSteps.select():
        print(steps.model, steps.door_closed_steps)
