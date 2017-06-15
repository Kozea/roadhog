import hmac
from datetime import datetime
from hashlib import sha1
from urllib.parse import unquote, urlencode

from flask import Flask, g, redirect, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .model import Base, Commit, Job, Project


class Roadhog(Flask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.route('/redirect', methods=['GET', 'POST'])(redirect_to)
        self.cli.command('init_db')(self.init_db)
        self.before_request(self.before)

    def init_db(self):
        Base.metadata.create_all(bind=create_engine(self.config['DB']))

    def before(self):
        g.session = sessionmaker(bind=create_engine(self.config['DB']))()


def redirect_to():
    redirect_uri = request.args.get('redirect_uri')
    params = urlencode(request.args)
    return redirect(unquote(f'{redirect_uri}?{params}'))


def hmac_match(content, hmac_send, secret):
    compute_hmac = hmac.new(bytes(secret, 'utf-8'), digestmod=sha1)
    compute_hmac.update(content)
    compute_hmac = compute_hmac.hexdigest()
    return 'sha1=' + compute_hmac == hmac_send


def add_project(content):
    project = Project(
        id=content['project_id'],
        name=content['repository']['name'],
        url=content['repository']['homepage'],
        description=content['repository']['description']
    )
    g.session.add(project)
    g.session.commit()


def add_commit(content):
    commit = Commit(
        id=content['commit']['id'],
        branch=content['ref'],
        project_id=content['project_id']
    )
    g.session.add(commit)
    g.session.commit()


def format_date(date):
    date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S %Z')
    return date


def add_job(content, logs=None, request_headers=None):
    start = content['build_started_at']
    stop = content['build_finished_at']
    start_date = datetime.min if start is None else format_date(start)
    stop_date = datetime.min if stop is None else format_date(stop)
    headers = (request_headers if request_headers is None
               else str(request_headers))
    job = Job(
        id=content['build_id'],
        job_name=content['build_name'],
        start=start_date,
        stop=stop_date,
        status=content['build_status'],
        log=logs,
        request_headers=headers,
        request_content=str(content),
        commit_id=content['commit']['id']
    )
    g.session.add(job)
    g.session.commit()


def update_job(content):
    job_id = content['build_id']
    save_log = g.session.query(Job).filter(Job.id == job_id).first().log
    g.session.query(Job).filter(Job.id == job_id).delete()
    g.session.commit()
    add_job(content, logs=save_log)


def add_log(job_id, logs):
    g.session.query(Job).filter(Job.id == job_id).update({'log': logs})
    g.session.commit()


def exist(id, type):
    return g.session.query(type).filter(type.id == id).first()


def master(content, logs=None, request_headers=None):
    project_id = content['project_id']
    commit_id = content['commit']['id']
    job_id = content['build_id']
    if not exist(project_id, Project):
        add_project(content)
    if not exist(commit_id, Commit):
        add_commit(content)
    if not exist(job_id, Job):
        add_job(content, logs=logs, request_headers=request_headers)
    else:
        update_job(content)
