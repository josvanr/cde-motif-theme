#!/usr/bin/python
#Picbuttonwith a system command
import sys
from PyQt4 import QtCore, QtGui
from PicButton import PicButton
from JosQPainter import JosQPainter
from ColorFun import *
from WorkspaceFuncs import Run,RunDesktopEntry
import Globals
from xdg import DesktopEntry
from math import sqrt

class PicButtonCommand(PicButton):
    def __init__(self, filebgtag, filebgpressedtag, fileicon, command, htop, parent):
      super(PicButtonCommand, self).__init__(filebgtag, filebgpressedtag, fileicon, htop, parent)
      self.clicked.connect(self.runApp)
      self.command=command
      self.setToolTip(command)
    def runApp(self):
        Run(self.command)

class PicButtonCommandLauncher1(PicButtonCommand):
    def __init__(self, filebgtag, filebgpressedtag, desktopentrypath  , htop, parent):
        self.desktopentrypath=desktopentrypath
        d=DesktopEntry.DesktopEntry(desktopentrypath)
        iconnamenoext=d.getIcon()
        fileicon=findIconFromName1(iconnamenoext)
        command=d.getExec()
        super(PicButtonCommandLauncher1, self).__init__(filebgtag, filebgpressedtag, fileicon, command, htop, parent)
        self.setAcceptDrops(True)
        self.mousePressPos=None
        self.dragThreshold=30
    #todo in need of cleaning see WorkspaceFuncs.Run() needs to be reconfigured to only use desktopentry
    def runApp(self):
        RunDesktopEntry(self.desktopentrypath)
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): 
            event.acceptProposedAction()
        else:
            super(PicButtonCommandLauncher, self).dragEnterEvent(event)
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                filename=str(url.toLocalFile())
                self.desktopentrypath=filename
                x=DesktopEntry.DesktopEntry(filename)
                icon=x.getIcon()
                iconfile=findIconFromName1(icon)
                label=x.getName().strip()
                cmd=x.getExec()
                self.imgicon = QtGui.QPixmap(iconfile)
                #these are in super classes
                #todo how do better
                self.command=cmd
                self.fileicon=iconfile
                self.parent().parent().parent().saveLayout()
            event.acceptProposedAction()
        else:
            super(PicButtonCommandLauncher,self).dropEvent(event)
    def mouseReleaseEvent(self,event):
        super(PicButtonCommandLauncher1, self).mouseReleaseEvent(event)
    def mousePressEvent(self,e):
        self.displayAlwaysUp=False
        #used for measuring if dragThreshold has been pastthinglargerthanned why cant we speak dutch
        self.mousePressPos=e.pos()
        super(PicButtonCommandLauncher1, self).mousePressEvent(e)
    #distance between two QPos
    def distance(self,p1,p2):
        x=p2.x()-p1.x()
        y=p2.y()-p1.y()
        return sqrt(x*x+y*y)
    def mouseMoveEvent(self, e):
        #if the main window is moving around a combobutton for placement, we dont want the drag event
        #for dragging around the app inside the buttont to be initiated. So exit function as if not here:
        if self.parent().parent().parent().moveComboButtonInProgress:
            super(PicButtonCommandLauncher1, self).mouseMoveEvent(e)
            return
        #dragevent starts to quickly! introduce threshold
        if self.distance(e.pos(),self.mousePressPos)<self.dragThreshold:return
        #mousemoveevent on a button lets the button stay in the 'pressed down' state,
        #even after the mousemoveevent. So it is stuck there, and it refuses to come up again. Even when
        #manually calling butt.mouseReleaseEvent(e) on it after the move. So this is hack: Let the but
        #display the 'up' image, even when it is pressed down. And then the next time it is pressed
         #in 'mousepressevent', set but.displayAlwaysUp=False again. (is flag inside paintevent of the but)
        #dont know how else to get this to work
        self.displayAlwaysUp=True
        self.update()
        if e.buttons() == QtCore.Qt.RightButton:
            return
        #convert freedesktop entry to url for mimedata
        url=QtCore.QUrl(self.desktopentrypath)
        urls=[url]
        mimeData = QtCore.QMimeData()
        mimeData.setUrls(urls) 
        #grab image from widget and set translucent for display during drag
        pixmap = QtGui.QPixmap.grabWidget(self)
        painter = QtGui.QPainter(pixmap)
        painter.setCompositionMode(painter.CompositionMode_DestinationIn)
        painter.fillRect(pixmap.rect(), QtGui.QColor(0, 0, 0, 180))
        painter.end()
        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setPixmap(pixmap)
        # shift the Pixmap so that it coincides with the cursor position
        drag.setHotSpot(e.pos())
        # start the drag operation
        # exec_ will return the accepted action from dropEvent (?)
        if drag.exec_(QtCore.Qt.CopyAction | QtCore.Qt.MoveAction) == QtCore.Qt.MoveAction:
            #super(PicButtonCommandLauncher1, self).mouseReleaseEvent(e)
            self.update()
        else:
            self.update()
            #super(PicButtonCommandLauncher1, self).mouseReleaseEvent(e)

#clock.py what s with the timeoffset oid???? todo
class PicButtonClock(PicButtonCommandLauncher1):
    def __init__(self, filebgtag, filebgpressedtag, desktopentrypath  , htop, parent):
        super(PicButtonClock, self).__init__(filebgtag, filebgpressedtag, desktopentrypath  , htop, parent)
        self.imgclock=Globals.IMG['iconclock'].img
        #self.timeZoneOffset = 0
        self.hourColor = QtGui.QColor(Globals.colorshash['ts_color_3'])
        self.minuteColor= QtGui.QColor(Globals.colorshash['ts_color_3'])
        self.secondColor= QtGui.QColor(Globals.colorshash['ts_color_3'])
        self.hourHand = QtGui.QPolygon([
            QtCore.QPoint(7, 8),
            QtCore.QPoint(-7, 8),
            QtCore.QPoint(0, -40) ])
        self.minuteHand = QtGui.QPolygon([
            QtCore.QPoint(7, 8),
            QtCore.QPoint(-7, 8),
            QtCore.QPoint(0, -60) ])
        self.secondHand = QtGui.QPolygon([
            QtCore.QPoint(2, 19),#foot left side
            QtCore.QPoint(-2, 19),#foot right side
            QtCore.QPoint(0, -60)
            ]) #the top point
        rdot,ddot=44,6
        self.secondDot = QtGui.QPolygon([
            QtCore.QPoint(0, -(rdot+ddot)),
            QtCore.QPoint(ddot, -rdot),
            QtCore.QPoint(0, -(rdot-ddot)),
            QtCore.QPoint(-ddot,-rdot) ])
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update)
        #'sweeping' hand ;)
        self.ntickspersec=5
        self.mspertick=1000/float(self.ntickspersec)
        print self.mspertick
        timer.start(self.mspertick)
        self.prevtime=None
        self.ms=0
    def mouseMoveEvent(self, e):
        pass
        #no dragging the clock
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
        else: painter.setOpacity(1)
        painter.drawPixmapCenter1(event.rect(),0.75,Globals.IMG['iconclock'].img)
        #for moving the button
        if self.displayArrows:
            painter.setOpacity(1)
            painter.drawPixmapCenter(event.rect(), self.arrowspng)
        time = QtCore.QTime.currentTime() #hmm this is accurate to 1 sec not sub second hmmmmmmmm
        second=time.second()
        if second==self.prevtime:
            self.ms+=self.mspertick
        else:
            self.ms=0
        self.prevtime=second
        subsecond=second+self.ms/1000.0
        #time = time.addSecs(self.timeZoneOffset * 3600)#??
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        side = min(self.width(), self.height())
        painter.scale(side / 200.0, side / 200.0)
        allcolor= QtGui.QColor(Globals.colorshash['ts_color_3'])
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(allcolor))
        #hourhand
        painter.save()
        painter.rotate(30.0 * ((time.hour() + time.minute() / 60.0)))
        painter.drawConvexPolygon(self.hourHand)
        painter.restore()
        #minutehand
        painter.save()
        painter.rotate(6.0 * (time.minute() + time.second() / 60.0))
        painter.drawConvexPolygon(self.minuteHand)
        painter.restore()
        #secondshand
        painter.save()
        painter.rotate(subsecond*360/60.0)
        painter.drawConvexPolygon(self.secondHand)
        painter.drawConvexPolygon(self.secondDot)
        painter.restore()
        painter.end()

def main():
    print 'MAIN '
    app = QtCore.QApplication(sys.argv)
    window = QtGui.QWidget()
    layout = QtGui.QHBoxLayout(window)
    layout.setSpacing(0)
    layout.setMargin(0)

    button = PicButtonCommand("launcherbg.xpm","launcherbgpressed.xpm","terminal.xpm",'echo pressed',Globals1.TESTOPTS,window)
    layout.addWidget(button)

    window.show()
    window.resize(200,200)
    sys.exit(app.exec_())

if __name__ == '__main__':
   main()




