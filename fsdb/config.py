from __future__ import unicode_literals
import json

from .utils import calc_dir_mode
from .compat import string_types


ACCEPTED_HASH_ALG = ['md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512']
TAG = "fsdb_config"

__defaults = dict(
        fmode="660",
        depth=3,
        hash_alg='sha1',
    )


def get_defaults():
    return __defaults.copy()


def update_backword(conf):
    # Previous to version 1.0 the depth parameter was called deep
    if 'depth' not in conf and 'deep' in conf:
        conf['depth'] = conf.pop('deep')


def check_config(conf):
    '''Type and boundary check'''
    if 'fmode' in conf and not isinstance(conf['fmode'], string_types):
        raise TypeError(TAG + ": `fmode` must be a string")

    if 'dmode' in conf and not isinstance(conf['dmode'], string_types):
        raise TypeError(TAG + ": `dmode` must be a string")

    if 'depth' in conf:
        if not isinstance(conf['depth'], int):
            raise TypeError(TAG + ": `depth` must be an int")
        if conf['depth'] < 0:
            raise ValueError(TAG + ": `depth` must be a positive number")

    if 'hash_alg' in conf:
        if not isinstance(conf['hash_alg'], string_types):
            raise TypeError(TAG + ": `hash_alg` must be a string")
        if conf['hash_alg'] not in ACCEPTED_HASH_ALG:
            raise ValueError(TAG + ": `hash_alg` must be one of " + str(ACCEPTED_HASH_ALG))


def from_json_format(conf):
    '''Convert fields of parsed json dictionary to python format'''
    if 'fmode' in conf:
        conf['fmode'] = int(conf['fmode'], 8)
    if 'dmode' in conf:
        conf['dmode'] = int(conf['dmode'], 8)


def to_json_format(conf):
    '''Convert fields of a python dictionary to be dumped in json format'''
    if 'fmode' in conf:
        conf['fmode'] = oct(conf['fmode'])[-3:]
    if 'dmode' in conf:
        conf['dmode'] = oct(conf['dmode'])[-3:]


def normalize_conf(conf):
    '''Check, convert and adjust user passed config

       Given a user configuration it returns a verified configuration with
       all parameters converted to the types that are needed at runtime.
    '''
    conf = conf.copy()
    # check for type error
    check_config(conf)
    # convert some fileds into python suitable format
    from_json_format(conf)
    if 'dmode' not in conf:
        conf['dmode'] = calc_dir_mode(conf['fmode'])
    return conf


def loadConf(configPath):
    with open(configPath, 'r') as configFile:
        loaded = json.load(configFile)
    return loaded


def writeConf(configPath, conf):
    with open(configPath, 'w') as outfile:
        json.dump(conf, outfile, indent=4)
