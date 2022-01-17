"""
Usage:
    docker-compose up # Terminal 1
    # On terminal 2
    # Change DATABASE_URL hostname and port to access from host to:
    # DATABASE_URL=postgresql://ofisino:ofisino@localhost:54320/ofisino
    FLASK_APP=app.shell flask shell
"""
from app.api import create_app
import app.persistence.models as m
from app.persistence.session import get_session


app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'m': m, 's': get_session()}
