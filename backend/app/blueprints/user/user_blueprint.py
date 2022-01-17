from flask import jsonify
from flask.views import MethodView
from flask_login import login_required
from flask_smorest import Blueprint
from loguru import logger

from app.blueprints.helpers import get_model_by_id, ok
from app.blueprints.user.schemas import (
    QueryInputGetUser,
    UserResponse,
    UserListResponse,
    UserSchema, QueryInputPostUser,
)
from app.persistence.models.user_model import User
from app.persistence.session import get_session

bp = Blueprint('User', __name__, description='Operations on user')


@bp.route('/user')
class UserAPI(MethodView):

    @login_required
    @bp.arguments(QueryInputGetUser, location='query')
    @bp.response(200, UserResponse())
    def get(self, args):
        """Get user by id"""
        user_id = args.get("id")
        if user_id is None:
            logger.info("Fetching all users")
            users = get_session().query(User).all()
            return ok(UserListResponse().dump({"data": UserSchema().dump(users, many=True)}))
        else:
            logger.info(f"Fetching box con id {user_id}.")
            user = get_model_by_id(user_id, User, "User")
            return ok(UserResponse().dump({"data": user}))

    @bp.arguments(QueryInputPostUser)
    @bp.response(200, UserResponse())
    def post(self, args):
        """Add new box"""
        logger.debug("Handling add user request")
        user = User(domain_id=args['domain_id'],
                    name=args['name'],
                    email=args['email'],
                    avatar_url=args['avatar_url'])
        if args.get('admin'):
            user.admin = args['admin']

        logger.info(f"Adding user {user}")
        get_session().add(user)
        get_session().commit()
        return ok(UserResponse().dump({"data": user}))

@bp.errorhandler(422)
@bp.errorhandler(400)
def handle_error(err):
    headers = err.data.get("headers", None)
    messages = err.data.get("messages", ["Invalid request."])
    if headers:
        return jsonify({"errors": messages}), err.code, headers
    else:
        return jsonify({"errors": messages}), err.code
