#!/usr/bin/python
from ColorFun import *
#import subprocess
#import os.path
#from Opts import Opts #kan niet hier omat in opts zelf globals wordt geimporteerd
#!!!!!!!!!!!!!!!!!!IN OTHER FILES THESE BECOME 'Globals.COLORS' ETC
#!!!!!!!!!!!!!!!!!!IN OTHER FILES THESE BECOME 'Globals.COLORS' ETC
#!!!!!!!!!!!!!!!!!!IN OTHER FILES THESE BECOME 'Globals.COLORS' ETC
#!!!!!!!!!!!!!!!!!!IN OTHER FILES THESE BECOME 'Globals.COLORS' ETC
#!!!!!!!!!!!!!!!!!!IN OTHER FILES THESE BECOME 'Globals.COLORS' ETC
#!!!!!!!!!!!!!!!!!!IN OTHER FILES THESE BECOME 'Globals.COLORS' ETC
#!!!!!!!!!!!!!!!!!!IN OTHER FILES THESE BECOME 'Globals.COLORS' ETC
NCOLORS=8
CURRENTPALETTE=3
PALETTEDIR='palettes'
#COLORS=readMotifColors(NCOLORS,PALETTEDIR+'/'+'BeigeRose.dp')
#keep global for now
PALETTES=['Broica.dp', 'Alpine.dp', 'Arizona.dp', 'BeigeRose.dp', 'Black.dp', 'BlackWhite.dp', 'BlueOrange.dp', 'BlueShades.dp', 'Broica.dp', 'BroicaMod.dp', 'BroicaWhite.dp', 'BrownShades.dp', 'Cabernet.dp', 'Camouflage.dp', 'Charcoal.dp', 'Chocolate.dp', 'Cinnamon.dp', 'Clay.dp', 'Crimson.dp', 'DarkBlue2.dp', 'DarkBlue.dp', 'DarkGold.dp', 'Default.dp', 'Delphinium.dp', 'Desert.dp', 'Golden.dp', 'Grass.dp', 'GrayScale.dp', 'GreenShades.dp', 'lilac2.dp', 'Lilac.dp', 'Mustard1.dp', 'Mustard.dp', 'Neptune.dp', 'NorthernSky.dp', 'Nutmeg.dp', 'Olive.dp', 'Orange.dp', 'Orchid.dp', 'Outcomes.dp', 'PBNJ.dp', 'Sand.dp', 'SantaFe.dp', 'Savannah.dp', 'SeaFoam.dp', 'SkyRed.dp', 'SoftBlue.dp', 'SouthWest.dp', 'Summer.dp', 'Test1.dp', 'Test2.dp', 'Test.dp', 'Testing.dp', 'Tundra.dp', 'Tust.dp', 'Urchin.dp', 'Wheat.dp', 'WhiteBlack.dp', 'White.dp', 'Windows.dp']
WIN=[]
EXECUTABLE=None

OPTS=[]

cdepanel=None

#return list with all palettefiles
#def loadPALETTES(palettedir):
    #cmd='ls'+' '+palettedir+'/*.dp'
    #output = subprocess.check_output(cmd, shell=True)
    #lines=output.splitlines() #array with elements=lines
    #return [os.path.basename(l) for l in lines]
#has to be globals for other files also to use
#def paletteFile2Ix(palettefile):
    #return PALETTES.index('Delphinium.dp')
#def ix2PaletteFile(ix):
    #return PALETTES[22]
#def lastPaletteIx():
    #return len(PALETTES)-1

#PALETTES=loadPALETTES('palettes')
#print lastPalette
#print PALETTES
#print PALETTES.index('Delphinium.dp')
#print PALETTES[22]
#Globals.PALETTES=loadPALETTES('palettes')

#def currentPalettefile2Num(palettefile):
    #print 

    
#TESTOPTS=Opts()
#TESTOPTS.NCOLORS=8
#TESTOPTS.CURRENTPALETTE=5
#TESTOPTS.COLORS=readMotifColors(TESTOPTS.NCOLORS,PALETTEDIR+'/'+'Lilac.dp')
