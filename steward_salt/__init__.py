""" Steward extension that integrates with salt """
import json
import threading

import salt.client
import salt.config
import salt.key
import salt.utils


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


class EventListener(threading.Thread):
    """
    Background thread that listens for salt events and replays them as steward
    events

    """
    def __init__(self, config):
        super(EventListener, self).__init__()
        self.daemon = True
        self._config = config
        self.event = salt.utils.event.MasterEvent(
            config.registry.salt_opts['sock_dir'])

    def run(self):
        while True:
            data = self.event.get_event()
            if data:
                if 'tag' in data:
                    name = 'salt/' + data['tag']
                    self._config.post('pub', data={'name':name,
                                                   'data':json.dumps(data)})


def include_client(client):
    """ Add commands to client """
    client.set_cmd('salt', 'steward_salt.client.do_salt')
    client.set_cmd('salt.call', 'steward_salt.client.do_salt_call')

def includeme(config):
    """ Configure the app """
    settings = config.get_settings()
    config.add_request_method(_salt_client, name='salt', reify=True)
    config.add_request_method(_salt_caller, name='salt_caller', reify=True)
    config.add_request_method(_salt_key, name='salt_key', reify=True)
    config.add_route('salt', '/salt')
    config.add_route('salt_call', '/salt/call')
    config.add_route('salt_key', '/salt/key')
    config.add_acl_from_settings('salt')
    salt_conf = settings.get('salt.master_config', '/etc/salt/master')
    config.registry.salt_opts = salt.config.master_config(salt_conf)

    config.scan()
    event = EventListener(config)
    event.start()
