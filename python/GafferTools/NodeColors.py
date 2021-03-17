import Gaffer
import GafferUI
import GafferScene
import imath


def ShowNodeColorsWindow(menu):
    scriptWindow = menu.ancestor( GafferUI.ScriptWindow )
    root = scriptWindow.scriptNode()
    window = NodeColorsWindow(scriptWindow, scriptWindow)
    scriptWindow.addChildWindow( window )
    window.setVisible( True )

class NodeColorsWindow( GafferUI.Window) :
    def __init__( self, title, scriptWindow, **kw ) :
        GafferUI.Window.__init__( self, title = "Node Color Palette", sizeMode=GafferUI.Window.SizeMode.Manual, borderWidth = 6, **kw )
        self.scriptWindow = scriptWindow
        #print(dir(type(self.root.selection())))

        #colors generated on  https://coolors.co - hit "export" an then "code" to get them in array format
        #https://coolors.co/22424b-366473-3e9491-6e7b26-bb991e-975f17-ce2a27-b1286a-b336c4-6f2995
        #https://coolors.co/3e1414-3e2314-3a3012-313310-253310-0e2d2f-102533-101c33-101133-1e1033
        hexColors = [
            ["22424b","366473","3e9491","6e7b26","bb991e","975f17","ce2a27","b1286a","b336c4","6f2995"],
            ["3e1414","3e2314","3a3012","313310","253310","0e2d2f","102533","101c33","101133","1e1033"],
            ["212121","2f2f2f","3e3e3e","444444","494949","666666","828282","8e8e8e","999999","ffffff"]
        ]

        with self:
            with GafferUI.ListContainer( GafferUI.ListContainer.Orientation.Vertical, spacing = 4 ) :
                for row in hexColors:
                    with GafferUI.ListContainer( GafferUI.ListContainer.Orientation.Horizontal, spacing = 4 ) :
                        for c in row:
                            color = self.hexColorToImath(c)
                            self.colorSwatch = GafferUI.ColorSwatch( color, useDisplayTransform = False, parenting = { "expand" : True } )
                            self.colorSwatch.buttonPressSignal().connect( Gaffer.WeakMethod( self.applyColor ), scoped = False )
    
    def hexColorToImath(self, hexc):
        rgb = tuple(int(hexc[i:i+2], 16) for i in (0, 2, 4))
        return imath.Color3f( rgb[0]/255.0,rgb[1]/255.0,rgb[2]/255.0 )
    def applyColor( self, button, event ):
        # the root of the .gfr script open
        root = self.scriptWindow.scriptNode() 
        # list all open graph editors
        layout = self.scriptWindow.getLayout()
        graphEditors = [ e for e in layout.editors() if isinstance( e, GafferUI.GraphEditor ) ]
        #current root open in graph editor
        graphRoot = graphEditors[0].graphGadget().getRoot() # /todo handle situation when there's multiple graph editors open

        color = button.getColor()
        #if node is selcted, apply color
        for node in graphRoot.children( Gaffer.Node ) :
            if root.selection().contains(node):
                Gaffer.Metadata.registerValue(
                    node,
                    "nodeGadget:color", color
                )