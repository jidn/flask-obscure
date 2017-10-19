import sys
import itertools
import pytest
from flask import Flask, request, url_for, render_template_string
from jinja2 import Environment
from helper import FILTERS, METHODS, make_filters


def B(s):
    if sys.version_info.major == 2:
        return s
    return bytes(s, 'ascii')


def create_app(method):
    my_app = Flask('test_filter')

    filters = make_filters(FILTERS, method)
    for name, function in filters.items():
        my_app.add_template_filter(function, name)

    @my_app.route('/my_hex/<int:number>', endpoint='my_hex')
    @my_app.route('/my_bin/<int:number>', endpoint='my_bin')
    @my_app.route('/my_oct/<int:number>', endpoint='my_oct')
    def use_filter(number):
        filter_ = request.url_rule.endpoint
        template = '{{ filter_ }} {{ number|%s }}' % filter_
        pytest.set_trace()
        return render_template_string(template, **locals())
    return my_app


def test_flask_oct():
    app = create_app('LAMBDA')
    with app.test_client() as go:
        with app.test_request_context():
            url = url_for('my_oct', number=254)
        rv = go.get(url)
        assert 200 == rv.status_code
        assert rv.data.startswith(B('my_oct'))
        assert rv.data.endswith(B('0o376'))


@pytest.mark.parametrize('method,filter_',
                         itertools.product(METHODS, FILTERS))
def test_flask(method, filter_):
    NUM = 254
    app = create_app(method)
    with app.test_client() as go:
        with app.test_request_context():
            url = url_for(filter_, number=NUM)
        rv = go.get(url)
        assert 200 == rv.status_code
        func = __builtins__[filter_[3:]]
        assert rv.data.startswith(B(filter_))
        assert rv.data.endswith(B(func(NUM)))


@pytest.mark.parametrize('method,filter_',
                         itertools.product(METHODS, FILTERS))
def test_jinja2(method, filter_):
    filters = make_filters(FILTERS, method)
    env = Environment()
    env.filters.update(filters)
    for number in range(0, 0x10000, 0xfe):
        template = env.from_string("{{ filter_ }} {{ number|%s }}" % filter_)
        rv = template.render(**locals())
        assert rv.startswith(filter_)
        assert rv.endswith(filters[filter_](number))
