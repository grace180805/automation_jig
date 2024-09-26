from peewee import *


def database():
    return SqliteDatabase('/Users/yozhan/my new/new_jig.db')


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
    last_topic = CharField()
    MAC_address = CharField()
    device_type = CharField(default="lock")


class DeviceSupportTopic(BaseModel):
    id = PrimaryKeyField()
    model = CharField()
    device_type = CharField()
    support_topic = CharField()


class LockAndDoorAngle(BaseModel):
    id = PrimaryKeyField()
    model = CharField()
    door_closed_angle = IntegerField(null=0)
    door_ajar_angle = IntegerField(null=0)
    door_open_angle = IntegerField(null=0)
    lock_fully_lock_angle = IntegerField(null=0)
    lock_lock_angle = IntegerField(null=0)
    lock_just_lock_angle = IntegerField(null=0)
    lock_just_unlock_angle = IntegerField(null=0)
    lock_unlock_angle = IntegerField(null=0)
    lock_fully_unlock_angle = IntegerField(null=0)


def initialize_database():
    db.connect()
    db.create_tables([LockAndDoorAngle, Jig, DeviceSupportTopic], safe=True)


def add_jig(jig_id, model, MAC_address):
    jig = Jig(jig_id=jig_id,
              model=model,
              lock_state=2,
              door_state=2,
              last_topic='lock/close',
              MAC_address=MAC_address,
              device_type='lock')
    jig.save()


def add_support_topic(model, support_topic):
    support_topic = DeviceSupportTopic(model=model,
                                       device_type='lock',
                                       support_topic=support_topic)
    support_topic.save()


def add_angle(model, door_closed_angle, door_ajar_angle, door_open_angle, lock_fully_lock_angle
              , lock_lock_angle, lock_just_lock_angle, lock_just_unlock_angle, lock_unlock_angle
              , lock_fully_unlock_angle):
    angle = Jig(model=model,
                door_closed_angle=door_closed_angle,
                door_ajar_angle=door_ajar_angle,
                door_open_angle=door_open_angle,
                lock_fully_lock_angle=lock_fully_lock_angle,
                lock_lock_angle=lock_lock_angle,
                lock_just_lock_angle=lock_just_lock_angle,
                lock_just_unlock_angle=lock_just_unlock_angle,
                lock_unlock_angle=lock_unlock_angle,
                lock_fully_unlock_angle=lock_fully_unlock_angle)
    angle.save()


if __name__ == '__main__':
    initialize_database()
    # add_support_topic('terra_scan01', 'lock/open')

    # 遍历并打印每条记录
    for support_topic in DeviceSupportTopic.select():
        print(support_topic.model, support_topic.support_topic)
