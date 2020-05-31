#!/usr/bin/python
#normalbutton with 2 images met ff standaardimag voor test
#zie ComboButton.py
import sys
from PyQt4 import QtCore, QtGui
from PicButton import PicButton
from JosQPainter import JosQPainter
import Globals

class PicButtonToggle(PicButton):
   def __init__(self, filebgtag, filebgpressedtag, fileicon, htop, parent):
      super(PicButtonToggle, self).__init__(filebgtag, filebgpressedtag, fileicon, htop, parent)
      self.setAutoExclusive(False)
      self.setCheckable(True)
      self.drawerfile=''#hack
   def paintEvent(self, event):
       if self.isChecked(): pixbgcur=Globals.IMG[self.filebgpressedtag].img
       else: pixbgcur=Globals.IMG[self.filebgtag].img
       painter = JosQPainter(self)
       #painter.setRenderHint(QtGui.QPainter.Antialiasing)
       if Globals.smoothTransform:
            painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform);
       painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
       painter.drawPixmap(event.rect(), pixbgcur)
       painter.drawPixmapCenter(event.rect(), self.imgicon)

class PicButtonWorkspace(PicButton):
   def __init__(self, filebgtag, filebgpressedtag, fileicon, htop, parent):
      super(PicButtonWorkspace, self).__init__(filebgtag, filebgpressedtag, fileicon, htop, parent)
      self.setAutoExclusive(False)
      self.setCheckable(True)
      self.clicked.connect(self.clickTwiceStayDown)
   #make button stay pressed when clicking 2 or more times in a row. Actual state
   #of workspacebuttons is set by updateWorkspaceButtons
   def clickTwiceStayDown(self):
          self.setChecked(True)
   def setWorkspaceNr(self,workspacenr):
       self.workspacenr=workspacenr
   def paintEvent(self, event):
       if self.isChecked(): pixbgcur=Globals.IMG[self.filebgpressedtag].img
       else: pixbgcur=Globals.IMG[self.filebgtag].img
       painter = JosQPainter(self)
       #painter.setRenderHint(QtGui.QPainter.Antialiasing)
       if Globals.smoothTransform:
            painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform);
       #painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
       painter.drawPixmap(event.rect(), pixbgcur)
       #painter.drawPixmapCenter(event.rect(), self.imgicon)
       #painter.drawPixmapLeft(event.rect(), leftmarginfrac, heightfrac, yoffsetfrac, self.imgicon)
       painter.drawPixmapLeft(event.rect(), .1, .45, .05, self.imgicon)

 



def main():
    print 'MAIN '
    app = QtCore.QApplication(sys.argv)
    window = QtGui.QWidget()
    layout = QtGui.QHBoxLayout(window)
    layout.setSpacing(0)
    layout.setMargin(0)

    #button = PicButtonToggle("launcherbg.xpm","launcherbgpressed.xpm","terminal.xpm")
    #button = PicButtonToggle("xpm/launcher.xpm","xpm/launcher-pressed.xpm","terminal.xpm",Globals.TESTOPTS,window)
    #button = PicButtonWorkspace("xpm/launcher.xpm","xpm/launcher-pressed.xpm","terminal.xpm",Globals.TESTOPTS,window)
    button = PicButtonWorkspace('xpm/pager-button-2.xpm','xpm/pager-button-down-2.xpm',"empty.xpm",Globals.TESTOPTS,window)
    layout.addWidget(button)

    #button.toggle()

    button.setChecked(True)
    button.setChecked(False)

    window.show()
    window.resize(200,200)
    sys.exit(app.exec_())

if __name__ == '__main__':
   main()




