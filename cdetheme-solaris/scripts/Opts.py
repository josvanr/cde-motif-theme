import os.path
import yaml
import subprocess
#from ColorFun import readMotifColors, replaceColors
import Globals
#loadable opts for various classes. Maybe get rid of functions later
class Opts():
    def __init__(self):
        #default filename, use logic to find later
        pass
        

    #add missing default options to given opts to complete them if necessary
    #opts.addMissing(defaultopts)
    def addMissing(self,optsdefault):
        for key in optsdefault.__dict__:
            if not hasattr(self,key):
                value=optsdefault.__dict__[key]
                setattr(self,key,value)
    #def addMissing(self,optsnew):
        #for key in opts1.__dict__:
            #if not hasattr(opts,key):
                #value=opts1.__dict__[key]
                #setattr(opts,key,value)
        
    #opts.overwrite(opts1)
    def overwriteWith(self,optsnew):
        self.__dict__.update(optsnew.__dict__)
    #load and replace current object namespace with loaded
    #note: this way because yaml.load/save looks nicer when works on dict instead of class
    def load(self,filename):
        print 'Opts() LOADING '+filename
        with open(filename, 'r') as stream:
            tmpdict = yaml.load(stream)
        #if file is empty(tmpdict=None), do nothing. Then in all classes default values for opts will be used
        if tmpdict:
            self.__dict__.clear()
            self.__dict__.update(tmpdict) 
    #save namespace (or something)
    def save(self,filename):
        backup=filename+'.backup'
        print 'Copying old config file to '+backup
        cmd='cp'+' '+filename+' '+backup
        output = subprocess.check_output(cmd, shell=True)
        print 'Opts() SAVING CONFIG FILE '+filename
        with open(filename, 'w') as outfile:
            yaml.dump(self.__dict__, outfile)
    #todo move out of opts
    def loadPaletteDir(self,palettedir):
        cmd='ls'+' '+palettedir+'/*.dp'
        output = subprocess.check_output(cmd, shell=True)
        lines=output.splitlines() #array with elements=lines
        return [os.path.basename(l) for l in lines]
    #has to be globals for other files also to use
    @classmethod
    def paletteFile2Ix(self,palettefilename):
        return Globals.palettes.index(palettefilename)
    @classmethod
    def ix2PaletteFile(self,ix):
        return Globals.palettes[ix]
    @classmethod
    def lastPaletteIx(self):
        return len(Globals.palettes)-1

    #PALETTES=loadPALETTES('palettes')
    #print lastPalette

def main():
    print 'RUNNING OPTS TEST'

    #currentpalettefile: Broica.dp
    #defaultworkspacecolor: 2
    #initialheight: 85
    #ncolors: 8
    #nworkspaces: 6
    #palettedir: palettes
    #workspacecolors: [0, 8, 5, 6, 7, 2, 2, 2, 2, 2, 2]
    #workspacelabels: [Zero, One, Two, Three, Four, Five, Six, Seven]

    testopts=Opts()
    
    testopts.load('pycdeconfigtest')
    print testopts.__dict__ #print everything
    #print testopts.currentpalette
    #testopts.save('pycdeconfigtest')
    #print testopts.ix2PaletteFile(1)
    #print testopts.lastPaletteIx()


if __name__ == '__main__':
   main()

