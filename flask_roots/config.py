import copy
import os


_config = {}

def get_config():
    if not _config:
        _config.update(_get_config())
    return copy.deepcopy(_config)

def _get_config():

    our_path = os.path.abspath(os.path.join(__file__, '..', '..'))

    root_path = os.environ.get('FLASK_ROOT_PATH')
    if not root_path:
        raise RuntimeError('environ missing FLASK_ROOT_PATH')

    instance_path = os.environ.get('FLASK_INSTANCE_PATH')
    if not instance_path:
        instance_path = os.path.join(root_path, 'var')

    # Scan $root/etc/flask for config files. They are included
    # in sorted order, without respect for the base of their path.
    config_files = set()
    for root in (our_path, root_path, instance_path):
        dir_path = os.path.join(root, 'etc', 'flask')
        if not os.path.exists(dir_path):
            continue
        for file_name in os.listdir(dir_path):
            if os.path.splitext(file_name)[1] == '.py':
                config_files.add(os.path.join(dir_path, file_name))

    config_files = sorted(config_files, key=lambda path: os.path.basename(path))

    config = {
        'DEBUG': False,
        'TESTING': False,
    }
    for k, v in os.environ.iteritems():
        if k.isupper() and k.startswith('FLASK_'):
            config[k[6:]] = v

    # These will never be allowed to change.
    basics = dict(
        ROOT_PATH=root_path,
        INSTANCE_PATH=instance_path,
    )
    basics['setdefault'] = config.setdefault

    for path in config_files:
        config.update(basics)
        execfile(path, config)

    config.update(basics)
    return dict((k, v) for k, v in config.iteritems() if k.isupper())


def setup_config(app):
    config = get_config()
    app.config.update(config)
    app.root_path = config['ROOT_PATH']
    app.instance_path = config['INSTANCE_PATH']


