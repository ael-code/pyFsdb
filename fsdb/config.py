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


def normalizeConf(oldConf):

    if not isinstance(oldConf, dict):
        raise TypeError(TAG + ": bad format for config file, not a `dict`")

    conf = oldConf.copy()

    if 'fmode' not in conf:
        conf['fmode'] = int(__defaults['fmode'], 8)
    elif not isinstance(conf['fmode'], string_types):
        raise TypeError(TAG + ": `fmode` must be a string")
    else:
        conf['fmode'] = int(conf['fmode'], 8)

    if 'dmode' not in conf:
        conf['dmode'] = calc_dir_mode(conf['fmode'])
    elif not isinstance(conf['dmode'], string_types):
        raise TypeError(TAG + ": `dmode` must be a string")
    else:
        conf['dmode'] = int(conf['dmode'], 8)

    if 'depth' not in conf:
        conf['depth'] = __defaults['depth']
    elif not isinstance(conf['depth'], int):
        raise TypeError(TAG + ": `depth` must be an int")
    elif conf['depth'] < 0:
        raise ValueError(TAG + ": `depth` must be a positive number")

    if 'hash_alg' not in conf:
        conf['hash_alg'] = __defaults['hash_alg']
    elif not isinstance(conf['hash_alg'], string_types):
        raise TypeError(TAG + ": `hash_alg` must be a string")
    elif conf['hash_alg'] not in ACCEPTED_HASH_ALG:
        raise ValueError(TAG + ": `hash_alg` must be one of " + str(ACCEPTED_HASH_ALG))

    return conf


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


def loadConf(configPath):
    with open(configPath, 'r') as configFile:
        conf = json.load(configFile)

    return normalizeConf(conf)


def writeConf(configPath, conf):
    if not isinstance(conf, dict):
        raise TypeError(TAG + ": bad format for config file, not a `dict`")

    mConf = conf.copy()
    to_json_format(mConf)

    with open(configPath, 'w') as outfile:
        json.dump(mConf, outfile, indent=4)
