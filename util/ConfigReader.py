import os
import inspect
from configobj import ConfigObj

filedir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
basepath = os.path.join(os.path.dirname(filedir), 'Configuration')

def host_info(host_name):
    #host_name one of the following: Verify, Vote, Mix1, Mix2, Mix3
    c = ConfigObj(os.path.join(basepath, 'settings.ini'))

    return (c[host_name]['HOST'], c[host_name].as_int('PORT'))
