#!/usr/bin/python
#VER 1.2
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)
import sys
from PyQt4.QtTest import QTest
from PyQt4 import QtCore, QtGui
from JosQPainter import JosQPainter
from ColorFun import *
import Globals
from Opts import Opts
from PicButton import PicButton,PicButtonBlink
from PicButtonCommand import *
from PicButtonToggle import PicButtonToggle, PicButtonWorkspace
import WorkspaceFuncs
from functools import partial
from ewmh import EWMH
ewmh = EWMH()
import os
import copy
import time
from VBox import VBox
from Drawer import Drawer
import sip
import os.path
import re
#from xdg import BaseDirectory, DesktopEntry, IconTheme
from xdg import DesktopEntry
import subprocess
from ColorDialog import ColorDialog
from MotifColors import readMotifColors2, colorize_bg
from MiscFun import *
import shutil
from DesktopEnv import DesktopEnv
from SpritesResourcex import spriteLWHXY
import ThemeGtk
from Theme import Theme

#positioning of contained vboxes
class HBox(QtGui.QWidget):
    def __init__(self, opts, parent=None):
        super(HBox, self).__init__(parent)
        #opts passed for initing height
        self.opts=opts
        self.setFixedHeight(self.opts.initialheight)
        self.setFixedWidth(self.opts.initialheight) #arbitrary value, is changed in reSizeWidth
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        #resize event is propagated to children AFTER for self so they always lag behind in height->pixel
        #problems. So for now just set it. Then resize event for them is triggered and they set their own
        #width.  then position them to left align and stack horizontally
    def calcSetLayout(self):
        #all is based on height of hbox
        H=self.height()
        X=0
        #loop over contained vboxes and position/resize. Sometimes other children can appear (tooltips in qboxes or somehting,
        #or 'animation' object ???
        for w in self.findChildren(VBox):
            #triggers resizeevent in vbox, which lets it set its own width. So after this, the width of the children is known
            #and they can be put in a row next to eachother
            w.setFixedHeight(H)
            w.move(X,0)
            X=X+w.width()
        self.setFixedWidth(X)
        return X
    def initAfterFilling(self):
        self.calcSetLayout()
    def resizeEvent(self, e):
        self.calcSetLayout()

#for storing global resourcePng
class josImg():
    pass

# MAIN PANEL WIDGET #######################################################################

class CdePanel(QtGui.QWidget):
    def __init__(self, opts, parent=None):

        super(CdePanel, self).__init__()
        #default *necessary* options 
        defaultopts=Opts()
        defaultopts.currentpalettefile='Broica.dp'
        defaultopts.defaultworkspacecolor=2
        defaultopts.initialheight=85 
        defaultopts.contrast=0
        defaultopts.environment='xfce'
        defaultopts.saturation=100
        defaultopts.sharp=0.9
        defaultopts.ncolors=8
        defaultopts.nworkspaces=6
        defaultopts.panelcolor=5
        defaultopts.workspacecolors=[0, 8, 5, 6, 7, 2, 2, 2, 2, 2, 2]
        defaultopts.workspacelabels=['Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven']
        defaultopts.internalborderwidth=3
        defaultopts.internaltitleheight=22
        defaultopts.lockbuttoncommand='xflock4'
        defaultopts.exitbuttoncommand='xfce4-session-logout'
        #the backdrops are only used in ThemeXfce.py. But leave here for now, to have all settings in one place
        defaultopts.workspacebackdrops=['Gradient', 'Paver', 'Gradient', 'WaterDrops', 'Gradient', 'Gradient', 'Gradient', 'Gradient']
        defaultopts.themeGtk=True
        defaultopts.themeBackdrops='xfce'
        defaultopts.themeWindecs='xfce'
        #add defaults to given opts if missing there, else leave unchanged
        opts.addMissing(defaultopts)
        #store reference. Note: all classes/instances should only store a reference, not create new
        #copy of Opts() so that when opts are changed during run, chages are effected everywhere
        self.opts=opts

        self.theme=Theme(self.opts)
        self.theme.initTheme()

        #init some globals from opts. How to organize this.... todo
        #go for 1 panel (or more than one with smae cols) and save not the colros but only settings
        #todo move this fun out of opts
        Globals.palettes=opts.loadPaletteDir(Globals.palettedir)
        #Globals.currentpaletteix=Opts.paletteFile2Ix(opts.currentpalettefile)
        Globals.colorshash=readMotifColors2(self.opts.ncolors,Globals.palettedir+'/'+self.opts.currentpalettefile)
        #scale fac is calcualted from initialheight!
        Globals.scalefactor=float(self.opts.initialheight)/85
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        #RESOURCE IMAGE MANAGEMENT
        Globals.IMG={}
        #substitutions to map colors in resourcex.png to motif colorpalette colors. Not sure
        #if more are necessary (there are also some icons the the resource file) Done manually
        #by comparing the colors in the resource (listed by imagemagick identify) and the output
        #of the motifcolors script (screenshots were taken with palette 'Broica' in place)
        print 'LOAD RESOURCE INFO '
        #Load coordinates of sprites in resourcePng file (are produced by a gimp script jos-sprites.py)
        Globals.IMG={}
        for l in spriteLWHXY:
            i=josImg()
            label=l[0]
            i.rect=QtCore.QRect(l[3],l[4],l[1],l[2]) #qrect=xywh i prefer WxH+x+y
            Globals.IMG[label]=i
        #Load single resource file containing all sprites
        resourcepath=os.path.join(Globals.configdir,'resourcex.png')
        self.resourcePng=QtGui.QPixmap(checkFile(resourcepath))
        self.initUpdateResourceImgs()
        self.updateStyleSheet()

#__2
        self.theme.updateTheme()#hmm not sure if this is necessary... yes yes it is for updating the gtkrc etc. Maybe do that in initTheme instead
            #store reference to workspace buttons here for looping in updateWorkspaceButtons
        self.workspaceButtonList=[]
        self.workspaceButtonList=[]
        self.previousWorkspace=None
            #(note from earlier version:)
            #Pass self as parent to constructor of h otherwise not shown. note that if an unparented widget is added
            #to a LAYOUT, it set its parent is set automatically by calling setLayout afterwards
            #self.h = DynHBox() no worke , self.h = DynHBox(parent=self) #or: #self.h.setParent(self) #or:

            #THE CENTRAL HORIZONTAL WIDGET ROW:
        self.hbox = HBox(self.opts, self) 
            #Fill up the main widget
            #These put buttons into a vbox and put the vbox into the hbox. References to the buttons are not stored for now 
        self.insertLeftBorder(self.opts)
        self.insertLeftHandle(self.opts)
        #reat layout from file cdepanel/layout, inserting combobuttons and workspacebuttons if requested
        self.insertFromLayoutFile()
        self.insertRightHandle(self.opts)
        self.insertRightBorder(self.opts)
            #post-init hbox and adjust main window to hbox
        self.hbox.initAfterFilling()
        self.adjustWidthToMainWidget()

        self.configDialog=None
        self.movingComboButton=None
        self.moveComboButtonInProgress=False
            #init workspacebutton states (up/pressed) to reflect current workspace and poll every N ms 
            #to keep updated.  #Darn, timer has to be 'self' or else it will be thrown away 
        self.updateWorkspaceButtons()
        self.timer=QtCore.QTimer()
        self.timer.timeout.connect(self.updateWorkspaceButtons)
        self.timer.start(100)
        #STORE EXECUTABLE NAME IN GLOBALS  TO BE ABLE TO SET ALL WINDOWS STICKY
        #NOTE: by default pyinstaller removes the .py when making the executable, but __file__ still has the .py
        #so ..: so... um...yes... hack  I set 'cdepanel' manually in 'make_pyinstaller'
        if hasattr(sys,'_MEIPASS'):#(when run from pyinstaller bundle)
            Globals.EXECUTABLE='cdepanel'
        else:
            Globals.EXECUTABLE=os.path.basename(__file__)       
        print '>'+Globals.EXECUTABLE+'<'
            #set panel sticky  on all desktops #entry only appears in window list after some time so use timer for now
            #looks up executable name in x window list and sets that sticky--------------v
        QtCore.QTimer.singleShot(5000,partial(WorkspaceFuncs.setWindowSticky1,Globals.EXECUTABLE))
        #bla='cdepanel'
        #print '>'+bla+'<'
        #QtCore.QTimer.singleShot(800,partial(WorkspaceFuncs.setWindowSticky,bla))
            #hdd light will blink if app is started but window hasnt appeared yet (or at least try)
        self.timer2=QtCore.QTimer()
        self.timer2.timeout.connect(self.updateBlinkerList)
        self.timer2.start(1000)
        print 'setting timer'#__debug

    # METHODS ############################################################################
    # METHODS ############################################################################
    # METHODS ############################################################################

    def setEnvironment(self,environment):
        if environment=='xfce':
            self.opts.environment='xfce'
        else:
            self.opts.environment=''
        print 'Environment set to '+self.opts.environment

        
    # RESOURCE IMAGES AND COLORS ###########################################################

    def colorMap(self,panelColor):
        panelColor=str(panelColor)
        return [                #identify -verbose resourcex.png:               #./motifcolors 8 Broica.dp:
            #['#000100',''],             #0: (  0,  1,  0) #000100 srgb(0,1,0)         #bg_color_1 #ed00a8007000
            #['#1600FF',''],             #1: ( 22,  0,255) #1600FF srgb(22,0,255)      #fg_color_1 #ffffffffffff
            #['#20211F',''],             #2: ( 32, 33, 31) #20211F srgb(32,33,31)      #sel_color_1 #c9738ecc5f33
            #['#FF0000',''],             #3: (255,  0,  0) #FF0000 red                 #ts_color_1 #f7cbda02c1d5
            #['#204955',''],             #4: ( 32, 73, 85) #204955 srgb(32,73,85)      #bs_color_1 #7f2e5a273c1a
            ['#414240','bs_color_2'],   #5: ( 65, 66, 64) #414240 srgb(65,66,64)       #bg_color_2 #9900991b99fe
            #['#5C4549',''],             #6: ( 92, 69, 73) #5C4549 srgb(92,69,73)      #fg_color_2 #ffffffffffff
            #['#FD05FF',''],             #7: (253,  5,255) #FD05FF srgb(253,5,255)     #sel_color_2 #820c822382e4
            ['#464D54','bs_color_3'],   #8: ( 70, 77, 84) #464D54 srgb(70,77,84)       #ts_color_2 #d2aad2b6d31a
            ['#4D4F4C','bs_color_2'],   #9: ( 77, 79, 76) #4D4F4C srgb(77,79,76)       #bs_color_2 #4f864f94500a
            ['#7C5939','bs_color_1'],  #10: (124, 89, 57) #7C5939 srgb(124,89,57)      #bg_color_3 #89559808aa00
            #['#68615B','bs_color_5'],  #11: (104, 97, 91) #68615B srgb(104,97,91)      #fg_color_3 #ffffffffffff
            ['#68615B','bs_color_'+panelColor],  #11: (104, 97, 91) #68615B srgb(104,97,91)      #fg_color_3 #ffffffffffff
            #['#626461',''],            #12: ( 98,100, 97) #626461 srgb(98,100,97)     #sel_color_3 #74bb813a9080
            ['#3B7C8C','sel_color_6'], #13: ( 59,124,140) #3B7C8C srgb(59,124,140)     #ts_color_3 #cbb8d232da1c
            #['#727471',''],            #14: (114,116,113) #727471 srgb(114,116,113)   #bs_color_3 #47444ee55838
            ['#818380','sel_color_2'], #15: (129,131,128) #818380 srgb(129,131,128)    #bg_color_4 #68006f008200
            #['#4B92A7',''],            #16: ( 75,146,167) #4B92A7 srgb(75,146,167)    #fg_color_4 #ffffffffffff
            #['#B8878C',''],            #17: (184,135,140) #B8878C srgb(184,135,140)   #sel_color_4 #58665e596e80
            #['#929491',''],            #18: (146,148,145) #929491 srgb(146,148,145)   #ts_color_4 #bac4bdf4c69b
            ['#8998AB','bg_color_3'],  #19: (137,152,171) #8998AB srgb(137,152,171)    #bs_color_4 #32dc36493f93
            ['#979996','bg_color_2'],  #20: (151,153,150) #979996 srgb(151,153,150)    #bg_color_5 #c600b2d2a87e
            #['#A9988D','sel_color_5'], #21: (169,152,141) #A9988D srgb(169,152,141)    #fg_color_5 #000000000000
            ['#A9988D','sel_color_'+panelColor], #21: (169,152,141) #A9988D srgb(169,152,141)    #fg_color_5 #000000000000
            #['#ABADAA',''],            #22: (171,173,170) #ABADAA srgb(171,173,170)   #sel_color_5 #a84c97ff8f37
            ['#EDA86E','bg_color_1'],  #23: (237,168,110) #EDA86E srgb(237,168,110)    #ts_color_5 #e720dee6da78
            #['#C5B3A8','bg_color_5'],  #24: (197,179,168) #C5B3A8 srgb(197,179,168)    #bs_color_5 #6b6160fb5b61
            ['#C5B3A8','bg_color_'+panelColor],  #24: (197,179,168) #C5B3A8 srgb(197,179,168)    #bs_color_5 #6b6160fb5b61
            #['#0CFF00',''],            #25: ( 12,255,  0) #0CFF00 srgb(12,255,0)      #bg_color_6 #49009200a700
            #['#BBBDBA',''],            #26: (187,189,186) #BBBDBA srgb(187,189,186)   #fg_color_6 #ffffffffffff
            ['#ABCFD8','ts_color_6'],  #27: (171,207,216) #ABCFD8 srgb(171,207,216)    #sel_color_6 #3e0c7c198df3
            #['#00FFFF',''],            #28: (  0,255,255) #00FFFF cyan                #ts_color_6 #ada7ce80d7f3
            #['#DEC9CC',''],            #29: (222,201,204) #DEC9CC srgb(222,201,204)   #bs_color_6 #248149035383
            ['#C9D1DA','ts_color_3'],  #30: (201,209,218) #C9D1DA srgb(201,209,218)    #bg_color_7 #b70087008d00
            ['#CDD2D5','ts_color_2'],  #31: (205,210,213) #CDD2D5 srgb(205,210,213)    #fg_color_7 #ffffffffffff
            ['#FAD9BE','ts_color_1'],  #32: (250,217,190) #FAD9BE srgb(250,217,190)    #sel_color_7 #9b8c72c077d9
            #['#DDDFDC',''],            #33: (221,223,220) #DDDFDC srgb(221,223,220)   #ts_color_7 #dfd6cab1cd56
            #['#E7DED7',''],            #34: (231,222,215) #E7DED7 srgb(231,222,215)   #bs_color_7 #5ef8460f492c
            #['#FFFF01',''],            #35: (255,255,  1) #FFFF01 srgb(255,255,1)     #bg_color_8 #938eab73bf00
            #['#FEFFFC',''],            #36: (254,255,252) #FEFFFC srgb(254,255,252)   #fg_color_8 #ffffffffffff
            #['#C5B3A8','']             #37: (197,179,168) #C5B3A8 srgb(197,179,168)   #sel_color_8 #7d6b91bba259
        ]                                                                              #ts_color_8 #d0f0db4ee3ca
                                                                                       #bs_color_8 #4e845b3b65a2
    def replaceColorsInPixmap(self,pixmap,fromcolor,tocolor):
            mask = pixmap.createMaskFromColor(QtGui.QColor(fromcolor), QtCore.Qt.MaskOutColor)
            p = QtGui.QPainter(pixmap)
            p.setPen(QtGui.QColor(tocolor))
            p.drawPixmap(pixmap.rect(), mask, mask.rect())
            p.end()

    #all buttons and backround sit in single resourcePng. A copy of this is colored and sharpened/contrastmodified here
    #to use as actual buttons and backgrounds.  Used both for initialization and update
    def initUpdateResourceImgs(self):
        #HASH motifcolors[bg_color_6] => #882733 etc for lookup of cde color palette values
        motifcolors=Globals.colorshash
        #copy of resourcePng to modify and crop sprites from
        tmppixmap=QtGui.QPixmap(self.resourcePng)
            #replace colors with cde/motif color palette Note: color mapping has to be done first because sharpening etc
            #changes the color palette so no 1-1 correspondence to motif color theme can be made anymore
        colormap=self.colorMap(self.opts.panelcolor)
        for i in range(len(colormap)):
            fromcolor=colormap[i][0] #['#464D54','bs_color_3']
            tocolor=motifcolors[colormap[i][1]]#motifcolors[ts_color_4]=#72ab84
            self.replaceColorsInPixmap(tmppixmap,fromcolor,tocolor)
	    # apply sharpening etc to resource img
        tmppixmap=convertPixmap(tmppixmap,1,1,self.opts.saturation,self.opts.sharp)
            #finally crop out the individual sprites and store in IMG[key] = IMG[pager-button-1] etc for global usage by
            #all buttons.  Only loop over initial sprites, not over the workspacebuttons that are added below:
        #for key in Globals.IMG: ####NO
        for key in [col[0] for col in spriteLWHXY]:
            gi=Globals.IMG[key]
            gi.img=tmppixmap.copy(gi.rect)
        #NOW ADDTOIMG A NUMBER OF COLORED WORKSPACEBUTTONS FOR DIFFERENT WORKSPACES CORRESPONDING TO DIFFERENT COLORSETS
        #START FROM SINGLE ONE IN RESOURCE #FIGURE OUT WHICH COLOR SETS ARE PRESENT IN WORKSPACE 1-N:
        nw=self.opts.nworkspaces
        wc=self.opts.workspacecolors
        wl=self.opts.workspacelabels
            #copy out the original one (single present in resourcex called 'pagerbutton and pagerbuttonpressed')
        pbsrc={}
        for key in ['pagerbutton','pagerbuttonpressed']:
            gi=Globals.IMG[key]
            pbsrc[key] = self.resourcePng.copy(gi.rect)
        for n in range(1,nw+1):
            for key in ['pagerbutton','pagerbuttonpressed']:
                wscol=wc[n]
                #make copy for each button and replace the colors in that
                tmppixmap=QtGui.QPixmap(pbsrc[key])
                #(this is the area surrounding the actual button:)
                #self.replaceColorsInPixmap(tmppixmap,'#C5B3A8',motifcolors['bg_color_5'])
                self.replaceColorsInPixmap(tmppixmap,'#C5B3A8',motifcolors['bg_color_'+str(self.opts.panelcolor)])
                #(here button itself:
                self.replaceColorsInPixmap(tmppixmap,'#8998AB',motifcolors['bg_color_'+str(wscol)])
                self.replaceColorsInPixmap(tmppixmap,'#464D54',motifcolors['bs_color_'+str(wscol)])
                self.replaceColorsInPixmap(tmppixmap,'#C9D1DA',motifcolors['ts_color_'+str(wscol)])
                #label must be inserted here so it will also sharpen/soften
                drawTextOnPixmap(wl[n],Globals.fontSize-1,.1,0.05,tmppixmap)
                #sharpen etc. uses PIL. can of worms see above 
                tmppixmap=convertPixmap(tmppixmap,1,1,self.opts.saturation,self.opts.sharp)
                i=josImg()
                drawTextOnPixmap(wl[n],Globals.fontSize-1,.1,0.05,tmppixmap)
                label=key+str(n)#eg pagerbutton3 and pagerbuttonpressed3:
                i.rect=gi.rect
                i.img=tmppixmap
                Globals.IMG[label]=i
        self.update()
        for i in Drawer.instancelist:
            i.repaint()
                #i.x=x# are read only from now on, xy are only for cutting out of resource
                #i.y=y
                    #PROBLEMS HERE WITH GARBLED IMAGES. THIS WORKED BOTH WITH AND WITHOUT CONVERTPIXMAP:
                #i.img=tmppixmap.copy(QtCore.QRect(0, 0, width,height))
                    #WORKS ONLY WITHOUT THE CONVERTPIXMAP:
                    #BUT IF CONVERTPIXMAP DOES SAVELOAD BEFORE RETURNING, IT DOES WOERK:
                    #OR IF IT DOES A .COPY... SEE THE FUNC ABOVE. Maybe PIL results are not memory managed by qt or something
                #i.img=tmppixmap
        #needed for 'toggleNColors': (and for...)

    # SAVING AND LOADING AND SUCH #######################################################################

    #LAYOUT FILE CAN CONTAIN LINES:
    #workspacebuttons                                           #insert the pager
    #Mydrawerfile                                               #drawer file in configdir/drawers containing desktopentypaths
    #/usr/share/applications/k4dirstat.desktop                  #desktopentrypath
    #/usr/share/applications/k4dirstat.desktop Mydrawerfile     #both (in this order)
    #                                                           #empty line for an empty combobutton
    def insertFromLayoutFile(self):
        filename=checkFile(os.path.join(Globals.configdir,'layout'))
        with open(filename) as f:lines=f.read().splitlines() 
        for l in lines:
            #yes so..
            l=re.sub('__CONFIGDIR__',Globals.configdir,l)
            #split words separated by empty spaces into list
            x=l.split() 
            #for empty line insert empty combobutton
            if len(x)==0:
                self.insertComboButton(self.opts,'','')
                continue
            #for keyword 'workspacebuttons' insert the pager
            if x[0]=='clock':
                self.insertClock(self.opts,'','')
                continue
            if x[0]=='workspacebuttons':
                self.insertLeftPagerSpacer(self.opts)
                self.insertLockButton(self.opts)
                self.insertWorkspaceButtons(self.opts)
                self.insertExitButton(self.opts)
                self.insertRightPagerSpacer(self.opts)
            elif len(x)==1: #one word on the line
                pathorfile=x[0]
                #if full path given, presume its a desktopentry, if not, a drawerfile
                if os.path.isfile(pathorfile): self.insertComboButton(self.opts,pathorfile,'')
                else:   
                    drawerfile=os.path.join(Globals.drawerdir,pathorfile)
                    if not os.path.isfile(drawerfile):
                        print 'WARNING: Drawer file not found '+drawerfile
                        drawerfile=''
                    self.insertComboButton(self.opts,'',drawerfile)
            elif len(x)==2:#two words: first desktopentryfile, then drawerfile
                desktopentrypath=x[0]
                drawerfile=os.path.join(Globals.drawerdir,x[1])
                if not os.path.isfile(drawerfile):
                    print 'WARNING: Drawer file not found '+drawerfile
                    drawerfile=''
                self.insertComboButton(self.opts,desktopentrypath,drawerfile)
    def readPaletteFile(self):
        print 'def readPaletteFile(self):'
        #self.opts.currentpalettefile deternines current palette #eg Broica.dp:
        #this one is still used by drawers
        Globals.colorshash=readMotifColors2(self.opts.ncolors,Globals.palettedir+'/'+self.opts.currentpalettefile)
        print 'exit def readPaletteFile(self):'

    def saveAll(self,delay=3000):
        #auto saving files when eg changing the window size makes things slow because
        #the save is called too often quickly in a row. So put on timer. If timer is called
        #again before it has fired, it will be replaced by a new one. So func will be called only
        #once after X ms
        #hmm this format creates different timers, not overwrite !:
        #self.savetimer=QtCore.QTimer.singleShot(1000,self.doSave)
        #so use this, here the timer gets overwritten if called again:
        self.saveTimer=QtCore.QTimer()
        self.saveTimer.setSingleShot(True)
        self.saveTimer.timeout.connect(self.doSave)
        self.saveTimer.start(delay)
    def doSave(self):
        self.saveLayout()
        self.saveOpts()
    def savePalette(self):
        currentpalettefilefullpath=os.path.join(Globals.palettedir,self.opts.currentpalettefile)
        #if ncolors is 4 (cde reduced palette) Globals.colorshash is only 4 col. But saving the palette
        #after possible modifying, we dont want to loose cols 4-7 so :
        #first load old ones
        colorshashtmp=readMotifColors2(Globals.ncolorsmax,currentpalettefilefullpath)
        #then if n=4: replace the first 4 colors with the new (maybe modified) ones.
         #if n=8 overwrite all. Thus preserve old 4-7:
        if self.opts.ncolors==4:N=4
        else: N=Globals.ncolorsmax
        for i in range(1,N+1):
            colorshashtmp['bg_color_'+str(i)]=Globals.colorshash['bg_color_'+str(i)]
        #save them all
        with open(currentpalettefilefullpath, 'w') as f:
            for i in range(1,Globals.ncolorsmax+1):
                f.write(colorshashtmp['bg_color_'+str(i)]+'\n')
    def saveOpts(self):
        self.opts.save(Globals.configfile)
    def saveLayout(self):
        filename=os.path.join(Globals.configdir,'layout')
        backup=filename+'.backup'
        print 'Copying old layout file to '+backup
        cmd='cp'+' '+filename+' '+backup
        execWithShell(cmd)
        print 'SAVING LAYOUT TO FILE '+filename
        with open(filename, 'w') as f:
            for c in self.findChildren(VBox):
                if c.isComboButton:
                    b=c.findChildren(PicButtonCommandLauncher1)[0]
                    drawerfilenopath=os.path.basename(c.drawerfile)
                    desktopentrypath=b.desktopentrypath
                    desktopentrypath=re.sub(Globals.configdir,'__CONFIGDIR__',desktopentrypath)
                    f.write( (desktopentrypath + ' ' + drawerfilenopath).strip() +'\n')
                if c.isLeftPagerSpacer:
                    f.write('workspacebuttons\n')
                if c.isClock:
                    f.write('clock\n')

    # WORKSPACE SWITCHING AND SUCH ##################################################################

    #Set the toggeled state (in/out) of the workspacebuttons to reflect the actual current workspace
    #called by timer, every N ms, only from mainpanel
    #only change state and update screenshot when currentworkspace has changed,
    def updateWorkspaceButtons(self):
        currentworkspace=WorkspaceFuncs.getCurrentWorkspace()
        if (currentworkspace != self.previousWorkspace): 
            print 'WORKSPACE CHANGED TO '+str(currentworkspace)
            self.previousWorkspace=currentworkspace
            for i in self.workspaceButtonList:
                if currentworkspace==i.workspacenr: i.setChecked(True)
                else: i.setChecked(False)

    #display cdepanel on all virtual workspaces.(sticky)  called by timer, only from main panel
    #need to call this from timer, because program doesnt appear in windowlist until ... x sec after start
    #todo is this still true when using the new module??
    def setPanelSticky(self):
        print 'def setPanelSticky(self):'
        panelExecutableName=os.path.basename(__file__)
        WorkspaceFuncs.setWindowSticky1(panelExecutableName)

    #backdrops are handled in ThemeXfce.py but setting is kept here for now (to keep all settings in one place)
    def setBackdropForWorkspaceNr(self,N,backdrop):
        self.opts.workspacebackdrops[N]=backdrop 
    def getBackdropForWorkspaceNr(self,N):
        return self.opts.workspacebackdrops[N]

    # DRAWING/RENDERING FUNCTIONS ############################################################

    def updateStyleSheet(self): #(all colors are pixmap, but necessary for readable tooltips !)
        tooltipbackground=Globals.colorshash['bg_color_2']
        tooltipforeground=Globals.colorshash['fg_color_2']
        tooltipborder=Globals.colorshash['ts_color_2']
        #(hide pixelgap at bottom of panel by giving it the same color as the bottom shadow
        # maybe try and remove it later in another way, shouldnt be there):
        cdepanelbackground=Globals.colorshash['bs_color_2']
        style="""
            CdePanel {{ background-color:{cdepanelbackground}; }}
            QToolTip {{ background-color:{tooltipbackground}; color:{tooltipforeground}; border-color:{tooltipborder}; border-width: 1px; border-style:solid;}}
        """.format(**locals())
        self.setStyleSheet(style)


    def updateAfterSettingChange(self):
        self.updateStyleSheet()
        self.initUpdateResourceImgs()
        self.theme.updateTheme(delay=300)
        self.saveAll(delay=5000)

    #for readable tooltips:
    #fit main window around toplevel hbox (same size). 
    def adjustWidthToMainWidget(self):
        c=self.hbox #the central widget
        self.setFixedWidth(c.width())
        self.setFixedHeight(c.height())
    def positionBottomCenter(self):    
        screen = QtGui.QDesktopWidget().screenGeometry()
        widget = self.geometry()
        x = (screen.width() - widget.width())/2
        y = screen.height() - widget.height()
        self.move(x, y)
    def changeBlinker(delta):
        Globals.blinker+=delta
        #print Globals.blinker

    # SWITCHING PANEL SETTINGS ###################################################################

    #keyboard input
    def keyPressEvent(self, event):
        if type(event) == QtGui.QKeyEvent:
            print 'KEY '+str(event.key())#__debug
            modifiers = QtGui.QApplication.keyboardModifiers()
            M=QtGui.QApplication.keyboardModifiers()
            K=event.key()
            S=QtCore.Qt.ShiftModifier
            C=QtCore.Qt.ControlModifier
            #for debugging
            if event.key()==67:#c
                self.openConfigDialog()
            if event.key()==82:#r
                self.saveLayout()
            if event.key()==84:#t
                pass
                #self.savePalette()
                #self.test()
            if event.key()==80 and modifiers==QtCore.Qt.ShiftModifier:#P
                self.switchPalette(0)
            elif event.key()==80:#p
                self.switchPalette(1)
            elif K==72:
                if M==S: self.sharpLess()#H
                else: self.sharpMore()#h
            elif K==83:
                if M==S: self.saturationLess()#S
                elif M==C: self.saveAll() 
                else: self.saturationMore()#s
            elif event.key()==61:#=
                self.growWindow()
            elif event.key()==45:#-
                self.shrinkWindow()
            elif event.key()==78:#n
                self.toggleNColors()
            elif event.key() == QtCore.Qt.Key_Escape:
                self.closeAllDrawers()
            #control key pressed
            elif modifiers == QtCore.Qt.ControlModifier:
                if event.key()==67:#ctrl-c
                    self.exitProgram()
            event.accept()
        else:
            event.ignore()

    # mouse intput
    def wheelEvent(self,event):
        if QtGui.QApplication.keyboardModifiers()==QtCore.Qt.ControlModifier:
            if event.delta()<=0:self.changeWindowHeight(-2)
            else:self.changeWindowHeight(+2) 
        elif QtGui.QApplication.keyboardModifiers()==QtCore.Qt.ShiftModifier:
            if event.delta()<=0:self.reSharp(-0.2)
            else: self.reSharp(+0.2)
        else: 
            if event.delta()<0: WorkspaceFuncs.switchToNextWorkspace()
            else: WorkspaceFuncs.switchToPrevWorkspace()
    
    def setPanelColor(self,N):
        self.opts.panelcolor=N
        self.readPaletteFile()
        Drawer.updateStyleSheets()# for tooltips
        self.updateAfterSettingChange()
    #switch between 4 and 8 color palette
    def setNColors(self,N):
        if not (N==4 or N==8): N=8
        self.opts.ncolors=N
        self.readPaletteFile()
        Drawer.updateStyleSheets()# for tooltips
        self.updateAfterSettingChange()
    def toggleNColors(self):
        if self.opts.ncolors==8:self.opts.ncolors=4
        else: self.opts.ncolors=8
        self.readPaletteFile()
        Drawer.updateStyleSheets()# for tooltips
        self.updateAfterSettingChange()
    #traverse palette list, up or down currentpaletteix and currentpalettefile
    def switchPalette(self,direction):
        currentpaletteix=Opts.paletteFile2Ix(self.opts.currentpalettefile)
        if direction==0:#back
            P=currentpaletteix-1
            if P<0:P=len(Globals.palettes)-1
        else:#forward
            P=currentpaletteix+1
            if P>len(Globals.palettes)-1:P=0
        currentpaletteix=P
        self.opts.currentpalettefile=Opts.ix2PaletteFile(currentpaletteix)
        print 'Palette file '+self.opts.currentpalettefile#__debug
        print 'N Colors '+str(self.opts.ncolors)
        self.readPaletteFile()
        print """Drawer.updateStyleSheets()# for tooltips"""#__debug
        Drawer.updateStyleSheets()# for tooltips
        self.updateAfterSettingChange()

    #mainwindow, not hbox. This does not trigger resizeevent for 
    #hbox so set hbox height manually in resizeevent.
    def changeWindowHeight(self,delta):
        self.opts.initialheight+=delta
        #Globals.scalefactor=float(self.opts.initialheight)/85
        Globals.scalefactor=float(self.opts.initialheight)/85
        print 'Globals.scalefactor '+str(Globals.scalefactor)#__debug
        self.setFixedHeight(self.opts.initialheight) 
        print 'HEIGHT '+str(self.height())
        #this triggers resizeevent in hbox:
        self.hbox.setFixedHeight(self.height()) 
        self.adjustWidthToMainWidget()
        self.positionBottomCenter()
        #rescale before positioning , because the correct positioning of the drawers depends on their size
        #as the bottom must be placed on top of the main window so we need to know their hight
        self.rescaleDrawers()
        self.positionDrawers()
        self.saveAll()
    def saturationMore(self):
        self.opts.saturation*=1.1
        print 'SATURATION '+str(self.opts.saturation)
        self.initUpdateResourceImgs()
        self.saveAll()
    def saturationLess(self):
        print 'here'
        self.opts.saturation*=0.9
        print 'SATURATION '+str(self.opts.saturation)
        self.initUpdateResourceImgs()
        self.saveAll()
    def growWindow(self):
        self.changeWindowHeight(+1)
    def shrinkWindow(self):
        self.changeWindowHeight(-1)
    def reSharp(self,delta):
        self.opts.sharp+=delta
        if self.opts.sharp>4:
            self.opts.sharp=4
            print 'MAX ALLOWED SHARPNESS, YOU ARE AT RISK OF DAMAGING YOUR SCREEN !!!!'
        if self.opts.sharp<0:
            self.opts.sharp=0
            print 'MAX SOFTNESS/ANTIALIAS, NO FURTHER POSSIBLE'
        print 'SHARPNESS '+str(self.opts.sharp)	    
        self.initUpdateResourceImgs()	    
        self.saveAll()
    def sharpMore(self):
        self.reSharp(+0.1)
        self.saveAll()
    def sharpLess(self):
        self.reSharp(-0.1)
        self.saveAll()


    # PANEL MENU / EDITING FUNCTIONS #####################################################################

    #right click menus
    def contextMenuEvent(self, event):
        #dont display contextmenu while moving combobutton. Click should then
        #stop the moving operation instead (in mouseReleaseEvent):
        if self.moveComboButtonInProgress:return
        #display different menus for different buttons, always display 'configure panel'
        b=self.childAt(event.pos())#these are picbuttons of various kinds
        pickdrawerfile=deletebutton=insertbutton=clearbutton=movebutton=deletedrawer=newdrawer=0
        menu = QtGui.QMenu(self)
        if b.isLauncher:
            vbox=b.parent()
            deletebutton = menu.addAction('Delete button')
            insertbutton= menu.addAction('New')
            clearbutton = menu.addAction('Show empty')
            movebutton = menu.addAction('Move')
        if b.isDrawer:
            deletedrawer= menu.addAction('Hide drawer')
            pickdrawerfile = menu.addAction('Pick drawer file')
            newdrawer = menu.addAction('New drawer')
        menu.addSeparator()
        configure = menu.addAction('Configure Panel')
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == configure:
            self.openConfigDialog()
        if action == deletebutton:
            self.deleteComboButton(vbox)
        if action == clearbutton :
            self.clearComboButtonLauncher(b)
        if action == insertbutton:
            self.insertComboButtonAfter(vbox)
        if action == movebutton:
            self.moveComboButton(vbox)
        if action == deletedrawer:
            self.deleteDrawerButton(b)
        if action == newdrawer:
            self.newDrawerButton(b,self.newDrawerFile())
            #self.newDrawerButton(b)
        if action == pickdrawerfile:
            self.newDrawerButton(b,self.pickDrawerFile())
            
    def openConfigDialog(self):
        try: 
            self.configDialog.close()
            self.configDialog.setParent(None)
        except: pass
        self.configDialog=ColorDialog(self)
        self.configDialog.show()

    def test(self):
        #necessary for cProfile
        QtCore.QCoreApplication.quit()
        

    def clearComboButtonLauncher(self,b):
        b.imgicon = QtGui.QPixmap(Globals.defaultxpm)
        b.desktopentrypath=''
        b.command=''
        b.fileicon=''
        b.update()
        b.setToolTip('')
    def deleteDrawerButton(self,b):
        bnew = PicButtonToggle('drawerbuttonempty','drawerbuttonempty','empty',self.opts,b.parent())
        bnew.isDrawer=True
        bnew.show()
        #the enclosing vbox also carries reference to the drawerfile
        bnew.parent().drawerfile=''
        self.stackWidgetAfter(b,bnew)
        b.setParent(None)
        bnew.parent().initAfterFilling()
        self.postMutateComboButtons()
        self.saveLayout()
    def moveComboButton(self,vbox): 
        self.moveComboButtonInProgress=True
        self.movingComboButton=vbox
        self.setMouseTracking(True)
        self.setAllEnabled(False)
        b=vbox.findChildren(PicButtonCommandLauncher1)[0]
        #display picbutton icon faded and leftright arrows on top
        b.displayArrows=True
        b.update()
    #move the movingComboButton to position after vboxto
    #todo use 'stackBefore' (didnt know it existed) 
        #no: not availble for 'picbutton'
    def moveComboButtonAfter(self,vboxto):
        C=self.hbox.children()
        vbox=self.movingComboButton
        vbox.raise_()
        self.postMutateComboButtons()
        C=self.hbox.children()
        ixto=C.index(vboxto)
        for i in range(ixto+1,len(C)-1):
            C[i].raise_()
        self.postMutateComboButtons()
    def moveComboButtonBefore(self,vboxto):
        C=self.hbox.children()
        vbox=self.movingComboButton
        vbox.raise_()
        self.postMutateComboButtons()
        C=self.hbox.children()
        ixto=C.index(vboxto)
        for i in range(ixto,len(C)-1):
            C[i].raise_()
        self.postMutateComboButtons()
    #0 1 2 3 (4) 5 ... N-1
    #<-lower()   raise_()->
    #insert new combobutton after given vbox
    #todo use same here as in reading from file to make dynamic read possible
    def insertComboButtonAfter(self,vbox):
        self.insertComboButton(self.opts,'','')
        C=self.hbox.children()
        #new combobutton was pasted at end (N-1)
        cn=C[len(C)-1]
        cn.show()
        #index after of the vbox that was right clicked on
        ix=C.index(vbox)+1
        #move the new one by 'raising' the ones that should be to the right of it
        for i in range(ix,len(C)-1):
            C[i].raise_()
        self.postMutateComboButtons()
    def deleteComboButton(self,vbox):
        vbox.setParent(None) #delete NOW 
        self.postMutateComboButtons()
    #recalculate positions etc after insert/remove/move combobuttons
    def postMutateComboButtons(self):
        self.closeAllDrawers()#the easy way out
        self.hbox.initAfterFilling()
        self.adjustWidthToMainWidget()
        self.positionBottomCenter()
        self.rescaleDrawers()
        self.positionDrawers()

    def mouseMoveEvent(self, event):
        #moveComboButton has started
        if self.moveComboButtonInProgress:
            curChild=self.childAt(event.pos())
            if curChild==None:return
            #offset of mousepointer in current child coordinates
            dx=event.pos().x()-curChild.parent().x()
            ccw=curChild.parent().width()
            if dx<ccw/2.0: putBefore=True
            else: putBefore=False
            #make sure curChild.parent is vbox
            curvbox=curChild.parent()
            if isinstance(curvbox,VBox):
                #if mouse ends up on the moving child itself after move, do nothing
                if curvbox==self.movingComboButton:return
                if curvbox.isComboButton:
                    if putBefore: self.moveComboButtonBefore(curvbox)
                    else: self.moveComboButtonAfter(curvbox)
                #dont move the movingComboButton into the pager
                elif curvbox.isLeftPagerSpacer:
                    if putBefore: self.moveComboButtonBefore(curvbox)
                elif curvbox.isRightPagerSpacer:
                    if not putBefore: self.moveComboButtonAfter(curvbox)
            
    #end the move combobutton operation by left click
    def mouseReleaseEvent(self,event):  
        if self.moveComboButtonInProgress:
            self.setMouseTracking(False)
            self.setAllEnabled(True)
            #this doesnt work if the mouse is released on a neighbouring combubut:
            #b=self.childAt(event.pos())#these are picbuttons of various kinds
            #so use the stored movingComboButton instead
            b=self.movingComboButton.findChildren(PicButtonCommandLauncher1)[0]
            b.displayArrows=False
            b.update()
            #because things are getting mixed up a bit this placement is pretty critical: (last)
            self.moveComboButtonInProgress=False
            #for w in self.findChildren(QtGui.QLabel):w.pmUp()
        else:
            super(CdePanel, self).mouseReleaseEvent(event)

    def pickDrawerFile(self):
    #def pickDrawerFile(self,b):
        drawerdir=Globals.drawerdir
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', drawerdir,"Drawers (*)")
        fname=str(fname)
        drawerfile=os.path.join(drawerdir,fname)
        #drawertitle=os.path.basename(drawerfile)
        return drawerfile
        #b.setToolTip(drawertitle)
        #b.drawerfile=drawerfile
        #b.parent().drawerfile=drawerfile
        #self.saveLayout()
    def newDrawerFile(self):
        appmanager=self.findAppBrowser()
        drawerdir=Globals.drawerdir
        cmd='ls -v '+drawerdir+'/Drawer*'
        lines=subprocess.check_output(cmd, shell=True).splitlines()
        lastline=lines[len(lines)-1]
        match=re.search('Drawer(\d+)',lastline)
        N=int(match.group(1))+1
        newdrawerfile=re.sub('Drawer(\d+)','Drawer'+str(N),lastline)
        cmd='touch '+newdrawerfile
        #cmd="""echo '{appmanager}' > '{newdrawerfile}' """.format(**locals())
        print newdrawerfile
        #subprocess.check_output(cmd, shell=True).splitlines()
        execWithShell(cmd)
        return newdrawerfile
    def newDrawerButton(self,b,drawerfile):
    #def newDrawerButton(self,b):
        #drawerfile=self.newDrawerFile()
        #todo maybe better store this in thebutton but is used in savelayout
        #initially set in insertComboButton
        #this doesnt replace the original but just adds one
        bnew = PicButtonToggle('drawerbuttonclosed','drawerbuttonpressed','empty',self.opts,b.parent())
        bnew.isDrawer=True
        drawertitle=os.path.basename(drawerfile)
        bnew.setToolTip(drawertitle)
        bnew.drawerfile=drawerfile
        bnew.openfun=partial(self.openDrawer,bnew)
        bnew.clicked.connect(bnew.openfun)
        bnew.show()
        self.stackWidgetAfter(b,bnew)
        b.setParent(None)
        bnew.parent().initAfterFilling()
        #the enclosing vbox also carries reference to the drawerfile
        bnew.parent().drawerfile=drawerfile
        #for some reason this provides the magick prevent some drawing artefacts
        #   aha: the button with drawer arrow on it is a bit wider than the empty one
        #   so the total width of the hbox changes/has to be re-inited
        self.postMutateComboButtons()
        self.saveAll()
        self.openDrawer(bnew)
        bnew.setChecked(True)
        print bnew.drawerfile
    #move widget 'wmove' to  place after 'w' in stacking order
    #first put wmove on top, then move the other ones on top until wmove ends up at the right position
    def stackWidgetAfter(self,w,wmove):
        C=w.parent().children()
        wmove.raise_()
        C=w.parent().children()
        ix=C.index(w)
        for i in range(ix+1,len(C)-1): C[i].raise_()
        

    # THE WIDGLETS WIDGETS ###########################################################################

    #maybe pmut in classes later or something
    #just use this as shorthand for now Create a vbox parented to hbox, then create buttons parented
    #to the vbox Afterwards set the summed sizes and such by calling initAfterFilling Note that each
    #picbutton and receive entire initing from the parent this way but for now it suffices
    def insertRightHandle(self,opts):
       self.vbox = VBox(self.hbox)
       self.vbox.setToolTip('Try ctrl- and shift-mousewheel')
       b = PicButton('bordertopsquareunfocussed','bordertopsquareunfocussed','empty',opts,self.vbox)
       b = PicButton('handlerightbutton','handlerightbutton','empty',opts,self.vbox)
       b = PicButton('handlerightmiddle','handlerightmiddle','empty',opts,self.vbox)
       b.clicked.connect(self.activateAllWindows)
       b = PicButton('borderbottomsquareunfocussed','borderbottomsquareunfocussed','empty',opts,self.vbox)
       self.vbox.initAfterFilling()
    def insertLeftPagerSpacer(self,opts):
       self.vbox = VBox(self.hbox)
       self.vbox.isLeftPagerSpacer=True
       b = PicButton('bordertopsquareunfocussed','bordertopsquareunfocussed','empty',opts,self.vbox)
       b = PicButton('pagerspacerleftdrawer','pagerspacerleftdrawer','empty',opts,self.vbox)
       b = PicButton('pagerspacerleftlauncher','pagerspacerleftlauncher','empty',opts,self.vbox)
       b = PicButton('borderbottomsquareunfocussed','borderbottomsquareunfocussed','empty',opts,self.vbox)
       self.vbox.initAfterFilling()
    def insertRightPagerSpacer(self,opts):
       self.vbox = VBox(self.hbox)
       self.vbox.isRightPagerSpacer=True
       b = PicButton('bordertopsquareunfocussed','bordertopsquareunfocussed','empty',opts,self.vbox)
       b = PicButton('pagerspacerrightdrawer','pagerspacerrightdrawer','empty',opts,self.vbox)
       b = PicButton('pagerspacerrightlauncher','pagerspacerrightlauncher','empty',opts,self.vbox)
       b = PicButton('borderbottomsquareunfocussed','borderbottomsquareunfocussed','empty',opts,self.vbox)
       self.vbox.initAfterFilling()
    def insertLeftHandle(self,opts):
       self.vbox = VBox(self.hbox)
       self.vbox.setToolTip('Ctrl-Mousewheel:resize, Shift-Mousewheel: sharpen ')
       b = PicButton('bordertopsquareunfocussed','bordertopsquareunfocussed','empty',opts,self.vbox)
       b = PicButton('handleleftbutton','handleleftbutton','empty',opts,self.vbox)
       b = PicButton('handleleftmiddle','handleleftmiddle','empty',opts,self.vbox)
       b = PicButton('borderbottomsquareunfocussed','borderbottomsquareunfocussed','empty',opts,self.vbox)
       self.vbox.initAfterFilling()
    def insertLeftBorder(self,opts):
       self.vbox = VBox(self.hbox)
       b = PicButton('borderlefttopunfocussed','borderleftunfocussed','empty',opts,self.vbox)
       b = PicButton('borderleftunfocussed','borderleftunfocussed','empty',opts,self.vbox)
       b = PicButton('borderleftbottomfocussed','borderleftbottomfocussed','empty',opts,self.vbox)
       self.vbox.initAfterFilling()
    def insertRightBorder(self,opts):
       self.vbox = VBox(self.hbox)
       b = PicButton('borderrighttopunfocussed','borderrighttopunfocussed','empty',opts,self.vbox)
       b = PicButton('borderrightunfocussed','borderrightunfocussed','empty',opts,self.vbox)
       b = PicButton('borderrightbottomunfocussed','borderrightbottomunfocussed','empty',opts,self.vbox)
       self.vbox.initAfterFilling()
    def insertLockButton(self,opts):
       self.vbox = VBox(self.hbox)
       b = PicButton('bordertopsquareunfocussed','bordertopsquareunfocussed','empty',opts,self.vbox)
       b = PicButtonCommand('lockwithbg','lockwithbgpressed','',self.opts.lockbuttoncommand,opts,self.vbox)
       b = PicButton('lockbottom','lockbottom','empty',opts,self.vbox)
       b = PicButton('borderbottomsquareunfocussed','borderbottomsquareunfocussed','empty',opts,self.vbox)
       self.vbox.initAfterFilling()
    def insertExitButton(self,opts):
       self.vbox = VBox(self.hbox)
       b = PicButton('bordertopsquareunfocussed','bordertopsquareunfocussed','empty',opts,self.vbox)
       #b = PicButtonCommand('hddlight','hddlight','empty','',opts,self.vbox)
       b = PicButtonBlink(Globals.blinkerList,'hddlight','hddlighthi',opts,self.vbox)
       b = PicButtonCommand('exitbutton','exitbuttonpressed','',self.opts.exitbuttoncommand,opts,self.vbox)
       b = PicButton('borderbottomsquareunfocussed','borderbottomsquareunfocussed','empty',opts,self.vbox)
       self.vbox.initAfterFilling()

    def insertComboButton(self,opts,desktopentrypath,drawerfile):
        #b = PicButtonToggle('drawerbuttonempty','drawerbuttonempty','empty',opts,self.vbox)
        self.vbox = VBox(self.hbox)
        self.vbox.desktopentrypath=desktopentrypath
        self.vbox.drawerfile=drawerfile
        self.vbox.isComboButton=True
        b = PicButton('bordertopsquareunfocussed','bordertopsquareunfocussed','empty',opts,self.vbox)
        #IF DRAWERFILE GIVEN AND IT EXISTS, ADD A DRAWER BUTTON
        if os.path.isfile(drawerfile):
            b = PicButtonToggle('drawerbuttonclosed','drawerbuttonpressed','empty',opts,self.vbox)
            b.isDrawer=True
            drawertitle=os.path.basename(drawerfile)
            b.setToolTip(drawertitle)
            b.drawerfile=drawerfile
            b.openfun=partial(self.openDrawer,b)
            b.clicked.connect(b.openfun)
        else:
            #else add en empty drawer button
            b = PicButtonToggle('drawerbuttonempty','drawerbuttonempty','empty',opts,self.vbox)
            b.isDrawer=True
        #IF DESKTOPENTRYPATH GIVEN AND IT EXISTS:
        if os.path.isfile(desktopentrypath):
            #this is icon name without path or extension. is stored in the freedeskotp desktopentry
            #eg for xterm it could be xterm-icon-32 if actual icon name is xterm-icon-32.png etc
            #xdg module doesnt find icons well so do myself:
            d=DesktopEntry.DesktopEntry(desktopentrypath)
            iconnamenoext=d.getIcon()
            icon=findIconFromName1(iconnamenoext)
            command=d.getExec()
        else:
            icon=''
            command=''
        b = PicButtonCommandLauncher1('launcher','launcherpressed',desktopentrypath,opts,self.vbox)
        b.isLauncher=True
        b = PicButton('borderbottomsquareunfocussed','borderbottomsquareunfocussed','empty',opts,self.vbox)
        self.vbox.initAfterFilling()

    def insertClock(self,opts,desktopentrypath,drawerfile):
        #b = PicButtonToggle('drawerbuttonempty','drawerbuttonempty','empty',opts,self.vbox)
        self.vbox = VBox(self.hbox)
        self.vbox.desktopentrypath=desktopentrypath
        self.vbox.drawerfile=drawerfile
        #self.vbox.isComboButton=True
        self.vbox.isClock=True
        b = PicButton('bordertopsquareunfocussed','bordertopsquareunfocussed','empty',opts,self.vbox)
        #IF DRAWERFILE GIVEN AND IT EXISTS, ADD A DRAWER BUTTON
        if os.path.isfile(drawerfile):
            b = PicButtonToggle('drawerbuttonclosed','drawerbuttonpressed','empty',opts,self.vbox)
            b.isDrawer=True
            drawertitle=os.path.basename(drawerfile)
            b.setToolTip(drawertitle)
            b.drawerfile=drawerfile
            b.openfun=partial(self.openDrawer,b)
            b.clicked.connect(b.openfun)
        else:
            #else add en empty drawer button
            b = PicButtonToggle('drawerbuttonempty','drawerbuttonempty','empty',opts,self.vbox)
            b.isDrawer=True
        #IF DESKTOPENTRYPATH GIVEN AND IT EXISTS:
        if os.path.isfile(desktopentrypath):
            d=DesktopEntry.DesktopEntry(desktopentrypath)
            iconnamenoext=d.getIcon()
            icon=findIconFromName1(iconnamenoext)
            command=d.getExec()
        else:
            icon=''
            command=''

        b = PicButtonClock('launcher','launcherpressed',desktopentrypath,opts,self.vbox)

        b.isLauncher=True
        b = PicButton('borderbottomsquareunfocussed','borderbottomsquareunfocussed','empty',opts,self.vbox)
        self.vbox.initAfterFilling()

    def insertWorkspaceButtons(self,opts):
            #if i do 'import WorkspaceFuncs' the funcs inside can be accessed as globals like WorkspaceFuncs.setNumberOfWorkspaces etc
        WorkspaceFuncs.setNumberOfWorkspaces(opts.nworkspaces)
            #to be sure that correct number is set, get actual number of workspaces. (hmm)
            #that doesnt work for some reason so.. yes. 
            #nworkspaces=WorkspaceFuncs.getLastWorkspace()
        nworkspaces=self.opts.nworkspaces
        print 'nworkspaces '+str(nworkspaces)#__debug
        currentworkspace=WorkspaceFuncs.getCurrentWorkspace()
        print 'NUMBER OF WORKSPACES SET TO '+str(nworkspaces)
        workspacenr=0
            #workspacebuttons are inserted an columns of picbuttons stacked on top of eachother but they number as  eg (n=6):
               #1  2  3
               #4  5  6
            #etc so calculate the workspace number per row
            #python style range 0,4 -> 0 1 2 3
        for column in range(0,nworkspaces/2):
                #TOP BUTTON #######################
            workspacenr=column+1
            workspacecolor=self.getWorkspaceColor(workspacenr)
            self.vbox = VBox(self.hbox)
            self.vbox.setToolTip('Mousewheel = switch workspace')
            b = PicButton("bordertopsquareunfocussed","bordertopsquareunfocussed","empty",opts,self.vbox)
            b = PicButton("pagerspacertop","pagerspacertop","empty",opts,self.vbox)
            #self.createWorkspaceIcon(workspacenr)
            #workspacebuttons in different cols are generated in 
            b = PicButtonWorkspace('pagerbutton'+str(workspacenr),'pagerbuttonpressed'+str(workspacenr),'',opts,self.vbox)
            b.isWorkspaceButton=True
                #buttons are bound to call to function to switch to specific number, but each button
                #needs to also know to which workspace it belongs, for updateWorkspaceButtons to be able to check if
                #a given button belongs to a given workspacenr and put it in up or down state
            b.setWorkspaceNr(workspacenr)
            b.clicked.connect(partial(WorkspaceFuncs.setCurrentWorkspace,workspacenr))
            self.workspaceButtonList.append(b)
                #BOTTOM BUTTON ###################
            workspacenr=column+1+nworkspaces/2
            workspacecolor=self.getWorkspaceColor(workspacenr)
            #self.createWorkspaceIcon(workspacenr)
            b = PicButtonWorkspace('pagerbutton'+str(workspacenr),'pagerbuttonpressed'+str(workspacenr),'',opts,self.vbox)
            b.isWorkspaceButton=True
            b.setWorkspaceNr(workspacenr)
            b.clicked.connect(partial(WorkspaceFuncs.setCurrentWorkspace,workspacenr))
            self.workspaceButtonList.append(b)
            b = PicButton("pagerspacerbottom","pagerspacerbottom","empty",opts,self.vbox)
            b = PicButton("borderbottomsquareunfocussed","borderbottomsquareunfocussed","empty",opts,self.vbox)
            self.vbox.initAfterFilling()

    # DRAWERS ##########################################################################

    #hmmm should this be in Drawer.py? todo
    def openDrawer(self,b): # b is the drawer button that opened drawer 
        X=self.x()#location of mainpanel on screen
        Y=self.y()
        #self.drawer = Drawer(b.drawerfile,self.opts) #b remembers the drawerfile corresponding to drawer that it opened
        #NOTE: ADDED 'SELF' HERE NOT FOR PARENTING, BUT BECAUSE DRAWER NEEDS REFERENCE TO MAIN WINDOW
        #'SELF' HERE IS NOT PASSED TO INIT OF QT SUPERCLASS
        self.drawer = Drawer(b.drawerfile,self.opts,self) #b remembers the drawerfile corresponding to drawer that it opened
        #self.drawer = Drawer(b.drawerfile,self.opts,self) #dit kan niet dan gaat ie hem parenten
        #store reference to button that was pressed into the drawer object for later reference 
        self.drawer.originatingbutton=b
        #store reference to main window to be able to for when drawer closes using keybinding, the 
        #drawerbutton state changes (can butt do this by itslelf?)todo
        self.drawer.mainwindow=self
        #must show before placing the drawer in the right location (otherwise move() doesnt work) 
        self.drawer.show()   
        #make drawerdialog line up with drawer button in main window and get screenlocation
        x0,y0=self.positionDrawer(self.drawer)
        #store thes positions for if drawer gets new items dropped into them, it moves. Positioin needs to
        #be restored be able to later. Remember these are TOP LEFT of original drawer position. 
        #Better also store y of bottom of the drawer. This is where it needs to be fixed after size change later
        self.drawer.x0=x0
        self.drawer.y0=y0
        self.drawer.y0bottom=y0+self.drawer.height()
        #disconnect button and reconnect to now close drawer
        try: b.clicked.disconnect() 
        except Exception: pass
        #also store in button the function needed for closing, for later use
        b.closefun=partial(self.closeDrawer,self.drawer)
        b.clicked.connect(b.closefun)
    #drawer must be placed next to drawerbutton on main window that opened it. 
    #do this and return also position in screen coordinates
    def positionDrawer(self,drawer):
        b=drawer.originatingbutton
        p=b.parent()#a vbox (combobutton and such)
        x=p.x()#vbox location wrt main window (top left =0,0)
        X=self.x()#location of mainpanel on screen
        Y=self.y()
        x0=X+x#location of drawer on screen to line up with pressed drawer button b
        y0=Y-drawer.height()+3#location of drawer on screen
        drawer.move(x0,y0)
        drawer.activateWindow() #raise above main panel during move to sit on top of border
        return x0,y0
    def rescaleDrawers(self):
        alldrawers=Drawer.instancelist[:] 
        for drawer in alldrawers:
            drawer.positionEntriesAndResizeDrawer()
    def positionDrawers(self):
        alldrawers=Drawer.instancelist[:] 
        for drawer in alldrawers:
            self.positionDrawer(drawer)
    #maybe this should be in Drawer.py should close itself
    def closeDrawer(self,drawer):
        b=drawer.originatingbutton
        #save drawerfile in case new entries were dropped in
        drawer.saveDrawerFile()
        #close drawer window. should be cleaned up by python because no ref exists
        drawer.close() 
        #todo use .children() for this built in
        #remove from instancelist of drawers (used for updating all colors when changing palette)
        if drawer in Drawer.instancelist: Drawer.instancelist.remove(drawer)
        #set up drawer button for opening again
        #(why use 'try' again?>..... in case called twice?)
        try: b.clicked.disconnect() 
        except Exception: pass
        b.clicked.connect(b.openfun)
        #if closeDrawer is called from keyboard shortcut key, button doesnt go up by itself
        #so do explicitly. 
        b.setChecked(False)

    # HELPER FUNCTIONS #################################################################

    def exitProgram(self): 
        print '\n'
        print 'ncolors '+str(self.opts.ncolors)#__debug
        print 'initialheight '+str(self.opts.initialheight)#__debug
        print '\nBYE... '
        sys.exit()

    def activateAllWindows(self):
        alldrawers=Drawer.instancelist[:] 
        for i in alldrawers:
            i.activateWindow()
    def closeAllDrawers(self):
        #first make new copy because Drawer.instancelist changes when closing drawers. Iterate over the copy 
        alldrawers=Drawer.instancelist[:] 
        for i in alldrawers: self.closeDrawer(i)


    #set mousetracking true/false for all children recursively
    #used when dragging /moving a combobutton around with the mouse
    def setMouseTracking(self, flag):
        def recursive_set(parent):
            for child in parent.findChildren(QtCore.QObject):
                try: child.setMouseTracking(flag)
                except: pass
                recursive_set(child)
        QtGui.QWidget.setMouseTracking(self, flag)
        recursive_set(self)
    #after a combobutton has been moved, the move operation can be stopped by a left mouse
    #click on the button. To prevent the associated app from being launched, all buttons have
    #to be temporarily disabled. Do this by adding an event filer to all children
    #setAllEnabled(true/false)
    def setAllEnabled(self, flag):
        def recursive_set(parent):
            for child in parent.findChildren(QtCore.QObject):
                try:
                    if flag: child.removeEventFilter(self)
                    else: child.installEventFilter(self)
                except:
                    pass
                recursive_set(child)
        recursive_set(self)

    def eventFilter(self,o,event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            return True
        return False
    #To move a combo button, mouse tracking is enabled on all children. Move the chosen combobutton here to follow the
    #mouse pointer, until mouse is clicked again.  When mouse is over left side of a combobutton, the butn to be moved is
    #inserted on the left, when it is on the right half, it is moved to the right.
    #initiate move combobutton operation. Move the vbox clicked on
        #set from contexgtmennu

    def setWorkspaceColor(self,N,colorset):
        self.opts.workspacecolors[N]=colorset
        #print N
        #print colorset
    #workspaces number from 1 to ... N not from 0 to N+1 or whatever 
    #return workspace color from opts or default value if none given
    def getWorkspaceColor(self,N):
        w=self.opts.workspacecolors
        if N>len(w)-1: c=self.opts.defaultworkspacecolor
        else: c=w[N]
        return c

    #see WorkspaceFuncs.py: Run
    def updateBlinkerList(self):
        wins = ewmh.getClientList()
        #print '-----------------'
        #print Globals.blinkerList
        for w in wins:
            #<class 'Xlib.display.Window'>(0x04600002)
            #[0] is kleine letters/[1] is hoofdletters (exec/name?)
            pid=ewmh.getWmPid(w)
            #print 'pid '+str(pid)#__debug
            if pid in Globals.blinkerList: Globals.blinkerList.remove(pid)

    #try and find an application for browsing all available apps on the system
    #for freedesktop these are listed in /usr/share/applications. Just point a filemanager
    #to that location. Apps can then be dragged and dropped into the panel
    #new cdepanel-app-manager.desktop will be generated and put in configdir
    #this will launch the found filebrowser with /usr/share/applications as directory
    def findAppBrowser(self):
        path='/usr/share/applications'
        alternatives=['xfce4-appfinder.desktop','Thunar.desktop','org.kde.dolphin.desktop','firefox.desktop','google-chrome.desktop']
        for a in alternatives:
            pa=os.path.join(path,a)
            if os.path.isfile(pa):
                desktopentrypath=pa
                break
        #darn whats with the % this %that make it work or skip it
        command=DesktopEntry.DesktopEntry(desktopentrypath).getExec().split(' ')[0]
        s="""\
[Desktop Entry]
Name=App Finder
Exec={command} /usr/share/applications
Icon=edit-find
Terminal=false
StartupNotify=true
Type=Application
Categories=System;Utility;Core;FileTools;FileManager;
        """.format(**locals())
        newdesktopentrypath=os.path.join(Globals.configdir,'cdepanel-app-manager.desktop')
        with open(newdesktopentrypath, 'w') as f: f.write(s)
        return newdesktopentrypath

# CONFIG FILES AND SUCH ###################################################################

#two opts:
#   1) no opts
#>cdepanel
#   2) custom configdir
#>cdepanel /x/bin/bla/configdir
#
#search configdir and return path
#if not found try to create one from default in distribution
#for xpms, drawers, palettes etc and configfiles if you want
def findConfigDir(sysargv):
    if len(sysargv)>2:
        print """
            Usage: 
                cdepanel 
            or
                cdepanel /path/to/my/configdir
        """
        sys.exit()
    if len(sysargv)==2:     
        configdir=sysargv[1]
        if not os.path.isdir(configdir):
            print """
                Given configdir not found '{configdir}'
            """.format(**locals())
            sys.exit()
        print 'Expanding configdir to '+os.path.abspath(configdir)
        return configdir
    #no input args given use default configdirbasename
    configdirbasename='CdePanel'
    userhome=os.path.expanduser("~")
    userdotconfigdir=os.path.join(userhome,'.config')
    paths=[userhome,userdotconfigdir]
    #this one dereferences symlinks so dont use:
    #paths=[userhome,userhome+'/.config',os.getcwd()]
    for p in paths:
        configdir=os.path.join(p,configdirbasename)
        if os.path.isdir(configdir):
            print 'FOUND CONFIGDIR '+configdir
            return configdir
    print 'NO CONFIGDIR FOUND. Trying to create one in '+userdotconfigdir
    if not os.path.exists(userdotconfigdir):
        print 'NOT FOUND so CREATING '+userdotconfigdir
        try: os.makedirs(userdotconfigdir)
        except OSError as e: 
            print >>sys.stderr, "FAILED TO CREATE "+userdotconfigdir, e
            sys.exit()
    #configdirdefault=os.path.join(Globals.distdir,configdirbasename)
#__1
    #configdirdefault=os.path.join(Globals.distdir,'cdetheme/scripts/CdePanel')
    configdirdefault=os.path.join(Globals.themesrcdir,'scripts/CdePanel')
    configdiruserhome=os.path.join(userdotconfigdir,configdirbasename) 
    print 'configdirdefault '+str(configdirdefault)#__debug
    print 'configdiruserhome '+str(configdiruserhome)#__debug
    try:
        #had some trouble with this, exited when there was a stale link
                                #-------------------------------------v
        shutil.copytree(configdirdefault,configdiruserhome,symlinks=True)
    except OSError as e: 
        print >>sys.stderr, "FAILED TO CREATE DEFAULT CONFIGDIR. Please try and manually copy somewheres/CdePanel to ~/.config", e
        sys.exit()
    print 'Successfully copied '+configdirdefault+' to '+configdiruserhome
    #SETTINGS FOR INITIAL RUN###############################################
    defaultcfgscript=os.path.join(configdiruserhome,'gendefaultdrawersandlayout')
    cmd=defaultcfgscript
    execWithShell(cmd)
    writeConfigFileForFirstRun(configdiruserhome)
    return configdiruserhome

    sys.exit()
        
#some initial guess for config on the first run
def writeConfigFileForFirstRun(configdiruserhome):
    configfile=os.path.join(configdiruserhome,'config')
    screenHeight = QtGui.QDesktopWidget().screenGeometry().height()
    initialheight=screenHeight/10.0
    env=DesktopEnv().get_desktop_environment()
    environment=''
    if env=='xfce4':
        environment='xfce'

        print 'APPLYING XFCE THEME !!!!!!!!!'

    print initialheight
    s="""
antialias: 21
brightness: 0 
contrast: 0
currentpalettefile: Broica.dp
defaultworkspacecolor: 2
environment: {environment}
initialheight: {initialheight}
ncolors: 8
nworkspaces: 4
palettedir: palettes
panelcolor: 8
pycdeconfig: pycdeconfig
saturation: 1.0
scale: 1.1403931925618036
sharp: 1.5
themeBackdrops: {environment}
themeGtk: true
themeWindecs: {environment}
workspacebackdrops: [Gradient, Gradient, Paver, Gradient, Paver, Gradient, Paver,
  Gradient, Gradient]
workspacecolors: [0, 3, 5, 6, 7, 3, 2, 2, 2, 2, 2]
workspacelabels: [Zero, One, Two, Three, Four, Five, Six, Seven]
""".format(**locals())
    with open(configfile, 'w') as f:
            f.write(s)
    

#always use configfile 'config' in configdir
def findConfigFile1():
    tryconfigfile=os.path.join(Globals.configdir,'config')
    if os.path.isfile(tryconfigfile):
        print 'FOUND CONFIG FILE '+tryconfigfile
        return tryconfigfile
    else: 
        print 'CONFIG FILE NOT FOUND '+configfile
        sys.exit()

    
# MASTER CONTROL PROGRAM #####################################################################

def main():
    app = QtGui.QApplication(sys.argv)
    app.setStyle("Gtk+")
    #app.setStyle("CDE")

    print 'cdepanel VER 1.2'

    Globals.app=app

    Globals.distdir=''
    #when run from pyinstaller bundle, everything is unpacked to /tmp/_MEISblabla
    if hasattr(sys,'_MEIPASS'):
        Globals.distdir=sys._MEIPASS
    else:
        Globals.distdir=os.path.dirname(__file__)
    print 'Distdir: '+Globals.distdir

    Globals.themesrcdir=''
    if hasattr(sys,'_MEIPASS'):
        Globals.themesrcdir=os.path.join(sys._MEIPASS,'cdetheme')
    else:
        Globals.themesrcdir=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
    print 'Globals.themesrcdir '+str(Globals.themesrcdir)#__debug


    #init some directories and such
    Globals.ncolorstosave=8
    Globals.ncolorsmax=8
    Globals.userhome=os.path.expanduser("~")
    Globals.themedir=os.path.join(Globals.userhome,'.themes/cdetheme')
    Globals.configdir=findConfigDir(sys.argv)
#__1
    #Globals.themedir=os.path.join(Globals.configdir,'cdetheme')
    Globals.drawerdir=os.path.join(Globals.configdir,'drawers')
    Globals.configfile=findConfigFile1()
    print 'CONFIG DIR SET TO '+Globals.configdir
    print 'CONFIG FILE SET TO '+Globals.configfile
    #note: for stand alone MotifColors.py palettes/ was moved to ~/.themes . But turns out not to
    #be convenient; if cdepanel is used without .themes, that dir is not installed. So keep palettes/
    #in ~/.config/CdePanel (or both for now convenience)
    #Globals.palettedir=os.path.join(Globals.configdir,'palettes')
#__1
    Globals.palettedir=os.path.join(Globals.themedir,'palettes')
    Globals.xpmdir=os.path.join(Globals.configdir,'xpm')
    #xpm search paths
    Globals.xpmdirs=[Globals.xpmdir,Globals.configdir,'.']
    Globals.defaultxpm=os.path.join(Globals.xpmdir,'empty.xpm')
    Globals.cache=os.path.join(Globals.configdir,'cache')
    Globals.backdropdir=os.path.join(Globals.themedir,'backdrops')
    #for hdd light
    Globals.blinkerList=[]
    Globals.smoothTransform=True
    #Globals.smoothTransform=False

    Globals.font='DejaVu Serif'
    Globals.fontStyle='Book'
    Globals.fontSize=14

    #init opts (options) for main panel. Loaded from default file pycdeconfig
    #note: the opts are passed down to PicButton.py objects, so they can set their backgrounds to the right colors
    mainopts=Opts() 
    mainopts.load(Globals.configfile)
    print 'mainopts '+str(mainopts)#__debug
    cdepanel = CdePanel(mainopts)
    print 'cdepanel '+str(cdepanel)#__debug
    cdepanel.positionBottomCenter()
    #mainopts.save(Globals.configfile)
    print 'showing'#__debug
    cdepanel.show()
    print 'finished showing, but not really.. so why the delay??'#__debug
    Globals.cdepanel=cdepanel# oh.. yes i forgot

    #open colordiag autom for debug
    #cdepanel.test()


    #Globals.c=ColorDialog(cdepanel)
    #Globals.c.show()




    sys.exit(app.exec_())

if __name__ == '__main__':

    main()


