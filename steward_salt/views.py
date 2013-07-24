""" steward_salt endpoints """
import yaml
from pyramid.view import view_config
import fnmatch
import re

@view_config(route_name='salt_match', renderer='json', permission='salt')
def salt_match(request):
    """
    Get a list of minions that match a salt target

    Notes
    =====
    This is currently incomplete and only works for certain expr_forms. Salt
    does not expose their matching API. See
    https://github.com/saltstack/salt/issues/4957 for more details.

    """
    tgt = request.param('tgt')
    expr_form = request.param('expr_form', 'glob')
    minions = request.salt_key.list_keys()['minions']
    if expr_form == 'glob':
        return [minion for minion in minions if fnmatch.fnmatch(minion, tgt)]
    elif expr_form == 'pcre':
        return [minion for minion in minions if re.match(tgt, minion)]
    elif expr_form == 'list':
        targeted = set(tgt.split(','))
        return [minion for minion in minions if minion in targeted]
    else:
        return None

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
    for key, value in kwargs.iteritems():
        # We have to split it because yaml ends with \n...\n
        yaml_val = yaml.safe_dump(value).split('\n')[0]
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
