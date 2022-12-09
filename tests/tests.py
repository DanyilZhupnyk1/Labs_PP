from flask_testing import TestCase
from unittest.mock import ANY
from app import *
import base64
from models import *
from flask import request, url_for
from flask_bcrypt import generate_password_hash
from datetime import datetime


class BaseTest(TestCase):
    def setUp(self):
        super().setUp()
        self.create_tables()

        self.admin_data = {
            "name": "Volodymyr",
            "surname": "Shymanskyi",
            "email": "Volodymyr.Shymanskyi@email.com",
            "password": generate_password_hash('1'),
            "role": "admin"
        }

        self.user_wrong_email = {
            "name": "Volodymyr",
            "surname": "Shymanskyi",
            "email": "Volodymyr.Shymanskyi@email",
            "password": "1",
            "role": "admin"
        }

        self.user_wrong_role = {
            "name": "Volodymyr",
            "surname": "Shymanskyi",
            "email": "Volodymyr.Shymanskyi@email.com",
            "password": "1",
            "role": "adm"
        }

        self.user_succes = {
            "name": "Volodymyr",
            "surname": "Shymanskyi",
            "email": "Volodymyr.Shymanskyi@email.com",
            "password": "1",
            "role": "user"
        }

        self.user_succes_put = {
            "name": "Volodymyr",
            "surname": "Shymanskyi",
            "password": "2",
        }

        self.user_bad_put = {
            "name": 123,
            "surname": "Shymanskyi",
            "password": "2",
        }

        self.user_succes_get = {
            "name": "Volodymyr",
            "surname": "Shymanskyi",
            "email": "Volodymyr.Shymanskyi@email.com",
            "password": generate_password_hash('1'),
            "role": "user"
        }

        self.user2_succes_get = {
            "name": "Volodymyr",
            "surname": "Shymanskyi",
            "email": "Volodya.Shymanskyi@email.com",
            "password": generate_password_hash('1'),
            "role": "user"
        }

        self.auditorium_post_succes = {
            "seats": 55,
            "address": "Shevchenka st, 1",
            "price_per_hour": 10.2
        }

        self.order1_post_succes = {
            "user_id": 1,
            "auditorium_id": 1,
            "reservation_start": "2023-01-01 10:10:10",
            "hours_ordered": 2
        }

        self.order1_put_succes = {
            "auditorium_id": 1,
            "reservation_start": "2030-01-01 10:10:10",
            "hours_ordered": 3
        }

        self.order2_post_overlap = {
            "user_id": 1,
            "auditorium_id": 1,
            "reservation_start": "2023-01-01 10:10:10",
            "hours_ordered": 2
        }

        self.auditorium_put_succes = {
            "price_per_hour": 11.2
        }

    def tearDown(self):
        self.close_session()

    def create_tables(self):
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    def close_session(self):
        Session().close()

    def create_app(self):
        # app.config['TESTING'] = True
        return app


########################################################################
# USER
class TestPostUser(BaseTest):

    def test_post_user_succes(self):
        r = self.client.post('/user', json=self.user_succes)

        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json, {
            'name': self.user_succes['name'],
            'surname': self.user_succes['surname'],
            'email': self.user_succes['email'],
            'role': self.user_succes['role'],
        })

    def test_post_user_wrong_email(self):

        r = self.client.post(
            url_for('create_user'),
            json=self.user_wrong_email
        )

        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.data, b"{'email': ['Not a valid email address.']}")

    def test_post_user_wrong_role(self):

        r = self.client.post('/user', json=self.user_wrong_role)

        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.data, b"{'role': ['Invalid role']}")

    def test_email_already_exist(self):
        db_utils.create_entry(User, **self.user_succes)
        r = self.client.post(
            url_for('create_user'),
            json=self.user_succes
        )

        self.assertEqual(r.status_code, 400)

class TestPutUser(BaseTest):
    def test_put_user_succes(self):
        db_utils.create_entry(User, **self.user_succes_get)
        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        r = self.client.put(
            url_for('upd_user', user_id=1),
            json=self.user_succes_put,
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(r.status_code, 200)

    def test_put_user_not_found(self):
        db_utils.create_entry(User, **self.user_succes_get)
        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        r = self.client.put(
            url_for('upd_user', user_id=100),
            json=self.user_succes_put,
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(r.status_code, 404)

    def test_put_user_bad_auth(self):
        db_utils.create_entry(User, **self.user_succes_get)
        bad_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:2").decode("utf-8")

        r = self.client.put(
            url_for('upd_user', user_id=1),
            json=self.user_succes_put,
            headers={"Authorization": "Basic " + bad_credentials}
        )

        self.assertEqual(r.status_code, 401)
        self.assertEqual(r.data, b'Unauthorized Access')

    def test_put_user_unathorized_acces(self):
        db_utils.create_entry(User, **self.user_succes_get)
        db_utils.create_entry(User, **self.user2_succes_get)

        user1_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        r = self.client.put(
            url_for('get_user', user_id=2),
            headers={"Authorization": "Basic " + user1_credentials},
            json=self.user_succes_put
        )

        self.assertEqual(401, r.status_code)

    def test_put_validation_error(self):
        db_utils.create_entry(User, **self.user_succes_get)
        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        r = self.client.put(
            url_for('upd_user', user_id=100),
            json=self.user_bad_put,
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(r.status_code, 400)


class TestGetUser(BaseTest):
    def test_get_user_succes(self):
        db_utils.create_entry(User, **self.user_succes_get)
        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        r = self.client.get(
            url_for('get_user', user_id=1),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json, {
            'name': self.user_succes['name'],
            'surname': self.user_succes['surname'],
            'email': self.user_succes['email'],
            'role': self.user_succes['role'],
        })

    def test_get_user_bad_auth(self):
        db_utils.create_entry(User, **self.user_succes_get)
        bad_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:2").decode("utf-8")

        r = self.client.get(
            url_for('get_user', user_id=1),
            headers={"Authorization": "Basic " + bad_credentials}
        )

        self.assertEqual(r.status_code, 401)
        self.assertEqual(r.data, b'Unauthorized Access')

    def test_get_user_not_found(self):
        db_utils.create_entry(User, **self.user_succes_get)
        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")
        r = self.client.get(
            url_for('get_user', user_id=100),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(404, r.status_code)

    def test_user_unathorized_acces(self):
        db_utils.create_entry(User, **self.user_succes_get)
        db_utils.create_entry(User, **self.user2_succes_get)

        user1_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        r = self.client.get(
            url_for('get_user', user_id=2),
            headers={"Authorization": "Basic " + user1_credentials}
        )

        self.assertEqual(401, r.status_code)


class TestDeleteUser(BaseTest):
    def test_delete_user_succes(self):
        db_utils.create_entry(User, **self.user_succes_get)
        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        r = self.client.delete(
            url_for('delete_user', user_id=1),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(r.status_code, 200)

    def test_delete_user_not_found(self):
        db_utils.create_entry(User, **self.user_succes_get)
        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")
        r = self.client.delete(
            url_for('delete_user', user_id=100),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(404, r.status_code)

    def test_user_unathorized_acces(self):
        db_utils.create_entry(User, **self.user_succes_get)
        db_utils.create_entry(User, **self.user2_succes_get)

        user1_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        r = self.client.delete(
            url_for('delete_user', user_id=2),
            headers={"Authorization": "Basic " + user1_credentials}
        )

        self.assertEqual(401, r.status_code)


class TestUserOrders(BaseTest):
    def test_get_users_orders_succes(self):
        db_utils.create_entry(User, **self.user_succes_get)
        db_utils.create_entry(Auditorium, **self.auditorium_post_succes)
        db_utils.create_entry(Order, **self.order1_post_succes)

        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        r = self.client.get(
            url_for('get_user_orders', user_id=1),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(r.status_code, 200)

    def test_get_users_orders_wrong_user(self):
        db_utils.create_entry(User, **self.user_succes_get)
        db_utils.create_entry(Auditorium, **self.auditorium_post_succes)
        db_utils.create_entry(Order, **self.order1_post_succes)

        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        r = self.client.get(
            url_for('get_user_orders', user_id=404),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(r.status_code, 404)

    def test_get_users_orders_with_none_orders(self):
        db_utils.create_entry(User, **self.user_succes_get)
        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        r = self.client.get(
            url_for('get_user_orders', user_id=1),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(r.status_code, 404)

    def test_user_unathorized_acces(self):
        db_utils.create_entry(User, **self.user_succes_get)
        db_utils.create_entry(User, **self.user2_succes_get)
        db_utils.create_entry(Auditorium, **self.auditorium_post_succes)
        db_utils.create_entry(Order, **self.order1_post_succes)

        user1_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        r = self.client.get(
            url_for('get_user', user_id=2),
            headers={"Authorization": "Basic " + user1_credentials}
        )

        self.assertEqual(401, r.status_code)



########################################################################
# Auditorium
class TestPostAuditorium(BaseTest):
    def test_create_auditorium_succes(self):
        db_utils.create_entry(User, **self.admin_data)
        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        r = self.client.post(
            url_for('create_auditorium'),
            json=self.auditorium_post_succes,
            headers={"Authorization": "Basic " + valid_credentials}
        )
        self.assertEqual(r.status_code, 200)

    def test_create_auditorium_wrong_seats(self):
        db_utils.create_entry(User, **self.admin_data)
        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        auditorium = self.auditorium_post_succes
        auditorium['seats'] = -13

        r = self.client.post(
            url_for('create_auditorium'),
            json=auditorium,
            headers={"Authorization": "Basic " + valid_credentials}
        )
        self.assertEqual(r.status_code, 400)

    def test_create_auditorium_wrong_price(self):
        db_utils.create_entry(User, **self.admin_data)
        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        auditorium = self.auditorium_post_succes
        auditorium['price_per_hour'] = -13.2

        r = self.client.post(
            url_for('create_auditorium'),
            json=auditorium,
            headers={"Authorization": "Basic " + valid_credentials}
        )
        self.assertEqual(r.status_code, 400)

    def test_create_auditorium_wrong_role(self):
        db_utils.create_entry(User, **self.user_succes_get)
        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        r = self.client.post(
            url_for('create_auditorium'),
            json=self.auditorium_post_succes,
            headers={"Authorization": "Basic " + valid_credentials}
        )
        self.assertEqual(r.status_code, 403)


class TestPutAuditorium(BaseTest):
    def test_put_auditorium_succes(self):
        db_utils.create_entry(User, **self.admin_data)
        db_utils.create_entry(Auditorium, **self.auditorium_post_succes)

        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        r = self.client.put(
            url_for('upd_auditorium', auditorium_id=1),
            json=self.auditorium_put_succes,
            headers={"Authorization": "Basic " + valid_credentials}
        )
        self.assertEqual(r.status_code, 200)

    def test_put_auditorium_wrong_price(self):
        db_utils.create_entry(User, **self.admin_data)
        db_utils.create_entry(Auditorium, **self.auditorium_post_succes)

        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        auditorium = self.auditorium_put_succes
        auditorium['price_per_hour'] = -13.2

        r = self.client.put(
            url_for('upd_auditorium', auditorium_id=1),
            json=auditorium,
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(r.status_code, 400)

    def test_put_auditorium_not_found(self):
        db_utils.create_entry(User, **self.admin_data)
        db_utils.create_entry(Auditorium, **self.auditorium_post_succes)

        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        r = self.client.put(
            url_for('upd_auditorium', auditorium_id=100),
            json=self.auditorium_put_succes,
            headers={"Authorization": "Basic " + valid_credentials}
        )
        self.assertEqual(r.status_code, 404)


class TestGetAuditorium(BaseTest):
    def test_get_auditorium_succes(self):
        db_utils.create_entry(User, **self.admin_data)
        db_utils.create_entry(Auditorium, **self.auditorium_post_succes)

        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        r = self.client.get(
            url_for('get_auditorium', auditorium_id=1),
            headers={"Authorization": "Basic " + valid_credentials}
        )
        self.assertEqual(r.status_code, 200)

    def test_get_auditorium_not_found(self):
        db_utils.create_entry(User, **self.admin_data)
        db_utils.create_entry(Auditorium, **self.auditorium_post_succes)

        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        r = self.client.get(
            url_for('get_auditorium', auditorium_id=100),
            headers={"Authorization": "Basic " + valid_credentials}
        )
        self.assertEqual(r.status_code, 404)


class TestDeleteAuditorium(BaseTest):
    def test_delete_auditorium_succes(self):
        db_utils.create_entry(User, **self.admin_data)
        db_utils.create_entry(Auditorium, **self.auditorium_post_succes)

        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        r = self.client.delete(
            url_for('delete_auditorium', auditorium_id=1),
            headers={"Authorization": "Basic " + valid_credentials}
        )
        self.assertEqual(r.status_code, 200)

    def test_delete_auditorium_not_found(self):
        db_utils.create_entry(User, **self.admin_data)
        db_utils.create_entry(Auditorium, **self.auditorium_post_succes)

        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        r = self.client.delete(
            url_for('delete_auditorium', auditorium_id=100),
            headers={"Authorization": "Basic " + valid_credentials}
        )
        self.assertEqual(r.status_code, 404)


########################################################################
# ORDER
class TestPostOrder(BaseTest):
    def test_create_order_succes(self):
        db_utils.create_entry(User, **self.admin_data)
        db_utils.create_entry(Auditorium, **self.auditorium_post_succes)

        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        r = self.client.post(
            url_for('create_order'),
            json=self.order1_post_succes,
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(r.status_code, 200)

    def test_wrong_hours(self):
        db_utils.create_entry(User, **self.admin_data)
        db_utils.create_entry(Auditorium, **self.auditorium_post_succes)

        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")
        order = self.order1_post_succes
        order['hours_ordered'] = -1

        r = self.client.post(
            url_for('create_order'),
            json=self.order1_post_succes,
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(r.status_code, 400)

    def test_pastime(self):
        db_utils.create_entry(User, **self.admin_data)
        db_utils.create_entry(Auditorium, **self.auditorium_post_succes)

        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")
        order = self.order1_post_succes
        order['reservation_start'] = "2020-01-01 10:10:10"

        r = self.client.post(
            url_for('create_order'),
            json=self.order1_post_succes,
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(r.status_code, 400)

    def test_integrity_erro(self):
        db_utils.create_entry(User, **self.admin_data)
        db_utils.create_entry(Auditorium, **self.auditorium_post_succes)

        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")
        order = self.order1_post_succes
        order['user_id'] = 100

        r = self.client.post(
            url_for('create_order'),
            json=self.order1_post_succes,
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(r.status_code, 401)

    def test_overlap(self):
        db_utils.create_entry(User, **self.admin_data)
        db_utils.create_entry(Auditorium, **self.auditorium_post_succes)
        db_utils.create_entry(Order, **self.order2_post_overlap)

        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        r = self.client.post(
            url_for('create_order'),
            json=self.order1_post_succes,
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(r.status_code, 400)


class TestPutOrder(BaseTest):
    def test_put_order_succes(self):
        db_utils.create_entry(User, **self.admin_data)
        db_utils.create_entry(Auditorium, **self.auditorium_post_succes)
        db_utils.create_entry(Order, **self.order1_post_succes)

        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        r = self.client.put(
            url_for('upd_order', order_id=1),
            json=self.order1_put_succes,
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(r.status_code, 200)

    def test_put_order_not_found(self):
        db_utils.create_entry(User, **self.admin_data)
        db_utils.create_entry(Auditorium, **self.auditorium_post_succes)
        db_utils.create_entry(Order, **self.order1_post_succes)

        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        r = self.client.put(
            url_for('upd_order', order_id=404),
            json=self.order1_put_succes,
            headers={"Authorization": "Basic " + valid_credentials}
        )
        print(r.data, r.json)
        self.assertEqual(r.status_code, 404)

    def test_put_order_wrong_hours(self):
        db_utils.create_entry(User, **self.admin_data)
        db_utils.create_entry(Auditorium, **self.auditorium_post_succes)
        db_utils.create_entry(Order, **self.order1_post_succes)

        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")
        order = self.order1_put_succes
        order['hours_ordered'] = 0

        r = self.client.put(
            url_for('upd_order', order_id=1),
            json=order,
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(r.status_code, 400)

    def test_integrity_error(self):
        db_utils.create_entry(User, **self.admin_data)
        db_utils.create_entry(Auditorium, **self.auditorium_post_succes)
        db_utils.create_entry(Order, **self.order1_post_succes)

        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        order = self.order1_put_succes
        order['auditorium_id'] = 402

        r = self.client.put(
            url_for('upd_order', order_id=1),
            json=order,
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(r.status_code, 402)

    # todo: make this test work
    def test_put_unathorized_acces(self):
        db_utils.create_entry(User, **self.user_succes_get)
        db_utils.create_entry(Auditorium, **self.auditorium_post_succes)
        db_utils.create_entry(Order, **self.order1_post_succes)
        db_utils.create_entry(User, **self.user2_succes_get)

        user2_credentials = base64.b64encode(b"Volodya.Shymanskyi@email.com:1").decode("utf-8")

        r = self.client.get(
            url_for('get_order', order_id=1),
            headers={"Authorization": "Basic " + user2_credentials},
            json=self.order1_put_succes
        )

        self.assertEqual(401, r.status_code)
        self.assertEqual(b'Unauthorized Access', r.data)


class TestGetOrder(BaseTest):
    def test_get_succes(self):
        db_utils.create_entry(User, **self.admin_data)
        db_utils.create_entry(Auditorium, **self.auditorium_post_succes)
        db_utils.create_entry(Order, **self.order1_post_succes)

        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        r = self.client.get(
            url_for('delete_order', order_id=1),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(r.status_code, 200)

    def test_get_not_found(self):
        db_utils.create_entry(User, **self.admin_data)
        db_utils.create_entry(Auditorium, **self.auditorium_post_succes)
        db_utils.create_entry(Order, **self.order1_post_succes)

        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        r = self.client.get(
            url_for('delete_order', order_id=404),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(r.status_code, 404)

    def test_get_unathorized_acces(self):
        db_utils.create_entry(User, **self.user_succes_get)
        db_utils.create_entry(Auditorium, **self.auditorium_post_succes)
        db_utils.create_entry(Order, **self.order1_post_succes)
        db_utils.create_entry(User, **self.user2_succes_get)

        user2_credentials = base64.b64encode(b"Volodya.Shymanskyi@email.com:1").decode("utf-8")

        r = self.client.get(
            url_for('get_order', order_id=1),
            headers={"Authorization": "Basic " + user2_credentials},
        )

        self.assertEqual(401, r.status_code)
        self.assertEqual(b'Unauthorized Access', r.data)



class TestDeleteOrder(BaseTest):
    def test_delete_succes(self):
        db_utils.create_entry(User, **self.admin_data)
        db_utils.create_entry(Auditorium, **self.auditorium_post_succes)
        db_utils.create_entry(Order, **self.order1_post_succes)

        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        r = self.client.delete(
            url_for('delete_order', order_id = 1),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(r.status_code, 200)

    def test_delete_not_found(self):
        db_utils.create_entry(User, **self.admin_data)
        db_utils.create_entry(Auditorium, **self.auditorium_post_succes)
        db_utils.create_entry(Order, **self.order1_post_succes)

        valid_credentials = base64.b64encode(b"Volodymyr.Shymanskyi@email.com:1").decode("utf-8")

        r = self.client.delete(
            url_for('delete_order', order_id = 404),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(r.status_code, 404)

    def test_delete_unathorized_acces(self):
        db_utils.create_entry(User, **self.user_succes_get)
        db_utils.create_entry(Auditorium, **self.auditorium_post_succes)
        db_utils.create_entry(Order, **self.order1_post_succes)
        db_utils.create_entry(User, **self.user2_succes_get)

        user2_credentials = base64.b64encode(b"Volodya.Shymanskyi@email.com:1").decode("utf-8")

        r = self.client.delete(
            url_for('delete_order', order_id=1),
            headers={"Authorization": "Basic " + user2_credentials},
        )

        self.assertEqual(401, r.status_code)


class TestRoot(BaseTest):
    def test_root(self):
        r = self.client.get(
            url_for('index')
        )

        self.assertEqual(200, r.status_code)
