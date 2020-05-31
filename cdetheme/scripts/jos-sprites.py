#!/usr/bin/env python

from gimpfu import *
import re
import os

#see resourcex.xcf

def jos_sprites(img, layer) :
    print 'Looking for layers'
    spritefilename='/tmp/Sprites.py'
    #spritefilename='/tmp/sprites.py'
    sprites=[]
    num_layers, layer_ids = pdb.gimp_image_get_layers(img)
    #print num_layers
    #print layer_ids
    visibleLayers=[]
    for l in img.layers:
        visible = pdb.gimp_drawable_get_visible(l)
        if visible:
            visibleLayers.append(l)

    f = open(spritefilename, 'w')
    s="""spriteLWHXY=[\n""".format(**locals())
    f.write(s) 

    N=len(visibleLayers)
    for i in range(N):
        l=visibleLayers[i]
        width = pdb.gimp_drawable_width(l)
        height = pdb.gimp_drawable_height(l)
        x, y = pdb.gimp_drawable_offsets(l)
        filename = pdb.gimp_layer_get_name(l) 
        print 'filename '+str(filename)#__debug
        print 'width '+str(width)#__debug
        print 'height '+str(height)#__debug
        print 'x '+str(x)#__debug
        print 'y '+str(y)#__debug
        if i==N-1:comma=''
        else:comma=','
        label , file_extension = os.path.splitext(filename)
        s="""   ['{label}', {width}, {height}, {x}, {y}]{comma}\n""".format(**locals())
        f.write(s) 
    s="""]\n""".format(**locals())
    f.write(s) 
    f.close() 

    print 'SAVED TO '+spritefilename


register(
    "jos_sprites",#menu entry func
    "Do someting1",#something mysterious needs to be different
    "Do anything1",
    "JVR1",
    "Gimme Money1",
    "20131",
    "<Image>/Sprites/Export layer coordinates to sprites.py", #menu entry
    "*",
    [],
    [],
    jos_sprites)

main()
