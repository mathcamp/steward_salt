""" steward_salt endpoints """
import yaml
from pyramid.view import view_config


@view_config(route_name='salt_match', renderer='json', permission='salt')
def salt_match(request):
    """
    Get a list of minions that match a salt target

    """
    tgt = request.param('tgt')
    expr_form = request.param('expr_form', 'glob')
    return request.salt_checker.check_minions(tgt, expr_form)


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


@view_config(route_name='salt_ssh', renderer='json', permission='salt')
def do_salt_ssh_cmd(request):
    """ Run a salt command over ssh """
    tgt = request.param('tgt')
    cmd = request.param('cmd')
    args = request.param('arg', [], type=list)
    kwargs = request.param('kwarg', {}, type=dict)
    expr_form = request.param('expr_form', 'glob')
    timeout = request.param('timeout', 10, type=int)
    return request.salt_ssh.cmd(tgt, cmd, arg=args, timeout=timeout,
                                expr_form=expr_form, kwarg=kwargs)


@view_config(route_name='salt_call', renderer='json', permission='salt')
def do_salt_call(request):
    """ Run a local salt command """
    cmd = request.param('cmd')
    args = request.param('arg', [], type=list)
    kwargs = request.param('kwarg', {}, type=dict)
    for key, value in kwargs.iteritems():
        # We have to split it because yaml ends with \n...\n
        yaml_val = yaml.safe_dump(value).split('...')[0].strip()
        args.append('%s=%s' % (key, yaml_val))
    return request.salt_caller.function(cmd, *args)


@view_config(route_name='salt_key', renderer='json', permission='salt')
def do_salt_key(request):
    """ Run a command on the salt Key instance """
    cmd = request.param('cmd')
    arg = request.param('arg', [], type=list)
    kwarg = request.param('kwarg', {}, type=dict)
    fxn = getattr(request.salt_key, cmd)
    return fxn(*arg, **kwarg)
