from flask import Flask, jsonify, request
from sqlalchemy import exc
from marshmallow import ValidationError
from waitress import serve
from models import *
from schemas import *
import db_utils
from validations import validate_order_time
from flask_httpauth import HTTPBasicAuth
from flask_bcrypt import check_password_hash

app = Flask(__name__)
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email, password):
    try:
        user = Session.query(User).filter_by(email=email).one()
        if check_password_hash(user.password, password):
            return email

    except exc.NoResultFound:
        return False


@auth.get_user_roles
def get_user_roles(email):
    try:
        user = Session.query(User).filter_by(email=email).one()
        return user.role
    except exc.NoResultFound:
        return ''


########################################################################
# Auditorium
@app.route('/auditorium', methods=["POST"])
@auth.login_required(role='admin')
def create_auditorium():
    try:
        new_auditorium = AuditoriumToCreate().load(request.json)
        added_auditorium = db_utils.create_entry(Auditorium, **new_auditorium)
        return jsonify(AuditoriumToCreate().dump(added_auditorium))
    # !! по якійсь причині не вертає айдішник запису, хз чого
    except ValidationError as err:
        return str(err), 400


@app.route('/auditorium/<int:auditorium_id>', methods=["PUT"])
@auth.login_required(role='admin')
def upd_auditorium(auditorium_id):
    """
    user only alowed to update price_per_hour
    """
    try:
        auditorium_data = AuditoriumToUpdate().load(request.json)
        auditorium = db_utils.get_entry_byid(Auditorium, auditorium_id)
        db_utils.update_entry(auditorium, **auditorium_data)
        return jsonify({"Succes": 200})

    except exc.NoResultFound:
        return jsonify({"Error": "not found"}), 404

    except ValidationError:
        return jsonify({"Error": "Invalid input"}), 400


@app.route('/auditorium/<int:auditorium_id>', methods=["GET"])
@auth.login_required(role='admin')
def get_auditorium(auditorium_id):
    try:
        auditorium = db_utils.get_entry_byid(Auditorium, auditorium_id)
        return jsonify(AuditoriumInfo().dump(auditorium)), 200

    except exc.NoResultFound:
        return jsonify({"Error": "not found"}), 404


@app.route('/auditorium/<int:auditorium_id>', methods=["DELETE"])
@auth.login_required(role='admin')
def delete_auditorium(auditorium_id):
    try:
        auditorium = db_utils.get_entry_byid(Auditorium, auditorium_id)
        db_utils.delete_entry(Auditorium, auditorium_id)
        return jsonify({"Succes": "unit deleted"}), 200
    except exc.NoResultFound:
        return jsonify({"Error": "not found"}), 404


########################################################################
# USER
@app.route('/user', methods=["POST"])
def create_user():
    try:
        new_user = UserToCreate().load(request.json)
        added_user = db_utils.create_entry(User, **new_user)
        return jsonify(UserToCreate().dump(added_user)), 200
    # !! по якійсь причині не вертає айдішник запису, хз чого
    except ValidationError as err:
        return str(err), 400


@app.route('/user/<int:user_id>', methods=["PUT"])
@auth.login_required()
def upd_user(user_id):
    try:
        user_data = UserToUpdate().load(request.json)
        user = db_utils.get_entry_byid(User, user_id)
        if auth.current_user() != user.email:
            return 'Unauthorized Access', 401
        db_utils.update_entry(user, **user_data)
        return jsonify({"Succes": 200})

    except exc.NoResultFound:
        return jsonify({"Error": "not found"}), 404

    except ValidationError:
        return jsonify({"Error": "Invalid input"}), 400


@app.route('/user/<int:user_id>', methods=["GET"])
@auth.login_required()
def get_user(user_id):
    try:
        user = db_utils.get_entry_byid(User, user_id)
        if auth.current_user() != user.email:
            return 'Unauthorized Access', 401

        return jsonify(UserInfo().dump(user)), 200

    except exc.NoResultFound:
        return jsonify({"Error": "not found"}), 404


@app.route('/user/<int:user_id>', methods=["DELETE"])
@auth.login_required()
def delete_user(user_id):
    try:
        user = db_utils.get_entry_byid(User, user_id)
        if auth.current_user() != user.email:
            return 'Unauthorized Access', 401
        db_utils.delete_entry(User, user_id)
        return jsonify({"Succes": "unit deleted"}), 200
    except exc.NoResultFound:
        return jsonify({"Error": "not found"}), 404


@app.route('/user/<int:user_id>/orders', methods=["GET"])
@auth.login_required()
def get_user_orders(user_id):
    try:
        user_orders = db_utils.get_entries_byid(Order, Order.user_id, user_id)
        user = db_utils.get_entry_byid(User, user_orders[0].user_id)
        if auth.current_user() != user.email:
            return 'Unauthorized Access', 401

        return jsonify(OrderInfo().dump(user_orders, many=True))
    except exc.NoResultFound:
        return jsonify({"Error": "not found"}), 404
    except IndexError:
        return jsonify({"Error": "not found"}), 404


########################################################################
# Order
@app.route('/order', methods=["POST"])
@auth.login_required()
def create_order():
    try:
        new_order = OrderToCreate().load(request.json)
        validate_order_time(new_order['auditorium_id'], new_order['reservation_start'], new_order['hours_ordered'])
        added_order = db_utils.create_entry(Order, **new_order)
        return jsonify(OrderToCreate().dump(added_order))
    # !! по якійсь причині не вертає айдішник запису, хз чого
    except ValidationError as err:
        return str(err), 400

    except exc.IntegrityError as err:
        return str(err), 401


@app.route('/order/<int:order_id>', methods=["PUT"])
@auth.login_required()
def upd_order(order_id):
    try:
        order_data = OrderToUpdate().load(request.json)
        validate_order_time(order_data['auditorium_id'], order_data['reservation_start'], order_data['hours_ordered'])
        order = db_utils.get_entry_byid(Order, order_id)
        user = db_utils.get_entry_byid(User, order.user_id)

        if auth.current_user() != user.email:
            return 'Uauthorized Access', 401

        db_utils.update_entry(order, **order_data)

        return jsonify({"Succes": "updated"})

    except exc.NoResultFound:
        return jsonify({"Error": "not found"}), 404

    except ValidationError as err:
        return str(err), 400

    except exc.IntegrityError as err:
        return str(err), 402


@app.route('/order/<int:order_id>', methods=["GET"])
@auth.login_required()
def get_order(order_id):
    try:
        order = db_utils.get_entry_byid(Order, order_id)
        user = db_utils.get_entry_byid(User, order.user_id)

        if auth.current_user() != user.email:
            return 'Unauthorized Access', 401

        return jsonify(OrderInfo().dump(order)), 200

    except exc.NoResultFound:
        return jsonify({"Error": "not found"}), 404


@app.route('/order/<int:order_id>', methods=["DELETE"])
@auth.login_required()
def delete_order(order_id):
    try:
        order = db_utils.get_entry_byid(Order, order_id)
        user = db_utils.get_entry_byid(User, order.user_id)

        if auth.current_user() != user.email:
            return 'Unauthorized Access', 401
        db_utils.delete_entry(Order, order_id)
        return jsonify({"Succes": "unit deleted"}), 200
    except exc.NoResultFound:
        return jsonify({"Error": "not found"}), 404


@app.route('/')
def index():
    return 'Hello, World 7', 200


if __name__ == '__main__':
    # serve(app, host='0.0.0.0', port=5010, threads=1, url_prefix="/api/v1/hello-world-7")
    app.run(debug=True)