import pytest
import json
from flask import Flask, url_for, request, jsonify
from flask_obscure import Obscure, converters as _converters

customer_names = ["Adam", "Betty", "Carlos"]
converters = tuple(_converters.keys())
obs = Obscure()


@pytest.fixture(scope="function")
def app():
    _app = Flask(__name__)
    _app.config["OBSCURE_SALT"] = 0x1234  # Use a proper config
    obs.init_app(_app)

    def get_all():
        endpoint = request.url_rule.endpoint.split("-")[-1]
        return jsonify({"data": [c.to_dict(endpoint=endpoint) for c in customers]})

    # Add a route endpoint for each converter
    for conv in reversed(converters):
        get_all = _app.route("/customers/%s" % conv, endpoint="cust-%s" % conv)(get_all)

    def get_cust(customer_id):
        customer = customers[customer_id].to_dict(False)
        rv = {"legal": "FOR INTERNAL USE ONLY! UNOBSCURED"}
        rv.update(customer)
        return jsonify(rv)

    # Add a route endpoint for each converter
    for conv in converters:
        get_cust = _app.route("/{0}/<{0}:customer_id>".format(conv), endpoint=conv)(
            get_cust
        )
    return _app


class Generic(object):
    """This is taking the place of any database object.
    The `to_dict` looks ugly but since you will be using a single
    converter in your code, the bulk of the code goes away.
    """

    def __init__(self, **kwargs):
        self.fields = kwargs
        self.converters = {
            "num": obs.transform,
            "hex": obs.encode_hex,
            "b32": obs.encode_base32,
            "b64": obs.encode_base64,
            "tame": obs.encode_tame,
        }

    def to_dict(self, obscure=True, endpoint=None):
        fields = self.fields.copy()
        url = None
        if obscure is True:
            for k, v in fields.items():
                if k.lower().endswith("_id"):
                    if endpoint is not None:
                        url = url_for(endpoint, **{k: v})
                    v = self.converters[endpoint](v)
                    fields[k] = v
        if url is not None:
            fields["url"] = url
        return fields


customers = [Generic(name=_, customer_id=idx) for idx, _ in enumerate(customer_names)]


def rv2json(data):
    return json.loads(data.decode("ascii"))


@pytest.mark.parametrize("converter", converters)
def test_obscured_json_output(app, converter):
    """Verify the URLs on each customer."""
    with app.test_client() as c:
        with app.test_request_context():
            url = url_for("cust-" + converter)
        rv = c.get(url)
        assert rv.status_code == 200
        assert request.endpoint.endswith(converter)
        data = rv2json(rv.data)["data"]
        assert customer_names == [_["name"] for _ in data]

        for idx, url in enumerate([_["url"] for _ in data]):
            assert url[1:].startswith(converter)
            rv2 = c.get(url)
            assert rv.status_code == 200
            assert request.endpoint == converter
            cust_data = rv2json(rv2.data)
            assert "legal" in cust_data
            assert cust_data["name"] == data[idx]["name"]
            assert cust_data["customer_id"] == idx


@pytest.mark.parametrize(
    "url",
    [
        "/num/",  # missing number
        "/num/ABCDEF",  # bad no letters
        "/num/%s" % str(int(0xFFFFFFFF) + 1),  # too large
        "/hex/abcd",  # to short
        "/hex/AABBCCDD",  # bad CAPS
        "/hex/aabbccdg",  # bad 'g'
        "/b32/ANUIT01",  # bad '01'
        "/b32/anuit23",  # bad lower case
        "/b32/WRONGLEN",  # bad length
        "/b64/some+",  # bad '+'
        "/b64/len",  # bad length
        "/tame/CURSEWD",  # bad 'U'
        "/tame/IGNORES",  # bad 'I'
    ],
)
def test_bad_converter_regex(app, url):
    with app.test_client() as c:
        rv = c.get(url)
        assert rv.status_code == 404


@pytest.mark.parametrize(
    "url",
    ["/num/1234", "/hex/a1b2c3d4", "/b32/TESTING", "/b64/some-_", "/tame/SVCCESS",],
)
def test_bad_customer_id(app, url):
    """The URL is has proper coding but there is no such
    customer, which generates a IndexError and a 500 error.
    """
    with app.test_client() as c:
        rv = c.get(url)
        assert rv.status_code == 500
