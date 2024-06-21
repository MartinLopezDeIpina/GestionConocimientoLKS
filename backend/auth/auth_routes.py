import requests
from flask import Blueprint, jsonify, request

from auth.AuthError import AuthError
from auth.auth import requires_auth
from config import Config
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity


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

    """
        check here if user exists in database, if not, add him
    """

    jwt_token = create_access_token(identity=user_info['email'])  # create jwt token
    response = jsonify(user=user_info)
    response.set_cookie('access_token_cookie', value=jwt_token, secure=True)

    return response, 200


# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@auth_blueprint.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    jwt_token = request.cookies.get('access_token_cookie')  # Demonstration how to get the cookie
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@auth_blueprint.route('/login')
def llm_test():
    return 'login'


@auth_blueprint.route("/user")
@requires_auth
def user_view():
    """
    Endpoint Usuario, solo puede ser accedido por un usuario autorizado
    """
    return jsonify(msg="Hello user!")


@auth_blueprint.route("/admin")
@requires_auth
def admin_view():
    """
    Endpoint Admin, solo puede ser accedido por un admin
    """
    return jsonify(msg="Hello admin!")


@auth_blueprint.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response





