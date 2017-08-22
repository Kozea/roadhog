import hmac
from datetime import datetime
from hashlib import sha1
from urllib.parse import unquote, urlencode

from flask import Flask, g, redirect, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unrest import UnRest

from .model import Commit, Job, Project


class Roadhog(Flask):
    def create_session(self):
        return sessionmaker(bind=create_engine(self.config['DB']))()

    def before(self):
        g.session = self.create_session()

    def initialize(self):
        self.route('/redirect', methods=['GET', 'POST'])(redirect_to)
        self.before_request(self.before)
        rest = UnRest(self, self.create_session())
        rest(Project, methods=['GET'])
        rest(Commit, methods=['GET'],
             query=lambda q:
             q.filter(Commit.project_id == request.args['project_id'])
             if request.args else q)
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


def build_commit(content):
    return {
        'id': content['commit']['sha'],
        'branch': content['ref'],
        'pipeline_id': content['commit']['id'],
        'message': content['commit']['message'],
        'author': content['commit']['author_name'],
        'project_id': content['project_id']
    }


def format_date(date):
    return date and datetime.strptime(date, '%Y-%m-%d %H:%M:%S %Z')


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


def add_log(job_id, logs):
    (g.session.query(Job)
     .filter(Job.id == job_id)
     .update({'log': logs.decode('utf-8')}))
    g.session.commit()


def upsert(type, data):
    if not g.session.query(type).filter(type.id == data.get('id')).first():
        g.session.add(type(**data))
    else:
        g.session.query(type).filter(type.id == data.get('id')).update(data)
    g.session.commit()


def master(content, request_headers):
    upsert(Project, build_project(content))
    upsert(Commit, build_commit(content))
    upsert(Job, build_job(content, request_headers))
