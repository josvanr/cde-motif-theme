#!/usr/bin/python
import sys
from PyQt4 import QtCore, QtGui
import Globals
import os
from MotifColors import colorize_bg
from os.path import expanduser
from MiscFun import *
import ThemeGtk
import XfceDecor
import ThemeBackdrops
import shutil

class Theme():
    def __init__(self,opts):
        #import some stuff from main window
        self.opts=opts
        self.environment='xfce'
        self.curXfTheme='cdetheme'
        #some dummy val
        self.screenHeight='1024'
    def initTheme(self):
        N=self.opts.nworkspaces
        userhome=expanduser("~")
        #checkDir(userhome)
        homedotthemes=os.path.join(userhome,'.themes')
        if not os.path.exists(homedotthemes):
            print 'NOT FOUND so CREATING '+homedotthemes
            try: os.makedirs(homedotthemes)
            except OSError as e: print >>sys.stderr, "FAILED TO CREATE ~/.themes ", e

        #if .themes/cdetheme not exist: copy
        if os.path.exists(homedotthemes):
            #srcthemepath=os.path.join(Globals.distdir,'cdetheme')
            #print srcthemepath
            print Globals.themedir
            print Globals.themesrcdir
            #sys.exit()
            if not os.path.exists(Globals.themedir):
                print 'NOT FOUND THEME DIR '+Globals.themedir
                print 'Trying to copy from default '
                shutil.copytree(Globals.themesrcdir,Globals.themedir,symlinks=True)

            path=os.path.join(homedotthemes,'cdetheme1')
            if os.path.lexists(path): os.remove(path)
            os.symlink(Globals.themedir,path)

        #pick chosent components here
        if self.opts.themeBackdrops=='xfce':
            ThemeBackdrops.initXfceBackdrops(self.opts)
        if self.opts.themeWindecs=='xfce':
            XfceDecor.init()
        if self.opts.themeGtk:
            ThemeGtk.init()

    
    #for use in script outside of qt event loop
    def updateThemeNow(self):
        print 'updating theme'
        if self.opts.themeBackdrops=='xfce':
            ThemeBackdrops.prepareBackDrops(self.opts)
        self.doUpdateTheme()
    def updateTheme(self,delay=300):
        print 'updating theme'
        #Backdrop updating works quickly so do that first to fake responsive ui the rest is a bit laggy, so put on timer.
        #In case change is requesed often in a row, actual theme update will only happen a ssoon as the quick switching has
        #stopped
        if self.opts.themeBackdrops=='xfce':
            ThemeBackdrops.prepareBackDrops(self.opts)
        self.updatextimer=QtCore.QTimer()
        self.updatextimer.setSingleShot(True)
        self.updatextimer.timeout.connect(self.doUpdateTheme)
        self.updatextimer.start(delay)
    #Zees eeze nedded unly vunce
    def doUpdateTheme(self):
        print self.opts.themeGtk
        print self.opts.themeBackdrops
        print self.opts.themeWindecs

        #configdir=Globals.configdir
        N=self.opts.nworkspaces

        #write the rcfiles and switch xfce theme
        palettefilefullpath=os.path.join(Globals.palettedir,self.opts.currentpalettefile)

        if self.opts.themeWindecs=='xfce':
            #filename=Globals.configdir+'/cdetheme/xfwm4/themerc'
            filename=Globals.themedir+'/xfwm4/themerc'
            #this is still necessary for title font color and vertical offset 
            XfceDecor.genXfwmThemerc(filename,self.opts)
            #dirname=Globals.configdir+'/cdetheme/xfwm4'
            dirname=Globals.themedir+'/xfwm4'
            XfceDecor.genXfceDecor(dirname,self.opts)

        if self.opts.themeGtk:
            #filename=Globals.configdir+'/cdetheme/gtk-2.0/cdecolors.rc'
            filename=Globals.themedir+'/gtk-2.0/cdecolors.rc'
            ThemeGtk.gengtk2colors(filename,self.opts)
            #filename=os.path.join(Globals.configdir,'cdetheme/gtk-3.16/cdecolors.css')
            filename=os.path.join(Globals.themedir,'gtk-3.16/cdecolors.css')
            ThemeGtk.gengtk3colors(filename,self.opts)
            #filename=os.path.join(Globals.configdir,'cdetheme/gtk-3.20/cdecolors.css')
            filename=os.path.join(Globals.themedir,'gtk-3.20/cdecolors.css')
            ThemeGtk.gengtk3colors(filename,self.opts)
            ThemeGtk.updateThemeImages(self.opts)

        #the themedir .config/CdePanel/cdetheme is linked to ~/.themes/cdetheme and cdetheme1
        #To let the changed files take effect in gtk and xfwm, toggle back and forth between these 2 links
        #Maybe separate compnents later
        if self.curXfTheme=='cdetheme': self.curXfTheme='cdetheme1'
        else: self.curXfTheme='cdetheme'
        print '>>>'+self.curXfTheme
        cmd=''
        if self.opts.themeGtk:
            cmd+="""\
            xfconf-query -c xsettings -p /Net/ThemeName -s "{self.curXfTheme}"
            """.format(**locals())
        if self.opts.themeWindecs=='xfce':
            cmd+="""\
            xfconf-query -c xfwm4 -p /general/theme -s "{self.curXfTheme}" 
            """.format(**locals())
        execWithShell(cmd)



