import json

CONFIG_SECTION = "fsdb"
DEFAULT_MODE = 0770
DEFAULT_DEEP = 3

TAG = "fsdb_config"

def loadConf(configPath):
   with open(configPath, 'r') as configFile:    
    conf = json.load(configFile)
   
   if not isinstance(conf,dict):
      raise TypeError(TAG+": bad format for config file, not a `dict`");
   
   if 'mode' not in conf:
      conf['mode'] = DEFAULT_MODE
   elif not isinstance(conf['mode'],basestring):
      raise TypeError(TAG+": `mode` must be a string")
   else:
      conf['mode']= int(conf['mode'], 8)
   
   if 'deep' not in conf:
      conf['deep'] = DEFAULT_DEEP
   elif not isinstance(conf['deep'],int):
      raise TypeError(TAG+": `deep` must be an int")
   elif conf['deep'] < 0:
      raise ValueError(TAG+": `deep` must be a positive number")
      
   return conf

def writeConf(configPath, conf):
   if not isinstance(conf,dict):
      raise TypeError(TAG+": bad format for config file, not a `dict`");
   
   mConf = conf.copy()
   
   if 'mode' in mConf:
      mConf['mode'] = str(oct(mConf['mode']))
      
   with open(configPath, 'w') as outfile:
      json.dump(mConf, outfile, indent = 4)

def getDefaultConf():
   return {'mode':DEFAULT_MODE,'deep':DEFAULT_DEEP}
