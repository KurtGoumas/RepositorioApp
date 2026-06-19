import numpy as np 
import scipy as scp
import matplotlib.pyplot as plt

"""
Este script es el que nos va a ayudar a obtener todas las graficas que queramos y a calcular todas las
caracteristicas del movimiento del individuo
"""

def Movimiento(trayectoria, fps= 30):
    
    """
    A esta funcion le pasaremos un array del tipo [fotograma[x,y,z],...] y lo pintaremos en 3D en el tiempo.
    
    Tambien es interesante obtener parametros como la velocidad y la aceleracion.
    """
    
    n= len(trayectoria)#Esto es cada fotograma del video
    
    t_total= n/fps #Esto es el tiempo en segundos
    t= np.linspace(0,t_total,n)# array de tiempos que vamos a usar para graficar
    
    #Pintamos las posiciones en funcion del timepo para el individuo
    
    ax1= plt.figure().add_subplot(projection= '3d')
    
    #Preparamos los arrays de x,y,z
    
    x= trayectoria[:, 0]
    y= trayectoria[:, 1]
    z= trayectoria[:, 2]
    
    ax1.plot(x,y,z, label= 'Movimiento en todo el espacio de la gamba')
    ax1.legend(loc= 'best')
    
    plt.show()
    
    