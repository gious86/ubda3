from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


accessLevel_device = db.Table('accessLevel_device',
                                  db.Column('device_id', db.Integer, db.ForeignKey('device.id')),
                                  db.Column('access_level_id', db.Integer, db.ForeignKey('access_level.id'))
                                  )


accessLevel_output = db.Table('accessLevel_output',
                                  db.Column('output_id', db.Integer, db.ForeignKey('output.id')),
                                  db.Column('access_level_id', db.Integer, db.ForeignKey('access_level.id'))
                                  )


# accessLevel_person = db.Table('accessLevel_person',
#                                   db.Column('person_id', db.Integer, db.ForeignKey('person.id')),
#                                   db.Column('access_level_id', db.Integer, db.ForeignKey('access_level.id'))
#                                   )


# class Person(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     first_name = db.Column(db.String(50))
#     last_name = db.Column(db.String(50))
#     email = db.Column(db.String(50))
#     pin = db.Column(db.String(10), unique=True)
#     card_number = db.Column(db.Integer)
#     date_created = db.Column(db.DateTime(timezone=True), default=func.now())
#     department = db.Column(db.Integer, db.ForeignKey('department.id'))
#     created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
#     #access_levels = db.relationship('Access_level', secondary=accessLevel_person, back_populates='personnel'
#     access_level = db.Column(db.Integer, db.ForeignKey('access_level.id'))
#     valid_thru = db.Column(db.DateTime(timezone=True))
#     log = db.relationship('Access_log')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    card_number = db.Column(db.Integer)
    department = db.Column(db.Integer, db.ForeignKey('department.id'))
    access_level = db.Column(db.Integer, db.ForeignKey('access_level.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_users = db.relationship('User')
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    valid_thru = db.Column(db.DateTime(timezone=True))
    role = db.Column(db.Integer, db.ForeignKey('user_role.id'))
    access_log = db.relationship('Access_log')


class User_role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(50))
    users = db.relationship('User')

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(50))
    personnel = db.relationship('User')


class Access_level(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.String(50))
    devices = db.relationship('Device', secondary=accessLevel_device, back_populates='access_levels')
    outputs = db.relationship('Output', secondary=accessLevel_output, back_populates='access_levels')
    users = db.relationship('User') #, secondary=accessLevel_person, back_populates='access_levels')
    

class Time_zone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    start = db.Column(db.Time(timezone=True))
    end = db.Column(db.Time(timezone=True))


class Holyday(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    start = db.Column(db.Time(timezone=True))
    end = db.Column(db.Time(timezone=True))


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    model = db.Column(db.String(50))
    ip_address = db.Column(db.String(50))
    outputs = db.relationship('Output', cascade="all, delete")
    mac = db.Column(db.String(50))
    last_seen = db.Column(db.Integer)
    access_levels = db.relationship('Access_level', secondary=accessLevel_device, back_populates='devices')
    log = db.relationship('Access_log')


class Output(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    device = db.Column(db.Integer, db.ForeignKey('device.id'))
    n = db.Column(db.Integer)
    access_levels = db.relationship('Access_level', secondary=accessLevel_output, back_populates='outputs')


class Access_log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200))
    device  = db.Column(db.Integer, db.ForeignKey('device.id'))
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    date_time = db.Column(db.DateTime(timezone=True), default=func.now())
