import sys
import pytest
from flask import Flask, url_for, request, render_template_string
from jinja2 import Environment
import context
from obscure import Obscure
import flask_obscure as obscure

SALT = 0x1234
FILTERS = tuple(obscure.converters.keys())
TRANSLATE = {
    "num": "transform",
    "hex": "encode_hex",
    "b32": "encode_base32",
    "b64": "encode_base64",
    "tame": "encode_tame",
}


def B(s):
    # Yes, a proper if/else statement would be more readable, but I am
    # doing this for coverage.  Tox would also get this.
    return s if sys.version_info.major == 2 else bytes(s, "ascii")


def make_jinja_filter_for(encoder):
    enc = TRANSLATE[encoder]
    return lambda x, s=SALT, f=enc: str(getattr(Obscure(s), f)(x))


@pytest.fixture(scope="function")
def app():
    _app = Flask(__name__)
    obscure.Obscure(_app, SALT)  # works for test, but use flask.config

    def invoice(customer_id):
        """Show obfuscated customer number.
        Routes for each filter are created like:
            /invoice/b32/<b32:customer_id>
            /invoice/b64/<b64:customer_id>
            /invoice/hex/<hex:customer_id>
            /invoice/tame/<tame:customer_id>

        Arg:
            customer_id: actual customer number

            This number, while obfuscated in the URL, has been converted
            by the in the url_map.converters at this point.

        Return string:
            {obscure method}#{obscured customerID}
        """
        encoder = request.url_rule.endpoint
        template = "{{ encoder }}#{{ customer_id|%s }}" % encoder
        return render_template_string(template, **locals())

    for f in FILTERS:
        url = "/invoice/%s/<%s:customer_id>" % (f, f)
        invoice = _app.route(url, endpoint=f)(invoice)
    return _app


@pytest.mark.parametrize("encoder", FILTERS)
def test_flask_filter(app, encoder):
    obs = app.url_map.converters[encoder](SALT)
    with app.test_client() as c:
        for customer_id in range(0, 0x10000, 0x7FE):
            with app.test_request_context():
                url = url_for(encoder, customer_id=customer_id)
            rv = c.get(url)
            assert 200 == rv.status_code
            assert rv.data.startswith(B(encoder))
            assert rv.data.endswith(B(obs.to_url(customer_id)))


@pytest.mark.parametrize("encoder", FILTERS)
def test_jinja2_filter(encoder):
    obs = Obscure(SALT)

    def conv(x):
        return str(getattr(obs, TRANSLATE[encoder])(x))

    jinja2_filter = make_jinja_filter_for(encoder)
    env = Environment()
    env.filters[encoder] = jinja2_filter
    tmpl = env.from_string("{{ x|%s }}" % encoder)

    for x in range(0xFE, 0x1000, 0x1FE):
        rv = tmpl.render(x=x)
        assert rv == conv(x)

    with pytest.raises(TypeError):
        tmpl.render(x="silly string")
