""" Salt tasks """
import threading
import yaml
from celery.signals import beat_init
from salt.utils.event import MasterEvent
from steward_tasks.tasks import pub, config_settings

from salt import config as salt_config
from steward_tasks import celery, StewardTask


@celery.task(base=StewardTask)
def salt(tgt, cmd, arg=(), timeout=10, expr_form='glob', kwarg=None):
    """ Run a salt command """
    kwarg = kwarg or {}
    return salt.salt.cmd(tgt, cmd, arg=arg, timeout=timeout,
                         expr_form=expr_form, kwarg=kwarg)


@celery.task(base=StewardTask)
def salt_ssh(tgt, cmd, arg=(), timeout=10, expr_form='glob', kwarg=None):
    """ Run a salt command via the ssh transport """
    kwarg = kwarg or {}
    return salt_ssh.salt_ssh.cmd(tgt, cmd, arg=arg, timeout=timeout,
                                 expr_form=expr_form, kwarg=kwarg)


@celery.task(base=StewardTask)
def salt_call(cmd, *arg, **kwargs):
    """ Run a salt command via salt-call """
    args = list(arg)
    for key, value in kwargs.iteritems():
        # We have to split it because yaml ends with \n...\n
        yaml_val = yaml.safe_dump(value).split('...')[0].strip()
        args.append('%s=%s' % (key, yaml_val))
    return salt_call.salt_caller.function(cmd, *args)


@celery.task(base=StewardTask)
def salt_key(cmd, *args, **kwargs):
    """ Run a command on salt-key """
    fxn = getattr(salt_key.salt_key, cmd)
    return fxn(*args, **kwargs)


@celery.task(base=StewardTask)
def salt_match(tgt, expr_form='glob'):
    """ Find all minions matching a target """
    return salt_match.salt_checker.check_minions(tgt, expr_form)


class EventListener(threading.Thread):

    """
    Background thread that listens for salt events and replays them as steward
    events

    """
    def __init__(self, settings):
        super(EventListener, self).__init__()
        salt_conf = settings.get('salt.master_config', '/etc/salt/master')
        salt_opts = salt_config.master_config(salt_conf)
        self.daemon = True
        self.event = MasterEvent(salt_opts['sock_dir'])

    def run(self):
        while True:
            data = self.event.get_event()
            if data and 'tag' in data:
                name = 'salt/' + data['tag']
                if 'tok' in data:
                    del data['tok']
                pub.delay(name, data)


@beat_init.connect
def listen_for_salt_events(signal, sender):
    """ On startup, start a background thread to listen for salt events """
    settings = config_settings.delay().get()
    event = EventListener(settings)
    event.start()
