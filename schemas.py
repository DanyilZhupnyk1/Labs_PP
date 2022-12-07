from flask_bcrypt import generate_password_hash
from marshmallow import Schema, fields
from validations import *


class AuditoriumToCreate(Schema):
    seats = fields.Integer(validate=validate_seats)
    address = fields.String()
    price_per_hour = fields.Decimal(validate=validate_price_per_hour)


class AuditoriumInfo(Schema):
    auditorium_id = fields.Integer()
    seats = fields.Integer()
    address = fields.String()
    price_per_hour = fields.Decimal()


class AuditoriumToUpdate(Schema):
    price_per_hour = fields.Decimal(validate=validate_price_per_hour)


class UserToCreate(Schema):
    name = fields.String()
    surname = fields.String()
    email = fields.Email(validate=validate_email)
    password = fields.Function(
        deserialize=lambda obj: generate_password_hash(obj), load_only=True
    )
    role = fields.String(validate=validate_role)


class UserInfo(Schema):
    user_id = fields.Integer()
    name = fields.String()
    surname = fields.String()
    email = fields.Email()
    role = fields.String()


class UserToUpdate(Schema):
    name = fields.String()
    surname = fields.String()
    password = fields.Function(
        deserialize=lambda obj: generate_password_hash(obj), load_only=True
    )


class OrderToCreate(Schema):
    user_id = fields.Integer()
    auditorium_id = fields.Integer()
    reservation_start = fields.DateTime(validate=validate_reservation_start)  # todo: add validation for events to be only in future
    hours_ordered = fields.Integer(validate=validate_hours_ordered)


class OrderInfo(Schema):
    order_id = fields.Integer()
    user_id = fields.Integer()
    auditorium_id = fields.Integer()
    reservation_start = fields.DateTime()
    hours_ordered = fields.Integer()


class OrderToUpdate(Schema):
    auditorium_id = fields.Integer()
    reservation_start = fields.DateTime(validate=validate_reservation_start)
    hours_ordered = fields.Integer(validate=validate_hours_ordered)
