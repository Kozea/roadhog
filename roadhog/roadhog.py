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


def build_project(content):
    project = Project(
        id=content['project_id'],
        name=content['repository']['name'],
        url=content['repository']['homepage'],
        description=content['repository']['description']
    )
    return project


def add_project(content):
    project = build_project(content)
    g.session.add(project)
    g.session.commit()


def update_project(id, content):
    project_new = build_project(content)
    project_db = g.session.query(Project).filter(Project.id == id).first()
    if project_new != project_db:
        name = content['repository']['name']
        url = content['repository']['homepage']
        description = content['repository']['description']
        updates = {'name': name, 'url': url, 'description': description}
        g.session.query(Project).filter(Project.id == id).update(updates)
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


def build_job(content, request_headers):
    start = content['build_started_at']
    stop = content['build_finished_at']
    start_date = start if start is None else format_date(start)
    stop_date = stop if stop is None else format_date(stop)
    job = Job(
        id=content['build_id'],
        job_name=content['build_name'],
        start=start_date,
        stop=stop_date,
        status=content['build_status'],
        log=None,
        request_headers=str(request_headers),
        request_content=str(content),
        commit_id=content['commit']['id']
    )
    return job


def add_job(content, request_headers):
    job = build_job(content, request_headers)
    g.session.add(job)
    g.session.commit()


def update_job(id, content, request_headers):
    start = content['build_started_at']
    stop = content['build_finished_at']
    start_date = start if start is None else format_date(start)
    stop_date = stop if stop is None else format_date(stop)
    status = content['build_status']
    updates = {
        'start': start_date,
        'stop': stop_date,
        'status': status,
        'request_content': str(content),
        'request_headers': str(request_headers)
    }
    g.session.query(Job).filter(Job.id == id).update(updates)
    g.session.commit()


def add_log(job_id, logs):
    g.session.query(Job).filter(Job.id == job_id).update({'log': logs})
    g.session.commit()


def exist(id, type):
    return g.session.query(type).filter(type.id == id).first()


def master_project(content):
    project_id = content['project_id']
    if not exist(project_id, Project):
        add_project(content)
    else:
        update_project(project_id, content)


def master_commit(content):
    commit_id = content['commit']['id']
    if not exist(commit_id, Commit):
        add_commit(content)


def master_job(content, request_headers):
    job_id = content['build_id']
    if not exist(job_id, Job):
        add_job(content, request_headers)
    else:
        update_job(job_id, content, request_headers)


def master(content, request_headers):
    master_project(content)
    master_commit(content)
    master_job(content, request_headers)
