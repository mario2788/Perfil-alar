## Seleccionar todas las aristas del wire con alias alambre
for i in range(1,len(App.ActiveDocument.getObjectsByLabel('alambre74')[0].Shape.Edges) ):
    Gui.Selection.addSelection('perfilAlar','Wire074','Edge'+ i.__str__() )

# Numero de vertices en un Wire074
len(App.ActiveDocument.Wire075.Shape.Vertexes)

# Linea a parttir de vertices
points = [App.ActiveDocument.Wire074.Shape.Vertex1.Point ,App.ActiveDocument.Wire074.Shape.Vertex2.Point]
line = Draft.makeWire(points, closed=False, face=False, support=None)

#  constricccion de lineas que unen los vertices enfrentados en un wire cerrado
vertexes = len(App.ActiveDocument.getObjectsByLabel('alambre74')[0].Shape.Vertexes)
for n in range(1, vertexes ):
    points = [
        App.ActiveDocument.getObjectsByLabel('alambre74')[0].Shape.getElement('Vertex'+ (n+1).__str__() ).Point,
        App.ActiveDocument.getObjectsByLabel('alambre74')[0].Shape.getElement('Vertex'+ ( vertexes - n + 1 ).__str__() ).Point
    ]
    line = Draft.makeWire(points, closed=False, face=False, support=None)
    App.ActiveDocument.ActiveObject.Label = 'line' + n.__str__()
    if( n == vertexes/2): break


# Seleccion de objetos
Gui.Selection.addSelection(App.ActiveDocument.Wire074, 'Edge66')
Gui.Selection.addSelection(App.ActiveDocument.getObjectsByLabel('alambre74')[0], 'Edge66')


# constriccion de superficie a parttir de vertices
Gui.Selection.addSelection('perfilAlar','Wire074','Vertex1',41.8078,-9.77332,42.3362)
Gui.Selection.addSelection('perfilAlar','Wire074','Vertex66',41.9811,-9.69696,42.1644)
Gui.Selection.addSelection('perfilAlar','Wire074','Vertex2',41.9711,-9.67986,42.1743)
_=Part.makeFilledFace(Part.makePolygon([App.ActiveDocument.Wire074.Shape.Vertex1.Point, App.ActiveDocument.Wire074.Shape.Vertex66.Point, App.ActiveDocument.Wire074.Shape.Vertex2.Point, ], True).Edges)
App.ActiveDocument.addObject('Part::Feature','Face').Shape=_
del _



#  construcccion de superficies que unen los vertices enfrentados en un wire cerrado
vertexes = len(App.ActiveDocument.getObjectsByLabel('alambre74')[0].Shape.Vertexes)
for n in range(1, vertexes ):
    if( n==1 ):
        _=Part.makeFilledFace(Part.makePolygon([
            App.ActiveDocument.getObjectsByLabel('alambre74')[0].Shape.getElement('Vertex' + (n).__str__() ).Point,
            App.ActiveDocument.getObjectsByLabel('alambre74')[0].Shape.getElement('Vertex' + (n+1).__str__() ).Point,
            App.ActiveDocument.getObjectsByLabel('alambre74')[0].Shape.getElement('Vertex' + ( vertexes - n + 1 ).__str__() ).Point,
        ], True).Edges)
    else:
        _=Part.makeFilledFace(Part.makePolygon([
            App.ActiveDocument.getObjectsByLabel('alambre74')[0].Shape.getElement('Vertex' + (n).__str__() ).Point,
            App.ActiveDocument.getObjectsByLabel('alambre74')[0].Shape.getElement('Vertex' + (n+1).__str__() ).Point,
            App.ActiveDocument.getObjectsByLabel('alambre74')[0].Shape.getElement('Vertex' + ( vertexes - n + 1  ).__str__() ).Point,
            App.ActiveDocument.getObjectsByLabel('alambre74')[0].Shape.getElement('Vertex' + ( vertexes - n + 2 ).__str__() ).Point,
        ], True).Edges)
    App.ActiveDocument.addObject('Part::Feature','Face').Shape=_
    del _
    App.ActiveDocument.ActiveObject.Label = 'surf' + n.__str__()
    if( n == vertexes/2): break


# Crear shell con los segmentos de superficies
array = []
for n in range(1, int(vertexes/2)):
    array.append(App.ActiveDocument.getObjectsByLabel('surf' + n.__str__() )[0].Shape.getElement('Face1') )
    Gui.Selection.addSelection(App.ActiveDocument.getObjectsByLabel( 'surf' + n.__str__() )[0] )
    Gui.runCommand('Std_ToggleVisibility',0)
    Gui.Selection.clearSelection()
    
_=Part.Shell(array)
App.ActiveDocument.addObject('Part::Feature','Shell').Shape=_.removeSplitter()
del _
