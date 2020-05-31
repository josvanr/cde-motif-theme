#!/usr/bin/python
from PyQt4 import QtCore, QtGui
import Globals
from PicButton import PicButton

#hides positioning and resizing of PicButton.py objects and deriveds
#contains a stack of equal width pngs/buttons
#startpoint are the pngs grabbed from cde original front panel app. 
#   These have certain proportions to be kept. 
#First the UNSCALED y0 positions are calculated by stacking on top of each other
#Then these y0 and the heights h0 are multiplied by global scale factor to get SCALED versions
#The scaled versions will not fit exactly on pixel grid, so when necessary some pixmaps
#   will be drawn 1 pixel larger to fill the gaps
#Unscaled heights .h0 are stored in the picbuttons (from included pixmap)
#Unscaled widths .w0 also, except for the top and bottom border pixmaps, these are 
#    stretched in the x direction to prevent having to cut out N tiny  2x2 images. 
#   therefore the unscaled width of the box is set equal to the second pixmap in the column
class VBox(QtGui.QWidget):
    def __init__(self, parent=None):
        super(VBox, self).__init__(parent)
        #set when necessary
        self.desktopentrypath=''
        self.drawerfile=''
        self.isComboButton=False
        self.isClock=False
        self.isLeftPagerSpacer=False
        self.isRightPagerSpacer=False
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        #unscaled size of the box (summed stack of pixmaps)
        self.H0=0
        self.W0=0
        #init height from parent
        self.setFixedHeight(self.parent().height())
    def reScaleAndPosition(self):
        self.fac=Globals.scalefactor
        #caveat: setting tooltip acually ADDS CHILDREN without me knowing. So only iterate over my own buttons:
        picButtonChildren=self.findChildren(PicButton)
        #picButtonChildren=self.findChildren(PicButton)+self.findChildren(PyAnalogClock)
#hier
        #calculate UNSCALED positions y0 in box: (picbuttons store their own unscaled size)
        Y=0
        for w in picButtonChildren:
            w.y0=Y
            Y+=w.h0
        #---------------------
        #self.H0=Y #unscaled height of box=sum children
        #H=float(self.H0)*self.fac #scaled height
        # ^---------hmm hmm  H is set by parent so dont set again , otherwise infinite loop. keep like tis fornow:
        #scaled height of the box, set by parent, and scaled width:
        H=self.height()+1 
        #unscaled width is set to width of second pixmap (first and last are the border pixmap, will be stretched):
        #self.W0=self.children()[1].imgbg.width()
        self.W0=self.children()[1].w0
        W=float(self.W0)*self.fac
        self.setFixedWidth(W)
        #not sure if for pixel accuracy  fac should be calculated from given total height H
        #here. Want the height of the entire panel to be exactly H.. but yes it seems to work
        #self.fac=float(H)/self.H0
            #now calc SCALED positions and sizes: wa=w'accent' etc, and set:
        y=0
        for w in picButtonChildren:
            w.ya=w.y0*self.fac
            w.ha=w.h0*self.fac
            w.setFixedWidth(W)
            y+=w.ha
            w.setFixedHeight(w.ha)
            w.move(0,w.ya)
        #remove pixel gaps by making boxes 1px higher when necessary
        B=picButtonChildren
        last=len(B)
        for i in range(0,last-1):
            y=B[i].y()
            h=B[i].height()
            y1=B[i+1].y()
            if y+h != y1:
                B[i].setFixedHeight(h+1)
    #after putting picbuttons and such in the vbox, call this to set all sizes right
    #called from class where vboxes are instanciated
    def initAfterFilling(self):
        self.reScaleAndPosition()
    def resizeEvent(self, e):
        self.reScaleAndPosition()

