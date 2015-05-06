"""
Show how to use libRocket in Panda3D.
"""
import sys
from panda3d.core import loadPrcFile, loadPrcFileData, Point3,Vec4 # @UnusedImport
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

        self.openLoadingDialog()
        

    def loadRocketFonts(self):
        """ Load fonts referenced from e.g. 'font-family' RCSS directives.
        These are unfortunately not located using the model-path.
        TODO: should model-path be searched for these?
        """ 
        #rocket.LoadFontFace("modenine.ttf")
        rocket.LoadFontFace("assets/modenine.ttf")
        rocket.LoadFontFace("assets/D3Electronism.ttf")

    def openLoadingDialog(self):
        self.windowRocketRegion = RocketRegion.make('pandaRocket', self.win)
        self.windowRocketRegion.setActive(1)

        ih = RocketInputHandler()
        self.mouseWatcher.attachNewNode(ih)
        self.windowRocketRegion.setInputHandler(ih)

        self.windowContext = self.windowRocketRegion.getContext()

        #self.accept('escape', sys.exit)

        self.loadingDocument = self.windowContext.LoadDocument("assets/loading.rml");
        if not self.loadingDocument:
            raise AssertionError("did not find loading.rml")

        self.loadingDots = 0
        el = self.loadingDocument.GetElementById('loadingLabel')
        self.loadingText = el.first_child
        self.stopLoadingTime = globalClock.getFrameTime() + 5
        self.loadingTask = self.taskMgr.add(self.cycleLoading, 'doc changer')
        
        self.loadingDocument.AddEventListener('unload', self.onLoadingDialogClosed, False)
        self.loadingDocument.Show()

    def cycleLoading(self, task):
        """
        Update the "loading" text in the initial window until
        the user presses Enter or Escape or clicks (see loading.rxml)
        or sufficient time has elapsed (self.stopLoadingTime).
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
    
    def onLoadingDialogClosed(self):
        if self.loadingDocument:
            self.taskMgr.remove(self.loadingTask)
            self.loadingTask = None
            
            self.loadingDocument = None
            
            self.createConsole()
        
    def createConsole(self):
        # create the in-world console
        
        self.monitorNP = self.loader.loadModel("monitor")
        self.monitorNP.reparentTo(self.render) 
        faceplate = self.monitorNP.find("**/Faceplate")
        
        tex = Texture()
        image = PNMImage(256, 256)
        image.fill(0)
        tex.load(image)
        faceplate.setTexture(tex, 1)
        
        self.keyboardNP = self.loader.loadModel("takeyga_kb");
        self.keyboardNP.reparentTo(self.render) 
        self.keyboardNP.setHpr(-90, 0, 15)
        self.keyboardNP.setScale(15)
        self.keyboardNP.setPos(0, -1000, 10)
        
        zoomOutInterval = self.camera.posInterval(2,
                                                Point3(0, -20, 0),
                                                startPos=Point3(0, -1000, 0),
                                                blendType='easeOut')
        spinInterval = LerpHprInterval(self.monitorNP, 2,
                                                Point3(0, 0, 0),
                                                startHpr=Point3(0, 90, 90),
                                                blendType='easeOut')
        
        def backgroundColor(color):
            self.win.setClearColor(color)
            
        colorInterval = LerpFunc(backgroundColor,
                                 duration=3,
                                 fromData=self.win.getClearColor(),
                                 toData=Vec4(0.5, 0.5, 0.8, 1),
                                 blendType='easeIn')

        dropKeyboardInterval = LerpPosInterval(self.keyboardNP, 2, 
                                               Point3(0, -5, -2.5),
                                               startPos=Point3(0, -5, 10),
                                               blendType='easeOut')
        
        parallel = Parallel(zoomOutInterval, spinInterval, colorInterval)        
        sequence = Sequence(parallel, dropKeyboardInterval)
        sequence.start()

        
app = MyApp()
app.run()
