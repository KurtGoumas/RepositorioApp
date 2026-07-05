# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as matplotlib
from aplicacion.lectura import lectura as lec
#from aplicacion.lectura import movimiento as mov # Ojo, el agg de aqui dentro está liandola 
#matplotlib.use('qt5agg')#Para que no intente abrir ventanas
plt.close('all')
"""
Prueba de algoritmo sintetico

- Escogemos una trayectoria 3D bien conocida (linea 3D, helice, etc)
- Hacemos sus trayectorias asociadas a los planos de las cámaras 
- Aplicamos el algoritmo para comprobar si, efectivamente, obtenemos la trayectoria esperada (movimiento y lectura)

Usamos las dimensiones de la pecera y de la camara 
el rectangulo del plano de pecera es 
500 px alto x 800 px ancho (no uses el 500 para el factor de escala, porque es la altura del agua)
cuando la pecera mide
25,5 x 25,5 x 25,5

800 px --> 25'5 cm

"""
def Linea3D (t,m,n):
    """
    Construimos una recta en un espacio 3D con pendiente m y ordenada n
    """
    trayec = m*t[:,np.newaxis] + n
    return trayec[:,0], trayec[:,1], trayec[:,2]

def Helice3D (t,a=7,b=7,wx=1,wy=1):
    """
    Construimos una cardioide en el plano z = 0
    """
    x = 10 + a*np.cos(wx*t)
    y = 10 + b*np.sin(wy*t)
    z = t
    return x,y,z # en cm 
#%% Construimos la pecera virtual
unionCam = False # Pasas por todo union cam si true. En caso contrario, solo pasas por Resolver_sistema
# Grid en la pecera virtual
"""
# Limites de la pecera (0,1)
nPoints = 3
xArr = np.linspace(0,1,nPoints) # En espacio real, luego pasamos a pixeles
yArr = np.copy(xArr)
zArr = np.copy(xArr)
"""
#%% Construimos las trayectorias en los planos y la 3D teorica
nTimes = 1000
tArr = np.linspace(0,10,nTimes) # Nota: Luego probar con dos arrays de tiempo ligeramente desplazados entre si (por la interpolacion)
h = 800 #px
hm = 25.5 #m 
# Variables de la camara (cm)
xc1= 47.5
yc1= 12
zc1= 11
xc2= 12
yc2= 47.5
zc2= 11
Lx= 25.5
Ly= 25.5
# Construimos la trayectoria 3D
m = np.ones(3)
n = np.zeros(3)
#xTeo,yTeo,zTeo = Linea3D(tArr,m,n) # Sistema de referencia la esquina inferior izquierda de la pecera
xTeo,yTeo,zTeo = Helice3D(tArr)
# Construimos la trayectoria 2D. La proyeccion asi es mala, hay que hacerla bien porque no tiene en cuenta la perspectiva de la camara
Cam1 = np.zeros((nTimes,1,2),dtype = float) # (y,z)
# Calculemos los puntos vistos desde el plano de la camara:
# Usamos triangulos equivalentes
H1z = zTeo - zc1
H1y = yTeo - yc1
L1 = xc1-xTeo
l1 = xc1 - Lx

Cam1[:,:,0] = (yc1 + H1y * l1/L1)[:,np.newaxis] # Y
Cam1[:,:,1] = (zc1 + H1z*l1/L1)[:,np.newaxis] # Z


Cam2 = np.zeros((nTimes,1,2),dtype = float) # (x,z)
H2z = zTeo-zc2
H2x = xTeo-xc2
L2 = yc2-yTeo
l2 = yc2-Ly

Cam2[:,:,0] = (xc2 + H2x*l2/L2)[:,np.newaxis] # X
Cam2[:,:,1] = (zc2 + H2z*l2/L2)[:,np.newaxis] # Z

#%%% Pasamos a pixeles
"""
Podemos considerar que el agua llega hasta 25.5, pero que la gamba no sube mas de 500 px y ya. Asi el cambio es 800 x 800
regla de 3: 
    25,5 cm --> 800 px
    x cm --> y px
Así:
    y = 800/25.5 * x
"""
scale = 800./25.5 # Pasamos de cm a pixeles
Cam1 = scale*Cam1
Cam2 = scale*Cam2

#%% Pasamos por el algoritmo (desde centroides para abajo)
if unionCam:
    print("Modo union Cam")
    TrayecNum, tNum = lec.Union_camaras(Cam1,Cam2,tArr,tArr, N_objetos = 1, peso = 1000, xc1= 1.86, yc1= 0.47, zc1= 0.43 , xc2= 0.47, yc2= 1.86, zc2= 0.43, Lx= 1, Ly= 1)
else:
    print("Modo a mano (resolver sistema)")
    TrayecNum = np.zeros((nTimes,1,3), dtype = float)
    
    for i in range(nTimes):
        TrayecNum[i] = lec.Resolver_Sistema(Cam1[i],Cam2[i],xc1= 1.86 , yc1= 0.47, zc1= 0.43 , xc2= 0.47, yc2= 1.86, zc2= 0.43, Lx= 1, Ly= 1, w = 800, h = 800) # Cambio a h = 800 suponiendo agua muy alta (para facilitarme pasar la teorica a adimensional)

# Comprobar error
if unionCam:
    error_z =  abs(zTeo/hm - TrayecNum[0,:,2])
else:
    error_z = abs(zTeo/hm - TrayecNum[:,0,2])
#%% Ploteamos para comparar
# Plot
fig = plt.figure()

ax = fig.add_subplot(projection='3d')
if unionCam:
    fig.suptitle("Union Cam")
    ax.scatter(TrayecNum[0,:,0],TrayecNum[0,:,1],TrayecNum[0,:,2], label = 'numerica', s = 8) # Version union camaras
else:
    fig.suptitle("Solo resolver sistema")
    ax.scatter(TrayecNum[:,0,0],TrayecNum[:,0,1],TrayecNum[:,0,2], label='numerica', s = 8)


ax.scatter(xTeo/hm,yTeo/hm,zTeo/hm, label = "teorica", s = 8) # Para estar en adimensional. Esta perfe

ax.set_xlabel("x/Lx")
ax.set_ylabel("y/Ly")
ax.set_zlabel("z/Lz")
ax.legend()
fig.show()

fig2 = plt.figure()
fig2.suptitle("Plano Y-Z")
ax2 = fig2.add_subplot()
ax2.scatter(Cam1[:,:,0],Cam1[:,:,1])
ax2.set_xlabel("y (px)")
ax2.set_ylabel("z (px)")
fig2.show()

fig3 = plt.figure()
fig3.suptitle("Plano X-Z")
ax3 = fig3.add_subplot()
ax3.scatter(Cam2[:,:,0],Cam2[:,:,1])
ax3.set_xlabel("x (px)")
ax3.set_ylabel("z (px)")
fig3.show()

fig4 = plt.figure()
fig4.suptitle("Error en z")
ax4 = fig4.add_subplot()
ax4.scatter(tArr,error_z)
#ax4.scatter(tArr,(TrayecNum[:,0,2] / (zTeo/hm)))
ax4.set_xlabel("t")
ax4.set_ylabel("err_Z")
fig4.show()

