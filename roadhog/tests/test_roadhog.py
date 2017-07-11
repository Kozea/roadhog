import datetime

from roadhog import roadhog

from ..model import Commit, Job, Project


def test_hmac_match(app, json_content):
    assert roadhog.hmac_match('toto'.encode('utf-8'),
                              'sha1=51c53ab8853ab958acf65ce09b8f68c65fac821c',
                              app.config['XHUB'])


def test_api(http, alembic_config):
    assert http.get('/api/project')[0] == 200
    assert http.get('/api/commit_')[0] == 200
    assert http.get('/api/job')[0] == 200


def test_build_project(json_content):
    assert roadhog.build_project(json_content) == {
        'id': 1320772,
        'name': 'hydra',
        'url': 'https://gitlab.com/Kozea/hydra',
        'description': 'Serpent-like water monster with reptilian traits'
    }


def test_build_commit(json_content):
    assert roadhog.build_commit(json_content) == {
        'id': 9632758,
        'branch': 'phoenix_2223',
        'project_id': 1320772
    }


def test_build_job(json_content, json_headers):
    assert roadhog.build_job(json_content, json_headers) == {
        'commit_id': 9632758,
        'id': 21339678,
        'job_name': 'deploy_test',
        'request_content':
        "{'object_kind': 'build', 'ref': 'phoenix_2223', "
        "'build_id': 21339678, 'build_name': 'deploy_test', "
        "'build_status': 'success', 'build_started_at': "
        "'2017-07-06 13:39:16 UTC', 'build_finished_at': "
        "'2017-07-06 13:43:56 UTC', 'project_id': 1320772, "
        "'commit': {'id': 9632758}, 'repository': {'name': "
        "'hydra', 'description': 'Serpent-like water monster with "
        "reptilian traits', 'homepage': "
        "'https://gitlab.com/Kozea/hydra'}}",
        'request_headers':
        "{'Content-Type': 'application/json', 'X-Gitlab-Token': 'token'}",
        'start': datetime.datetime(2017, 7, 6, 13, 39, 16),
        'status': 'success',
        'stop': datetime.datetime(2017, 7, 6, 13, 43, 56)
    }


def test_master(app, db_session, json_content, json_headers):
    with app.test_request_context():
        app.preprocess_request()
        roadhog.master(json_content, json_headers)
        assert db_session.query(Job).first() is not None
        assert db_session.query(Commit).first() is not None
        assert db_session.query(Project).first() is not None
