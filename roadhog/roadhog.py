import hmac
from hashlib import sha1
from urllib.parse import unquote, urlencode

from flask import Flask, redirect, request
from sqlalchemy import create_engine

from .model import Base


class Roadhog(Flask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.route('/redirect', methods=['GET', 'POST'])(redirect_to)
        self.cli.command('init_db')(self.init_db)

    def init_db(self):
        Base.metadata.create_all(bind=create_engine(self.config['DB']))


def redirect_to():
    redirect_uri = request.args.get('redirect_uri')
    params = urlencode(request.args)
    return redirect(unquote(f'{redirect_uri}?{params}'))


def hmac_match(content, hmac_send, secret):
    compute_hmac = hmac.new(bytes(secret, 'utf-8'), digestmod=sha1)
    compute_hmac.update(content)
    compute_hmac = compute_hmac.hexdigest()
    return 'sha1=' + compute_hmac == hmac_send
