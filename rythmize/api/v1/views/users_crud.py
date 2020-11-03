"""
User  CRUD views

"""
import flask_praetorian
from flask import jsonify, request
from rythmize.api.v1.views import api_views
from ....models.user import User


@api_views.route('auth/user/current', methods=['GET'])
@flask_praetorian.auth_required
def user_details():
    """
    Gets user details like username email
    Returns:
        200, details or 401
    """
    user_id = flask_praetorian.current_user().id
    if user := User.query.get(user_id):
        details = {
            "username": user.username,
            "email": user.email
        }
        return jsonify(details), 200
    return 404
