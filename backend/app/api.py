from flask import Flask, current_app, request
from flask_login import current_user, login_required
from flask_smorest import Api
from redis import Redis
from rq import Queue
from rq.job import Job

from app.blueprints.box.box_blueprint import bp as box_blueprint
from app.blueprints.building.building_blueprint import bp as building_blueprint
from app.blueprints.calendar.calendar_api import bp as calendar_api_blueprint
from app.blueprints.data.data_blueprint import bp as data_blueprint
from app.blueprints.login.login_blueprint import bp as login_blueprint, login_manager
from app.blueprints.meeting.meeting_blueprint import bp as meeting_blueprint
from app.blueprints.meeting_request.meeting_request_blueprint import bp as meeting_request_blueprint
from app.blueprints.meeting_room.meeting_room_blueprint import bp as meeting_room_blueprint
from app.blueprints.organization.organization_blueprint import bp as organization_blueprint
from app.blueprints.reservation.reservation_blueprint import bp as reservation_blueprint
from app.blueprints.user.user_blueprint import bp as user_blueprint
from app.blueprints.working_space.working_space_blueprint import bp as working_space_blueprint
from app.persistence.models import User
from app.persistence.session import get_session
from app.task_queue.tasks import example


def create_app(config_cls='app.api_config.ProductionConfig'):
    app = Flask(__name__)

    app.config.from_object(config_cls)

    api = configure_api_documentation(app)
    register_blueprints(app, api)
    register_task_queue(app)
    register_extensions(app)
    register_dbsession_hooks(app)

    @app.route('/', methods=['GET'])
    def hello_world():
        return {
            'Hello': 'World'
        }

    @app.route('/whoami', methods=['GET'])
    def whoami():
        """Demo endpoint to show how to get info from current user"""
        me: User = current_user
        return {
            'authed': me.is_authenticated,
            'id': me.get_id()  # Can't to me.id because it fails if unathenticated. See AnonymousUserMixin
        }

    @app.route('/protected', methods=['GET'])
    @login_required
    def protected():
        """Demo endpoint to show how to get info from current user"""
        me: User = current_user
        assert me.is_authenticated  # Always true because of decorator
        return me.to_dict()         # Now will always work because it's never unauthenticated.

    @app.route('/task', methods=['GET'])
    def tasktest():
        seconds = request.args.get('seconds', 3)
        q: Queue = current_app.task_queue
        job: Job = q.enqueue(example, args=(seconds, ), kwargs={'test': 1})
        return {
            'id': job.id,
            'seconds': seconds,
            'status': 'Scheduled'
        }

    @app.route('/task/<task_id>', methods=['GET'])
    def task_status(task_id: str):
        q: Queue = current_app.task_queue
        job: Job = q.fetch_job(task_id)
        if not job:
            return {'error': f'Task {task_id} does not exist'}
        else:
            return {
                "task_id": job.get_id(),
                "task_status": job.get_status(),
                "task_result": job.result,
            }

    @app.route('/hello', methods=['GET'])
    def greeting():
        return {
            "greeting": "Ofisino to the world 🚀🚀🚀"
        }

    return app


def register_task_queue(app):
    """Bind attributes to app object to be accesible through current_app flask proxt"""
    app.task_queue = Queue(connection=Redis.from_url(app.config['REDIS_URL']))


def register_extensions(app):
    login_manager.init_app(app)


def configure_api_documentation(app):
    app.config['API_TITLE'] = 'Ofisino API'
    app.config['API_VERSION'] = 'v1'
    app.config['OPENAPI_VERSION'] = '3.0.2'
    api = Api(app, spec_kwargs={'host': 'http://localhost:8000'})
    return api


def register_blueprints(app, api):
    app.register_blueprint(login_blueprint)
    api.register_blueprint(user_blueprint)
    api.register_blueprint(reservation_blueprint)
    api.register_blueprint(calendar_api_blueprint)
    api.register_blueprint(meeting_blueprint)
    api.register_blueprint(meeting_request_blueprint)
    api.register_blueprint(meeting_room_blueprint)
    api.register_blueprint(organization_blueprint)
    api.register_blueprint(box_blueprint)
    api.register_blueprint(working_space_blueprint)
    api.register_blueprint(building_blueprint)
    api.register_blueprint(data_blueprint)


def register_dbsession_hooks(app):

    @app.before_request
    def bind_session():
        """Bind session into Flask's g object (g.session)"""
        get_session()

    @app.teardown_appcontext
    def shutdown_session(exception):
        s = get_session()
        if exception is None:
            s.commit()
        else:
            s.rollback()

        s.remove()
