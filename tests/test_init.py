import pytest
from flask import Flask
from flask.ext.obscure import Obscure


def make_app(salt=None):
    app = Flask(__name__)
    if salt is not None:
        app.config['OBSCURE_SALT'] = salt
    return app


def test_salt_from_config():
    app = make_app(0x1234)
    obscure = Obscure(app)

    assert obscure.salt == 0x1234


def test_salt_init_over_config():
    # Parameter salt superior to config
    app = make_app(0x54321)
    obscure = Obscure(app, 0x1234)

    assert obscure.salt == 0x1234


def test_salt_initapp_over_config():
    app = make_app(0x54321)
    obscure = Obscure()
    obscure.init_app(app, 0x1234)

    assert obscure.salt == 0x1234


def test_missing_salt():
    app = make_app()
    with pytest.raises(KeyError):
        obscure = Obscure(app)
        obscure.transform(0)
