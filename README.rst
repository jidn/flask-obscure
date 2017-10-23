|version| |build| |coverage| |pyversions|

=======================================
Flask-Obscure
=======================================

Showing a steadily increasing sequence of integer IDs leaks information to customers, competitors, or malicious entities about the number and frequency of customers, orders, etc.
Some URL examples include::

    /customer/123
    /order/308

This module implements routing variable converters in `Flask`_ and `Jinja2`_ filters to obscure sequential integer IDs using the `Obscure`_ python module.

Features
=======================================

 *  Automatically obscures sequential integer IDs in the variable
    part of a URL when using :py:func:`flask.url_for`
 *  Provides five different converters and filters.
 *  Automatically converts obscured IDs back to your sequential
    integer IDs in the parameter of the function bound to the URL.
 *  Jinja filters automatically available.
 *  Use a 32-bit number to salt the transformation.


Converters and Filters
=======================================

There are five converters and filters.  
They are `num`_, `hex`_, `b32`_, `b64`_, and `tame`_.
Assume you are using :py:func:`flask.url_for` to create the URLs for two sequential customer IDs.
Let's take a look and the obscured numbers for 1-9 with a salt of 4049.

======  ==========  ========  =======  ======  =======
Number  Converters
------  ----------------------------------------------
Input   `num`_      `hex`_    `b32`_   `b64`_  `tame`_
======  ==========  ========  =======  ======  =======
  1     3363954640  c881dfd0  ZCA57UA  yIHf0A  6EC0BZC
  2      781239386  2e90c45a  F2IMIWQ  LpDEWg  H7LQL3V
  3     2649118836  9de65874  TXTFQ5A  neZYdA  Y4YHV0C
  4     1498905894  59577d26  LFLX2JQ  WVd9Jg  PHP47MV
  5     2772037181  a539ee3d  UU464PI  pTnuPQ  ZZ9A9TL
  6      842981965  323ee24d  GI7OETI  Mj7iTQ  JLBSGYL
  7      240566679  0e56c197  BZLMDFY  DlbBlw  D6PQFH5
  8     3654613332  d9d4f954  3HKPSVA  2dT5VA  8KNTX2C
  9     2665083367  9ed9f1e7  T3M7DZY  ntnx5w  Y8QBF65
======  ==========  ========  =======  ======  =======

num
-----

A symmetic feistel cipher which when used with a salt, or 32 bit number unique to you, transforms a sequential series of numbers into a seamingly sequence of random numbers.  All of the following are just different presentations of this basic transformation.

hex
-----

Display the transformed number as an eight character hexadecimal number.

b32
-----

Display the transformed number in seven character base32 using upper-case letters and numbers.

b64
-----

Display the transformed number in six character base64 using upper-case, lower-case, and numbers.

tame
-----

This is a variation of `b32`_ with a rotated, alternate alphabet.
The vowels 'I', 'O', and 'U' are replaced with the number '8', '9', and '0' to avoid common offensive words.
Otherwise, it performs just like base32.


Install
=======================================

Pip is our friend. It will also install the `Obscure`_ module as well. ::

    $ pip install flask_obscure

Configure
=======================================

The ``Obscure`` class needs a ``salt`` or random number to make your obscured number sequence unique.  Pick any 32-bit number or use the following snippet to generate one for you::

    python -c "import uuid; print(hex(uuid.uuid1().int >> 96))"

``Obscure`` uses the value ``OBSCURE_SALT`` in the flask configuration file if not given as the second parameter to either the constructor or ``Obscure.init_app``.

.. warning::
    If your source goes to a public repository, you will want 
    to place ``OBSCURE_SALT`` in the ``flask.Flask`` instance path or 
    some other method of keeping secrets.

Usage
=======================================

Import the class ``Obscure`` and initialize the ``flask.Flask`` application by either using the constructor

.. code-block:: python

    from flask import Flask
    from flask.ext.obscure import Obscure

    app = Flask(app)
    app.config['OBSCURE_SALT'] = 4049
    obscure = Obscure(app)

or by using delayed initialization with ``Obscure.init_app``

.. code-block:: python

    obscure = Obscure()
    ...
    obscure.init_app(app, salt=4940)


URL Routing Variables
---------------------------------------

When creating your routes with variables, you have five converters.
The converter is similar to any of the other built-in coverters.
It takes the obscured ID given in the variable portion of the URL and converts it to your sequential ID in the callable bound to the URL.

Here is an example using ``num`` as the converter in the url route.

.. code-block:: python

    # flask.request.url is '/customers/3303953358'
    @app.route('/customers/<num:cust_id>', endpoint='get-cust')
    def get(cust_id):
        # cust_id is the sequential ID of 1
        customer = get_customer_by_id(cust_it)

        url = flask.url_for('get-cust', cust_id=customer.customer_id)
        # when you create the URL, it is automatically obscured
        # /customers/3303953358


Jinja2 Filters
---------------------------------------

The URL is not the only place you can have leaking integer IDs.
It can also happen in the data returned from your routing function.
If you are using Jinja2 for templating, those same converters are available as filters.

.. code-block:: html+jinja

    <h1>Invoice #{{ invoice_number|tame }}</h1>

Within Code
---------------------------------------

To obscure numbers within your code, use the methods of the ``flask_obscure.Obscure`` instance object, which in turn is inherited from the python module `Obscure`_.  Assuming we used one of the code blocks from ``configure``

.. code-block:: python

    visible_customer_id = obscure.encode_tame(customer_id)

Contribute
=======================================

| Issue Tracker: `http://github.com/jidn/flask-obscure/issues`
| Source Code: `http://github.com/jidn/flask-obscure`


.. _Obscure: http://github.com/jidn/obscure
.. _Flask: http://flask.pocoo.org/
.. _Jinja2: http://jinja.pocoo.org/

.. |version| image:: https://img.shields.io/pypi/v/flask-obscure.svg
    :target: https://pypi.python.org/pypi/flask-obscure
    :alt: Latest version on PyPi

.. |build| image:: https://img.shields.io/travis/jidn/flask-obscure.svg
    :target: http://travis-ci.org/jidn/flask-obscure
    :alt: Build status of the master branch on Linux

.. |coverage| image:: https://coveralls.io/repos/github/jidn/flask-obscure/badge.svg
    :target: https://coveralls.io/github/jidn/flask-obscure
    :alt: Code coverage when testing

.. |pyversions| image:: https://img.shields.io/pypi/pyversions/flask-obscure.svg
    :target: https://pypi.python.org/pypi/flask-obscure
    :alt: Versions on PyPi
