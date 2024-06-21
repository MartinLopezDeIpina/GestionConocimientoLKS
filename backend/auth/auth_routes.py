
from flask import Blueprint, jsonify, request

from auth.AuthError import AuthError
from auth.auth import requires_auth

auth_blueprint = Blueprint('auth', __name__)


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





