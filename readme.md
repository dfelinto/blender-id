The Blender ID
==============

Bringing all web applications together!


Installation & Configuration
----------------------------

Create a copy of `config.py.example` and name it `config.py`. Adapt it
to your needs/environment.

Installation requires a MySQL database, the URL of which can be set in
`config.py`. Make sure the named database exists (it can be empty).

Make sure you also have the Git submodule:

    git submodule update --init --recursive

Install NPM, the node.js package manager. This is OS-specific, and out
of scope for this documentation. Once installed, run:

    npm install
    ./node_modules/.bin/gulp

Run these commands to install the Python dependencies and get your
database in shape:

- `pip install -r requirements.txt`: installs Python dependencies.
- `cd blender-id`
- `python manage.py db upgrade`: upgrades the database to the latest
  schema version.
- `python manage.py create_oauth_clients`: creates the default OAuth
  clients you added to `config.py`.

A test server can then be run using `python manage.py runserver`. Create
a new user and log in!


Notes
-----

These are some notes to help you get everything up & running.

- When authenticating a web application, that application and Blender ID
  should run on different hostnames. Just a different port number is not
  enough; add some hostnames as aliases for 'localhost' in /etc/hosts.


Running inside Docker
---------------------

To create the docker image, run:

    cd docker
    ./build.sh dev

Also do this after an upgrade that changed `requirements.txt`.
