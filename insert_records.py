from models import *

session = Session

user1 = User(user_id=1, name="Volodymyr", surname="Shymanskyi",
             email="Volodymyr.Shymanskyi@email.nulp", password="1", role="user")
user2 = User(user_id=2, name="Natalya", surname="Shakhovska",
             email="Natalya.Shakhovska@email.nulp", password="1", role="user")

session.add(user1)
session.add(user2)
session.commit()


auditorium1 = Auditorium(auditorium_id=1, seats=1000, adress="Shevchenka st, 1", price_per_hour=10.2)
auditorium2 = Auditorium(auditorium_id=2, seats=250, adress="Bandery st, 2", price_per_hour=20.2)

session.add(auditorium1)
session.add(auditorium2)
session.commit()

order1 = Order(order_id=1, user_id=1, auditorium_id=1, reservation_start="2023-01-01 10:10:10", hours_ordered=2)
order2 = Order(order_id=2, user_id=2, auditorium_id=2, reservation_start="2023-01-02 10:10:10", hours_ordered=1)

session.add(order1)
session.add(order2)
session.commit()

session.close()
