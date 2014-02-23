import os
import inspect
from configobj import ConfigObj

filedir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
basepath = os.path.join(os.path.dirname(filedir), 'Configuration')

def host_info(host_name):
    c = ConfigObj(os.path.join(basepath, '{}_server.ini'.format(host_name)))

    return (c['HOST'], c.as_int('PORT'))
