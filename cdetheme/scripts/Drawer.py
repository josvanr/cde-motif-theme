#!/usr/bin/python
import sys
from PyQt4 import QtCore, QtGui
import Globals
from functools import partial
import WorkspaceFuncs
import os
from xdg import DesktopEntry
from ColorFun import *
import re
from math import sqrt

class Drawer(QtGui.QWidget):
    instancelist = []
    #def __init__(self, drawerfile,  opts, parent=None):
    #need reference to mainwindow/cdepanel.. maybe do different later
    def __init__(self, drawerfile,  opts, mainwindow=None, parent=None): #hm yes yes
        super(Drawer, self).__init__(parent)
        self.opts=opts
        self.drawerfile=drawerfile
        #set in cdepanel, change later
        if mainwindow:self.mainwindow=mainwindow
        #set drawer sticky  on all desktops #entry only appears in window list after some time so use timer :
        self.timer1=QtCore.QTimer()
        self.timer1.setSingleShot(True)
        #this window is listed in x11 window list same as executablemain ------------v
        self.timer1.timeout.connect(partial(WorkspaceFuncs.setWindowSticky,Globals.EXECUTABLE))
        self.timer1.start(500)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.activateWindow() #raise?
        self.setAcceptDrops(True)
        #add this window to the instancelist. For looping over all drawer instances for use esc=close all drawers
        #TODO: IF DRAWERFILE IS ALREADY USED, COPY IT TO A NEW ONE
        #AND OPEN DRAWER FOR THAT ONE. TO PREVENT DUPLICATE DRAWERS
        Drawer.instancelist.append(self)
        #READ DRAWER ENTRIES FROM DRAWER FILE AND PUT WIDGETS IN DRAWER
        d=DrawerEntryHBorderSpacer(9,'top',self)
        self.addEntriesFromDrawerFile()
        #always include copy of the 'app manager' for finding/adding apps
        #but dont save that one to the drawerfile
        appmanager=self.mainwindow.findAppBrowser()
        ex=DrawerEntry1(appmanager,self.opts,self)
        ex.noSave=True
        d=DrawerEntryHBorderSpacer(9,'bottom',self)
        self.positionEntriesAndResizeDrawer()
        self.updateStyleSheets()
    #add drawerentries from drawer file to the drawer. Each line contains a freedesktop desktopentry path
    def addEntriesFromDrawerFile(self):
        with open(self.drawerfile) as f:lines=f.read().splitlines() 
        for l in lines:
            l=l.strip() #strip newlines and whitespaces (space/tab)
            if l: # (if '') => skip emtpy lines
                if os.path.isfile(l): #the desktopentrypath exists
                    ex=DrawerEntry1(l,self.opts,self)
                else:
                    print 'ERROR in drawer file '+self.drawerfile+', '+l+' not found'
                    continue
    def saveDrawerFile(self):
        print 'SAVING DRAWER FILE '+self.drawerfile
        with open(self.drawerfile, 'w') as f:
            for e in self.findChildren(DrawerEntry1):
                if not e.noSave:
                    f.write(e.desktopentrypath+'\n')
    @classmethod 
    def updateStyleSheets(self):
        for i in Drawer.instancelist:
            i.updateStyleSheet()
    def updateStyleSheet(self):
        background=Globals.colorshash['bg_color_2']
        border=Globals.colorshash['sel_color_2']
        foreground=Globals.colorshash['fg_color_2']
        ########the double {{ is 'escaping' for literal {
        ########these stylesheets... it would surprise me if this looks the same on all systems
        self.setStyleSheet("""
            QToolTip {{ background-color:{background}; color:{foreground}; border:{border} 2px}}
        """.format(**locals()))
            #Drawer {{ background-color:{background}; border:5px {background}}}
            #DrawerEntry1         {{ background-color:{background}; border:5px {border}}}
            #DrawerEntry1:pressed {{ background-color:{backgroundpressed}; border:1px solid {borderpressed}; margin:6px;}}
    def positionEntriesAndResizeDrawer(self):
	#todo here call resize drawer #or inresizeevent of drawer
        #get width of widest child:
        largestWidth=0
        for w in self.findChildren(DrawerEntryBase):
        #for w in self.children(): #again, someoneis adding more children to my box
                #need to init all children again here to be able to determine the width of the largest
                #drawerentry.  Alternative: store the largest unscaled width at init and then later just resize to scale or whatever
            w.setGeom(False) 
            w=w.width()
            if w>largestWidth:
                largestWidth=w
        #y position to stack on top of each other and set each child width to width of largest child in drawer
        Y=0
        for w in self.findChildren(DrawerEntryBase):
            h=w.height()
            w.move(0,Y)
            Y+=h
            #reconfigure the drawerentries and included stuff to have desired width
            w.setGeom(largestWidth)
        #resize enclosing Drawer to fit children drawer entries
        self.setFixedHeight(Y)
        self.setFixedWidth(largestWidth)
    def resizeEvent(self, e):
        print 'resize'
        self.positionEntriesAndResizeDrawer()
    #is called 2 times for some reason maybe qpushbut and parent or somehting?
    #so test if it is still there before deleting:
    def deleteEntry(self,entry):
        #hmm closeis the same as make invisible so entry realy still there
        #hmm this is too much 'Later' because the self.height is still  old height from 
        #before deleting then. And we rely on positioning on the self.height. So :
        #entry.deleteLater() #          v-------------------------------------/
        entry.setParent(None) #delete NOW instead
        self.positionEntriesAndResizeDrawer()
        self.move(self.x0,self.y0bottom-self.height())
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): 
            event.acceptProposedAction()
        else:
            #also call original handler for... whatever . what ever it wants to do by itself
            super(Drawer, self).dragEnterEvent(event)
    # ability to drag over / in put drawer desktopentries in freedesktop style
    #see /usr/share/applications and drag icons here
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                #print url
                desktopentrypath=str(url.toLocalFile())
                self.ex=DrawerEntry1(desktopentrypath,self.opts,self)
                self.ex.show() #UUUUMMMM .... it remained invisible until this 'show'!!! WHY. It is parented after all
                #remember for save
                self.positionEntriesAndResizeDrawer()
                self.saveDrawerFile()
                self.positionEntriesAndResizeDrawer()
                #These were stored at time of creation of drawer. maybe do this in positionEntriesAndResizeDrawer?
                #y of widget is top so to preserve bottom position (ontop of main window) do this
                #                              v---------------------------------------------/
                self.move(self.x0,self.y0bottom-self.height())
                # but doesnt work if mainwin was resized while drawer was open. Main window must place
                # the drawer because drawer itself doesnt know about its required position so call
                # mainwindow function instead
                self.mainwindow.positionDrawers()
            event.acceptProposedAction()
        else:
            super(Button,self).dropEvent(event)
    def keyPressEvent(self, event):
        if type(event) == QtCore.QKeyEvent:
            print 'KEY '+str(event.key())#__debug
            modifiers = QtCore.QApplication.keyboardModifiers()
            if event.key()==61:#=
                print self.parent()
                self.mainwindow.growWindow()
            if event.key()==45:#-
                self.mainwindow.shrinkWindow()
                print 't'
            if event.key() == QtCore.Qt.Key_Escape:
                self.closeDrawer()
            if modifiers == QtCore.Qt.ControlModifier:
                if event.key()==67:#ctrl-c
                    self.exitProgram()
            event.accept()
        else:
            event.ignore()
    #hmm should the function be here instead of calll to mainwindow? todo
    def closeDrawer(self):
        self.mainwindow.closeDrawer(self)


#todo dit in ext bestand
class JosQPainter1 (QtGui.QPainter):
   def __init__(self, parent=None):
      super(JosQPainter1, self).__init__(parent)
   def drawPixmapCenter(self, rect, marginfac, pixmap):
        w=rect.width()
        h=rect.height()
	wp=pixmap.size().width()
	hp=pixmap.size().height()
	hpn=h*marginfac #new h for the pixmap, frac portion of rect height
	wpn=float(wp)/hp*hpn #new w for pixmap perserve aspect
	dxn=(w-wpn)/2.0 #offsets for centering
	dyn=(h-hpn)/2.0
	QtGui.QPainter.drawPixmap(self,dxn,dyn,wpn,hpn, pixmap)
   def drawPixmapLeft(self, rect, marginfac, xoffsetfrac, pixmap):
        w=rect.width()
        h=rect.height()
        wp=pixmap.size().width()
        hp=pixmap.size().height()
        hpn=h*marginfac #new h for the pixmap, frac portion of rect height
        wpn=float(wp)/hp*hpn #new w for pixmap perserve aspect
        dxn=float(h)*xoffsetfrac#widths differ so left marginfrac must be frac of height for straight margin
        dyn=(h-hpn)/2.0
        QtGui.QPainter.drawPixmap(self,dxn,dyn,wpn,hpn, pixmap)

#icon label for inside button, adapts to state of button:
#will look 'pressed' if the button if pressed
#to put icon and textlabel inside button and have both look up or pressed at the same time
class ButtonLabel(QtGui.QLabel):
    def __init__(self,iconfile,marginfac,align,pmup,pmdown,parent=None):
        super(ButtonLabel,self).__init__(parent)
        self.pmup=pmup
        self.pmdown=pmdown
        self.button=self.parent()
        self.iconfile=iconfile
        self.marginfac=marginfac
        self.align=align
        self.filebgtag=pmup
        self.filebgpressedtag=pmdown
        self.currentPixmap=Globals.IMG[self.filebgtag].img
        self.setPixmap(self.currentPixmap)
        #to distinguishchche (why write all these letters you dont rponoune anhyway)
        #distingwishsdcheigheiwwkd between buttonlabels: need to grab the icon for
        #making a shot for drag operation:
        self.isIcon=False
        self.isdown=False
        if self.iconfile:
            self.img=QtGui.QPixmap(iconfile)
    #these are called by the parent button to let the buttonlabel reflect the state of the button:
    def pmDown(self):
            self.isdown=True 
            self.currentPixmap=Globals.IMG[self.filebgpressedtag].img
            self.setPixmap(self.currentPixmap)
    def pmUp(self):
            self.isdown=False
            self.currentPixmap=Globals.IMG[self.filebgtag].img
            self.setPixmap(self.currentPixmap)
    def paintEvent(self, event):
        super(ButtonLabel, self).paintEvent(event)
        if self.isdown:
            if self.currentPixmap!=Globals.IMG[self.filebgpressedtag].img:
                self.setPixmap(Globals.IMG[self.filebgpressedtag].img)
        else:
            if self.currentPixmap!=Globals.IMG[self.filebgtag].img:
                self.setPixmap(Globals.IMG[self.filebgtag].img)
        if self.iconfile:
            painter = JosQPainter1(self)
            if Globals.smoothTransform:
                painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform);
            painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
            if self.align=='left': 
                painter.drawPixmapLeft(event.rect(),self.marginfac,0.25, self.img)
            else: painter.drawPixmapCenter(event.rect(),self.marginfac, self.img)
            painter.end()

class DrawerEntryBase(QtGui.QPushButton):
    def __init__(self,h0,fac,parent=None):
        super(DrawerEntryBase,self).__init__(parent)
        self.fac=Globals.scalefactor
        self.h0=h0 #original unscaled height
        #reparent spacer to self in the right spot when adding the other items:
        self.spacer= QtGui.QLabel()
        self.spacer.w0=0#initial
        self.spacer.h0=h0
        self.spacer.setScaledContents(True)
        #for initing, setGeom(False) is called in the child classes
    #setgeom(None): 
        #for init:
        #scale children of drawerentry according  to globals.scalefactor 
        #move them to align left
        #resize the drawerentry to fit around the children
    #setgeom(desiredtotalwidth): 
        #scale children of drawerentry according  to globals.scalefactor 
        #resize drawerentry to given width
        #grow spacer to fill the empty space between (icon,label) and right border
    def setGeom(self,desiredtotalwidtha): #desired total scaled width
        self.fac=Globals.scalefactor
        #UNSCALED positions x0 for spacer 0
        self.spacer.w0=0
        X=0
        for w in self.findChildren(QtGui.QLabel):
            w.x0=X
            #these are not necessary to actually set,but useful for debugging
            #w.move(w.x0,0)
            #w.setFixedWidth(w.w0)
            #w.setFixedHeight(w.h0)
            X+=w.w0
        self.W0=X #total unscaled width with spacer set to 0
        #insert spacer to make equal width if required. Dont do if called as setgeom(False), for init
        if desiredtotalwidtha: 
            desiredtotalwidth0=float(desiredtotalwidtha)/Globals.scalefactor
            self.spacer.w0=desiredtotalwidth0-self.W0
        #UNSCALED positions x0 for set spacer (amounts to same if spacer 0)
        X=0
        for w in self.findChildren(QtGui.QLabel):
            w.x0=X
            #w.move(w.x0,0)
            #w.setFixedWidth(w.w0)
            #w.setFixedHeight(w.h0)
            X+=w.w0
        self.W0=X #total unscaled width with spacer when set
        #SCALED positions. xa
        if True:
            X=0
            for w in self.findChildren(QtGui.QLabel):
                w.xa=w.x0*self.fac
                w.wa=w.w0*self.fac
                w.ha=w.h0*self.fac
                w.setFixedWidth(w.wa)
                w.setFixedHeight(w.ha)
                w.move(w.xa,0)
                X+=w.wa
        #total scaled size
        self.Wa=X
        self.Ha=self.h0*self.fac
        self.setFixedWidth(self.Wa)
        self.setFixedHeight(self.Ha)
        #Mathematically scaled positions are truncated/rounded when positions are
        #actually set. So pixelgaps appear. Fill here by widening the children if necessary
        #loop through and if next starts further away than position + width, increase width
        B=self.findChildren(QtGui.QLabel)
        last=len(B)
        for i in range(0,last-1):
            x=B[i].x()
            w=B[i].width()
            x1=B[i+1].x()
            if x+w != x1:
                B[i].setFixedWidth(w+1)
    def mousePressEvent(self,event):  
        for w in self.findChildren(QtGui.QLabel):w.pmDown()
        super(DrawerEntryBase, self).mousePressEvent(event)
    def mouseReleaseEvent(self,event):  
        for w in self.findChildren(QtGui.QLabel):w.pmUp()
        super(DrawerEntryBase, self).mouseReleaseEvent(event)

#todo this can be based on non-pressable button later
class DrawerEntryHBorderSpacer(DrawerEntryBase):
    def __init__(self,h0,topmiddlebottom,parent=None):
        super(DrawerEntryHBorderSpacer,self).__init__(h0,1.2,parent)
        if topmiddlebottom=='top':
            self.imgs=['drawerbordertopleft','drawerbordertop','drawerbordertopright']
        elif topmiddlebottom=='bottom':
            self.imgs=['drawerborderbottomleft','drawerborderbottom','drawerborderbottomright']
        else:
            self.imgs=['drawerborderleft','drawerborderleft','drawerborderright']

        self.borderleft = ButtonLabel('',1,None,self.imgs[0],self.imgs[0],self)
        self.borderleft.w0=9
        self.borderleft.h0=9
        self.borderleft.setScaledContents(True)

        self.spacer=ButtonLabel('',1,None,self.imgs[1],self.imgs[1],self)
        self.spacer.w0=0#initial
        self.spacer.h0=h0
        self.spacer.setScaledContents(True)

        self.borderright = ButtonLabel('',1,None,self.imgs[2],self.imgs[2],self)
        self.borderright.w0=9
        self.borderright.h0=h0
        self.borderright.setScaledContents(True)
        self.setGeom(None)

class DrawerEntry1(DrawerEntryBase):
    def __init__(self,desktopentrypath,opts,parent=None):
    #def __init__(self,labeltext,iconfile,command,desktopentrypath,opts,parent=None):
        super(DrawerEntry1,self).__init__(38,1.2,parent)
        #self.iconfile=iconfile
        #self.labeltext=labeltext
        #self.command=command
        self.opts=opts
        self.desktopentrypath=desktopentrypath

        #some entries in the drawer we dont want to save (the app manager)
        self.noSave=False

        d=DesktopEntry.DesktopEntry(desktopentrypath)
        self.labeltext=d.getName()
        self.command=d.getExec()
        icon=d.getIcon()#'desktopentry' icon without path and extension
        self.iconfile=findIconFromName1(icon)


        self.setToolTip(self.command)

        #children labels of drawerentry must have w0/h0
        self.borderleft = ButtonLabel('',1,None,'drawerentryleft','drawerentryleftpressed',self)
        self.borderleft.w0=9
        self.borderleft.h0=38
        self.borderleft.setScaledContents(True)

        self.iconimgheight=self.height()*0.7
        self.iconimgwidth=self.iconimgheight
        #self.iconboxwidth=self.H
        #self.iconboxheight=self.H
        self.setFocusPolicy(0)
        self.icon=ButtonLabel(self.iconfile,.95,'center','drawerentry','drawerentrypressed',self)
        self.icon.isIcon=True
        self.icon.w0=38
        self.icon.h0=38
        self.icon.setScaledContents(True)
        self.icon.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        
        Globals.filecounter=1
        tempiconfile='/tmp/CDEpanel-iconlabel'+str(Globals.filecounter)+'.png'
        #self.labelwidth=createTextIcon(tempiconfile,labeltext)+20
        self.labelwidth=createTextIcon(self.labeltext,Globals.fontSize,tempiconfile,self.opts)+20

        #todo use fontmetrics for this--------v
        self.label= ButtonLabel(tempiconfile,.4,'left','drawerentry','drawerentrypressed',self)
        self.label.w0=self.labelwidth
        self.label.h0=38
        self.label.setScaledContents(True)
        self.label.setFixedHeight(self.label.h0)

        self.spacer=ButtonLabel('',1,None,'drawerentry','drawerentrypressed',self)
        self.spacer.w0=0#initial
        self.spacer.h0=38
        self.spacer.setScaledContents(True)

        self.borderright=ButtonLabel('',1,None,'drawerentryright','drawerentryrightpressed',self)
        self.borderright.w0=9
        self.borderright.h0=38
        self.borderright.setScaledContents(True)
        
        self.mousePressPos=None
        self.dragThreshold=30

        self.clicked.connect(self.runApp)

        self.setGeom(None)
    def contextMenuEvent(self, event):
        print 'context'
        menu = QtGui.QMenu(self)
        remove = menu.addAction("Remove Entry")
        close= menu.addAction("Close Drawer")
        closeall= menu.addAction("Close All Drawers")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == remove:
            self.parent().deleteEntry(self)
        if action == close:
            self.parent().mainwindow.closeDrawer(self.parent())
        if action == closeall:
            self.parent().mainwindow.closeAllDrawers()
    def mouseReleaseEvent(self,event):  
        self.parent().setAcceptDrops(True)
	print 'release'
        #if event.button()==QtCore.Qt.RightButton:
            #self.parent().deleteEntry(self)
	super(DrawerEntry1,self).mouseReleaseEvent(event)
    #distance between two QPos
    def distance(self,p1,p2):
        x=p2.x()-p1.x()
        y=p2.y()-p1.y()
        return sqrt(x*x+y*y)
    def mousePressEvent(self,e):  
        #remember to be able to calculate drag threshold
        self.mousePressPos=e.pos()
        super(DrawerEntry1, self).mousePressEvent(e)
    #drag desktopentry from drawer to other drawer or combobutton
    def mouseMoveEvent(self, e):
        #initiate drag event only until threshold has been superpassed, to prevent
        #drag thing when just clicking to start an app
        if self.distance(e.pos(),self.mousePressPos)<self.dragThreshold:return
        #what was this for
        if e.buttons() == QtCore.Qt.RightButton:
            return
        #prevent the dragged app from being dropped in the drawer itself
        self.parent().setAcceptDrops(False)
        for w in self.findChildren(QtGui.QLabel):w.pmUp()
        super(DrawerEntryBase, self).mouseReleaseEvent(e)
        #convert freedesktop entry to url for mimedata
        url=QtCore.QUrl(self.desktopentrypath)
        urls=[url]
        mimeData = QtCore.QMimeData()
        mimeData.setUrls(urls) 
        #find the child with the icon inside, grab and set translucent for display during drag
        for c in self.children():   
            if c.isIcon: break
        pixmap = QtGui.QPixmap.grabWidget(c)
        painter = QtGui.QPainter(pixmap)
        painter.setCompositionMode(painter.CompositionMode_DestinationIn)
        painter.fillRect(pixmap.rect(), QtGui.QColor(0, 0, 0, 180))
        painter.end()
        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setPixmap(pixmap)
        #set 'hot spot' in the center of the dragged pixmap
        drag.setHotSpot(QtCore.QPoint(pixmap.width()/2,pixmap.height()/2))
        # start the drag operation
        # exec_ will return the accepted action from dropEvent (?)
        if drag.exec_(QtCore.Qt.CopyAction | QtCore.Qt.MoveAction) == QtCore.Qt.MoveAction:
            print 'moved'
            #accept drops again after dragging operation 
            self.parent().setAcceptDrops(True)
        else:
            print 'copied'
            self.parent().setAcceptDrops(True)
    def runApp(self):
	if QtGui.qApp.mouseButtons() & QtCore.Qt.RightButton:pass
        #self.parent() is the drawer dialog 
        drawer=self.parent()
        if True:


            #keep drawer open if app manager is started; then we want to drag in apps
            if not re.match('.*cdepanel-app-manager.*',self.desktopentrypath):
                #uncheck the drawerbutton and close drawer 
                b=drawer.originatingbutton
                b.setChecked(False)
                drawer.close()
                if drawer in Drawer.instancelist: Drawer.instancelist.remove(drawer)
                #reconnect the drawerbutton for open again
                try: b.clicked.disconnect() 
                except Exception: pass
                b.clicked.connect(b.openfun)
        WorkspaceFuncs.RunDesktopEntry(self.desktopentrypath)

def main():
    
    app = QtCore.QApplication(sys.argv)
    #app.setStyle("motif")

    d=Drawer('drawers/Firefox',Globals.TESTOPTS)
    d.show()
    
    
    #ex=DrawerEntry('mozilla.xpm','Firefox Explorer')
    #ex.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
