import json
from os.path import dirname, join

import pytest
from alembic import command
from alembic.config import Config
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


@pytest.fixture
def http(app):
    return app.test_client()


@pytest.yield_fixture(scope='function')
def app():
    app_roadhog = roadhog.Roadhog(__name__)
    app_roadhog.config.from_pyfile('testing_settings.py')
    app_roadhog.initialize()
    app_roadhog.test_client_class = HTTPClient
    return app_roadhog


@pytest.yield_fixture(scope='function')
def db_session(app, alembic_config):
    session = app.create_session()
    yield session


@pytest.yield_fixture(scope='function')
def alembic_config(app):
    ini_location = join(dirname(__file__), '..', '..', 'alembic.ini')
    sqlalchemy_url = app.config['DB']
    config = Config(ini_location)
    config.set_main_option('sqlalchemy.url', sqlalchemy_url)
    command.upgrade(config, 'head')
    yield config
    command.downgrade(config, 'base')


@pytest.fixture(scope='function')
def json_content_push_hook():
    return {
        'object_kind': 'push',
        'event_name': 'push',
        'before': '1111aaaa',
        'after': '2222bbbb',
        'ref': 'refs/heads/phoenix_2223',
        'checkout_sha': '2222bbbb',
        'message': None,
        'project_id': 1320772,
        'project': {
            'name': 'hydra',
            'description': 'Serpent-like water monster with reptilian traits',
            'web_url': 'https://gitlab.com/Kozea/hydra',
        },
        'commits': [
            {
                'id': '1234abcd',
                'message': 'message',
                'timestamp': '2017-10-10T17:55:08+02:00',
                'url': 'https://gitlab.com/Kozea/hydra/commit/1324abcd',
                'author': {
                    'name': 'Juste LeBlanc',
                },
            },
            {
                'id': '5678efgh',
                'message': 'other message',
                'timestamp': '2017-10-11T14:27:47+02:00',
                'url': 'https://gitlab.com/Kozea/hydra/commit/5678efgh',
                'author': {
                    'name': 'Juste LeBlanc',
                },
            }
        ],
        'total_commits_count': 2,
        'repository': {
            'name': 'hydra',
            'description': 'Serpent-like water monster with reptilian traits',
            'homepage': 'https://gitlab.com/Kozea/hydra',
        }
    }


@pytest.fixture(scope='function')
def json_content_pipeline_hook():
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
            'sha': '1234abcd',
            'message': 'message',
            'author_name': 'Juste LeBlanc',
        },
        'repository': {
            'name': 'hydra',
            'description': 'Serpent-like water monster with reptilian traits',
            'homepage': 'https://gitlab.com/Kozea/hydra',
        }
    }


@pytest.fixture(scope='function')
def json_content_update_pipeline_hook():
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
            'sha': '1234abcd',
            'message': 'message',
            'author_name': 'Juste LeBlanc',
        },
        'repository': {
            'name': 'change name',
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
