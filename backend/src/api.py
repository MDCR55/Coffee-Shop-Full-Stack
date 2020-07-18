import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()


# ROUTES


@app.route('/drinks', methods=['GET'])
def get_drinks(*args, **kwargs):
    '''
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
    '''
    try:
        drinks = list(map(Drink.short, Drink.query.all()))
        return jsonify({
            "success": True,
            "drinks": drinks
        })
    except:
        abort(500)


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(*args, **kwargs):
    '''
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
    '''
    try:
        drinks = list(map(Drink.long, Drink.query.all()))
        return jsonify({
            "success": True,
            "drinks": drinks
        })
    except:
        abort(500)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink():
    '''
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
    '''
    try:
        data = request.get_json()
        title = data.get('title', None)
        recipe = data.get('recipe', None)

        drink_to_post = Drink(title=title, recipe=json.dumps(recipe))
        drink_to_post.insert()

        return jsonify({
            "success": True,
            'drinks': drink_to_post.long()
        })
    except Exception:
        abort(422)


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(*args, **kwargs):
    '''
   PATCH /drinks/<id>
       where <id> is the existing model id
       it should respond with a 404 error if <id> is not found
       it should update the corresponding row for <id>
       it should require the 'patch:drinks' permission
       it should contain the drink.long() data representation
   returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
       or appropriate status code indicating reason for failure
   '''
    drink_id = kwargs.get("drink_id", None)
    if drink_id is None:
        abort(400)

    data = request.get_json()
    title = data.get('title', None)
    recipe = data.get('recipe', None)

    drink = Drink.query(drink_id)

    if drink is None:
        abort(404)  # drink not found
    if title is None:
        abort(400)

    try:
        drink.title = title
        drink.recipe = json.dumps(recipe)
        drink.update()
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        })
    except Exception:
        abort(422)


@app.route('/drinks/<int:id>', methods=['DELETE'])
def delete_drink(*args, **kwargs):
    '''
        DELETE /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should delete the corresponding row for <id>
            it should require the 'delete:drinks' permission
        returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
            or appropriate status code indicating reason for failure
    '''

    drink_id = kwargs.get("drink_id", None)
    if drink_id is None:
        abort(400)

    drink = Drink.query(drink_id)
    if drink is None:
        abort(404)
    try:
        drink.delete()
        return jsonify({
            "success": True,
            "delete": drink_id
        })
    except:
        abort(422)


# Error Handling
@app.errorhandler(422)
def unprocessable(error):
    try:
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable Entity"
        }), 422
    except:
        abort(500)


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource is not found"
    }), 404


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized Access"
    }), 401


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400
