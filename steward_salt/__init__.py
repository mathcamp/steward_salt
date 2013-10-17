""" Steward extension that integrates with salt """
import json
import salt.client.ssh
import salt.config
import salt.key
import salt.utils
import threading


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


def _salt_client(request):
    """ Get the salt client """
    if not hasattr(request.registry, 'salt_client'):
        request.registry.salt_client = salt.client.LocalClient()
    return request.registry.salt_client


def _salt_ssh_client(request):
    """ Get the salt ssh client """
    if not hasattr(request.registry, 'salt_ssh_client'):
        request.registry.salt_ssh_client = salt.client.SSHClient()
    return request.registry.salt_ssh_client


def _salt_caller(request):
    """ Get the salt caller """
    if not hasattr(request.registry, 'salt_caller'):
        request.registry.salt_caller = salt.client.Caller()
    return request.registry.salt_caller


def _salt_key(request):
    """ Get a salt Key instance """
    if not hasattr(request.registry, 'salt_key'):
        request.registry.salt_key = salt.key.Key(request.registry.salt_opts)
    return request.registry.salt_key


def _salt_checker(request):
    """ Get the salt Minion Checker """
    if not hasattr(request.registry, 'salt_checker'):
        request.registry.salt_checker = salt.utils.minions.CkMinions(
            request.registry.salt_opts)
    return request.registry.salt_checker


class EventListener(threading.Thread):

    """
    Background thread that listens for salt events and replays them as steward
    events

    """
    def __init__(self, config, tasklist):
        super(EventListener, self).__init__()
        salt_conf = config.get('salt.master_config', '/etc/salt/master')
        salt_opts = salt.config.master_config(salt_conf)
        self.daemon = True
        self.tasklist = tasklist
        self.event = salt.utils.event.MasterEvent(salt_opts['sock_dir'])

    def run(self):
        while True:
            data = self.event.get_event()
            if data:
                if 'tag' in data:
                    name = 'salt/' + data['tag']
                    self.tasklist.post('pub', data={'name': name,
                                                    'data': json.dumps(data)})


def include_client(client):
    """ Add commands to client """
    client.set_cmd('salt', 'steward_salt.client.do_salt')
    client.set_cmd('salt.ssh', 'steward_salt.client.do_salt_ssh')
    client.set_cmd('salt.call', 'steward_salt.client.do_salt_call')
    client.set_cmd('omnishell', 'steward_salt.client.do_omnishell')


def include_tasks(config, tasklist):
    """ Add tasks """
    event = EventListener(config, tasklist)
    event.start()


def includeme(config):
    """ Configure the app """
    settings = config.get_settings()
    config.add_request_method(_salt_client, name='salt', reify=True)
    config.add_request_method(_salt_caller, name='salt_caller', reify=True)
    config.add_request_method(_salt_key, name='salt_key', reify=True)
    config.add_request_method(_salt_ssh_client, name='salt_ssh', reify=True)
    config.add_request_method(_salt_checker, name='salt_checker', reify=True)
    config.add_route('salt', '/salt')
    config.add_route('salt_ssh', '/salt/ssh')
    config.add_route('salt_call', '/salt/call')
    config.add_route('salt_key', '/salt/key')
    config.add_route('salt_match', '/salt/match')
    config.add_acl_from_settings('salt')
    salt_conf = settings.get('salt.master_config', '/etc/salt/master')
    config.registry.salt_opts = salt.config.master_config(salt_conf)

    config.scan()
