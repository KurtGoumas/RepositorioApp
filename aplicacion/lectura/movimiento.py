import numpy as np 
import scipy as scp
import matplotlib
matplotlib.use('Agg')#Para que no intente abrir ventanas
from matplotlib import animation 
import matplotlib.pyplot as plt
from numba import njit, prange
import pandas as pd
import os

"""
Este script es el que nos va a ayudar a obtener todas las graficas que queramos y a calcular todas las
caracteristicas del movimiento del individuo
"""

def Escribir_p_t_v_a(Nombre, pos, t, v, v_vec, a, a_vec):
    
    Nombre_nuevo= 'resultados/' + Nombre + '_parametros_movimiento'

    dataframe= pd.DataFrame({'x': pos[:,0], 'y': pos[:,1], 'z': pos[:,2],
                              'Tiempo': t, 'vx': v_vec[:,0], 'vy': v_vec[:,1], 
                              'vz': v_vec[:,2],'Módulo Velocidad': v, 
                              'ax': a_vec[:,0], 'ay': a_vec[:,1], 'az': a_vec[:,2],
                              'Módulo Aceleración': a})
    dataframe.to_csv(Nombre_nuevo + '.csv', sep= '\t', index= False, encoding= 'latin-1')

    return True

def Obtener_p_t_v_a(Nombre):

    """
    Esta funcion es la que invocaremos en screens para que tome el csv con las posiciones 
     , tiempos y demas y lo convierta en arrays
    """

    dataframe= pd.read_csv(Nombre + '.csv', sep= '\t', usecols= ['x', 'y', 'z', 'Tiempo',
                                                                  'Módulo Velocidad', 
                                                                  'Módulo Aceleración'], encoding= 'latin-1')
    
    #Cogemos el tiempo, velocidad y aceleracion
    t= dataframe['Tiempo'].to_numpy()
    v= dataframe['Módulo Velocidad'].to_numpy()
    a= dataframe['Módulo Aceleración'].to_numpy()

    #Hacemos la posicion
    x= dataframe['x'].to_numpy()
    y= dataframe['y'].to_numpy()
    z= dataframe['z'].to_numpy()

    pos= np.zeros((len(x),3))
    pos[:,0]= x
    pos[:,1]= y
    pos[:,2]= z

    return pos, t, v, a
    

@njit(fastmath= True, parallel= True)
def velocidades(pos, t):
    """
    Esta funcion es simplemente una funcion auxiliar de Movimiento para sacar las velocidades 
    usando numba.

    Inicialmente pos tiene la forma [fotograma:[x,y,z],...]
    Y t de la forma [t1,t2,...,tn]
    """

    n= len(t) #pos y t deberian tener la misma longitud asi que da igual cual coja
    v= np.zeros(n) #Modulo de la velocidad, se considerara inicialmente 0 (primer fotograma)
    v_vec= np.zeros((n,3))
    a= np.zeros(n) #Modulo de la aceleracion
    a_vec= np.zeros((n,3))

    for i in prange(1,n):#Recuerda que la velocidad inicial es 0

        #Sacamos velocidades
        dpos= pos[i]-pos[i-1]
        dt= abs(t[i]-t[i-1])

        v_vec_inst= dpos/dt
        v_mod= (v_vec_inst[0]**2 + v_vec_inst[1]**2 + v_vec_inst[2]**2)**0.5

        v_vec[i]= v_vec_inst
        v[i]= v_mod

        #Sacamos aceleraciones

        dv= v_vec[i]-v_vec[i-1]

        a_vec_inst= dv/dt

        a_mod= (a_vec_inst[0]**2 + a_vec_inst[1]**2 + a_vec_inst[2]**2)**0.5

        a_vec[i]= a_vec_inst
        a[i]= a_mod

    return v_vec, v, a_vec, a

def Animacion_Movimiento(pos,t,skip = 1, save = False, saveName = "Animacion"):
    
    """
    Dada las posiciones tipo [fotograma[x,y,z], ...], se hace una animacion en el tiempo
    Cambia skip si quieres hacer que la animacion vaya mas rapido
    """
    fig = plt.figure()
    ax = fig.add_subplot(projection = '3d')
    ax.set_title("Animación del movimiento")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    timeText = ax.text2D(.01, .99, 'Tiempo actual: 0 s', ha='left', va='top', transform=ax.transAxes)
    
    # Pongamos el minimo y maximo de los ejes
    ax.set_xlim3d(np.min(pos[:,0]), np.max(pos[:,0]))
    ax.set_ylim3d(np.min(pos[:,1]), np.max(pos[:,1]))
    ax.set_zlim3d(np.min(pos[:,2]), np.max(pos[:,2]))
    
    # Dibujamos trayectoria?
    ax.plot(pos[:,0],pos[:,1],pos[:,2], linestyle = "dashed", color = "black", linewidth = 0.5)
    
    # Inicializamos la animacion
    lines = [ax.scatter([],[],[], s = 30)]
    def init():
        # frame inicial animacion
        timeText.set_text('Tiempo actual: 0.000 s ')
        for line in lines:
            line._offsets3d = ([], [],[])
        return lines + [timeText]
    def animate(frame):
        timeText.set_text(f'Tiempo actual: {round(t[frame],3)} s ')
        for line in lines:
            line._offsets3d = ([pos[frame,0]],[pos[frame,1]],[pos[frame,2]])
        return lines + [timeText]
    framesTotal = len(t)
    frames_indices = range(0, framesTotal, skip)
    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                   frames=frames_indices, blit=False)
    if save: anim.save(saveName, writer="pillow")
    return anim

def Movimiento(Nombre, pos, t):
    
    """
    A esta funcion le pasaremos un array del tipo [fotograma[x,y,z],...] y lo pintaremos en 3D en el tiempo.
    
    Tambien es interesante obtener parametros como la velocidad y la aceleracion.

    Nombre servira para etiquetar lo que vayamos sacando
    """

    if not os.path.exists('./resultados'):
        os.makedirs('./resultados')

    Nombre_cortado= os.path.basename(Nombre).split('_')[0]#Asi nos quedamos solo con la fecha en qeu fue grabado el video
    Nombre_3D= 'resultados/' + Nombre_cortado + '_plot_trayectoria'
    
    Nombre_vel= 'resultados/' + Nombre_cortado + '_plot_velocidad'
    Nombre_ac= 'resultados/' + Nombre_cortado + '_plot_aceleracion'
    Nombre_animacion= 'resultados/' + Nombre_cortado + '_Animacion.gif'

    #Pintamos las posiciones en funcion del timepo para el individuo
    fig = plt.figure()
    ax1= fig.add_subplot(projection= '3d')

    ax1.set_title('Reconstrucción de la trayectoria del inviduo en el espacio.')
    ax1.set_xlabel(r'$x [cm]$')
    ax1.set_ylabel(r'$y [cm]$')
    ax1.set_zlabel(r'$z [cm]$')
    
    #Preparamos los arrays de x,y,z

    pos= pos[0]# Porque el array es de la forma (trayectorias, Fotogramas, posiciones)
    
    x= pos[:, 0]
    y= pos[:, 1]
    z= pos[:, 2]
    
    ax1.scatter(x,y,z, label= 'Movimiento en todo el espacio de la gamba', s= 8)
    ax1.legend(loc= 'best')
    fig.savefig(Nombre_3D)#creo que tengo que crear un directorio pero bueno, veremos 
    #fig.show()

    """
    Ahora vamos a hacer una animacion 
    """

    anim= Animacion_Movimiento(pos, t, save= True, saveName= Nombre_animacion)

    '''
    """
    Lo siguiente que vamos a hacer es calcularnos las velocidades y las aceleraciones 
    y las guardaremos en un ultimo csv para disponer ellas si hiciera falta
    """

    v_vec, v, a_vec, a= velocidades(pos,t)

    idx_max_v= np.argmax(v)
    idx_max_a= np.argmax(a)

    fig2, ax2= plt.subplots()

    ax2.set_title('Módulo de la velocidad frente al tiempo')
    
    ax2.set_xlabel(r'$t [s]$')
    ax2.set_ylabel(r'$v [\frac{cm}{s}]$')

    ax2.plot(t,v, label= 'Módulo de la velocidad')

    #Pintamos la velocidad maxima
    ax2.plot(t[idx_max_v],v[idx_max_v], '*', label= f'Velocidad máxima: $v= {v[idx_max_v]:.2f} cm/s $')#Marcamos la velocidad maxima

    ax2.legend(loc= 'best')

    plt.savefig(Nombre_vel)
    plt.show()

    fig3, ax3= plt.subplots()

    ax3.set_title('Módulo de la aceleración frente al tiempo')
    
    ax3.set_xlabel(r'$t [s]$')
    ax3.set_ylabel(r'$a [\frac{cm}{s^{2}}]$')

    ax3.plot(t,a, label= 'Módulo de la aceleración')

    #Pintamos la velocidad maxima
    ax3.plot(t[idx_max_a],a[idx_max_a], '*', label= f'Aceleración máxima: $a= {a[idx_max_a]:.2f} cm/s^{{2}} $')#Marcamos la velocidad maxima

    ax3.legend(loc= 'best')

    plt.savefig(Nombre_ac)
    plt.show()

    """
    Ya tenemos todas las figuras hechas y guardadas, ahora solo queda meterlas en el 
    csv
    """

    Guardado= Escribir_p_t_v_a(Nombre_cortado, pos, t, v, v_vec, a, a_vec)
    '''
    return True

def Movimiento_csv(Nombre, pos, t, v, a):

    if not os.path.exists('./resultados'):
        os.makedirs('./resultados')

    Nombre_3D= 'resultados/' + Nombre + '_plot_trayectoria'
    Nombre_vel= 'resultados/' + Nombre + '_plot_velocidad'
    Nombre_ac= 'resultados/' + Nombre + '_plot_aceleracion'

    #Pintamos las posiciones en funcion del timepo para el individuo
    
    ax1= plt.figure().add_subplot(projection= '3d')

    ax1.set_title('Reconstrucción de la trayectoria del inviduo en el espacio.')
    ax1.set_xlabel(r'$x [cm]$')
    ax1.set_ylabel(r'$y [cm]$')
    ax1.set_zlabel(r'$z [cm]$')
    
    #Preparamos los arrays de x,y,z
    
    x= pos[:, 0]
    y= pos[:, 1]
    z= pos[:, 2]
    
    ax1.scatter(x,y,z, label= 'Movimiento en todo el espacio de la gamba')
    ax1.legend(loc= 'best')
    
    plt.savefig(Nombre_3D)#creo que tengo que crear un directorio pero bueno, veremos 
    plt.show()
    
    """
    Lo siguiente que vamos a hacer es calcularnos las velocidades y las aceleraciones 
    y las guardaremos en un ultimo csv para disponer ellas si hiciera falta
    """

    idx_max_v= np.argmax(v)
    idx_max_a= np.argmax(a)

    fig2, ax2= plt.subplots()

    ax2.set_title('Módulo de la velocidad frente al tiempo')
    
    ax2.set_xlabel(r'$t [s]$')
    ax2.set_ylabel(r'$v [\frac{cm}{s}]$')

    ax2.plot(t,v, label= 'Módulo de la velocidad')

    #Pintamos la velocidad maxima
    ax2.plot(t[idx_max_v],v[idx_max_v], '*', label= f'Velocidad máxima: $v= {v[idx_max_v]:.2f} cm/s $')#Marcamos la velocidad maxima

    ax2.legend(loc= 'best')

    plt.savefig(Nombre_vel)
    plt.show()

    fig3, ax3= plt.subplots()

    ax3.set_title('Módulo de la aceleración frente al tiempo')
    
    ax3.set_xlabel(r'$t [s]$')
    ax3.set_ylabel(r'$a [\frac{cm}{s^{2}}]$')

    ax3.plot(t,a, label= 'Módulo de la aceleración')

    #Pintamos la velocidad maxima
    ax3.plot(t[idx_max_a],a[idx_max_a], '*', label= f'Aceleración máxima: $a= {a[idx_max_a]:.2f} cm/s^{{2}} $')#Marcamos la velocidad maxima

    ax3.legend(loc= 'best')

    plt.savefig(Nombre_ac)
    plt.show()

    return True
