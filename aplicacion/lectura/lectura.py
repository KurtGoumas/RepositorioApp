import numpy as np 
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
        
        video_lista.append(frame)
    video_array= np.array(video_lista)
    video_array= video_array[:,:,:,-1]#Para quedarnos con una matriz de 3D del tipo que queremos

    '''
    Una vez tenemos el video en forma de array queremos.

    Normalizar, para que todos los valores esten entre 0 y 1
    Binarizar, para que todos los valores por debajo de un umbral sean cero y los superiores 1

    Normalizamos dividiendo entre 255 porque al ser 8bit, ese sera el valor maximo de luminancia

    Binarizamos con np.where(array< umbral, valor si verdadero= 0, valor si falso=1 )
    '''

    video_array= video_array/255
    
    video_array= np.where(video_array<0.5,0,1)

    video_array= video_array.astype(np.float64)

    return video_array

#aqui trato el video como array 

video_array= leer(r"C:\Users\adelu\OneDrive\Escritorio\FisicaAlicante\Año_V\Gambas_con_Alzheimer\RepositorioApp\videos\5-4-2026-12-3-21_0.mp4")

#Ahora vamos a representarlo

Frame1= video_array[1]
cv2.imshow('prueba', Frame1)