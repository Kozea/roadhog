import hmac
from hashlib import sha1
from os import system
from urllib.parse import unquote, urlencode

import requests
from flask import Flask, jsonify, redirect, request

app = Flask(__name__)
app.config.from_envvar('ROADHOG_SETTINGS')


def format_key(key):
    return ''.join(char for char in key if char.isalnum()).upper()


def compute_xhubsignature(content):
    secret = app.config['XHUB']
    compute_hmac = hmac.new(bytes(secret, 'utf-8'), digestmod=sha1)
    compute_hmac.update(content)
    return compute_hmac.hexdigest()


def hmac_match(content, hmac_send):
    compute_hmac = compute_xhubsignature(content)
    return 'sha1=' + compute_hmac == hmac_send


def is_pull_request(project, branch):
    access = app.config['GITHUB_ACCESS']
    uri = app.config['GITHUB_URI']
    param = {
        'access_token': access,
        'state': 'open'
    }
    req = requests.get(
        uri + project + '/pulls',
        params=param
    )
    return branch in req.text


@app.route('/update', methods=['GET', 'POST'])
def update():
    base_path = app.config['BASE_PATH']
    content = request.get_json()
    raw_content = request.get_data()
    project_name = content['repository']['name'].lower()
    token = app.config['TOKEN_' + format_key(project_name)]
    update = 1
    if(hmac_match(raw_content, request.headers['X-Hub-Signature'])):
        update = system(f'{base_path}/{token}/update.sh {project_name}')
    return jsonify({'success': str(update)})


@app.route('/redirect', methods=['GET'])
def redirect_to():
    redirect_uri = request.args.get('redirect_uri')
    params = urlencode(request.args)
    return redirect(unquote(f'{redirect_uri}?{params}'))


@app.route('/deploy', methods=['GET', 'POST'])
def deploy():
    base_path = app.config['BASE_PATH']
    content = request.get_json()
    token = content['token']
    build_stage = content['build_stage']
    project_name = content['project_name'].lower()
    branch = content['branch']
    deploy = 1
    pull_request = is_pull_request(content['project_name'], content['branch'])
    if (content['build_stage'] == 'deploy_test'
            and (content['branch'] == 'master' or pull_request)): # noqa
        url = content['url']
        password = content.get('password', '')
        deploy = system(
            f'{base_path}/{token}/{build_stage}.sh '
            f'{url} {project_name} {branch} {password} || exit $?')
    elif content['build_stage'] == 'deploy_prod':
        deploy = system(
            f'{base_path}/{token}/{build_stage}.sh {project_name} || exit $?')
    else:
        deploy = 0
    deploy = 1 if deploy != 0 else deploy
    return jsonify({'success': str(deploy)})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
