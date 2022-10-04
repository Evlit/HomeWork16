# Домашка 16
import json
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)


# Описание моделей таблиц базы данных
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text(200))
    last_name = db.Column(db.Text(200))
    age = db.Column(db.Integer)
    email = db.Column(db.Text(200))
    role = db.Column(db.Text(200))
    phone = db.Column(db.Text(200))


class Order(db.Model):
    __tablename__ = "order"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(200))
    description = db.Column(db.Text(200))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.Text(200))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    customer = db.relationship("User", foreign_keys=[customer_id])
    executor = db.relationship("User", foreign_keys=[executor_id])


class Offer(db.Model):
    __tablename__ = "offer"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User")
    order = db.relationship("Order")


db.create_all()
session = db.session()


# Функции
def add_user():
    """
    Заполнение таблицы пользователей
    """
    with open("users.json", 'r', encoding='utf-8') as file:
        dict_data = json.load(file)
        for data in dict_data:
            user = User(id=data['id'], first_name=data['first_name'], last_name=data['last_name'],
                        age=data['age'], email=data['email'], role=data['role'], phone=data['phone'])
            db.session.add(user)
        db.session.commit()


def add_order():
    """
    Заполнение таблицы ордеров
    """
    with open("orders.json", 'r', encoding='utf-8') as file:
        dict_data = json.load(file)
        for data in dict_data:
            order = Order(id=data['id'], name=data['name'], description=data['description'],
                          start_date=datetime.strptime(data['start_date'], "%m/%d/%Y"),
                          end_date=datetime.strptime(data['end_date'], "%m/%d/%Y"), address=data['address'],
                          price=data['price'], customer_id=data['customer_id'], executor_id=data['executor_id'])
            db.session.add(order)
        db.session.commit()


def add_offer():
    """
    Заполнение таблицы предложений
    """
    with open("offers.json", 'r', encoding='utf-8') as file:
        dict_data = json.load(file)
        for data in dict_data:
            offer = Offer(id=data['id'], order_id=data['order_id'], executor_id=data['executor_id'])
            db.session.add(offer)
        db.session.commit()


def user_to_dict(instance):
    """
    Вывод в словарь записи таблицы пользователей
    """
    return {
        "id": instance.id,
        "first_name": instance.first_name,
        "last_name": instance.last_name,
        "age": instance.age,
        "email": instance.email,
        "role": instance.role,
        "phone": instance.phone,
    }


def order_to_dict(instance):
    """
    Вывод в словарь записи таблицы ордеров
    """
    return {
        "id": instance.id,
        "name": instance.name,
        "description": instance.description,
        "start_date": instance.start_date,
        "end_date": instance.end_date,
        "address": instance.address,
        "price": instance.price,
        "customer_id": instance.customer_id,
        "executor_id": instance.executor_id,
    }


def offer_to_dict(instance):
    """
    Вывод в словарь записи таблицы предложений
    """
    return {
        "id": instance.id,
        "order_id": instance.order_id,
        "executor_id": instance.executor_id,
    }


# Заполнение таблиц
add_user()
add_order()
add_offer()


@app.route("/users", methods=(['GET', 'POST']))
def get_users():
    """
    Получение списка всех пользователей
    или добавление нового в зависимости от метода
    """
    if request.method == 'GET':
        result = []
        users = User.query.all()
        for user in users:
            result.append(user_to_dict(user))
        return jsonify(result)
    if request.method == 'POST':
        data = request.json
        user = User(
            id=data.get('id'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            age=data.get('age'),
            email=data.get('email'),
            phone=data.get('phone')
        )
        db.session.add(user)
        db.session.commit()
        return jsonify(user_to_dict(user))


@app.route("/users/<int:uid>", methods=(['GET', 'PUT', 'DELETE']))
def get_one_user(uid):
    """
    Получение, обновление или удаление пользователя
    в зависимости от метода
    """
    users = User.query.get(uid)
    if users is None:
        return "<h1>Нет записи с таким номером</h1>"
    else:
        if request.method == 'GET':
            return jsonify(user_to_dict(users))
        if request.method == 'DELETE':
            db.session.delete(users)
            db.session.commit()
            return "<h1>Запись удалена</h1>"
        if request.method == 'PUT':
            data = request.json
            users.id = data.get('id')
            users.first_name = data.get('first_name')
            users.last_name = data.get('last_name')
            users.age = data.get('age')
            users.email = data.get('email')
            users.phone = data.get('phone')
            db.session.commit()
            return "<h1>Запись обновлена</h1>"


@app.route("/orders", methods=(['GET', 'POST']))
def get_orders():
    """
    Получение списка всех ордеров
    или добавление нового в зависимости от метода
    """
    if request.method == 'GET':
        result = []
        orders = Order.query.all()
        for order in orders:
            result.append(order_to_dict(order))
        return jsonify(result)
    if request.method == 'POST':
        data = request.json
        order = Order(**data)
        db.session.add(order)
        db.session.commit()
        return jsonify(order_to_dict(order))


@app.route("/orders/<int:uid>", methods=(['GET', 'PUT', 'DELETE']))
def get_one_order(uid):
    """
    Получение, обновление или удаление ордера
    в зависимости от метода
    """
    orders = Order.query.get(uid)
    if orders is None:
        return "<h1>Нет записи с таким номером</h1>"
    else:
        if request.method == 'GET':
            return jsonify(order_to_dict(orders))
        if request.method == 'DELETE':
            db.session.delete(orders)
            db.session.commit()
            return "<h1>Запись удалена</h1>"
        if request.method == 'PUT':
            data = request.json
            orders.id = data.get('id')
            orders.name = data.get('name')
            orders.description = data.get('description')
            orders.start_date = data.get('start_date')
            orders.end_date = data.get('end_date')
            orders.address = data.get('address')
            orders.price = data.get('price')
            orders.customer_id = data.get('customer_id')
            orders.executor_id = data.get('executor_id')
            db.session.commit()
            return "<h1>Запись обновлена</h1>"


@app.route("/offers", methods=(['GET', 'POST']))
def get_offers():
    """
    Получение списка всех предложений
    или добавление нового в зависимости от метода
    """
    if request.method == 'GET':
        result = []
        offers = Offer.query.all()
        for offer in offers:
            result.append(offer_to_dict(offer))
        return jsonify(result)
    if request.method == 'POST':
        data = request.json
        offer = Offer(**data)
        db.session.add(offer)
        db.session.commit()
        return jsonify(offer_to_dict(offer))


@app.route("/offers/<int:uid>", methods=(['GET', 'PUT', 'DELETE']))
def get_one_offer(uid):
    """
    Получение, обновление или удаление предложения
    в зависимости от метода
    """
    offers = Offer.query.get(uid)
    if offers is None:
        return "<h1>Нет записи с таким номером</h1>"
    else:
        if request.method == 'GET':
            return jsonify(offer_to_dict(offers))
        if request.method == 'DELETE':
            db.session.delete(offers)
            db.session.commit()
            return "<h1>Запись удалена</h1>"
        if request.method == 'PUT':
            data = request.json
            offers.id = data.get('id')
            offers.order_id = data.get('order_id')
            offers.executor_id = data.get('executor_id')
            db.session.commit()
            return "<h1>Запись обновлена</h1>"


if __name__ == '__main__':
    app.run()
