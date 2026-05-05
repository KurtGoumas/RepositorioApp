import numpy as np 
import scipy as scp
import matplotlib.pyplot as plt
import cv2

from matplotlib import cm
from matplotlib.ticker import LinearLocator

'''
En este script crearemos las funciones que estan realcionadas con la lectura de videos o de
carpetas con videos. 

De esta forma podremos transformar un video en un array de (ancho, alto, frame) y tratarlo mas 
comodamente. 

Por otro lado podremos tomar toda una carpeta y trabajar con ella.
'''

#plt.close('all')

def leer(filename):

    cap= cv2.VideoCapture(filename)
    
    #ret, frame= cap.read()
    #h,w,_= frame.shape
    #_,_,l= frame.shape

    #video_array= np.zeros([h,w,l])

    video_lista= []
    while True:
        ret, frame= cap.read()
        if not ret:
            break
        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)#Lo pasamos a escala de grises para quedarnos solo con uno
        video_lista.append(frame[100:620:,400:880])#Lo añadimos a una lista recortando a mano todo lo que no sea pecera, se debe cambiar segun el setup
    video_array= np.array(video_lista)#Lo transformamos en un array que nos gusta mas trabajar asi 
    fondo= scp.stats.mode(video_array[:])[0]#Creamos un fondo quedandonos con la moda de cada uno de los puntos de cada fotograma en el tiempo

    '''
    En fondo nos quedamos con el cero porque suelta dos arrays, y el unico que
    interesa es el primero
    '''

    '''
    Una vez tenemos el video en forma de array queremos.

    Normalizar, para que todos los valores esten entre 0 y 1
    Binarizar, para que todos los valores por debajo de un umbral sean cero y los superiores 1

    Normalizamos dividiendo entre 255 porque al ser 8bit, ese sera el valor maximo de luminancia

    Binarizamos con np.where(array< umbral, valor si verdadero= 0, valor si falso=1 )
    '''

    video_array= video_array/255 #Normalizamos
    
    fondo= fondo/255 #Normalizamos fondo
    
    video_array= np.where(video_array<0.5,0,1) #Binarizamos
    
    fondo= np.where(fondo<0.5,0,1) #Binarizamos fondo

    video_array= video_array.astype(np.float64)#Esto hay que ponerlo tras tratar el video para que se lea bien, cuando no, no se pone
    
    fondo= fondo.astype(np.float64)

    return video_array, fondo

#aqui trato el video como array 

video_array, fondo= leer(r"C:\Users\adelu\OneDrive\Escritorio\FisicaAlicante\Año_V\Gambas_con_Alzheimer\RepositorioApp\videos\24-4-2026-14-43-19_0.mp4")

#Ahora vamos a representarlo

Frame1= video_array[1]
cv2.imshow('prueba', Frame1)

fondo= fondo
cv2.imshow('prueba fondo', fondo)

Frame_No_Fondo= Frame1-fondo

cv2.imshow('Restado', Frame_No_Fondo)