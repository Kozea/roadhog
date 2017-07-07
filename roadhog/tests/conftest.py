import json

import pytest
from flask.testing import FlaskClient

from roadhog import roadhog


class HTTPClient(FlaskClient):
    def open(self, *args, **kwargs):
        json_data = kwargs.pop('json', '')
        if json_data:
            kwargs.setdefault('data', json.dumps(json_data))
            kwargs.setdefault('content_type', 'application/json')
        response = super(HTTPClient, self).open(*args, **kwargs)
        if response.content_type == 'application/json':
            rv = json.loads(response.data.decode('utf-8'))
        else:
            rv = {'html': response.data.decode('utf-8')}
        return response.status_code, rv


@pytest.yield_fixture(scope='function')
def app():
    app_roadhog = roadhog.Roadhog(__name__)
    app_roadhog.config.from_envvar('TESTING_SETTINGS')
    app_roadhog.initialize()
    app_roadhog.test_client_class = HTTPClient
    app_roadhog.init_db()
    return app_roadhog


@pytest.fixture
def http(app):
    return app.test_client()


@pytest.yield_fixture(scope='function')
def db_session(app):
    return app.create_session()


@pytest.fixture(scope='function')
def json_content():
    return {
        'object_kind': 'build',
        'ref': 'phoenix_2223',
        'build_id': 21339678,
        'build_name': 'deploy_test',
        'build_status': 'success',
        'build_started_at': '2017-07-06 13:39:16 UTC',
        'build_finished_at': '2017-07-06 13:43:56 UTC',
        'project_id': 1320772,
        'commit': {
            'id': 9632758,
        },
        'repository': {
            'name': 'hydra',
            'description': 'Serpent-like water monster with reptilian traits',
            'homepage': 'https://gitlab.com/Kozea/hydra',
        }
    }


@pytest.fixture(scope='function')
def json_headers():
    return {
        'Content-Type': 'application/json',
        'X-Gitlab-Token': 'token',
    }
