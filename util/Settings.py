import os
import inspect
from configobj import ConfigObj

filedir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
basepath = os.path.join(os.path.dirname(filedir), 'Configuration')

def mix_count():
    c = ConfigObj(os.path.join(basepath, 'settings.ini'))
    
    return c.as_int('MixServerCount')

def host_info(host_name):
    #host_name one of the following: Verify, Vote, Mix1, Mix2, Mix3
    c = ConfigObj(os.path.join(basepath, 'settings.ini'))

    return (c[host_name]['HOST'], c[host_name].as_int('PORT'))

def generate_rand_votes(count=200):
    #Votes consist of a range of numbers from 1 to 5
    from random import choice

    vote_range = range(1, 6)
    votes = [choice(vote_range) for i in range(count)]

    return map(str, votes)
