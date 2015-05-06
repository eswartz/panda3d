"""
Simple console widget for rocket
"""
import sys

# workaround: https://www.panda3d.org/forums/viewtopic.php?t=10062&p=99697#p99054
#from panda3d import rocket
import _rocketcore as rocket

from panda3d.rocket import RocketRegion, RocketInputHandler

class Console(object):
    def __init__(self, base, context, cols, rows, commandHandler):
        self.base = base

        self.context = context
        self.loadFonts()
        self.cols = cols
        self.rows = rows
        self.commandHandler = commandHandler

        self.allowEditing(True)
        self.input = ""
        self.setupConsole()

    def getTextContainer(self):
        return self.textEl

    def setPrompt(self, prompt):
        self.consolePrompt = prompt

    def allowEditing(self, editMode):
        self.editMode = editMode

    def loadFonts(self):
        rocket.LoadFontFace("assets/Perfect DOS VGA 437.ttf")

    def setupConsole(self):
        self.document = self.context.LoadDocument("assets/console.rml");
        if not self.document:
            raise AssertionError("did not find console.rml")

        el = self.document.GetElementById('content')

        self.textEl = el

        # roundabout way of accessing the current object through rocket event...

        # add attribute to let Rocket know about the receiver
        self.context.console = self

        # then reference through the string format (dunno how else to get the event...)
        self.document.AddEventListener(
            'keydown', 'document.context.console.handleKeyDown(event)', True)
        self.document.AddEventListener(
            'textinput', 'document.context.console.handleTextInput(event)', True)

        self.consolePrompt = "C:\\>"

        self.blinkState = False
        self.queueBlinkCursor()

        self.document.Show()

    def queueBlinkCursor(self):
        self.base.taskMgr.doMethodLater(0.2, self.blinkCursor, 'blinkCursor')

    def blinkCursor(self, task):
        self.blinkState = not self.blinkState
        if self.editMode:
            self.updateEditLine(self.input)
        self.queueBlinkCursor()

    def escape(self, text):
        return text. \
                replace('<', '&lt;'). \
                replace('>', '&gt;'). \
                replace('"', '&quot;')

    def addLine(self, text):
        curKids = list(self.textEl.child_nodes)
        while len(curKids) >= self.rows * 2:        # two kids per row: text, <br>
            self.textEl.RemoveChild(curKids[0])
            self.textEl.RemoveChild(curKids[1])
            curKids = curKids[2:]

        line = self.document.CreateTextNode(self.escape(text))
        self.textEl.AppendChild(line)
        self.lastLine = line
        self.textEl.AppendChild(self.document.CreateElement('br'))

    def addLines(self, lines):
        for line in lines:
            self.addLine(line)

    def updateEditLine(self, newInput=''):
        newText = self.consolePrompt + newInput
        self.lastLine.text = self.escape(newText) + (self.blinkState and '_' or '')
        self.input = newInput

    def handleKeyDown(self, event):
        if not self.editMode:
            return

        # handle control key
        keyId = event.parameters['key_identifier']
        if keyId == rocket.key_identifier.RETURN:
            # emit line without cursor
            self.blinkState = False
            self.updateEditLine(self.input)

            # handle command
            self.commandHandler(self.input)

            if self.editMode:
                # start with new "command"
                self.addLine(self.consolePrompt)
                self.updateEditLine("")

        elif keyId == rocket.key_identifier.BACK:
            self.updateEditLine(self.input[0:-1])

    def handleTextInput(self, event):
        if not self.editMode:
            return

        # handle normal text character
        data = event.parameters['data']
        if 32 <= data < 128:
            self.updateEditLine(self.input + chr(data))

    def newEditLine(self):
        self.addLine("")
        self.updateEditLine()

    def cls(self):
        curKids = list(self.textEl.child_nodes)
        for kid in curKids:
            self.textEl.RemoveChild(kid)