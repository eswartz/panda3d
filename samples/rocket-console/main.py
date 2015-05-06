"""
Show how to use libRocket in Panda3D.
"""
import sys
from panda3d.core import loadPrcFile, loadPrcFileData, Point3,Vec4, LoaderOptions  # @UnusedImport
from panda3d.core import DirectionalLight, AmbientLight, PointLight
from panda3d.core import Texture, PNMImage
import time
from direct.interval.MetaInterval import Parallel, Sequence
from direct.interval.LerpInterval import LerpHprInterval, LerpPosInterval, LerpFunc

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

        self.win.setClearColor(Vec4(0.2, 0.2, 0.2, 1))

        self.disableMouse()

        dlight = DirectionalLight('dlight')
        alight = AmbientLight('alight')
        dlnp = self.render.attachNewNode(dlight)
        alnp = self.render.attachNewNode(alight)
        dlight.setColor((0.8, 0.8, 0.5, 1))
        alight.setColor((0.2, 0.2, 0.2, 1))
        dlnp.setHpr(0, -60, 0)
        self.render.setLight(dlnp)
        self.render.setLight(alnp)

        # Put lighting on the main scene
        plight = PointLight('plight')
        plnp = render.attachNewNode(plight)
        plnp.setPos(0, 0, 10)
        self.render.setLight(plnp)
        self.render.setLight(alnp)

        self.loadRocketFonts()

        self.loadingTask = None

        self.startModelLoading()

        self.openLoadingDialog()

    def loadRocketFonts(self):
        """ Load fonts referenced from e.g. 'font-family' RCSS directives.
        These are unfortunately not located using the model-path.
        TODO: should model-path be searched for these?
        """
        #rocket.LoadFontFace("modenine.ttf")
        rocket.LoadFontFace("assets/modenine.ttf")
        rocket.LoadFontFace("assets/D3Electronism.ttf")

    def startModelLoading(self):
        self.monitorNP = None
        self.keyboardNP = None
        self.loadingError = False

        # force the "loading" to take some time after the first run...
        options = LoaderOptions()
        options.setFlags(options.getFlags() | LoaderOptions.LFNoCache)

        def gotMonitorModel(model):
            if not model:
                self.loadingError = True
            self.monitorNP = model

        self.loader.loadModel("monitor", loaderOptions=options, callback=gotMonitorModel)

        def gotKeyboardModel(model):
            if not model:
                self.loadingError = True
            self.keyboardNP = model

        self.loader.loadModel("takeyga_kb", loaderOptions=options, callback=gotKeyboardModel)

    def openLoadingDialog(self):
        self.windowRocketRegion = RocketRegion.make('pandaRocket', self.win)
        self.windowRocketRegion.setActive(1)

        ih = RocketInputHandler()
        self.mouseWatcher.attachNewNode(ih)
        self.windowRocketRegion.setInputHandler(ih)

        self.windowContext = self.windowRocketRegion.getContext()

        self.loadingDocument = self.windowContext.LoadDocument("assets/loading.rml");
        if not self.loadingDocument:
            raise AssertionError("did not find loading.rml")

        self.loadingDots = 0
        el = self.loadingDocument.GetElementById('loadingLabel')
        self.loadingText = el.first_child
        self.stopLoadingTime = globalClock.getFrameTime() + 5
        self.loadingTask = self.taskMgr.add(self.cycleLoading, 'doc changer')

        self.attachCustomRocketEvent()

        self.loadingDocument.Show()

    def attachCustomRocketEvent(self):
        # handle custom event

        # note: you may encounter errors like 'KeyError: 'document'"
        # when invoking events using methods from your own scripts with this
        # obvious code:
        # self.loadingDocument.AddEventListener('aboutToClose',
        #                                       self.onLoadingDialogDismissed, True)
        #
        # a workaround is to define callback methods in standalone Python
        # files with event, self, and document defined to None.
        #
        # see https://www.panda3d.org/forums/viewtopic.php?f=4&t=16412

        # Or, use this indirection technique to work around the problem:
        #
        # unfortunately, it loses any data passed from Rocket via DispatchEvent() :(

        self.loadingDocument.AddEventListener(
            'aboutToClose',     # rocket event
            "messenger.send('loadingAboutToClose')")       # Panda3D event

        def handleAboutToClose():
            if self.monitorNP and self.keyboardNP:
                self.onLoadingDialogDismissed()

        self.accept('loadingAboutToClose', handleAboutToClose)


    def cycleLoading(self, task):
        """
        Update the "loading" text in the initial window until
        the user presses Space, Enter, or Escape or clicks (see loading.rxml)
        or sufficient time has elapsed (self.stopLoadingTime).
        """
        text = self.loadingText

        now = globalClock.getFrameTime()
        if self.monitorNP and self.keyboardNP:
            text.text = "Ready"
            if now > self.stopLoadingTime:
                self.onLoadingDialogDismissed()
                return task.done
        elif self.loadingError:
            text.text = "Assets not found"
        else:
            count = 5
            intv = int(now * 4) % count  # @UndefinedVariable
            text.text = "Loading" + ("." * (1+intv)) + (" " * (2 - intv))

        return task.cont

    def onLoadingDialogDismissed(self):
        if self.loadingDocument:
            self.taskMgr.remove(self.loadingTask)
            self.loadingTask = None

            self.loadingText.text = 'Starting...'
            def updateAlpha(t):
                attr = 'color: rgba(192,255,255,' + str(int(t)) +');'
                self.loadingText.SetAttribute('style', attr)

            alphaInterval = LerpFunc(updateAlpha,
                                 duration=1,
                                 fromData=255,
                                 toData=0)

            alphaInterval.setDoneEvent('fadeOutFinished')

            def fadeOutFinished():
                self.loadingDocument.Close()
                self.loadingDocument = None
                self.createConsole()

            self.accept('fadeOutFinished', fadeOutFinished)

            alphaInterval.start()

    def createConsole(self):
        # create the in-world console

        self.monitorNP.reparentTo(self.render)
        faceplate = self.monitorNP.find("**/Faceplate")

        tex = Texture()
        image = PNMImage(256, 256)
        image.fill(0)
        tex.load(image)
        faceplate.setTexture(tex, 1)

        self.keyboardNP.reparentTo(self.render)
        self.keyboardNP.setHpr(-90, 0, 15)
        self.keyboardNP.setScale(15)

        self.placeItems()

    def placeItems(self):
        self.camera.setPos(0, -20, 0)
        self.camera.setHpr(0, 0, 0)
        self.keyboardNP.setPos(0, -5, -2.5)

        self.win.setClearColor(Vec4(0.5, 0.5, 0.8, 1))

app = MyApp()
app.run()
