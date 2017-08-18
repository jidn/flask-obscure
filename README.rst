|version| |build| |coverage| |pyversions|

=======================================
Flask-Obscure
=======================================

.. contents::

Showing a steadily increasing sequence of integer IDs leaks information to customers, competitors, or malicious entities about the number and frequency of customers, orders, etc.  Some URL example include::

    /customer/123
    /order/308

This module impliments routing variable converters in `Flask`_ and `Jinja2`_ filters to obscure sequential integer IDs.
This is based on the `Obscure`_ python module, which is installed automagically when you install this module.

Features
=======================================

 *  Automatically obscures sequential integer IDs in the variable
    part of a URL when using ``flask.url_for``
 *  Automatically converts obscured IDs back to your sequential
    integer IDs in the parameter of the function bound to the URL.
 *  Jinja filters automatically available.
 *  Provide five different converters and filters.


Converters and Filters
=======================================

There are five new converters: ``num``, ``hex``, ``b32``, ``b64``, and ``tame``.
Lets assume we are using ``flask.url_for`` to create the URLs for two sequential customer IDs.  Lets take a look and the obscured numbers for 1 - 10 with a salt of 4049.

``num``
    Non-sequential numbers::

    3363954640 781239386 2649118836 1498905894 2772037181
    842981965 240566679 3654613332 2665083367


``hex``
    Hexadecimal displays in eight characters::

    c881dfd0 2e90c45a 9de65874 59577d26 a539ee3d
    323ee24d 0e56c197 d9d4f954 9ed9f1e7

``b32``
    Base32 displays in seven characters::

    ZCA57UA F2IMIWQ TXTFQ5A LFLX2JQ UU464PI
    GI7OETI BZLMDFY 3HKPSVA T3M7DZY

``b64``
    Base64 URL safe displays in six characters::

    yIHf0A LpDEWg neZYdA WVd9Jg pTnuPQ
    Mj7iTQ DlbBlw 2dT5VA ntnx5w

``tame``
    Is a Base32 with a rotated, alternate alphabet.
    The letters 'I', 'O', and 'U' are replaced with the numbers '8', '9', and '0' to avoid common offensive words.
    Otherwise, it performs just like Base32.

    6EC0BZC H7LQL3V Y4YHV0C PHP47MV ZZ9A9TL
    JLBSGYL D6PQFH5 8KNTX2C Y8QBF65


Install
=======================================

Pip is our friend. It will also install the `Obscure`_ module as well. ::

    $ pip install flask_obscure

Configure
=======================================

The ``Obscure`` class needs a ``salt`` or random number to make your obscured number sequence unique.  Pick any 32-bit number or use the following snippit to generate one for you::

    python -c "import os; print(int(os.urandom(4).encode('hex'),16))"

``Obscure`` uses the value ``OBSCURE_SALT`` in the flask configuration file if not given as the second parameter to either the constructor or ``Obscure.init_app``.

.. warning::
    If your source goes to a public repository, you will want 
    to place ``OBSCURE_SALT`` in the ``flask.Flask`` instance path.

Usage
=======================================

Import the class ``Obscure`` and initialize the with the ``flask.Flask`` appliation by either using the constructor

.. code-block:: python
    :emphasize-lines: 5

    from flask import Flask
    from flask.ext.obscure import Obscure

    app = Flask(app)
    obscure = Obscure(app)

or by using delayed initialization with ``Obscure.init_app``

.. code-block:: python
    :emphasize-lines: 2

    obscure = Obscure()
    obscure.init_app(app)


URL Routing Variables
---------------------------------------

When creating your routes with variables, you have five converters.
The converter is similar to any of the other built in coverters.
It takes the obscured ID given in the variable portion of the URL and converts it to your sequential ID in the callable bound to the URL.

Lets look at an example using ``num`` as the converter in the route.

.. code-block:: python

    @app.route('/customers/<num:cust_id>', endpoint='get-cust')
    def get(cust_id):
        # flask.request.url is '/customers/3303953358'
        # cust_id is the sequential ID of 1
        customer = get_customer_by_id(cust_it)

        url = flask.url_for('get-cust', cust_id=customer.customer_id)
        # when you create the URL, it is automatically obscured
        # /customers/3303953358


Jinja2 Filters
---------------------------------------

The URL is not the only place you can have leaking interger IDs.  It can
also happen in the data returned from your routing function.  If you are
using Jinja2 for templating, those same converters are available as filters.

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
