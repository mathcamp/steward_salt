""" Steward extension that integrates with salt """
import logging
import salt.client.ssh
import salt.config
import salt.key
import salt.utils


LOG = logging.getLogger(__name__)


def validate_state(retval):
    """
    Validate that a state run completed normally

    Parameters
    ----------
    retval : dict
        The response from a LocalClient.cmd() on a state.highstate or state.sls

    """
    success = True
    for data in retval.itervalues():
        for result in data.itervalues():
            if not result.get('result'):
                success = False
                break
    return success


def include_client(client):
    """ Add commands to client """
    client.set_cmd('salt', 'steward_salt.client.do_salt')
    client.set_cmd('salt.ssh', 'steward_salt.client.do_salt_ssh')
    client.set_cmd('salt.call', 'steward_salt.client.do_salt_call')
    client.set_cmd('omnishell', 'steward_salt.client.do_omnishell')


class SaltTaskMixin(object):

    """ Celery task mixin with salt objects """
    _salt = None
    _salt_opts = None
    _salt_ssh = None
    _salt_caller = None
    _salt_key = None
    _salt_checker = None

    @property
    def salt_opts(self):
        """ Get the salt opts from the salt config file """
        if self._salt_opts is None:
            salt_conf = self.config.settings.get('salt.master_config',
                                                 '/etc/salt/master')
            self._salt_opts = salt.config.master_config(salt_conf)
        return self._salt_opts

    @property
    def salt(self):
        """ Get the salt local client """
        if self._salt is None:
            self._salt = salt.client.LocalClient()
        return self._salt

    @property
    def salt_ssh(self):
        """ Get the salt-ssh client """
        if self._salt_ssh is None:
            self._salt_ssh = salt.client.SSHClient()
        return self._salt_ssh

    @property
    def salt_caller(self):
        """ Get the salt caller """
        if self._salt_caller is None:
            self._salt_caller = salt.client.Caller()
        return self._salt_caller

    @property
    def salt_key(self):
        """ Get the salt-key object """
        if self._salt_key is None:
            self._salt_key = salt.key.Key(self.salt_opts)
        return self._salt_key

    @property
    def salt_checker(self):
        """ Get the minion checker """
        if self._salt_checker is None:
            self._salt_checker = salt.utils.minions.CkMinions(self.salt_opts)
        return self._salt_checker


def include_tasks(config):
    """ Add tasks """
    config.mixins.append(SaltTaskMixin)


def includeme(config):
    """ Configure the app """
    config.add_route('salt', '/salt')
    config.add_route('salt_ssh', '/salt/ssh')
    config.add_route('salt_call', '/salt/call')
    config.add_route('salt_key', '/salt/key')
    config.add_route('salt_match', '/salt/match')
    config.add_acl_from_settings('salt')

    config.scan()
