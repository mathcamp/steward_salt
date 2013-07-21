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

Events
======
If you want salt events to be published to Steward, you will need to set up
steward_tasks. The steward_tasks process will listen for salt events and post
them to Steward. Events will be prefixed with 'salt/'. So when Salt receives a
'minion_start' event, Steward will fire a 'salt/minion_start' event.

Configuration
=============
::

    # The location of the salt master configuration file (defaults to /etc/salt/master)
    salt.master_config = /etc/salt/master

Permissions
===========
::

    # This permission is required to make calls to salt
    salt.perm.salt = group1 group2
