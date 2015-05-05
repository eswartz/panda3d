"""
Show how to use libRocket in Panda3D.
"""
import sys
from panda3d.core import loadPrcFile, loadPrcFileData  # @UnusedImport
import time

loadPrcFileData("", "model-path assets")

from direct.showbase.ShowBase import ShowBase
# workaround: https://www.panda3d.org/forums/viewtopic.php?t=10062&p=99697#p99054
#from panda3d import rocket
import _rocketcore as rocket
from panda3d.rocket import RocketRegion, RocketInputHandler

global globalClock

class MyApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        rocket.LoadFontFace("assets/modenine.ttf")

        r = RocketRegion.make('pandaRocket', self.win)
        r.setActive(1)

        ih = RocketInputHandler()
        self.mouseWatcher.attachNewNode(ih)
        r.setInputHandler(ih)

        context = r.getContext()

        self.accept('escape', sys.exit)

        self.document = context.LoadDocument("assets/loading.rml");
        if self.document:
            self.loadingDots = 0
            el = self.document.GetElementById('loadingLabel')
            self.loadingText = el.first_child
            self.stopLoadingTime = globalClock.getFrameTime() + 5
            self.taskMgr.add(self.cycle_loading, 'doc changer')
            self.document.Show()
        else:
            sys.exit(1)

    def cycle_loading(self, task):
        """
        Update the "loading" text in the initial window until
        sufficient time has elapsed (self.stopLoadingTime).
        """
        text = self.loadingText
        count = 5
        intv = int(globalClock.getFrameTime() * 4) % count  # @UndefinedVariable
        #text.text = "Loading" + ("." * (1+intv)) + (" " * (2 - intv))
        text.text = ("." * (count - intv)) + "loading" + ("." * (1+intv))
        if globalClock.getFrameTime() > self.stopLoadingTime:
            return task.done
        return task.cont

app = MyApp()
app.run()
