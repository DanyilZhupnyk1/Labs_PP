from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DATETIME, DECIMAL
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session

engine = create_engine('mysql://root:123456@localhost:3306/mydb')
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)
Base = declarative_base()


class User(Base):
    __tablename__ = "User"

    user_id = Column('user_id', Integer, primary_key=True)
    name = Column('name', String(45))
    surname = Column('surname', String(45))
    email = Column('email', String(45))
    password = Column('password', String(200))
    role = Column('role', String(45))


class Auditorium(Base):
    __tablename__ = "Auditorium"

    auditorium_id = Column('auditorium_id', Integer, primary_key=True)
    seats = Column('seats', Integer)
    adress = Column('adress', String(45))
    price_per_hour = Column('price_per_hour', DECIMAL(10, 2))


class Order(Base):
    __tablename__ = "Order"

    order_id = Column('order_id', Integer, primary_key=True)
    user_id = Column('user_id', ForeignKey(User.user_id))
    auditorium_id = Column('auditorium_id', ForeignKey(Auditorium.auditorium_id))
    reservation_start = Column('reservation_start', DATETIME)
    hours_ordered = Column('hours_ordered', Integer)
