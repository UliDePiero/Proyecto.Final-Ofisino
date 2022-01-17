from flask import Response, request, abort, Blueprint, make_response
from flask_login import (
    LoginManager,
    login_required,
    login_user,
    logout_user,
    current_user,
)

from app.blueprints.helpers import ok
from app.persistence.models import User
from app.persistence.session import get_session


bp = Blueprint('login2', __name__)
login_manager = LoginManager()
login_manager.login_view = "login2.login"


@login_manager.user_loader
def load_user(userid):
    return get_session().query(User).get(userid)


@bp.route('/free')
def free():
    return Response(f"Free World! Authed? {current_user.is_authenticated}")


@bp.route('/locked')
@login_required
def locked():
    return Response(f"Protected World! Authed? {current_user.is_authenticated}")


@bp.route("/login", methods=["POST"])
def login():
    user_from_db = None
    S = get_session()

    args = request.get_json(force=True, silent=True)
    if not args:
        abort(make_response({'status': 400, 'error': 'Bad Request, missing user json body'}, 400))

    if args.get('domain_id') is not None:
        user_from_db = S.query(User).filter_by(domain_id=args['domain_id']).filter(
            User.deleted_at.is_(None)
        ).one_or_none()
    if not user_from_db:
        """Cuando invitas a una reunion a un usuario que nunca se logeo, 
        crea el usuario pero sin domain_id. Entonces cuando te logeas lo unico que le actualizas 
        es el domain_id y el avatar. Se modifican estos campos en vez de borrar y hacer uno nuevo 
        o tener 2 usuarios, para mantener el id que se uso en otro momento para ese usuario, 
        sino podrias tener ids perdidos o un usuario con varios id"""
        user_from_db = S.query(User).filter_by(email=args['email']).filter(
            User.deleted_at.is_(None)
        ).one_or_none()
        if user_from_db:
            if args['domain_id'] is not None:
                user_from_db.domain_id = args['domain_id']
                user_from_db.name = args['name']
                user_from_db.avatar_url = args.get('avatar_url')
                S.commit()
        else:
            user_from_db = User(
                domain_id=args['domain_id'],
                name=args['name'],
                email=args['email'],
                avatar_url=args.get('avatar_url')
            )
            S.add(user_from_db)
            S.commit()
    else:
        user_from_db.avatar_url = args.get('avatar_url')
        S.commit()

    assert login_user(user_from_db), "User not logged in. Is it active?"

    return ok({'data': user_from_db.to_dict()})


# somewhere to logout
@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return Response("Logged out")
