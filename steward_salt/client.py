""" steward_salt client commands """
from pprint import pprint


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


def do_salt_ssh(client, tgt, cmd, *args, **kwargs):
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
    response = client.cmd('salt/ssh', **data)
    pprint(response.json())


def do_salt_call(client, mod, *args, **kwargs):
    """
    Run a salt command on the server

    Parameters
    ----------
    mod : str
        The salt module to run
    *args : list
        List of positional arguments to pass to the command
    **kwargs : dict
        Dict of keyword arguments to pass to the command

    """
    response = client.cmd('salt/call', cmd=mod, arg=args, kwarg=kwargs)
    pprint(response.json())


def do_omnishell(client):
    """ Activate the OMNISHELL """
    from .omnishell import load_dotfile, SaltTerm

    def delegate(transport, tgt, cmd, arg, timeout, expr_form):
        """ Delegates commands to the salt endpoints """
        if transport == 'zmq':
            return client.cmd('salt', tgt=tgt, cmd=cmd, arg=arg,
                              timeout=timeout, expr_form=expr_form).json()
        elif transport == 'ssh':
            return client.cmd('salt/ssh', tgt=tgt, cmd=cmd, arg=arg,
                              timeout=timeout, expr_form=expr_form).json()
        else:
            return "Unknown transport '%s'" % transport
    SaltTerm().start(delegate, load_dotfile())
