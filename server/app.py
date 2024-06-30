#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request,make_response
from flask_restful import Api
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/restaurants")
def get_restaurants():
    restaurants = Restaurant.query.all()
    return make_response([restaurant.to_dict(rules=('-restaurant_pizzas',)) for restaurant in restaurants], 200)

    
@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant is None:
        return make_response({"error": "Restaurant not found"},404)
    return make_response(restaurant.to_dict(),200)
    

@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    return make_response([pizza.to_dict(rules=('-restaurant_pizzas',)) for pizza in pizzas],200)


@app.route("/pizzas/<int:id>", methods=["GET"])
def get_pizza(id):
    pizza = Pizza.query.get(id)
    if pizza is None:
        return make_response({"error": "Pizza not found"},404)
    return make_response(pizza.to_dict(),200)


@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant is None:
        return make_response({"error": "Restaurant not found"},404)
    
    # Delete associated RestaurantPizzas first
    RestaurantPizza.query.filter_by(restaurant_id=restaurant.id).delete()
    db.session.delete(restaurant)
    db.session.commit()
    return make_response({"message": "Restaurant deleted"},204)


@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()
    try:
        restaurant_pizza = RestaurantPizza(
                price=data["price"],
                restaurant_id=data["restaurant_id"],
                pizza_id=data["pizza_id"]
            )
        db.session.add(restaurant_pizza)
        db.session.commit()

        return make_response(restaurant_pizza.to_dict(),201)
    except ValueError:
        return make_response({"errors": ["validation errors"]},400)
    
if __name__ == "__main__":
    app.run(port=5555, debug=True)
