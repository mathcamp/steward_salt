""" steward_salt endpoints """
from pyramid.view import view_config

from .tasks import salt, salt_ssh, salt_call, salt_key, salt_match


@view_config(route_name='salt_match', renderer='json', permission='salt')
def do_salt_match(request):
    """
    Get a list of minions that match a salt target

    """
    tgt = request.param('tgt')
    expr_form = request.param('expr_form', 'glob')
    return salt_match(tgt, expr_form)


@view_config(route_name='salt', renderer='json', permission='salt')
def do_salt_cmd(request):
    """ Run a salt command """
    tgt = request.param('tgt')
    cmd = request.param('cmd')
    args = request.param('arg', [], type=list)
    kwargs = request.param('kwarg', {}, type=dict)
    expr_form = request.param('expr_form', 'glob')
    timeout = request.param('timeout', 10, type=int)
    return salt(tgt, cmd, arg=args, timeout=timeout, expr_form=expr_form,
                kwarg=kwargs)


@view_config(route_name='salt_ssh', renderer='json', permission='salt')
def do_salt_ssh_cmd(request):
    """ Run a salt command over ssh """
    tgt = request.param('tgt')
    cmd = request.param('cmd')
    args = request.param('arg', [], type=list)
    kwargs = request.param('kwarg', {}, type=dict)
    expr_form = request.param('expr_form', 'glob')
    timeout = request.param('timeout', 10, type=int)
    return salt_ssh(tgt, cmd, arg=args, timeout=timeout, expr_form=expr_form,
                    kwarg=kwargs)


@view_config(route_name='salt_call', renderer='json', permission='salt')
def do_salt_call(request):
    """ Run a local salt command """
    cmd = request.param('cmd')
    args = request.param('arg', [], type=list)
    kwargs = request.param('kwarg', {}, type=dict)
    return salt_call(cmd, *args, **kwargs)


@view_config(route_name='salt_key', renderer='json', permission='salt')
def do_salt_key(request):
    """ Run a command on the salt Key instance """
    cmd = request.param('cmd')
    arg = request.param('arg', [], type=list)
    kwarg = request.param('kwarg', {}, type=dict)
    return salt_key(cmd, *arg, **kwarg)
