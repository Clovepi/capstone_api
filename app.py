from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS

import os

app = Flask(__name__)
CORS(app)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    product_image = db.Column(db.String, unique=True)

    def __init__(self, title, description, price, product_image):
        self.title = title
        self.description = description
        self.price = price
        self.product_image = product_image

class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'description', 'price', 'product_image')

product_schema = ProductSchema()
multi_product_schema = ProductSchema(many=True)

@app.route('/product/add', methods=["POST"])
def add_product():
    if request.content_type != 'application/json':
        return jsonify('error: data must be sent as json')
    post_data = request.get_json()
    title = post_data.get('title')
    description = post_data.get('description')
    price = post_data.get('price')
    product_image = post_data.get('product_image')

    # if title == None:
    #     return jsonify('error: must have a title')

    # if description == None:
    #     return jsonify('error: must have a description')

    new_record = Product(title, description, price, product_image)
    db.session.add(new_record)
    db.session.commit()
    return jsonify(product_schema.dump(new_record))

@app.route('/product/add/multi', methods=["POST"])
def add_multiple_products():
    if request.content_type != 'application/json':
        return jsonify('error: data must be sent as json')
    post_data = request.get_json()
    data = post_data.get("data")

    new_records = []

    for product in data:
        title = product.get('title')
        description = product.get('description')
        price = product.get('price')
        product_image = product.get('product_image')
    
        new_record = Product(title, description, price, product_image)
        db.session.add(new_record)
        db.session.commit()
        new_records.append(new_record)
        
    return jsonify(multi_product_schema.dump(new_records))

@app.route('/product/get', methods=['GET'])
def get_all_products():
    all_products = db.session.query(Product).all()
    return jsonify(multi_product_schema.dump(all_products))

@app.route('/product/get/<id>', methods=['GET'])
def get_one_product(id):
    one_product = db.session.query(Product).filter(Product.id == id).first()
    return jsonify(product_schema.dump(one_product))

@app.route('/product/delete/<id>', methods=['DELETE'])
def product_delete(id):
    delete_product = db.session.query(Product).filter(Product.id == id).first()
    db.session.delete(delete_product)
    db.session.commit()
    return jsonify("This product has been deleted.")
    
@app.route('/product/update/<id>', methods=['PUT'])
def update_product(id):
    if request.content_type != 'application/json':
        return jsonify('error: data must be sent as json')
    put_data = request.get_json()
    title = put_data.get('title')
    description = put_data.get('description')
    price = put_data.get('price')
    product_image = put_data.get('product_image')
    product_to_update = db.session.query(Product).filter(Product.id == id).first()
    if title != None:
        product_to_update.title = title
    if description != None:
        product_to_update.description = description
    if price != None:
        product_to_update.price = price
    if product_image != None:
        product_to_update.product_image = product_image
    db.session.commit()
    return jsonify(product_schema.dump(product_to_update))


if __name__ == '__main__':
    app.run(debug=True)