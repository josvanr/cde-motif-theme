#!/usr/bin/python
#   cb .jos http://ewmh.readthedocs.io/en/latest/ewmh.html#examples
import subprocess
import os,sys
import re
from ewmh import EWMH
ewmh = EWMH()
import Globals
from PyQt4 import QtCore, QtGui
from functools import partial
from xdg import BaseDirectory, DesktopEntry

APP_NAME='xterm'

def get_desktop_environment():
    #From http://stackoverflow.com/questions/2035657/what-is-my-current-desktop-environment
    # and http://ubuntuforums.org/showthread.php?t=652320
    # and http://ubuntuforums.org/showthread.php?t=652320
    # and http://ubuntuforums.org/showthread.php?t=1139057
    if sys.platform in ["win32", "cygwin"]:
        return "windows"
    elif sys.platform == "darwin":
        return "mac"
    else: #Most likely either a POSIX system or something not much common
        desktop_session = os.environ.get("DESKTOP_SESSION")
        if desktop_session is not None: #easier to match if we doesn't have  to deal with caracter cases
            desktop_session = desktop_session.lower()
            if desktop_session in ["gnome","unity", "cinnamon", "mate", "xfce4", "lxde", "fluxbox", 
                                   "blackbox", "openbox", "icewm", "jwm", "afterstep","trinity", "kde"]:
                return desktop_session
            ## Special cases ##
            # Canonical sets $DESKTOP_SESSION to Lubuntu rather than LXDE if using LXDE.
            # There is no guarantee that they will not do the same with the other desktop environments.
            elif "xfce" in desktop_session or desktop_session.startswith("xubuntu"):
                return "xfce4"
            elif desktop_session.startswith("ubuntu"):
                return "unity"       
            elif desktop_session.startswith("lubuntu"):
                return "lxde" 
            elif desktop_session.startswith("kubuntu"): 
                return "kde" 
            elif desktop_session.startswith("razor"): # e.g. razorkwin
                return "razor-qt"
            elif desktop_session.startswith("wmaker"): # e.g. wmaker-common
                return "windowmaker"
        if os.environ.get('KDE_FULL_SESSION') == 'true':
            return "kde"
        elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
            if not "deprecated" in os.environ.get('GNOME_DESKTOP_SESSION_ID'):
                return "gnome2"
        #From http://ubuntuforums.org/showthread.php?t=652320
        elif is_running("xfce-mcs-manage"):
            return "xfce4"
        elif is_running("ksmserver"):
            return "kde"
    return "unknown"

def is_running(process):
    #From http://www.bloggerpolis.com/2011/05/how-to-check-if-a-process-is-running-using-python/
    # and http://richarddingwall.name/2009/06/18/windows-equivalents-of-ps-and-kill-commands/
    try: #Linux/Unix
        s = subprocess.Popen(["ps", "axw"],stdout=subprocess.PIPE)
    except: #Windows
        s = subprocess.Popen(["tasklist", "/v"],stdout=subprocess.PIPE)
    for x in s.stdout:
        if re.search(process, x):
            return True
    return False

def set_wallpaper(file_loc, first_run):
    # Note: There are two common Linux desktop environments where 
    # I have not been able to set the desktop background from 
    # command line: KDE, Enlightenment
    desktop_env = get_desktop_environment()
    try:
        if desktop_env in ["gnome", "unity", "cinnamon"]:
            uri = "'file://%s'" % file_loc
            try:
                SCHEMA = "org.gnome.desktop.background"
                KEY = "picture-uri"
                gsettings = Gio.Settings.new(SCHEMA)
                gsettings.set_string(KEY, uri)
            except:
                args = ["gsettings", "set", "org.gnome.desktop.background", "picture-uri", uri]
                subprocess.Popen(args)
        elif desktop_env=="mate":
            try: # MATE >= 1.6
                # info from http://wiki.mate-desktop.org/docs:gsettings
                args = ["gsettings", "set", "org.mate.background", "picture-filename", "'%s'" % file_loc]
                subprocess.Popen(args)
            except: # MATE < 1.6
                # From https://bugs.launchpad.net/variety/+bug/1033918
                args = ["mateconftool-2","-t","string","--set","/desktop/mate/background/picture_filename",'"%s"' %file_loc]
                subprocess.Popen(args)
        elif desktop_env=="gnome2": # Not tested
            # From https://bugs.launchpad.net/variety/+bug/1033918
            args = ["gconftool-2","-t","string","--set","/desktop/gnome/background/picture_filename", '"%s"' %file_loc]
            subprocess.Popen(args)
        ## KDE4 is difficult
        ## see http://blog.zx2c4.com/699 for a solution that might work
        elif desktop_env in ["kde3", "trinity"]:
            # From http://ubuntuforums.org/archive/index.php/t-803417.html
            args = 'dcop kdesktop KBackgroundIface setWallpaper 0 "%s" 6' % file_loc
            subprocess.Popen(args,shell=True)
        elif desktop_env=="xfce4":
            #From http://www.commandlinefu.com/commands/view/2055/change-wallpaper-for-xfce4-4.6.0
            if first_run:
                args0 = ["xfconf-query", "-c", "xfce4-desktop", "-p", "/backdrop/screen0/monitor0/workspace4/last-image", "-s", file_loc]
                args1 = ["xfconf-query", "-c", "xfce4-desktop", "-p", "/backdrop/screen0/monitor0/workspace4/image-style", "-s", "2"]
                output=subprocess.Popen(args0)
                output=subprocess.Popen(args1)
            args = ["xfdesktop","--reload"]
            subprocess.Popen(args)
        elif desktop_env=="razor-qt": #TODO: implement reload of desktop when possible
            if first_run:
                desktop_conf = configparser.ConfigParser()
                # Development version
                desktop_conf_file = os.path.join(get_config_dir("razor"),"desktop.conf") 
                if os.path.isfile(desktop_conf_file):
                    config_option = r"screens\1\desktops\1\wallpaper"
                else:
                    desktop_conf_file = os.path.join(get_home_dir(),".razor/desktop.conf")
                    config_option = r"desktops\1\wallpaper"
                desktop_conf.read(os.path.join(desktop_conf_file))
                try:
                    if desktop_conf.has_option("razor",config_option): #only replacing a value
                        desktop_conf.set("razor",config_option,file_loc)
                        with codecs.open(desktop_conf_file, "w", encoding="utf-8", errors="replace") as f:
                            desktop_conf.write(f)
                except:
                    pass
            else:
                #TODO: reload desktop when possible
                pass 
        elif desktop_env in ["fluxbox","jwm","openbox","afterstep"]:
            #http://fluxbox-wiki.org/index.php/Howto_set_the_background
            # used fbsetbg on jwm too since I am too lazy to edit the XML configuration 
            # now where fbsetbg does the job excellent anyway. 
            # and I have not figured out how else it can be set on Openbox and AfterSTep
            # but fbsetbg works excellent here too.
            try:
                args = ["fbsetbg", file_loc]
                subprocess.Popen(args)
            except:
                sys.stderr.write("ERROR: Failed to set wallpaper with fbsetbg!\n")
                sys.stderr.write("Please make sre that You have fbsetbg installed.\n")
        elif desktop_env=="icewm":
            # command found at http://urukrama.wordpress.com/2007/12/05/desktop-backgrounds-in-window-managers/
            args = ["icewmbg", file_loc]
            subprocess.Popen(args)
        elif desktop_env=="blackbox":
            # command found at http://blackboxwm.sourceforge.net/BlackboxDocumentation/BlackboxBackground
            args = ["bsetbg", "-full", file_loc]
            subprocess.Popen(args)
        elif desktop_env=="lxde":
            args = "pcmanfm --set-wallpaper %s --wallpaper-mode=scaled" % file_loc
            subprocess.Popen(args,shell=True)
        elif desktop_env=="windowmaker":
            # From http://www.commandlinefu.com/commands/view/3857/set-wallpaper-on-windowmaker-in-one-line
            args = "wmsetbg -s -u %s" % file_loc
            subprocess.Popen(args,shell=True)
        ## NOT TESTED BELOW - don't want to mess things up ##
        #elif desktop_env=="enlightenment": # I have not been able to make it work on e17. On e16 it would have been something in this direction
        #    args = "enlightenment_remote -desktop-bg-add 0 0 0 0 %s" % file_loc
        #    subprocess.Popen(args,shell=True)
        #elif desktop_env=="windows": #Not tested since I do not run this on Windows
        #    #From https://stackoverflow.com/questions/1977694/change-desktop-background
        #    import ctypes
        #    SPI_SETDESKWALLPAPER = 20
        #    ctypes.windll.user32.SystemParametersInfoA(SPI_SETDESKWALLPAPER, 0, file_loc , 0)
        #elif desktop_env=="mac": #Not tested since I do not have a mac
        #    #From https://stackoverflow.com/questions/431205/how-can-i-programatically-change-the-background-in-mac-os-x
        #    try:
        #        from appscript import app, mactypes
        #        app('Finder').desktop_picture.set(mactypes.File(file_loc))
        #    except ImportError:
        #        #import subprocess
        #        SCRIPT = """/usr/bin/osascript<<END
        #        tell application "Finder" to
        #        set desktop picture to POSIX file "%s"
        #        end tell
        #        END"""
        #        subprocess.Popen(SCRIPT%file_loc, shell=True)
        else:
            if first_run: #don't spam the user with the same message over and over again
                sys.stderr.write("Warning: Failed to set wallpaper. Your desktop environment is not supported.")
                sys.stderr.write("You can try manually to set Your wallpaper to %s" % file_loc)
            return False
        return True
    except:
        sys.stderr.write("ERROR: Failed to set wallpaper. There might be a bug.\n")
        return False

def get_config_dir(app_name=APP_NAME):
    if "XDG_CONFIG_HOME" in os.environ:
        confighome = os.environ['XDG_CONFIG_HOME'] 
    elif "APPDATA" in os.environ: # On Windows
        confighome = os.environ['APPDATA'] 
    else:
        try:
            from xdg import BaseDirectory   
            confighome =  BaseDirectory.xdg_config_home
        except ImportError: # Most likely a Linux/Unix system anyway
            confighome =  os.path.join(get_home_dir(),".config")
    configdir = os.path.join(confighome,app_name)
    return configdir

def get_home_dir():
    if sys.platform == "cygwin":
        home_dir = os.getenv('HOME')
    else:
        home_dir = os.getenv('USERPROFILE') or os.getenv('HOME')
    if home_dir is not None:
        return os.path.normpath(home_dir)
    else:
        raise KeyError("Neither USERPROFILE or HOME environment variables set.")













































#command is launched somewhere earlier
#looks for NEWEST occurence of command in ps uxa
#then puts pid on blinkerList
#and removes 'dummypid' from blnkerlist
def findPidAddToBlinkerList(command):
    #if command=='google-chrome-stable':command='chrome'#hmm doesnt seem tow ork try some other time
    cmd="""
    ps --sort=start_time uxa|grep {command}
    """.format(**locals())
    output=subprocess.check_output(cmd, shell=True)
    lines=output.splitlines()
    if len(lines)==2:
        print 'findPidAddToBlinkerList no worke leave for now'
        #google-chrome-stable couples to some other process or somehting or it is just
        #a script that launches another executable. So leave for now. Maybe add a list of
        #other options here to try and find the correct one eg for google-chrome-stable look for 'chrome'
    else:
        #output contains newest occurrences of command in ps on the bottom. But last 2 occurrences are
        #the ps command itself and the grep ! So third from last is the command we are looking for.
        line=lines[-3]
        words=line.split()
        pidIHope=int(words[1])#should be int  for updateBlinkerList
        Globals.blinkerList.append(pidIHope)
    #to make the blinker go right away, a dummypid can be added on it. Remove if present
    if 'dummypid' in Globals.blinkerList: Globals.blinkerList.remove('dummypid')


def execFromDesktopentrypath (desktopentrypath):
    d=DesktopEntry.DesktopEntry(desktopentrypath)
    getexec=d.getExec()#all kind of junk..?: 'set BLABLA command %f %Bla'
    getexec=os.path.basename(getexec)
    getexec1=re.sub('%.*','',getexec) #remove the %Fs and what not: 
    command=getexec1.split()[-1]#hopefully the actual execultutble 'command' 
    print command

#in picbuttoncommand for start and exit buttons i still use Run(command) 
#should be reconfigured to do only Run(desktopentry) or something (mabye)
def Run(command,desktopentrypath=None):
    if desktopentrypath: #Run(command,desktopentrypath)
        #cmd='xdg-open '+desktopentrypath#aha this only works 'with shell' and then the blinkerlist doesnt owrk
        #xdg-open doesnt work consistently on all systems. Sometimes it just opens the .desktop file
        #in a text editor. So use gtk-launch for now. But this doesnt accept the full path
        desktopentrybase=os.path.basename(desktopentrypath)
        cmd='gtk-launch '+desktopentrybase 
    else:
        #if it is a plain command only, ie Run(command), just exec
        cmd=command
    if cmd:
        p=None
        try:
            print 'TRYING TO RUN "'+str(cmd)+'"'
            p = subprocess.Popen(cmd,shell=False) # NOTE: with 'True' the blinkerlist doesnt work because exe has different pid then
        except OSError as e:
            print >>sys.stderr, "Extzecyootschn wailed temm eeeet:", e
            try:
                print 'TRYING TO RUN "'+str(cmd)+'" WITH SHELL'
                p = subprocess.Popen(cmd,shell=True) # NOTE: with 'True' the blinkerlist doesnt work because exe has different pid then
            except OSError as e:
                  print >>sys.stderr, "Jegzecyoochan failed djem eeeet:", e
        if p:
            #try and find the pid of the process launched by xdg-open and put it on the blinkerlist
            #but give it a second to appear (add dummypid right away, see below)
            Globals.timer3=QtCore.QTimer()
            Globals.timer3.timeout.connect(partial(findPidAddToBlinkerList,command))
            Globals.timer3.setSingleShot(True)
            Globals.timer3.start(200)
            #see CdePanel.py: def updateBlinkerList():
            #hmmm if one of these timers is run as local var inside func, it doesnt work:    
            #var gets cleaned up before timer is finished
            #put a dummy pid in the blinkerlist right away, to make the blinker blink directly after
            #the button is pressed. The dummypid is replaced by the real one by findPidAddToBlinkerList 
            # updateBlinkerList then watches the windowlist, and removes the found pid if the window
            # appears. Then the blinker stops blinking.
            #If all doesnt work.. just kill the blinker after 5 seconds
            Globals.blinkerList.append('dummypid')
            Globals.timer2=QtCore.QTimer()
            Globals.timer2.timeout.connect(purgeBlinkerList)
            Globals.timer2.setSingleShot(True)
            Globals.timer2.start(5000)


def purgeBlinkerList():
    print 'PURGE BLINKERLIST'
    #if pid in Globals.blinkerList: Globals.blinkerList.remove(pid)
    Globals.blinkerList[:]=[]

############################################################################################
#Keep panel on all desktops
def setWindowSticky(executable):
    print 'setWindowSticky for '+executable
    allwins = ewmh.getClientList()
    executablewins=[]
    for w in allwins:
        #this sometimes is 'None'
        if w.get_wm_class():
            if w.get_wm_class()[0]==executable:
                executablewins.append(w)
    for w in executablewins:
        ewmh.setWmState(w,1,'_NET_WM_STATE_STICKY')
        ewmh.display.flush()

def setWindowSticky1(executable):
    print 'setWindowSticky for '+executable
    allwins = ewmh.getClientList()
    executablewins=[]
    for w in allwins:
        #this sometimes is 'None'
        if w.get_wm_class():
            #if w.get_wm_class()[0]==executable:
            if re.search(executable,w.get_wm_class()[0]):
                executablewins.append(w)
    for w in executablewins:
        ewmh.setWmState(w,1,'_NET_WM_STATE_STICKY')
        ewmh.display.flush()


def getLastWorkspace():
    return ewmh.getNumberOfDesktops()




#VERSION BASED ON WMCTRL WORKS FASTER AND LESS POLOINKY
#still use that so we dont need wmctrl installed
#Switch to new desktop
#def setCurrentWorkspace1(workspace):
    #workspace-=1
    #cmd='wmctrl -s '+str(workspace)
    #output = subprocess.check_output(cmd, shell=True)
def setCurrentWorkspace(workspace):
        ewmh.setCurrentDesktop(workspace-1)

#Get currently displayed workspace
#NOT SURE WHICH ONE WORKS BEST HERE, BUT HAS TO BE CALLED EVERY 300 MS
#SO MAYBE BETTER NOT USE EXTERNAL COMMAND
#def getCurrentWorkspace():
    #cmd='wmctrl -d'
    #output = subprocess.check_output(cmd, shell=True)
    #lines=output.splitlines() #array with elements=lines
    #for c in lines:
        #if re.search('\\*',c):
            #x=c.split(' ') 
    #currentdestkop=int(x[0])+1
    #return currentdestkop
def getCurrentWorkspace():
    #on MWM this returns error..
    try:
        W=ewmh.getCurrentDesktop()
    except:
        return 1
    return W+1

#best not rely on wmctrl
def setNumberOfWorkspaces(n):
    ewmh.setNumberOfDesktops(n)
    ewmh.display.flush()
#def setNumberOfWorkspaces(n):
    #cmd='wmctrl -n '+str(n)
    #output = subprocess.check_output(cmd, shell=True)

def switchToNextWorkspace():
    N=getLastWorkspace()
    C=getCurrentWorkspace()
    C+=1
    if C>N:C=1
    setCurrentWorkspace(C)

def switchToPrevWorkspace():
    N=getLastWorkspace()
    C=getCurrentWorkspace()
    C-=1
    if C<1:C=N
    setCurrentWorkspace(C)






#def main():
    #app = QApplication(sys.argv)


    #d=Dum()

    #print d.get_desktop_environment()

    #d.set_wallpaper('/a/cdetheme/cde-theme/cdemu/.cdemu/backdrops/BACKDROP4.xpm', True)
    #d.set_wallpaper('/a/bg/Gradient.xpm', True)


    #sys.exit(app.exec_())


#if __name__ == '__main__':
   #main()




##################################################################
#FOR GETTING CORRECT ENTRY IN WINDOWLIST ---------------V
#pycdewins = filter(lambda w: w.get_wm_class()[1] == 'HBox.py', wins)
def printWindowList():
    wins = ewmh.getClientList()
    for w in wins:
        #<class 'Xlib.display.Window'>(0x04600002)
        #[0] is kleine letters/[1] is hoofdletters (exec/name?)
        #!?!?!bij [1]: is executalbe (script) 'cdepanel' dan staat er in [1]: 'Cdepanel' Waar komt de HL vandaan????
        #wacht bij [0] staat erbij CdePanel ook gewoon hoofdletters, die dus gebruiken
        #ook bij stwindowsticky
        print '>>>'+w.get_wm_class()[0]
        print ewmh.getWmPid(w)
#printWindowList()
#setWindowSticky('HBox.py')
##################################################################
##################################################################
##################################################################
##################################################################

#def getDesktopList():
    #cmd='wmctrl -d'
    #output = subprocess.check_output(cmd, shell=True)
    #lines=output.splitlines() #array with elements=lines
    #desktops=[]
    #for c in lines:
        #x=c.split(' ')[0]
        #desktops.append(x)
    #return desktops 

#def getLastWorkspace():
    #cmd='wmctrl -d'
    #output = subprocess.check_output(cmd, shell=True)
    #lines=output.splitlines() #array with elements=lines
    #return len(lines)

#def setPanelSticky():
    #wins = ewmh.getClientList()
    #pycdewins = filter(lambda w: w.get_wm_class()[1] == 'HBox.py', wins)
    #for pycdewin in pycdewins:
        #pycdewin=pycdewins[0]
        #ewmh.setWmState(pycdewin,1,'_NET_WM_STATE_STICKY')
        #ewmh.display.flush()


