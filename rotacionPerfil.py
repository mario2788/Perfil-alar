import Draft
import numpy as npy
import math as m

# parametros de operacion y geometricos
f = open( "/home/mario/Documents/Imp/puntos_eppler420_Selig format dat.txt" )
largo = 45 # mm
r = 20 # mm

arrayNum = []
for i in range(1, 100):

	temp = f.readline().split()
	if ( len(temp) > 1 ) :
		[n1, n2] = temp
		arrayNum.append( [float(n1), float(n2), 0] )
	else:
		break

f.close()

# Escalado de la geometria
arrayNum = npy.array( arrayNum )*largo

# Proyeccion del plano al cilindro
puntosCilindro = [] # (y,r,teta)
for p in arrayNum:
    puntosCilindro.append([ p[1],r,p[0]/r])

# Cambio de coordenadas
puntosCartecianos = [] # (x,y,z)
for p in puntosCilindro:
    puntosCartecianos.append([r*m.cos(p[2]), p[0], r*m.sin(p[2])])

# crear documento:
name = "perfilAlar"
App.newDocument(name)
Gui.activeDocument().activeView().viewDefaultOrientation()

#seleccionar entorno:
Gui.activateWorkbench("DraftWorkbench")

# contruccion de la spline
def closeCurve( array3Dimesional ):
	points = []
	for index in range(0, len( array3Dimesional ) ) :
		points.append( FreeCAD.Vector( array3Dimesional[index] ) )

	spline = Draft.makeBSpline(points, closed=False, face=False, support=None)
	Draft.autogroup(spline)

closeCurve( puntosCartecianos )
FreeCAD.ActiveDocument.recompute()
Gui.SendMsgToActiveView("ViewFit")

# Rotacion y traslado


Draft.rotate([FreeCAD.ActiveDocument.BSpline], 25, FreeCAD.Vector(0.0, 0.0, 0.0), axis=FreeCAD.Vector(0.0, 0.0, 1.0), copy=True)
#Draft.move([FreeCAD.ActiveDocument.BSpline001], FreeCAD.Vector(0.0, 0.0, 1.0), copy=False)
