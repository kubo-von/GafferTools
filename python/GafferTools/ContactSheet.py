import IECore

import Gaffer
import GafferImage
import imath
import math

class ContactSheet( GafferImage.ImageProcessor ) :

    def __init__(self, name = 'ContactSheet' ):
        GafferImage.ImageProcessor.__init__( self, name )

        self.internalNetwork = []
        self.uiPlugs = []
        
        self["in"] = Gaffer.ArrayPlug( "in", Gaffer.Plug.Direction.In, element = GafferImage.ImagePlug( flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic) )

        self.addChild( Gaffer.IntPlug( "Columns", defaultValue = 2 ) )
        self.addChild( Gaffer.IntPlug( "SpacingPixels", defaultValue = 0 ) )
        self.addChild( Gaffer.Color4fPlug( "BackgroundColor" ) )
        self.addChild( Gaffer.BoolPlug( "FillAlpha", defaultValue = True ) )
        self.uiPlugs.extend( (self["Columns"], self["SpacingPixels"], self["FillAlpha"]) )

        if (len(self["in"])==1):
            self.addChild(GafferImage.Constant("__BG"))
            self.internalNetwork.append(self["__BG"])

            self['out'].setFlags(Gaffer.Plug.Flags.Serialisable, False)
            self['out'].setInput( self['__BG']['out'] )
        else:
            self.generateInternalNetwork()

        self.plugSetSignal().connect(  Gaffer.WeakMethod(self.update), scoped = False )
        self["in"].childAddedSignal().connect(  Gaffer.WeakMethod(self.update), scoped = False )
        self["in"].childRemovedSignal().connect(  Gaffer.WeakMethod(self.update), scoped = False )
        

    def update(self,plug,subplug=None):
        #print(plug, subplug)
        if (plug in self.uiPlugs):
            #print(plug)
            self.generateInternalNetwork()
        if (plug == self["in"]):
            #print(plug)
            self.generateInternalNetwork()
        if (subplug in self["in"].children()):
            #print(subplug)
            self.generateInternalNetwork()

    def generateInternalNetwork(self):
        imageSize = imath.V2i( 256, 256 )
        columns = self["Columns"].getValue()
        spacingPixels = self["SpacingPixels"].getValue()
        fillAlpha = self["FillAlpha"].getValue()

        if (self["in"][1].getInput() != None):
            imageSize = self["in"][0].dataWindow().size()
            print(self["in"][0].dataWindow().size())
        
        #delete everything inside
        for i in self.internalNetwork:
            if i in self.children():
                self.removeChild(i)
                self.internalNetwork.remove(i)
        
        self["__BG"] = GafferImage.Constant()
        self["__BG"]["color"].setInput( self["BackgroundColor"] )
        self["__BG"]["format"].setValue( GafferImage.Format( int(imageSize.x+spacingPixels)*columns +spacingPixels, int( math.ceil((len(self["in"])-1)/columns) ) * int(imageSize.y+spacingPixels) +spacingPixels ) )
        self.internalNetwork.append(self["__BG"])

        prevNode = self["__BG"]
        #construct the node chain
        for pi in range( 0,len(self["in"]) ):
            if (self["in"][pi].getInput() != None):
                self["__xform"+str(pi)] = GafferImage.ImageTransform()
                xform = self["__xform"+str(pi)]
                xform['in'].setInput( self["in"][pi] )
                row = math.ceil( (len(self["in"])-1) / columns)- math.floor( pi / columns ) -1
                col = ((pi)%columns)
                #print(row,col)
                xform["transform"]["translate"].setValue( imath.V2f( col*(imageSize.x+float(spacingPixels)) +float(spacingPixels), row*(imageSize.y+float(spacingPixels)) +float(spacingPixels) ) )

                self["__shuffle"+str(pi)] = GafferImage.Shuffle()
                shuffle = self["__shuffle"+str(pi)] 
                shuffle['in'].setInput(xform['out'])
                shuffle["channels"].addChild( GafferImage.Shuffle.ChannelPlug( "channel", flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
                shuffle["channels"].addChild( GafferImage.Shuffle.ChannelPlug( "channel1", flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
                shuffle["channels"].addChild( GafferImage.Shuffle.ChannelPlug( "channel2", flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
                shuffle["channels"].addChild( GafferImage.Shuffle.ChannelPlug( "channel3", flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
                shuffle["channels"]["channel"]["out"].setValue( 'R' )
                shuffle["channels"]["channel"]["in"].setValue( 'R' )
                shuffle["channels"]["channel1"]["out"].setValue( 'G' )
                shuffle["channels"]["channel1"]["in"].setValue( 'G' )
                shuffle["channels"]["channel2"]["out"].setValue( 'B' )
                shuffle["channels"]["channel2"]["in"].setValue( 'B' )
                shuffle["channels"]["channel3"]["out"].setValue( 'A' )
                if fillAlpha:
                    shuffle["channels"]["channel3"]["in"].setValue( '__white' )

                self["__merge"+str(pi)] = GafferImage.Merge()
                mergeNode = self["__merge"+str(pi)]
                mergeNode['in']['in0'].setInput( prevNode['out'] )
                mergeNode['in']['in1'].setInput(shuffle['out'])
                mergeNode["operation"].setValue( 8 )

                prevNode = mergeNode
                self.internalNetwork.extend( (mergeNode, xform, shuffle) )

        self['out'].setFlags(Gaffer.Plug.Flags.Serialisable, False)
        self['out'].setInput( prevNode['out'] )


IECore.registerRunTimeTyped( ContactSheet, typeName = "GafferImage::ContactSheet" )