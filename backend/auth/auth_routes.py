from datetime import timedelta

import requests
from flask import Blueprint, jsonify, request

import utils
from auth.AuthError import AuthError
from config import Config
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity

from database import db
from models import Usuario, ConocimientoUsuario, NodoArbol

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/google_login', methods=['POST'])
def login():
    auth_code = request.get_json()['code']

    data = {
        'code': auth_code,
        'client_id': Config.GOOGLE_CLIENT_ID,  # client ID from the credential at google developer console
        'client_secret': Config.GOOGLE_SECRET_KEY,  # client secret from the credential at google developer console
        'redirect_uri': 'postmessage',
        'grant_type': 'authorization_code'
    }

    response = requests.post('https://oauth2.googleapis.com/token', data=data).json()
    headers = {
        'Authorization': f'Bearer {response["access_token"]}'
    }
    user_info = requests.get('https://www.googleapis.com/oauth2/v3/userinfo', headers=headers).json()

    jwt_token = create_access_token(identity=user_info['email'], expires_delta=timedelta(hours=2))
    response = jsonify(user=user_info)
    response.set_cookie('access_token_cookie', value=jwt_token, httponly=True, secure=True)

    utils.create_user_if_not_exists(user_info['email'], user_info['name'])

    return response, 200


@auth_blueprint.route('/get_user_info/<email>', methods=['GET'])
@jwt_required()
def get_user_info(email):
    user = Usuario.query.filter_by(email=email).first()
    if user:
        return jsonify(name=user.nombre), 200
    return jsonify(message='User not found'), 404


# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@auth_blueprint.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    debug_request = request
    # Access the identity of the current user with get_jwt_identity
    jwt_token = request.cookies.get('access_token_cookie')  # Demonstration how to get the cookie
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@auth_blueprint.route('/logout', methods=['POST'])
def logout():
    response = jsonify({"message": "Logout successful"})
    response.delete_cookie('access_token_cookie')
    return response, 200


@auth_blueprint.route('/api_personal/get_user_email', methods=['GET'])
@jwt_required()
def get_user_email():
    print('get_user_email')
    jwt_token = request.cookies.get('access_token_cookie')
    current_user = get_jwt_identity()
    return jsonify(email=current_user), 200


@auth_blueprint.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response





