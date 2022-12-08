from models import *


def create_entry(model_class, *, commit=True, **kwargs):
    session = Session()
    entry = model_class(**kwargs)
    session.add(entry)
    if commit:
        session.commit()
    return entry


def get_entry_byid(model_class, uid, **kwargs):
    session = Session()
    return session.query(model_class).filter_by(id=uid, **kwargs).one()


def get_entries_byid(model_class, key, uid, **kwargs):
    session = Session()
    return session.query(model_class).filter(key == uid, **kwargs).all()


def update_entry(entry, *, commit=True, **kwargs):
    session = Session()
    for key, value in kwargs.items():
        setattr(entry, key, value)
    if commit:
        session.commit()
    else:
        return entry


def delete_entry(model_class, uid, *, commit=True, **kwargs):
    session = Session()
    session.query(model_class).filter_by(id=uid, **kwargs).delete()
    if commit:
        session.commit()