
from pymjin2 import *

class Test(object):
    def __init__(self, sceneName, nodeName, env):
        self.name = "Test/" + nodeName
        print "{0}.__init__({1})".format(self.name, id(self))
    def __del__(self):
        print "{0}.__del__({1})".format(self.name, id(self))

def SCRIPT_CREATE(sceneName, nodeName, env):
    return Test(sceneName, nodeName, env)

def SCRIPT_DESTROY(instance):
    del instance

