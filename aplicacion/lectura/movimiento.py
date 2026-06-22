import numpy as np 
import scipy as scp
import matplotlib.pyplot as plt
from numba import njit, prange

"""
Este script es el que nos va a ayudar a obtener todas las graficas que queramos y a calcular todas las
caracteristicas del movimiento del individuo
"""

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

        v[i]= v_mod

        #Sacamos aceleraciones

        dv= v_vec[i]-v_vec[i-1]

        a_vec_inst= dv/dt

        a_mod= (a_vec_inst[0]**2 + a_vec_inst[1]**2 + a_vec_inst[2]**2)**0.5

        a[i]= a_mod

    return v_vec, v, a_vec, a

def Movimiento(Nombre, pos, t):
    
    """
    A esta funcion le pasaremos un array del tipo [fotograma[x,y,z],...] y lo pintaremos en 3D en el tiempo.
    
    Tambien es interesante obtener parametros como la velocidad y la aceleracion.

    Nombre servira para etiquetar lo que vayamos sacando
    """
    
    #Pintamos las posiciones en funcion del timepo para el individuo

    Nombre_3D= Nombre + '_Trayectorias_3D'
    
    ax1= plt.figure().add_subplot(projection= '3d')

    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.set_zlabel('Z')
    
    #Preparamos los arrays de x,y,z
    
    x= pos[:, 0]
    y= pos[:, 1]
    z= pos[:, 2]
    
    ax1.scatter(x,y,z, label= 'Movimiento en todo el espacio de la gamba')
    ax1.legend(loc= 'best')
    
    plt.save(Nombre_3D)#creo que tengo que crear un directorio pero bueno, veremos 
    plt.show()
    
    """
    Lo siguiente que vamos a hacer es calcularnos las velocidades y las aceleraciones 
    y las guardaremos en un ultimo csv para disponer ellas si hiciera falta
    """

    v_vec, v, a_vec, a= velocidades(pos,t)


    