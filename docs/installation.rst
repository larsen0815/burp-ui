Installation
============

``Burp-UI`` is written in Python with the `Flask`_ micro-framework.
The easiest way to install Flask is to use ``pip``.

On Debian, you can install ``pip`` with the following command:

::

    aptitude install python-pip


Once ``pip`` is installed, you can install ``Burp-UI`` this way:

::

    pip install burp-ui


You can setup various parameters in the `burpui.cfg`_ file.
This file can be specified with the ``-c`` flag or should be present in
``/etc/burp/burpui.cfg``.
By default ``Burp-UI`` ships with a default file located in
``$BURPUIDIR/../share/burpui/etc/burpui.sample.cfg``.

Then you can run ``burp-ui``: ``burp-ui``

By default, ``burp-ui`` listens on all interfaces (including IPv6) on port 5000.

You can then point your browser to http://127.0.0.1:5000/

Instructions
------------

In order to make the *on the fly* restoration/download functionality work, you
need to check a few things:

1. Provide the full path of the burp (client) binary file
2. Provide the full path of an empty directory where a temporary restoration
   will be made. This involves you have enough space left on that location on
   the server that runs ``Burp-UI``
3. Launch ``Burp-UI`` with a user that can proceed restorations and that can
   write in the directory above
4. Make sure to configure a client on the server that runs ``Burp-UI`` that can
   restore files of other clients (option *restore_client* in burp-server
   configuration)

Options
-------

::

    Usage: burp-ui [options]

    Options:
      -h, --help            show this help message and exit
      -v, --verbose         verbose output
      -d, --debug           verbose output (alias)
      -V, --version         print version and exit
      -c CONFIG, --config=CONFIG
                            configuration file
      -l FILE, --logfile=FILE
                            output logs in defined file


.. _Flask: http://flask.pocoo.org/
.. _burpui.cfg: https://git.ziirish.me/ziirish/burp-ui/blob/master/share/burpui/etc/burpui.sample.cfg