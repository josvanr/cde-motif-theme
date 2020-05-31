#!/usr/bin/python
import signal
import os.path
import sys
signal.signal(signal.SIGINT, signal.SIG_DFL)
from PIL import Image,ImageQt,ImageFilter,ImageEnhance,ImageDraw
from MiscFun import *
import Globals
#


#xfcedecor.py  /x/cdepanel/CdePanel/cdetheme/xfwm4 /x/cdepanel/CdePanel/palettes/Broica.dp 8 3 22 

targetdir='/x/cdepanel/CdePanel/cdetheme/xfwm4'
ibw=3       #inner border width
ith=22      #inner title height
#ith=20
#ith=28      #inner title height
#ith=38      #inner title height
#ith=18      #inner title height
#ith=14      #inner title height
#ith=12      #inner title height

bs='#7f5a3c' #bottomshadow
bg='#eda870' #background
ts='#f8dac2'  #topshadow

tbw=ibw+3   #total border width
tth=ith+3   #total title height
tdh=tbw+tth #total decor height


def state(state):
    global im
    global draw
    global mx,my


    #if state=='active':
        #bs='#7f5a3c' #bottomshadow
        #bg='#eda870' #background
        #ts='#f8dac2'  #topshadow
    #else:
        #bs='#4e4e4e' #bottomshadow
        #bg='#999999' #background
        #ts='#d1d1d1'  #topshadow

    draw=None
    im=None
    mx=None
    my=None

    def new(x,y):
        global im
        global draw
        global mx,my
        im = Image.new('RGBA', (x,y), (0,0,0,0))
        draw = ImageDraw.Draw(im)
        mx=im.width/2.0
        my=im.height/2.0
    def line(x1,y1,x2,y2,c,w):
        global im
        global draw
        if x1<0: x1=im.width+x1
        if x2<0: x2=im.width+x2
        if y1<0: y1=im.height+y1
        if y2<0: y2=im.height+y2
        l=[ (x1,y1), (x2,y2) ]
        draw.line(l, c, w)
    def save(name):
        global im
        global draw
        filenamefullpath=os.path.join(targetdir,name)
        im.save(filenamefullpath, 'PNG')
    def rect(x1,y1,x2,y2,c):
        if x1<0: x1=im.width+x1
        if x2<0: x2=im.width+x2
        if y1<0: y1=im.height+y1
        if y2<0: y2=im.height+y2
        l=[ (x1,y1), (x2,y2) ]
        draw.rectangle(l, c, None)
    def box(x1,y1,x2,y2,c):
        if x1<0: x1=im.width+x1
        if x2<0: x2=im.width+x2
        if y1<0: y1=im.height+y1
        if y2<0: y2=im.height+y2
        line(x1,y1,x2,y1,c,1)
        line(x1,y1,x1,y2,c,1)
        line(x2,y2,x1,y2,c,1)
        line(x2,y2,x2,y1,c,1)




    ######################################
    new(tdh,tdh)
    rect(0,0,tdh-1,tdh-1,bg)
    line(0,0,-1,0,ts,2)
    line(0,0,0,-1,ts,2)
    line(0,-1,-1,-1,ts,1)
    line(tdh-1,0,tdh-1,tdh-1,ts,1)
    line(tbw,tbw,tbw,tdh-1,ts,1)
    line(tbw-1,tbw-1,tbw-1,tdh-1,bs,1)
    line(tbw-1,tbw-1,tdh-1,tbw-1,bs,1)
    line(0,tdh-2,tbw-1,tdh-2,bs,1)
    line(tdh-2,0,tdh-2,tbw-1,bs,1)
    save('top-left-'+state+'.png')

    new(tdh,tdh)
    rect(0,0,tdh-1,tdh-1,bg)
    line(0,0,-1,0,ts,1)
    line(0,1,-2,1,ts,1)
    line(0,tbw-1,-tbw,tbw-1,bs,1)
    line(0,tbw,-tbw,tbw,ts,1)
    line(0,-2,-1,-2,bs,1)
    line(0,-1,-1,-1,ts,1)
    line(0,0,0,-2,bs,1)
    line(1,0,1,tbw-2,ts,1)
    line(1,tbw,1,-2,ts,1)
    line(-tbw-1,tbw,-tbw-1,-2,bs,1)
    line(-tbw,tbw,-tbw,-1,ts,1)
    line(-2,2,-2,-2,bs,1)
    line(-1,1,-1,-2,bs,1)
    save('top-right-'+state+'.png')

    new(tdh,tdh)
    rect(0,0,tdh-1,tdh-1,bg)
    line(0,0,0,-1,ts,2)
    line(0,2,tbw-1,2,ts,1)
    line(tbw,-tbw,-1,-tbw,ts,1)
    line(-1,-tbw+1,-1,-1,ts,1)
    line(tbw-1,0,tbw-1,-tbw,bs,1)
    line(0,1,tbw-1,1,bs,1)
    line(1,-1,-3,-1,bs,1)
    line(2,-2,-3,-2,bs,1)
    line(-2,-tbw+1,-2,-1,bs,1)
    save('bottom-left-'+state+'.png')

    new(tdh,tdh)
    rect(0,0,tdh-1,tdh-1,bg)
    line(-tbw+1,1,-1,1,bs,1)
    line(-tbw+1,2,-1,2,ts,1)
    line(0,-tbw,-tbw,-tbw,ts,1)
    line(0,-1,tdh,-1,bs,1)
    line(0,-2,tdh,-2,bs,1)
    line(1,-tbw+1,1,-1,bs,1)
    line(2,-tbw+1,2,-1,ts,1)
    line(-tbw,0,-tbw,-tbw,ts,1)
    line(-2,0,-1,0,bs,1)
    line(-2,3,-2,-1,bs,2)
    save('bottom-right-'+state+'.png')

    new(1,tdh)
    rect(0,0,0,tdh,bg) 
    line(0,0,0,1,ts,1)
    line(0,tbw-1,0,tdh,ts,1)
    save('title-1-'+state+'.png')

    new(1,tdh)
    rect(0,0,0,tdh,bg) 
    line(0,0,0,1,ts,1)
    line(0,tbw-1,0,tdh,bs,1)
    line(0,-1,0,-1,ts,1)
    save('title-4-'+state+'.png')

    new(1,tdh)
    rect(0,0,0,tdh,bg) 
    line(0,0,0,1,ts,1)
    line(0,tbw-1,0,tbw-1,bs,1)
    line(0,tbw,0,tbw,ts,1)
    line(0,-2,0,-2,bs,1)
    line(0,-1,0,-1,ts,1)
    save('title-2-'+state+'.png')
    save('title-3-'+state+'.png')
    save('title-5-'+state+'.png')

    new(tbw,tbw)
    rect(0,0,tbw,tbw,bg)
    line(0,0,tbw,0,ts,1)
    line(0,-2,tbw,-2,bs,2)
    save('bottom-'+state+'.png')

    new(tbw,tbw)
    rect(0,0,tbw,tbw,bg)
    line(0,0,0,tbw,ts,1)
    line(-2,0,-2,tbw,bs,2)
    save('right-'+state+'.png')

    new(tbw,tbw)
    rect(0,0,tbw,tbw,bg)
    line(0,0,0,-1,ts,2)
    line(-1,0,-1,-1,bs,1)
    save('left-'+state+'.png')

    def buttonbox():
        rect(0,tbw,-1,-1,bg) 
        line(0,tbw-1,tdh,tbw-1,bs,1)
        box(0,tbw,-1,-1,ts)
        line(1,-2,-2,-2,bs,1)
        line(-1,tbw,-1,-2,bs,1)
    def buttonboxpressed():
        rect(0,tbw,-1,-1,bg) 
        line(0,tbw-1,tdh,tbw-1,bs,1)
        box(0,tbw,-1,-1,bs)
        line(1,-2,-2,-2,ts,1)
        line(0,-1,-1,-1,ts,1)
        line(-1,tbw,-1,-2,ts,1)
    def minimizeicon():
        box(mx-2,my-2,mx+1,my+1,ts)
        line(mx-1,my+1,mx+1,my+1,bs,1)
        line(mx+1,my+1,mx+1,my-1,bs,1)

    new(tdh-tbw-1,tdh)
    my+=tbw/2.0
    buttonbox()
    minimizeicon()
    save('hide-'+state+'.png')

    new(tdh-tbw-1,tdh)
    my+=tbw/2.0
    buttonboxpressed()
    minimizeicon()
    save('hide-pressed.png')

    #def menuicon():
        #d=int(w*0.70/2.0)
        #dy=int(w*0.24/2.0)
        #if dy<2:dy=2
        #box(mx-d,my-dy,mx+d-1,my+dy-1,bs)
        #line(mx-d,my-dy,mx-d,my+dy-1,ts,1)
        #line(mx-d,my-dy,mx+d-1,my-dy,ts,1)
    def menuicon():
        d=int(w*0.70/2.0)
        dy2=int(w*0.17)
        if dy2<2:dy=2
        t=int(my-dy2/2.0)-1
        box(mx-d,t,mx+d-1,t+dy2,bs)
        line(mx-d,t,mx-d,t+dy2,ts,1)
        line(mx-d,t,mx+d-1,t,ts,1)
    w=tdh-tbw-1
    new(w,tdh)
    my+=tbw/2.0
    buttonbox()
    menuicon()
    save('menu-'+state+'.png')

    w=tdh-tbw-1
    new(w,tdh)
    my+=tbw/2.0
    buttonboxpressed()
    menuicon()
    save('menu-pressed.png')

    def shadeicon(toggled):
        if toggled=='toggled':
            ts1=bs
            bs1=ts
        else:
            ts1=ts
            bs1=bs
        d=int(w*0.70/2.0)
        dy=int(w*0.24/2.0)
        if dy<2:dy=2
        Dy=int(w*0.40/2.0)
        global my
        my-=Dy
        box(mx-d,my-dy,mx+d-1,my+dy-1,ts1)
        line(mx-d+1,my+dy-2,mx+d-2,my+dy-2,bs1,1)

    w=tdh-tbw-1
    new(w,tdh)
    my+=tbw/2.0
    buttonbox()
    shadeicon('')
    save('shade-'+state+'.png')

    w=tdh-tbw-1
    new(w,tdh)
    my+=tbw/2.0
    buttonbox()
    shadeicon('toggled')
    save('shade-toggled-'+state+'.png')
    save('shade-toggled-pressed.png')

    w=tdh-tbw-1
    new(w,tdh)
    my+=tbw/2.0
    buttonboxpressed()
    shadeicon('')
    save('shade-pressed.png')

    def cross(mx,my,ts):
        d=int(w*0.45/2.0)
        line(mx-d,my-(d-1),mx+(d-1),my+d,ts,1)
        line(mx-(d-1),my-d,mx+d,my+(d-1),ts,1)
        line(mx+d,my-(d-1),mx-(d-1),my+d,ts,1)
        line(mx+(d-1),my-d,mx-d,my+(d-1),ts,1)
        line(mx+d,my-d,mx+d,my-d,ts,1)
        line(mx-d,my-d,mx-d,my-d,ts,1)
        line(mx-d,my+d,mx-d,my+d,ts,1)
        line(mx+d,my+d,mx+d,my+d,ts,1)
        line(mx-(d-1),my-(d-1),mx+(d-1),my+(d-1),bg,1)
        line(mx+(d-1),my-(d-1),mx-(d-1),my+(d-1),bg,1)

    w=tdh-tbw-1
    new(w,tdh)
    my+=tbw/2.0
    buttonbox()
    cross(mx,my-1,bs)
    cross(mx-1,my-1,ts)
    save('close-'+state+'.png')

    w=tdh-tbw-1
    new(w,tdh)
    my+=tbw/2.0
    buttonboxpressed()
    cross(mx,my-1,bs)
    cross(mx-1,my-1,ts)
    save('close-pressed.png')

    def maximizeicon(toggled):
        if toggled=='toggled':
            ts1=bs
            bs1=ts
        else:
            ts1=ts
            bs1=bs
        d=int(w*0.60/2.0)
        box(mx-d,my-d,mx+d-1,my+d-1,bs1)
        line(mx-d,my-d,mx-d,my+d-1,ts1,1)
        line(mx-d,my-d,mx+d-1,my-d,ts1,1)

    w=tdh-tbw-1
    new(w,tdh)
    my+=tbw/2.0
    buttonbox()
    maximizeicon('')
    save('maximize-'+state+'.png')

    w=tdh-tbw-1
    new(w,tdh)
    my+=tbw/2.0
    buttonboxpressed()
    maximizeicon('toggled')
    save('maximize-toggled-'+state+'.png')
    save('maximize-toggled-pressed.png')

    w=tdh-tbw-1
    new(w,tdh)
    my+=tbw/2.0
    buttonboxpressed()
    maximizeicon('')
    save('maximize-pressed.png')

    def plus(mx,my,ts,d):
        line(mx-d,my,mx+d,my,ts,1)
        line(mx,my-d,mx,my+d,ts,1)
    def stickicon(toggled):
        if toggled=='toggled':
            ts1=bs
            bs1=ts
        else:
            ts1=ts
            bs1=bs
        d=int(w*0.40/2.0)
        plus(mx,my,bs1,d)
        plus(mx-1,my-1,ts1,d)

    w=tdh-tbw-1
    new(w,tdh)
    my+=tbw/2.0
    buttonbox()
    stickicon('')
    save('stick-'+state+'.png')

    w=tdh-tbw-1
    new(w,tdh)
    my+=tbw/2.0
    buttonboxpressed()
    stickicon('')
    save('stick-pressed.png')

    w=tdh-tbw-1
    new(w,tdh)
    my+=tbw/2.0
    buttonboxpressed()
    stickicon('toggled')
    save('stick-toggled-'+state+'.png')
    save('2.png')

    w=tdh-tbw-1
    new(w,tdh)
    my+=tbw/2.0
    buttonboxpressed()
    stickicon('')
    save('stick-toggled-pressed.png')

#inactive must first for overwriting whatever
#some images exist in active (orange) and inactive (grey) variants, but
#some images (like the pressed ones) only exist in orange variant (always active)
#The state(active) writes in the orange colorset, the state(inactive) in the
#grey one. So write inactive first (including pressed things) and then overwrite
#in the orange ones but the active do generate separate.. bla see code
#state('inactive')
#state('active')

def genXfceDecor(targetdir1,opts):
    global targetdir,ibw,ith,bs,bg,ts,tbw,tth,tdh
    targetdir=targetdir1
    ibw=opts.internalborderwidth
    ith=opts.internaltitleheight
    tbw=ibw+3   #total border width
    tth=ith+3   #total title height
    tdh=tbw+tth #total decor height
    bs=Globals.colorshash['bs_color_2']
    bg=Globals.colorshash['bg_color_2']
    ts=Globals.colorshash['ts_color_2']
    state('inactive')
    bs=Globals.colorshash['bs_color_1']
    bg=Globals.colorshash['bg_color_1']
    ts=Globals.colorshash['ts_color_1']
    state('active')
    

#writethemerc(filename,palettefilefullpath,self.opts.ncolors,self.opts.internalborderwidth)
#def writethemerc(filename,palettefile,n,ibw):
def genXfwmThemerc(filename,opts):
    ibw=opts.internalborderwidth
    #titlebar text is vertically centered in the middle of the entire decor 
    #in our cde setup titlebar consists of border+title. So add border/2 as offset
    #to center title in middle of our titlebar. The border consists of 'internal borderwidth'
    # plus 4 pixels so. But put a bit higher so:
    titleoffsety=(ibw+2)/2.0
    fg1=Globals.colorshash['fg_color_1']
    bg1=Globals.colorshash['bg_color_1']
    ts1=Globals.colorshash['ts_color_1']
    bs1=Globals.colorshash['bs_color_1']
    fg2=Globals.colorshash['fg_color_2']
    bg2=Globals.colorshash['bg_color_2']
    ts2=Globals.colorshash['ts_color_2']
    bs2=Globals.colorshash['bs_color_2']
    lines="""\
#XFCE Themerc for CDE Palette: {opts.currentpalettefile}
active_text_color={fg1}
inactive_text_color={fg2}
button_offset=0
button_spacing=0
full_width_title=true
maximized_offset=0
shadow_delta_height=0
shadow_delta_width=0
shadow_delta_x=0
shadow_delta_y=0
shadow_opacity=0
show_app_icon=false
title_horizontal_offset=1
title_shadow_active=false
title_shadow_inactive=false
title_vertical_offset_active={titleoffsety}
title_vertical_offset_inactive={titleoffsety}
active_color_1={bg1}
active_hilight_1={ts1}
active_shadow_1={bs1}
inactive_color_1={bg2}
inactive_hilight_1={ts2}
inactive_shadow_1={bs2}
    """.format(**locals())
    with open(filename, 'w') as f: 
        for l in lines:
            f.write(l)


def init():
    cmd="""\
    xfconf-query -c xfwm4 -p /general/theme -s "cdetheme"
    xfconf-query -c xfwm4 -p /general/button_layout -s 'O|THCM'
    """
    execWithShellThread(cmd)


