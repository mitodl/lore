LORE
----
.. image:: https://img.shields.io/travis/mitodl/lore.svg
    :target: https://travis-ci.org/mitodl/lore
.. image:: https://img.shields.io/coveralls/mitodl/lore.svg
    :target: https://coveralls.io/r/mitodl/lore
.. image:: https://img.shields.io/github/issues/mitodl/lore.svg
    :target: https://github.com/mitodl/lore/issues
.. image:: https://img.shields.io/badge/license-AGPLv3-blue.svg
    :target: https://github.com/mitodl/lore/blob/master/LICENSE


Getting Started
===============

You can either run this locally with a default sqlite database after
installing the requirements.txt file, or if you have Docker and
prefer a cleaner environment, install docker-compose with ``pip
install docker-compose`` and run ``docker-compose up``. This will set up
a near production-ready containerized development environment that
runs migrations, with the django development server running on
port 8070.

To run one-off commands, like shell, you can run
``docker-compose run web python manage.py shell`` or to create root
user, etc.

Adding an application
=====================

To add an application to this, add it to the requirements file, add
its needed settings, include its URLs, and provide any needed template
overrides.


Adding JavaScript or CSS Libraries
==================================

We have `bower <http://bower.io/>`_ installed and configured in the
docker image.  This is very handy for documenting and adding
dependencies like backbone or bootstrap.  To add a new dependency,
just run ``docker-compose run web bower install jquery --save`` for
example.  This will download jquery to the
``lore/static/bower/jquery`` folder and add it to the bower.json file.
The assets downloaded should be stripped down to as little as needed
before checking in, but the files should be checked into the repository.


Testing
=======

The project is setup with
`tox <https://tox.readthedocs.org/en/latest/>`_ and
`py.test <http://pytest.org/latest/>`_. It will run pylint, pep8, and
py.test tests with coverage. It will also generate an HTML coverage
report. To run them all inside the docker image, run ``docker-compose
run web tox``, or if you are running locally, after installing the
requirements file, just run ``tox``.


Continuous Testing
~~~~~~~~~~~~~~~~~~

If you want test to run on file changes, the ``test_requirements.txt``
adds pytest-watcher, which can be started with:
``docker-compose run web ptw --poll``
For additional options like having it say "passed"
out loud, or sending desktop notifications for failures see the
`README <https://github.com/joeyespo/pytest-watch/blob/master/README.md>`_.
Keep in mind, there can be a bit of a lag between saves and the test running.
