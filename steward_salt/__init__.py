""" Steward extension that integrates with salt """
import json
import salt.client
import salt.utils
import threading
from pprint import pprint
from pyramid.view import view_config


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

@view_config(route_name='salt', renderer='json', permission='salt')
def do_salt_cmd(request):
    """ Run a salt command """
    tgt = request.param('tgt')
    cmd = request.param('cmd')
    args = request.param('arg', [], type=list)
    kwargs = request.param('kwarg', {}, type=dict)
    expr_form = request.param('expr_form', 'glob')
    timeout = request.param('timeout', 10, type=int)
    return request.salt.cmd(tgt, cmd, arg=args, timeout=timeout,
                            expr_form=expr_form, kwarg=kwargs)

@view_config(route_name='salt_call', renderer='json', permission='salt')
def do_salt_call(request):
    """ Run a local salt command """
    cmd = request.param('cmd')
    args = request.param('arg', [], type=list)
    kwargs = request.param('kwarg', {}, type=dict)
    return request.salt_caller.function(cmd, *args, **kwargs)

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

class EventListener(threading.Thread):
    """
    Background thread that listens for salt events and replays them as steward
    events

    """
    def __init__(self, config):
        super(EventListener, self).__init__()
        self.daemon = True
        self._config = config
        settings = config.get_settings()
        salt_conf_dir = settings.get('salt.master_config', '/etc/salt/master')
        salt_conf = salt.config.master_config(salt_conf_dir)
        self.event = salt.utils.event.MasterEvent(salt_conf['sock_dir'])

    def run(self):
        while True:
            data = self.event.get_event()
            if data:
                if 'tag' in data:
                    name = 'salt/' + data['tag']
                    self._config.post('pub', data={'name':name,
                                                   'data':json.dumps(data)})

def do_salt(client, tgt, cmd, *args, **kwargs):
    """
    Run a command using salt

    Parameters
    ----------
    tgt : str
        The servers to run the command on
    cmd : str
        The salt module to run
    timeout : int, optional
        How long to wait for a response from the minions
    expr_form : str, optional
        The format of the target str (default 'glob')
    args : list
        List of positional arguments to pass to the command
    kwargs : dict
        Dict of keyword arguments to pass to the command

    """
    timeout = kwargs.pop('timeout', None)
    expr_form = kwargs.pop('expr_form', None)
    data = {
        'tgt': tgt,
        'cmd': cmd,
        'arg': args,
        'kwarg': kwargs,
    }
    if timeout is not None:
        data['timeout'] = timeout
    if expr_form is not None:
        data['expr_form'] = expr_form
    response = client.cmd('salt', **data)
    pprint(response.json())

def salt_call(client, cmd, *args, **kwargs):
    """
    Run a salt command on the server

    Parameters
    ----------
    cmd : str
        The salt module to run
    args : list
        List of positional arguments to pass to the command
    kwargs : dict
        Dict of keyword arguments to pass to the command

    """
    response = client.cmd('salt/call', cmd=cmd, arg=args, kwarg=kwargs)
    pprint(response.json())

def include_client(client):
    """ Add commands to client """
    client.set_cmd('salt', do_salt)
    client.set_cmd('salt.call', salt_call)

def includeme(config):
    """ Configure the app """
    config.add_request_method(_salt_client, name='salt', reify=True)
    config.add_request_method(_salt_caller, name='salt_caller', reify=True)
    config.add_route('salt', '/salt')
    config.add_route('salt_call', '/salt/call')
    config.add_acl_from_settings('salt')

    config.scan()
    event = EventListener(config)
    event.start()
