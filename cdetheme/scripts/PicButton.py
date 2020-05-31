#!/usr/bin/python
import sys
from PyQt4 import QtCore, QtGui
from JosQPainter import JosQPainter
#import signal
#signal.signal(signal.SIGINT, signal.SIG_DFL)
#https://stackoverflow.com/questions/3400525/global-variable-from-a-different-file-python
import Globals
from Opts import Opts
from WorkspaceFuncs import purgeBlinkerList

#tags are global resource images from Globals.IMG[tag]
class PicButton(QtGui.QAbstractButton):
    def __init__(self, filebgtag, filebgpressedtag, fileicon, opts, parent=None):
    #def __init__(self, parent=None):
        super(PicButton, self).__init__(parent)
        self.filebgtag=filebgtag
        self.filebgpressedtag=filebgpressedtag
        #distinguis between drawers and launchers. Set when necessary
        self.isDrawer=False
        self.isLauncher=False
        self.isWorkspaceButton=False
        #hmm
        #if filebgtag==None or filebgpressedtag==None or fileicon==None or filebgtag=='' or filebgpressedtag=='' or fileicon=='':
            #print 'PICBUTTON NO IMAGE GIVEN '
            #print 'filebgtag '+str(filebgtag)#__debug
            #print 'filebgpressedtag '+str(filebgpressedtag)#__debug
            #print 'fileicon '+str(fileicon)#__debug
            
        #global options vor hbox like colors and such
        self.opts=opts
        #remember list of all instances to easy access attr or fun from all instances in one go
        #specifically: used to set transparent/opaque and color all imgbg simultaneously
        self.setFocusPolicy(0);
        self.imgbg=Globals.IMG[self.filebgtag].img
        #these contain screen grabbed pixmaps form the original cde frontpanel. 
        #store here the unscaled size
        self.w0=self.imgbg.width()
        self.h0=self.imgbg.height()
        self.imgicon = QtGui.QPixmap(fileicon)
        #to make the updated background visible if state changes:
        self.pressed.connect(self.update)
        self.released.connect(self.update)
        self.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.MinimumExpanding)   
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        #set background color green for pixelgap debugging
        palette = self.palette()
        role = self.backgroundRole()
        palette.setColor(role, QtGui.QColor('green'))
        self.setPalette(palette)
        #if true display display faded icon with double left/right arrows on top
        #used in CdePanel.py moveComboButton
        self.displayArrows=False
        self.arrowspng=QtGui.QPixmap(Globals.configdir+'/arrows.png')
        self.displayAlwaysUp=False
    def paintEvent(self, event):
        #draw background or (pressed-background when button is pressed)
        #images are retrieved from global resource
        #draw icon on top
        if self.isDown() and (not self.displayAlwaysUp): 
            pixbgcur=Globals.IMG[self.filebgpressedtag].img
        else: pixbgcur=Globals.IMG[self.filebgtag].img
        painter = JosQPainter(self)
        #painter.setRenderHint(QPainter.Antialiasing)
        #draw the icon
        if Globals.smoothTransform:
            painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform);
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        painter.drawPixmap(event.rect(), pixbgcur)
        if self.displayArrows: painter.setOpacity(0.2)
        else: painter.setOpacity(0.9)
        painter.drawPixmapCenter(event.rect(), self.imgicon)
        if self.displayArrows:
            painter.setOpacity(1)
            painter.drawPixmapCenter(event.rect(), self.arrowspng)
    #some mystery redrawing for some reason need
    def enterEvent(self, event):
        self.update()
    def leaveEvent(self, event):
        self.update()
    #raise panel and drawers when pressed anywhere
    def mousePressEvent(self,event):  
        try: Globals.cdepanel.activateAllWindows()
        except Exception: pass
        super(PicButton, self).mousePressEvent(event)




class PicButtonBlink(PicButton):
    def __init__(self, blinkerList, filebgtag, filebgpressedtag, htop, parent):
        fileicon=''
        super(PicButtonBlink, self).__init__(filebgtag, filebgpressedtag, fileicon, htop, parent)
        self.blinkerList=blinkerList
        self.blinkOn=False

        self.timer=QtCore.QTimer()
        self.timer.timeout.connect(self.updateBlinker)
        self.timer.start(200)
        self.clicked.connect(purgeBlinkerList)
    #def purgeBlinkerList(self):
        #purgeBlinkerList()
    def updateBlinker(self):
        if len(self.blinkerList)>0:
            if self.blinkOn==True:self.blinkOn=False
            else: self.blinkOn=True
        else:
            self.blinkOn=False
        self.update()
    def paintEvent(self, event):
        if self.isDown() or self.blinkOn: 
            pixbgcur=Globals.IMG[self.filebgpressedtag].img
        else: pixbgcur=Globals.IMG[self.filebgtag].img
        painter = JosQPainter(self)
        #painter.setRenderHint(QPainter.Antialiasing)
        #draw the icon
        if Globals.smoothTransform:
            painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform);
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        painter.drawPixmap(event.rect(), pixbgcur)
        #painter.drawPixmapCenter(event.rect(), self.imgicon)
    #some mystery redrawing for some reason need

def main():


    defaultopts=Opts()
    defaultopts.currentpalettefile='Broica.dp'
    defaultopts.defaultworkspacecolor=2
    defaultopts.initialheight=85 
    defaultopts.contrast=0
    defaultopts.saturation=100
    defaultopts.sharp=0.1
    defaultopts.antialias=20
    defaultopts.ncolors=8
    defaultopts.nworkspaces=6
    defaultopts.workspacecolors=[0, 8, 5, 6, 7, 2, 2, 2, 2, 2, 2]
    defaultopts.workspacelabels=['Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven']

    print 'MAIN '
    app = QtCore.QApplication(sys.argv)
    window = QtGui.QWidget()
    #hbox is parented here to 'window'
    #                      V
    #layout = QtGui.QHBoxLayout(window) 
    #layout.setSpacing(0)
    #layout.setMargin(0)

    #unparented button
    button = PicButton("launcher.xpm","launcher-pressed.xpm","terminal.xpm",defaultopts)
    # this func parents button to parent of hbox (='window')
    #layout.addWidget(button) 
    #parent the button otherwise explicit by adding 'window', but then the hbox doesnt work-------------V
    #button = PicButton("xpm/launcher.xpm","xpm/launcher-pressed.xpm","terminal.xpm",Globals.TESTOPTS,window)

    #blinker=0
    #but=PicButtonBlink(blinker,



    window.show()
    window.resize(200,200)
    sys.exit(app.exec_())

if __name__ == '__main__':
   main()




