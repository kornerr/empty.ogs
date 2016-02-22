
from pymjin2 import *

MAIN_BALL_NAME       = "ball"
MAIN_BALLS_NB        = 8
MAIN_CLEANER_NAME    = "cleaner"
MAIN_TRACK_PARTS_NB  = 8
MAIN_PLAIN_NAME      = "plain"
MAIN_CATCH_NAME      = "catch"
MAIN_SOUND_SELECTION = "soundBuffer.default.selection"
MAIN_SOUND_START     = "soundBuffer.default.start"

class MainImpl(object):
    def __init__(self, c):
        self.c = c
        self.trackPartID = 0
        self.ballInitialPos = None
        self.ballWaiting = None
        self.cleanerPicking = None
        self.ballsLeft = MAIN_BALLS_NB
        self.ballsCatched = 0
        self.isCatching = False
        self.isStarted = False
    def __del__(self):
        self.c = None
    def onBallStopped(self, key, value):
        # Ball stopped because of the catch. Do nothing.
        if (self.isCatching):
            return
        self.trackPartID = self.trackPartID + 1
        if (self.trackPartID == MAIN_TRACK_PARTS_NB):
            self.restartBallSequence()
        else:
            self.rollBall()
    def onBallWaiting(self, key, value):
        self.ballWaiting = None
        if (value[0] == "1"):
            self.ballWaiting = self.trackPartID
        self.tryToCatch()
    def onCatch(self, key, value):
        if (not self.isStarted):
            return
        nodeName = key[2]
        v = nodeName.split(MAIN_CATCH_NAME)
        if (len(v) == 2):
            self.c.set("$CLEANER.$SCENE.$CLEANER.catch", v[1])
            self.c.set("$SELSOUND.state", "play")
    def onCleanerPicking(self, key, value):
        self.cleanerPicking = None
        if (len(value[0])):
            self.cleanerPicking = int(value[0])
        self.tryToCatch()
    def onGameStart(self, key, value):
        self.isStarted = True
        print "Game started", key, value
        self.ballInitialPos = self.c.get("node.$SCENE.$BALL.position")[0]
        self.rollBall()
        self.c.set("$STARTSOUND.state", "play")
    def restartBallSequence(self):
        self.ballsLeft = self.ballsLeft - 1
        if (self.ballsLeft == 0):
            print "Game is over"
            print "Result: catched / overall", self.ballsCatched, MAIN_BALLS_NB
            if (self.ballsCatched == MAIN_BALLS_NB):
                print "YOU WON"
            else:
                print "YOU LOST"
        else:
            self.trackPartID = 0
            self.rollBall()
    def rollBall(self):
        self.c.set("node.$SCENE.$BALL.parent",
                   MAIN_PLAIN_NAME + str(self.trackPartID))
        self.c.set("node.$SCENE.$BALL.position", self.ballInitialPos)
        self.c.set("ball.$SCENE.$BALL.moving", "1")
    def stopBall(self):
        self.c.set("ball.$SCENE.$BALL.moving", "0")
    def tryToCatch(self):
        if ((self.ballWaiting is not None) and
            (self.cleanerPicking is not None) and
            self.ballWaiting == self.cleanerPicking):
            self.ballsCatched = self.ballsCatched + 1
            print "catched the ball at", self.ballWaiting
            self.isCatching = True
            self.stopBall()
            self.isCatching = False
            # Restart the sequence.
            self.restartBallSequence()
            print "catched/left", self.ballsCatched, self.ballsLeft

class Main(object):
    def __init__(self, sceneName, nodeName, env):
        self.c = EnvironmentClient(env, "Main")
        self.impl = MainImpl(self.c)
        self.c.setConst("SCENE",      sceneName)
        self.c.setConst("BALL",       MAIN_BALL_NAME)
        self.c.setConst("CLEANER",    MAIN_CLEANER_NAME)
        self.c.setConst("SELSOUND",   MAIN_SOUND_SELECTION)
        self.c.setConst("STARTSOUND", MAIN_SOUND_START)
        self.c.listen("input.SPACE.key", "1", self.impl.onGameStart)
        self.c.listen("$BALL.$SCENE.$BALL.moving", "0", self.impl.onBallStopped)
        self.c.listen("node.$SCENE..selected", "1", self.impl.onCatch)
        self.c.listen("$CLEANER.$SCENE.$CLEANER.picking", None, self.impl.onCleanerPicking)
        self.c.listen("$BALL.$SCENE.$BALL.waiting", None, self.impl.onBallWaiting)
    def __del__(self):
        # Tear down.
        self.c.clear()
        # Destroy.
        del self.impl
        del self.c

def SCRIPT_CREATE(sceneName, nodeName, env):
    return Main(sceneName, nodeName, env)

def SCRIPT_DESTROY(instance):
    del instance

