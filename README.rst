Steward Salt
============
This is a Steward extension for integrating with Salt.

Setup
=====
To use steward_salt, just add it to your includes either programmatically::

    config.include('steward_salt')

or in the config.ini file::

    pyramid.includes = steward_salt

Make sure you include it in the client config file as well.

Configuration
=============
* **salt.master_config** - The location of the salt master configuration file (defaults to /etc/salt/master)

Permissions
===========
* **salt.perm.salt** - This permission is required to make calls to salt

Notes
=====
In addition to exposing the Salt client, ``steward_salt`` listens for Salt
events and replays them as Steward events with the prefix 'salt/'. So when Salt
receives a 'minion_start' event, Steward will fire a 'salt/minion_start' event.
