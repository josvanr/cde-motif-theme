#!/usr/bin/python
#pixmap from text
import cStringIO
from PIL import Image,ImageQt,ImageFilter,ImageEnhance
import os,sys
from PyQt4 import QtGui,QtCore
import re
import subprocess
import Globals
from JosQPainter import JosQPainter
#when switching to some themes, this makes the app crash, so remove
#(someting with py hook something):
#import gtk
#gtk.set_interactive(0)

from xdg import IconTheme

#create text icon the size of baseimage=QPixmap, save to destination file
def textIconSameSizeAsFile(baseimage,destinationfile,text):
    painter = JosQPainter(baseimage)
    painter.setCompositionMode(QtGui.QPainter.CompositionMode_Source)
    painter.fillRect(0, 0, 1000, 1000, QtCore.Qt.transparent)
    if Globals.smoothTransform:
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform);
    painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
    font=painter.font()
    font.setPointSize (20)
     #//font.setWeight(QtGui.QFont::DemiBold);
    painter.setFont(font)
    painter.setPen(QtGui.QColor('#111111'))
    x=10
    y=22
    painter.drawText(x,y,text)
    painter.setPen(QtCore.Qt.white)
    painter.drawText(x-1,y-1,text)
    painter.end()
    #baseimage.save(destinationfile)#__debug

def convertPixmap(pixmap,brightness,contrast,saturation,sharpness):
    img = QtGui.QImage(pixmap)
    buffer = QtCore.QBuffer()
    buffer.open(QtCore.QIODevice.ReadWrite)
    img.save(buffer, "PNG")
    strio = cStringIO.StringIO()
    strio.write(buffer.data())
    buffer.close()
    strio.seek(0)
    im = Image.open(strio)
    im=ImageEnhance.Brightness(im).enhance(brightness) #default 1
    im=ImageEnhance.Contrast(im).enhance(contrast)
    im=ImageEnhance.Sharpness(im).enhance(sharpness) 
    im=im.filter(ImageFilter.UnsharpMask(radius=0, percent=100, threshold=0)) # default 0 100 0

    converter = ImageEnhance.Color(im)
    im = converter.enhance(saturation)
    #im1.save('/tmp/test.png')

    qt=ImageQt.ImageQt(im)
    imgout=QtGui.QImage(qt)
    rect=imgout.rect()
    #pixmapout=QtGui.QPixmap(imgout) #-> GARBLED IMAGES-----------------------v
    pixmapout=QtGui.QPixmap(imgout.copy(rect)) #Darn.. why. has to do with memory management?
    ################## This also worked: no garbled images when save/load was here:
    #tempfile='/tmp/TempCDEPanelResource'+str(self.tmpfilecounter)+'.png'
    #pixmapout.save(tempfile)
    #pixmapout=QtGui.QPixmap(tempfile)
    return pixmapout

#icon in pixbut is no global resource yet,but file. maybe later
#returns the width
def createTextIcon(text,pixelsize,destinationfile,opts=None):
    #font=QtGui.QFont('Lucida Bright') #werkt wel
    font=QtGui.QFont(Globals.font) #werkt wel
    #font.setStyleName('Book') 
    font.setStyleName(Globals.fontStyle) 
    font.setPixelSize (pixelsize)
    spacing=1
    font.setLetterSpacing(QtGui.QFont.PercentageSpacing,spacing*100)
    #font=QtGui.QFont('Helvetica')
    fm=QtGui.QFontMetrics(font)
    fm.width(text)
    r=fm.boundingRect(text)
    #hmmm------------------v
    xpm=QtGui.QPixmap(r.width()*1.1,r.height())
    c = QtGui.QColor(0)
    c.setAlpha(0)
    xpm.fill(c)
    #for some reason the string is in the negative half plane so pull it down
    x=-r.x()*spacing*1.1#??
    y=-r.y()
    painter = JosQPainter(xpm)
    painter.setCompositionMode(QtGui.QPainter.CompositionMode_Source)
    #if Globals.smoothTransform:
    painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform);
    painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
    painter.setFont(font)
    painter.setPen(QtGui.QColor('#000000'))
    painter.drawText(x,y,text)
    painter.setPen(QtCore.Qt.white)
    painter.drawText(x-1,y-1,text)
    painter.end()
    if opts:
	xpm=convertPixmap(xpm,1,1,opts.saturation,opts.sharp)
    xpm.save(destinationfile)

    return r.width()

def drawTextOnPixmap(text,pixelsize,leftmarginfrac,yoffsetfrac,pixmap):
    #font=QtGui.QFont('Lucida Bright') #werkt wel
    #font=QtGui.QFont('DejaVu Serif') #werkt wel
    font=QtGui.QFont(Globals.font) #werkt wel
    #font.setStyleName('Book') #doet niks. andere keer uitzoeken
    font.setStyleName(Globals.fontStyle) #doet niks. andere keer uitzoeken
    font.setPixelSize (pixelsize)
    spacing=1
    font.setLetterSpacing(QtGui.QFont.PercentageSpacing,spacing*100)
    #font=QtGui.QFont('Helvetica')
    fm=QtGui.QFontMetrics(font)
    fm.width(text)
    r=fm.boundingRect(text)
    #xpm=QtGui.QPixmap(r.width(),r.height())
    #c = QtGui.QColor(0)
    #c.setAlpha(0)
    #xpm.fill(c)
    #for some reason the string is in the negative half plane so pull it down
    wp=pixmap.size().width()
    hp=pixmap.size().height()
    wt=r.width()
    ht=r.height()
    xt=-r.x()
    yt=-r.y()

    x=xt+leftmarginfrac*wp
    y=yt+(hp-ht)/2+yoffsetfrac*hp

    #dyn=(h-hpn)/2.0+h*yoffsetfrac
    painter = JosQPainter(pixmap)
    painter.setCompositionMode(QtGui.QPainter.CompositionMode_Source)
    #if Globals.smoothTransform:
    painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform);
    painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
    painter.setFont(font)
    painter.setPen(QtGui.QColor('#111111'))
    painter.drawText(x,y,text)
    painter.setPen(QtCore.Qt.white)
    painter.drawText(x-1,y-1,text)
    painter.end()


#QFont myFont(fontName, fontSize);;
#QString str("I wonder how wide this is?");

#QFontMetrics fm(myFont);
#int width=fm.width(str);

        


#d = {'x': 1, 'y': 2, 'z': 3} 
#for key in d:
    #print key, 'corresponds to', d[key]


#take python 
def replaceColors(colors,xpm1):
    rows=len(colors)
    xpm=list(xpm1) #make a copy of the list and make replacements in that, return that
    for row in range(rows):
        colorname=colors[row][0]
        colorval=colors[row][1]
        for j in range(len(xpm)):
            if re.search(colorname,xpm[j]):
                xpm[j]=re.sub('#(?:[0-9a-fA-F]{3}){1,2}',colorval,xpm[j]) #take xpm[j] and replace colorname with colorval and return string
    return xpm


def copyToCacheAndGenCdeIcon(filename):
#hier
        basename=os.path.basename(filename)
        basenamenoext, file_extension = os.path.splitext(basename)
        fullname=os.path.join(Globals.cache,basenamenoext)+'.png'
        cmd="""
        convert -background none -stroke black -fill white \
        {filename}\
          \( +clone -background '#222222' -shadow 80x0-1-1 \) \
          \( +clone -background black -shadow 80x0+2+1 \) \
          \( +clone -background white -shadow 80x0+3+2 \) \
          -background none -compose DstOver -flatten  {fullname}
        """.format(**locals())
        #print 'cmd '+str(cmd)#__debug
        #cmd=("""cp {filename} {c} """.format(**locals()))
        out = subprocess.Popen(cmd,shell=True,stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        (stdout, stderr) = out.communicate()
def copyToCache(filename):
        c=Globals.cache
        cmd=("""cp {filename} {c} """.format(**locals()))
        out = subprocess.Popen(cmd,shell=True,stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        (stdout, stderr) = out.communicate()

#xpm / png dond treally need separate cmd call todo
#darn why is this not built in to qt .. improve 
def findIconFromName1(name):
    def err(name):
        print """ICON NOT FOUND {name} PLEASE CHECK. USING DEFAULT ICON """.format(**locals())

    #do this here for quick
    #IF NONE GIVEN OR WHATEVER, RETURN DEFAULT ICON
    if name=='' or name==None: 
        err(name)
        return Globals.defaultxpm
    basedirs=['/usr/share/icons/elementary-xfce','/usr/share/icons'] #xpmdir only for system xpms. 
    #basedirs=['/usr/share/icons']
    extensions=['png','xpm']

    #IF FULL PATH GIVEN 
    if not os.path.basename(name)==name:
        #first check if nonfullpath is in cache
        basenameext=os.path.basename(name)
        basename, file_extension = os.path.splitext(basenameext)
        for e in extensions:
            fullname=os.path.join(Globals.cache,basename+'.'+e)
            if os.path.isfile(fullname):
                #print 'icon with substituted extension found in cache'
                return fullname
        #if not, get the icon
        if os.path.isfile(name): 
            #todo
            #print 'full icon path found, using and copy to cache'
            print '1'
            copyToCacheAndGenCdeIcon(name)
            return name
        else: 
            #'print full icon path not found, use default'
            err(name)
            return Globals.defaultxpm

    #NO PATH GIVEN...
    #print 'icon no path given'
    basename, file_extension = os.path.splitext(name)
    #if has extension, first only check if exist in cache (mmaybe if has full path always only check if exist)
    if file_extension:
        #print 'icon has extension'
        fullname=os.path.join(Globals.cache,basename)
        if os.path.isfile(fullname):
            #print 'icon with extension found in cache'
            return fullname

    #if no extension first check if exist in cache with .png or .xpmhmm or assume .png?
    #print 'icon has no extension'
    for e in extensions:
        fullname=os.path.join(Globals.cache,basename+'.'+e)
        if os.path.isfile(fullname):
            #print 'icon with substituted extension found in cache'
            return fullname

    print 'LOOKING FOR ICONS (No icon in cache)'

    #search my own icons first, 
    print 'trying cdepanel/xpm'
    b=Globals.xpmdir
    for e in extensions:
        #mayb use 'basename' here (de-extensioned version of name)
        #always QUOTE globs in 'find' statements WHY!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        cmd=("""find {b} -name "{basename}*" -print|grep {e}""".format(**locals()))
        out = subprocess.Popen(cmd,shell=True,stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        (stdout, stderr) = out.communicate()
        #print stdout
        if stdout:
            l=stdout.splitlines()
            c=Globals.cache
            #todo make a cache dir for this 
            copyToCache(l[0])
            #cmd=("""cp {l[0]} {c} """.format(**locals()))
            #out = subprocess.Popen(cmd,shell=True,stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            #(stdout, stderr) = out.communicate()
            return l[0]

    #try try 
    if QtGui.QIcon.hasThemeIcon(basename):
        icon = QtGui.QIcon.fromTheme(basename)
        pixmap=icon.pixmap(48,48)
        filename='/tmp/'+basename+'.png'
        pixmap.save(filename)
        copyToCacheAndGenCdeIcon(filename)
        return filename

    #try this.. Does this work... maybe
    print 'trying xdg icon'
    xdgicon=IconTheme.getIconPath(basename, 48)
    if xdgicon:
        if os.path.isfile(xdgicon):
            print '2'
            copyToCacheAndGenCdeIcon(xdgicon)
            return xdgicon

    #when swithing to some gtk themes, this makes the app crash for some reason
    #try that....any one will do just find it
    #print 'trying gnome icon'
    #icon_theme = gtk.icon_theme_get_default()
    #icon_info = icon_theme.lookup_icon(basename, 48, 0)
    #if icon_info:
        #gtkicon=icon_info.get_filename()
        #if gtkicon:
            #copyToCacheAndGenCdeIcon(gtkicon)
            #if os.path.isfile(gtkicon):return gtkicon

    #more extensive search and copy to cache if found
    #add check exist
    #note if search 'xterm' can come up with 'xterm-color' eg but then in cache end up: 'xterm-color'
    #and is not found in cach next time because look for cache/xterm so yes.. change
    #search for big enough
    print 'more extensive search'
    print name
    for b in basedirs:
        for e in extensions:
            #mayb use 'basename' here (de-extensioned version of name)
            #always QUOTE globs in 'find' statements WHY!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            cmd=("""find {b} -name "{basename}*" -print|grep -E '48x48'|grep {e}""".format(**locals()))
            out = subprocess.Popen(cmd,shell=True,stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            (stdout, stderr) = out.communicate()
            #print stdout
            if stdout:
                l=stdout.splitlines()
                c=Globals.cache
                #todo make a cache dir for this 
                print '3'
                copyToCacheAndGenCdeIcon(l[0])
                #copyToCacheAndGenCdeIcon(l[0])
                #cmd=("""cp {l[0]} {c} """.format(**locals()))
                #out = subprocess.Popen(cmd,shell=True,stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                #(stdout, stderr) = out.communicate()
                return l[0]


    #search everything. maybe step through result with 'identify' later
    if which('locate'):
        for e in extensions:
            cmd=("""locate {basename}|grep icon|grep {e}""".format(**locals()))
            out = subprocess.Popen(cmd,shell=True,stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            (stdout, stderr) = out.communicate()
            if stdout:
                l=stdout.splitlines()
                c=Globals.cache
                #this search original eg 'xterm' couldnt be found, so maybe chooses 'xterm-color.png'
                #so for quick, make copy of that with name xterm in cache
                #or make cache 'xterm_alt.png' and then check next time also for filname'_alt' or something
                #.... later later leave for now 
                print """ICON {name} NOT FOUND SO USING ALTERNATIVE {l[0]} INSTEAD. PLS CHECK """.format(**locals())
                print '4'
                copyToCacheAndGenCdeIcon(l[0])
                #cmd=("""cp {l[0]} {c} """.format(**locals()))
                #out = subprocess.Popen(cmd,shell=True,stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                #(stdout, stderr) = out.communicate()
                return l[0]

    err(name)
    return Globals.defaultxpm

def which(program):
    path_ext = [""];
    ext_list = None

    if sys.platform == "win32":
        ext_list = [ext.lower() for ext in os.environ["PATHEXT"].split(";")]

    def is_exe(fpath):
        exe = os.path.isfile(fpath) and os.access(fpath, os.X_OK)
        # search for executable under windows
        if not exe:
            if ext_list:
                for ext in ext_list:
                    exe_path = "%s%s" % (fpath,ext)
                    if os.path.isfile(exe_path) and os.access(exe_path, os.X_OK):
                        path_ext[0] = ext
                        return True
                return False
        return exe

    fpath, fname = os.path.split(program)

    if fpath:
        if is_exe(program):
            return "%s%s" % (program, path_ext[0])
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return "%s%s" % (exe_file, path_ext[0])
    return None


if __name__ == '__main__':

    #8 or reduced 4 color palette
    #colors=readMotifColors('4','Broica.dp')
    #colors=readMotifColors('8','Broica.dp')


    #xpm=extractXpm('xpm/launcher.xpm')
    #xpm1=replaceColors(colors,xpm)

    #app = QtCore.QApplication(sys.argv)
    #window = QtGui.QMainWindow()

    #pic = QtGui.QLabel(window)

    #########################
    #pixmap=QtGui.QPixmap(xpm) #the original one
    #pixmap=QtGui.QPixmap(xpm1) #the replaced one
    #########################

    #pic.setPixmap(pixmap)
    #pic.resize(200,100)

    #for testing
    Globals.cache='/x/pycde/scaletest/cdepanel/cache'
    Globals.defaultxpm='/x/pycde/scaletest/cdepanel/xpm/empty.xpm'
    Globals.xpmdir='/x/pycde/scaletest/cdepanel/xpm'

    ##################################################
    #print findIconFromName1('mozilla.xpm')
    #print findIconFromName1('xterm')
    #print findIconFromName1('firefox.png')
    #print findIconFromName1('')
    #print findIconFromName1(None)
    #print findIconFromName1('/x/pycde/scaletest/cdepanel/xpm/terminal.xpm')
    #print findIconFromName1('/x/ycde/scaletest/cdepanel/xpm/txxxxeminal.xpm')

    ##################################################
    #app = QtCore.QApplication(sys.argv)
    #p=QtGui.QPixmap('xpm/pager-button-1.xpm')
    #textIconSameSizeAsFile(p,'/tmp/testicon.png','My Text')
    #print 'done'
    #sys.exit(app.exec_())
    ##################################################






    app = QtCore.QApplication(sys.argv)

    ###########################3
    #print createTextIcon('/tmp/testicon.png','M111yTExxxxxxxxxxxxxxxXT 123')
    print 'done'

    ###########################3
    pixmap=QtGui.QPixmap('/tmp/testpagerbutton2.png')
    drawTextOnPixmap('Hello',14,.1,0.05,pixmap)
    pixmap.save('/tmp/1.png')
    
    sys.exit()

    sys.exit(app.exec_())


    #window.show()
    #sys.exit(app.exec_())
