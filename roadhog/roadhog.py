import hmac
import datetime
# from datetime import datetime
from hashlib import sha1
from urllib.parse import unquote, urlencode

from flask import Flask, g, redirect, request
from sqlalchemy import create_engine
from sqlalchemy.orm import joinedload, sessionmaker

from sassutils.wsgi import SassMiddleware

from unrest import UnRest

from .model import Commit, Job, Project


class Roadhog(Flask):
    def create_session(self):
        return sessionmaker(bind=create_engine(self.config['DB']))()

    def before(self):
        g.session = self.create_session()

    def initialize(self):
        self.wsgi_app = SassMiddleware(self.wsgi_app, {'junkrat': ('sass', 'static/css', '/static/css') })
        self.route('/redirect', methods=['GET', 'POST'])(redirect_to)
        self.before_request(self.before)
        rest = UnRest(self, self.create_session())
        rest(Project, methods=['GET'],
             query=lambda q: q.options(joinedload(Project.last_commit)),
             relationships={
                 'last_commit': rest(Commit, only=['id', 'commit_date'])})
        rest(Commit, methods=['GET'],
             query=lambda q:
             q.filter(Commit.project_id == request.args['project_id']).filter(Commit.branch == request.args['branch'])
             if request.args else q)
        rest(Commit, methods=['GET'], name='branche',
             only=['branch', 'project_id'], primary_keys=['branch'],
             query=lambda q:
             g.session.query(Commit.branch, Commit.project_id)
             .filter(Commit.project_id == request.args['project_id'])
             .distinct(Commit.branch))
        rest(Job, methods=['GET'],
             query=lambda q:
             q.filter(Job.commit_id == request.args['commit_id'])
             if request.args else q)


def redirect_to():
    redirect_uri = request.args.get('redirect_uri')
    params = urlencode(request.args)
    return redirect(unquote(f'{redirect_uri}?{params}'))


def hmac_match(content, hmac_send, secret):
    compute_hmac = hmac.new(secret.encode('utf-8'), digestmod=sha1)
    compute_hmac.update(content)
    compute_hmac = compute_hmac.hexdigest()
    return 'sha1=' + compute_hmac == hmac_send


def build_project(content):
    return {
        'id': content['project_id'],
        'name': content['repository']['name'],
        'url': content['repository']['homepage'],
        'description': content['repository']['description']
    }


def build_commit_from_pipeline(content):
    return {
        'id': content['commit']['sha'],
        'branch': content['ref'],
        'pipeline_id': content['commit']['id'],
        'message': content['commit']['message'],
        'author': content['commit']['author_name'],
        'project_id': content['project_id'],
        'status': content['build_status']
    }


def format_timestamp(timestamp):
    date = timestamp[:22] + timestamp[23:]
    date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z")
    return date.astimezone(tz=datetime.timezone.utc)


def build_commit_from_push(content, **kwargs):
    return {
        'id': content['id'],
        'branch': kwargs['branch'],
        'message': content['message'],
        'author': content['author']['name'],
        'commit_date': format_timestamp(content['timestamp']),
        'project_id': kwargs['project_id']
    }


def format_date(date):
    return date and datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S %Z')


def build_job(content, request_headers):
    return {
        'id': content['build_id'],
        'job_name': content['build_name'],
        'start': format_date(content['build_started_at']),
        'stop': format_date(content['build_finished_at']),
        'status': content['build_status'],
        'request_headers': str(request_headers),
        'request_content': str(content),
        'commit_id': content['commit']['sha']
    }


def add_data(type, type_id, data):
    g.session.query(type).filter(type.id == type_id).update(data)
    g.session.commit()


def upsert(type, data):
    if not g.session.query(type).filter(type.id == data.get('id')).first():
        g.session.add(type(**data))
    else:
        g.session.query(type).filter(type.id == data.get('id')).update(data)
    g.session.commit()


def master(content, request_headers, type_event):
    upsert(Project, build_project(content))
    if type_event == 'Push Hook':
        branch = content['ref'].split('/')[-1]
        project_id = content['project_id']
        for commit in content['commits']:
            upsert(Commit,
                   build_commit_from_push(
                       commit, branch=branch, project_id=project_id))
    else:
        upsert(Commit, build_commit_from_pipeline(content))
        upsert(Job, build_job(content, request_headers))
