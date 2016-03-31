"""Obscure sequential IDs in URL variables and templates.

Impliments routing converters and fiters in Flask to obscure sequential
integer IDs.  This is base on the 'Obscure' python module.

Once installed, the following converters and filters are available:
    num, hex, b32, b64, and tame
"""

from werkzeug.routing import BaseConverter, IntegerConverter
from obscure import Obscure as _mod_Obscure, _base32_custom as _tame_alphabet


__version__ = '0.1.0'


class Obscure(_mod_Obscure):
    """Obscure interger IDs in URLs.
    A ``salt`` value is needed.  You can provide it when initializing
    the app or from the flask configuration under the parameter
    ``OBSCURE_SALT``.
    """

    def __init__(self, app=None, salt=None):
        """Add converters and filters to a :class:`Flask` instance.

        Args:
          app: a :class:`flask:Flask' instance or None
          salt (integer): random 32-bit integer for uniqueness
        """
        self.app = app
        self.salt = salt
        if app is not None:
            self.init_app(app, self.salt)

    def init_app(self, app, salt=None):
        """Add converters and filters to a :class:`Flask` instance.

        Args:
          app: a :class:`flask:Flask` instance
          salt (integer): random 32-bit integer for uniqueness

        Raises:
            KeyError: ``OBSCURE_SALT`` must be in the
             :class:`flask.Config` if it is not given as a parameter.
        """
        salt = salt or int(app.config['OBSCURE_SALT'])
        _mod_Obscure.__init__(self, salt)

        for converter_name, base in converters.items():
            class_name = 'Obscure' + base.__name__
            class_ = type(class_name, (base,), {'obscure': self})
            app.url_map.converters[converter_name] = class_
            # Lambda can't use locals so we trick it here by binding
            # the local variables to input variables.
            filter_ = (lambda x, c=class_, s=salt: c(s).to_url(x))
            app.add_template_filter(filter_, converter_name)


class Num(IntegerConverter):
    """Obscure interger ID and format as alternate, non-sequential number.
    Rule('/customer/<num:customer_id>')
    """
    def __init__(self, map):
        IntegerConverter.__init__(self, map, max=4292967295)

    def to_python(self, value):
        """Restores original number.

        Args:
          value (number string): obscured, non-sequential number

        Returns:
            integer: the original number

        See Also:
            to_url
        """
        value = IntegerConverter.to_python(self, int(value))
        return self.obscure.transform(value)

    def to_url(self, value):
        """Convert value to alternate, non-sequential integer format.

        Args:
          value (integer): number to obscure

        Returns:
          string: an obscured, non-sequential number

        See Also:
          to_python
        """
        """
        :param value: integer to convert
        :returns: integer as a string
        """
        return str(self.obscure.transform(value))


class Hex(BaseConverter):
    """Obscure numerical ID and format as hex.
    Rule('/customer/<hex:customer_id>')
    """
    weight = 50
    regex = '[abcdef0123456789]{8}'

    def to_python(self, value):
        """Restores original number.

        Args:
          value: 8 digit hexadecimal string

        Returns:
          integer: original integer

        See Also:
          to_url
        """
        """
        :param value: 8 digit hexadecimal format string
        :returns: integer
        """
        return self.obscure.decode_hex(value)

    def to_url(self, value):
        """Convert value to hexadecimal format.

        :param value: integer to convert
        :returns: string in hexadecimal format
        """
        return self.obscure.encode_hex(value)


class Base32(BaseConverter):
    """Obscure numerical ID and format as base32.
    Rule('/customer/<b32:customer_id>')
    """
    weight = 50
    regex = '[A-Z2-7]{7}'

    def to_python(self, value):
        """Restores original number.

        :param value: 7 digit base32 format string
        :returns: integer
        """

        return self.obscure.decode_base32(str(value))

    def to_url(self, value):
        """Convert value to Base32 format.

        :param value: integer to convert
        :returns: string in Base32 format
        """
        return self.obscure.encode_base32(value)


class Base64(BaseConverter):
    """Obscure numerical ID and format as url-safe base64.
    Rule('/customer/<b64:customer_id>')
    """
    weight = 50
    regex = '[-_A-Za-z0-9]{6}'

    def to_python(self, value):
        """Restores original number.

        :param value: alternate Base64 format string
        :returns: integer
        """
        return self.obscure.decode_base64(str(value))

    def to_url(self, value):
        """Convert value to Base64 format.

        :param value: integer to convert
        :returns: string in Base64 format
        """
        return self.obscure.encode_base64(value)


class Tame(BaseConverter):
    """Obscure numerical ID and format as a custom base32
    with the letters 'I' and 'U' removed to eliminate common
    offensive words.
    Rule('/customer/<tame:customer_id>')
    """
    weight = 50
    regex = '[%s]{7}' % _tame_alphabet

    def to_python(self, value):
        """Restores original number.

        :param value: alternate Base32 format string
        :returns: integer
        """
        return self.obscure.decode_tame(str(value))

    def to_url(self, value):
        """Convert value to alternate Base32 format.

        :param value: integer to convert
        :returns: alternate Base32 format
        """
        return self.obscure.encode_tame(value)


converters = {'num': Num, 'hex': Hex, 'tame': Tame,
              'b32': Base32, 'b64': Base64}
