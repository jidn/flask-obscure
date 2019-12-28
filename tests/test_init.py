import pytest
from flask import Flask
import context
from flask_obscure import Obscure
from test_filter import B


def make_app(salt=None):
    app = Flask(__name__)

    if salt is not None:
        app.config["OBSCURE_SALT"] = salt
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


def test_obscure_init_salted():
    app = make_app()
    obscure = Obscure(salt=0x54321)
    obscure.init_app(app)

    assert 0x54321 == obscure.salt


def test_missing_salt():
    app = make_app()
    with pytest.raises(KeyError):
        Obscure(app).transform(0)


def test_multi_apps():
    app1 = make_app()
    app2 = make_app()

    salt = 0x12345
    obscure = Obscure()
    obscure.init_app(app1, salt)
    obscure.init_app(app2, salt)

    @app1.route("/<tame:number>")
    def index1(number):
        return "\n".join(("#1", str(number)))

    @app2.route("/<tame:number>")
    def index2(number):
        return "\n".join(("#2", str(number)))

    tame = obscure.encode_tame(0)
    with app1.test_client() as go:
        rv = go.get("/" + tame)
        assert 200 == rv.status_code
        assert rv.data.startswith(B("#1\n"))
        assert rv.data.endswith(B("\n0"))

    with app2.test_client() as go:
        rv = go.get("/" + tame)
        assert 200 == rv.status_code
        assert rv.data.startswith(B("#2\n"))
        assert rv.data.endswith(B("\n0"))
