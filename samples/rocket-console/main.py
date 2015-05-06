"""
Show how to use libRocket in Panda3D.
"""
import sys
from panda3d.core import loadPrcFile, loadPrcFileData  # @UnusedImport
import time

loadPrcFileData("", "model-path ./assets")

from direct.showbase.ShowBase import ShowBase

# workaround: https://www.panda3d.org/forums/viewtopic.php?t=10062&p=99697#p99054
#from panda3d import rocket
import _rocketcore as rocket

from panda3d.rocket import RocketRegion, RocketInputHandler

global globalClock

class MyApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        self.loadRocketFonts()

        self.windowRocketRegion = RocketRegion.make('pandaRocket', self.win)
        self.windowRocketRegion.setActive(1)

        ih = RocketInputHandler()
        self.mouseWatcher.attachNewNode(ih)
        self.windowRocketRegion.setInputHandler(ih)

        self.context = self.windowRocketRegion.getContext()

        #self.accept('escape', sys.exit)

        self.loadingDocument = self.context.LoadDocument("assets/loading.rml");
        if not self.loadingDocument:
            raise AssertionError("did not find loading.rml")

        self.loadingDots = 0
        el = self.loadingDocument.GetElementById('loadingLabel')
        self.loadingText = el.first_child
        self.stopLoadingTime = globalClock.getFrameTime() + 5
        self.loadingTask = self.taskMgr.add(self.cycleLoading, 'doc changer')
        
        self.loadingDocument.AddEventListener('click', 'self.on_loading_dialog_closed()', False)
        self.loadingDocument.Show()

    def loadRocketFonts(self):
        """ Load fonts referenced from e.g. 'font-family' RCSS directives.
        These are unfortunately not located using the model-path.
        TODO: should model-path be searched for these?
        """ 
        #rocket.LoadFontFace("modenine.ttf")
        rocket.LoadFontFace("assets/modenine.ttf")

    def cycleLoading(self, task):
        """
        Update the "loading" text in the initial window until
        sufficient time has elapsed (self.stopLoadingTime).
        """
        text = self.loadingText
        count = 5
        now = globalClock.getFrameTime()
        intv = int(now * 4) % count  # @UndefinedVariable
        #text.text = "Loading" + ("." * (1+intv)) + (" " * (2 - intv))
        text.text = ("." * (count - intv)) + "loading" + ("." * (1+intv))
        if now > self.stopLoadingTime:
            return task.done
        return task.cont

app = MyApp()
app.run()
