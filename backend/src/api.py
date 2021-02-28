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

@app.after_request
def after_request_func(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES

@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = [drink.short() for drink in Drink.query.all()]
    return jsonify({
        'success': True,
        'drinks': drinks
    })


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail():
    drinks = [drink.long() for drink in Drink.query.all()]
    return jsonify({
        'success': True,
        'drinks': drinks
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks():
    posted_json = request.get_json()

    title = posted_json.get('title', '')
    recipe = json.dumps(posted_json.get('recipe', ''))

    new_drink = Drink(title=title, recipe=recipe)
    new_drink.insert()

    drinks = [drink.long() for drink in Drink.query.all()]

    return jsonify({
        'success': True,
        'drinks': drinks
    })


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(id):
    posted_json = request.get_json()
    
    title = posted_json.get('title', None)
    recipe = json.dumps(posted_json.get('recipe', None))

    drink = Drink.query.get(id)

    if drink is None:
        abort(404)
    
    if title: drink.title = title
    if recipe: drink.recipe = recipe
    
    drink.update()

    drinks = [drink.long() for drink in Drink.query.all()]

    return jsonify({
        'success': True,
        'drinks': drinks
    })


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(id):
    drink = Drink.query.get(id)
    
    if drink is None:
        abort(404)
    
    drink.delete()
    
    return jsonify({
        'success': True,
        'id': id
    })


## Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "resource not found"
    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def auth_error(ex):
    return jsonify({
        'success': False,
        'error': ex.status_code,
        'message': ex.error['code']
    }), ex.status_code
