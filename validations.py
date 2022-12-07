from datetime import datetime, timedelta
from models import *
from marshmallow import ValidationError


def make_datatime(start, hours):
    return start + timedelta(hours=hours)


def is_time_overlaping(start, end, other_start, other_end):
    return end > other_start and start < other_end


def validate_order_time(auditorium_id, reservation_start, hours_ordered):

    orders = Session.query(Order).filter(Order.auditorium_id == auditorium_id).all()
    reservation_end = make_datatime(reservation_start, hours_ordered)

    for order in orders:
        other_reservation_start = order.reservation_start
        other_reservation_end = make_datatime(other_reservation_start, order.hours_ordered)

        if is_time_overlaping(reservation_start, reservation_end, other_reservation_start, other_reservation_end):
            raise ValidationError("Time is reserved")


def validate_email(email):
    if not (Session.query(User).filter(User.email == email).count() == 0):
        raise ValidationError("Email already taken")


def validate_hours_ordered(hours_ordered):
    if hours_ordered < 1 or hours_ordered > 5*24:
        raise ValidationError("Invalid data")


def validate_role(role):
    if role not in ['admin', 'user']:
        raise ValidationError("Invalid role")


def validate_price_per_hour(price_per_hour):
    if price_per_hour < 0:
        raise ValidationError("Invalid data")


def validate_seats(seats):
    if seats < 0:
        raise ValidationError("Invalid data")


def validate_reservation_start(reservation_start):
    if datetime.now() > reservation_start:
        raise ValidationError("Future events only")
