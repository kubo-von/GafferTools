print("Loading GafferTools")
import Gaffer
import GafferUI
import GafferScene
import GafferTools
import imath

nodeMenu = GafferUI.NodeMenu.acquire( application )
nodeMenu.append( "/Tools/Foo", GafferTools.Foo, searchText = "Foo" )
nodeMenu.append( "/Tools/FooDeformer", GafferTools.Foo, searchText = "FooDeformer" )
nodeMenu.append( "/Tools/ContactSheet", GafferTools.ContactSheet, searchText = "ContactSheet" )

mainMenuDefinition = GafferUI.ScriptWindow.menuDefinition( application )
mainMenuDefinition.append( "/Tools/Node Colors", { "command" : GafferTools.ShowNodeColorsWindow } )