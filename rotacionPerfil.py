import Draft
import numpy as npy
import math as m
from FreeCAD import Base
import Part

# crear documento:
name = "perfilAlar"
App.newDocument(name)
Gui.activeDocument().activeView().viewDefaultOrientation()

# parametros de operacion y geometricos
#f = open( "/home/mario/Documentos/Perfil-alar/puntos_eppler420_Selig_format_dat.txt" )
f = open( "/home/mario/Documents/Imp/puntos_eppler817_Selig_format_dat.txt" )
vel_angular = 3500 # rmp
diam_int = 45 # mm
diam_ext = 120 # mm
largo = m.pi*diam_int/2   # mm
ang_ataque = 8 # Grados
vel_axial = 6 # m/s
num_alabes = 4

# Lectura de puntos del perfil aerodinamico
arrayNum = []
for i in range(1, 100):
	temp = f.readline().split()
	if ( len(temp) > 1 ) :
		[n1, n2] = temp
		arrayNum.append( [float(n1), float(n2), 0] )
	else:
		break

f.close()

#  Proyeccion del perfil plano sobre la superficio de un cilindro.
def proyec( radio, array ):
	# Proyeccion del plano al cilindro
	puntosCilindro = [] # (y,r,teta), usando x
	for p in array:
	    puntosCilindro.append([ p[1], radio, p[0]/radio])

	# Cambio de coordenadas de cilindricas a cartecianas
	puntosCartecianos = [] # (x,y,z)
	for p in puntosCilindro:
	    puntosCartecianos.append([radio*m.cos(p[2]), p[0], radio*m.sin(p[2])])
	return puntosCartecianos

# Adelantar el perfil
def move( delta, array):
    puntosPerfil = []
    for p in array:
        puntosPerfil.append( [p[0]-(delta)/3, p[1], p[2]] )
    return puntosPerfil

# determinar el angulo de inclinacion
def ang_inclinacion(radio):
    omega = 2*m.pi*vel_angular/60 # radianes por segundo
    ang = m.atan(vel_axial/omega/radio)
    return ang + ang_ataque*m.pi/180

# Rotar el perfil plano el angulo proporcionado
def rotate( angRot, array ): # array 3-d que contiene una figura plana
    puntosRotados = []
    for p in array:
        r = m.sqrt(p[0]*p[0]+p[1]*p[1])
        d = m.sqrt(2*r*r*(1-m.cos(angRot)))
        ang_p = m.atan(p[1]/p[0])
        ang_d = ang_p + m.pi + angRot/2
        dx = d*m.cos(ang_d)
        dy = d*m.sin(ang_d)
        puntosRotados.append([ p[0]+dx, p[1]+dy, 0 ])
    return puntosRotados

# contruccion de la spline
def closeCurve( array3Dimesional ):
    points = []
    for index in range(0, len( array3Dimesional ) ) :
        points.append( App.Vector( array3Dimesional[index] ) )
    # spline = Draft.makeBSpline(points, closed=True, face=False, support=None)
    # Draft.autogroup(spline)
    line = Draft.makeWire(points, closed=True, face=False, support=None)
    Draft.autogroup(line)

# Seleccionar entorno de trabajo Draft
Gui.activateWorkbench("DraftWorkbench")
Gui.runCommand("Draft_ToggleGrid")

# Construccion de los alambres a diferentes angulos y radios
alambres = 0
d = diam_int
while d < diam_ext:
    alambres = alambres + 1
    # Escalado del perfil hasta el largo defido
    array = npy.array( arrayNum )*(d)
    # Creacion de alambre
    closeCurve( proyec( d/2, move(alambres, rotate( ang_inclinacion(d/2/1000), array) ) ) )
    App.ActiveDocument.ActiveObject.Label = 'alambre' + alambres.__str__()
    # Ocultar el alambre
    Gui.runCommand('Std_ToggleVisibility',0)
    d = d + 1

# Seleccionar entorno de trabajo Part
Gui.activateWorkbench("PartWorkbench")

# Crear superficie entre alambres
for alam in range(1, alambres):
    App.ActiveDocument.addObject('Part::RuledSurface', 'Ruled Surface')
    App.ActiveDocument.ActiveObject.Curve1=(App.ActiveDocument.getObjectsByLabel('alambre' + alam.__str__() )[0],[''])
    App.ActiveDocument.ActiveObject.Curve2=(App.ActiveDocument.getObjectsByLabel('alambre' + (alam+1).__str__() )[0],[''])
    App.ActiveDocument.ActiveObject.Label = 'surface' + alam.__str__()
    App.ActiveDocument.getObjectsByLabel('surface' + alam.__str__())[0].Orientation = u"Forward"
    Gui.runCommand('Std_ToggleVisibility',0)
    Gui.Selection.clearSelection()

App.ActiveDocument.recompute()

# construccion de las tapas
flag = True
for alambre in ['alambre1', 'alambre'+ alambres.__str__() ]:
    #  construcccion de superficies que unen los vertices enfrentados en un wire cerrado
    vertexes = len(App.ActiveDocument.getObjectsByLabel(alambre)[0].Shape.Vertexes)
    for n in range(1, vertexes ):
        if( n==1 ):
            _=Part.makeFilledFace(Part.makePolygon([
                App.ActiveDocument.getObjectsByLabel(alambre)[0].Shape.getElement('Vertex' + (n).__str__() ).Point,
                App.ActiveDocument.getObjectsByLabel(alambre)[0].Shape.getElement('Vertex' + (n+1).__str__() ).Point,
                App.ActiveDocument.getObjectsByLabel(alambre)[0].Shape.getElement('Vertex' + ( vertexes - n + 1 ).__str__() ).Point,
            ], True).Edges)
        else:
            _=Part.makeFilledFace(Part.makePolygon([
                App.ActiveDocument.getObjectsByLabel(alambre)[0].Shape.getElement('Vertex' + (n).__str__() ).Point,
                App.ActiveDocument.getObjectsByLabel(alambre)[0].Shape.getElement('Vertex' + (n+1).__str__() ).Point,
                App.ActiveDocument.getObjectsByLabel(alambre)[0].Shape.getElement('Vertex' + ( vertexes - n + 1  ).__str__() ).Point,
                App.ActiveDocument.getObjectsByLabel(alambre)[0].Shape.getElement('Vertex' + ( vertexes - n + 2 ).__str__() ).Point,
            ], True).Edges)
        App.ActiveDocument.addObject('Part::Feature','Face').Shape=_
        del _
        App.ActiveDocument.ActiveObject.Label = 'surf_' + alambre + '_' + n.__str__()
        if( n == vertexes/2): break

    # Crear shell con los segmentos de superficies
    array = []
    for n in range(1, int(vertexes/2)):
        array.append(App.ActiveDocument.getObjectsByLabel('surf_' + alambre + '_' + n.__str__() )[0].Shape.getElement('Face1') )
        Gui.Selection.addSelection(App.ActiveDocument.getObjectsByLabel( 'surf_' + alambre + '_' + n.__str__() )[0] )
        Gui.runCommand('Std_ToggleVisibility',0)
        Gui.Selection.clearSelection()

    _=Part.Shell(array)
    App.ActiveDocument.addObject('Part::Feature','Shell').Shape=_.removeSplitter()
    if flag :
        App.ActiveDocument.ActiveObject.Label = 'surface0'
        flag = False
    else:
        App.ActiveDocument.ActiveObject.Label = 'surface' + alambres.__str__()
    del _


# # Crear superficie para las tapas
# #tapa 1
# _ = Part.makeFilledFace(Part.__sortEdges__([App.ActiveDocument.getObjectsByLabel('surface'+ (alambres-2).__str__())[0].Shape.Edge3]))
# App.ActiveDocument.addObject('Part::Feature','Face').Shape=_
# App.ActiveDocument.ActiveObject.Label = 'surface' + (alambres-1).__str__()
# del _
# #tapa 2
# _ = Part.makeFilledFace(Part.__sortEdges__([App.ActiveDocument.getObjectsByLabel('surface'+ '0')[0].Shape.Edge1]))
# App.ActiveDocument.addObject('Part::Feature','Face').Shape=_
# App.ActiveDocument.ActiveObject.Label = 'surface' + (alambres).__str__()
# del _

# Crear shell con todas las superficies
surfs = []
for surf in range(0, alambres+1):
    surfs = npy.concatenate( (surfs, App.ActiveDocument.getObjectsByLabel('surface' + surf.__str__() )[0].Shape.Faces), axis=0 )
    # for face in App.ActiveDocument.getObjectsByLabel('surface' + surf.__str__() )[0].Shape.Faces :
    #     surfs.append( face )
        # print( 'surface' + surf.__str__() )
    # surfs.append( App.ActiveDocument.getObjectsByLabel('surface'+surf.__str__() )[0] )
    # ocultar superficies que ya no se usarán
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection( App.ActiveDocument.getObjectsByLabel('surface' + surf.__str__() )[0] )
    Gui.runCommand('Std_ToggleVisibility',0)

_ = Part.Shell(surfs)
App.ActiveDocument.addObject('Part::Feature','Shell').Shape=_.removeSplitter()
App.ActiveDocument.ActiveObject.Label = 'shell_base'
del _

# Crear solido desde el Shell
shell=App.ActiveDocument.getObjectsByLabel('shell_base')[0].Shape
_=Part.Solid(shell)
App.ActiveDocument.addObject('Part::Feature','Solid').Shape=_.removeSplitter()
App.activeDocument().recompute(None,True,True)
# ocultar shell
Gui.Selection.clearSelection()
Gui.Selection.addSelection(App.ActiveDocument.getObjectsByLabel('shell_base')[0])
Gui.runCommand('Std_ToggleVisibility',0)

# Crear cilindro para eje
App.ActiveDocument.addObject("Part::Cylinder","Cylinder")
App.ActiveDocument.ActiveObject.Label = "Cilindro"
FreeCAD.getDocument('perfilAlar').getObject('Cylinder').Radius = (diam_int/2).__str__() + ' mm'
FreeCAD.getDocument('perfilAlar').getObject('Cylinder').Height = (diam_int/2).__str__() + ' mm'
App.getDocument("perfilAlar").Cylinder.Placement=App.Placement(App.Vector(0.00,3.00,0.00),App.Rotation(App.Vector(1.00,0.00,0.00),90.00))

# Crear clones en un array polar
Gui.Selection.clearSelection()
Gui.Selection.addSelection('perfilAlar','Solid')
#Gui.runCommand('Draft_ArrayTools',1)
_obj_ = Draft.make_polar_array(App.ActiveDocument.Solid, number=4, angle=360.0, center=FreeCAD.Vector(0.0, 0.0, 0.0), use_link=True)
#Gui.Selection.addSelection('perfilAlar','Array')
_obj_.Fuse = False
Draft.autogroup(_obj_)
App.ActiveDocument.recompute()
FreeCAD.getDocument('perfilAlar').getObject('Array').Axis = (0.00, 1.00, 0.00)
Gui.Selection.clearSelection()

# fusionar objetos
App.activeDocument().addObject("Part::MultiFuse","Fusion")
App.activeDocument().Fusion.Shapes = [App.activeDocument().Cylinder,App.activeDocument().Array,]
Gui.activeDocument().Cylinder.Visibility=False
Gui.activeDocument().Array.Visibility=False
App.getDocument('perfilAlar').getObject('Fusion').ViewObject.ShapeColor=getattr(App.getDocument('perfilAlar').getObject('Cylinder').getLinkedObject(True).ViewObject,'ShapeColor',App.getDocument('perfilAlar').getObject('Fusion').ViewObject.ShapeColor)
App.getDocument('perfilAlar').getObject('Fusion').ViewObject.DisplayMode=getattr(App.getDocument('perfilAlar').getObject('Cylinder').getLinkedObject(True).ViewObject,'DisplayMode',App.getDocument('perfilAlar').getObject('Fusion').ViewObject.DisplayMode)
App.ActiveDocument.recompute()

Gui.SendMsgToActiveView("ViewFit")
