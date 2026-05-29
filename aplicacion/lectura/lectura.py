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

def leer(filename):

    cap= cv2.VideoCapture(filename)

    video_lista= []
    while True:
        ret, frame= cap.read()
        if not ret:
            break
        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)#Lo pasamos a escala de grises para quedarnos solo con uno
        video_lista.append(frame[200:800:,500:1300])#Lo añadimos a una lista recortando a mano todo lo que no sea pecera, se debe cambiar segun el setup
    video_array= np.array(video_lista)#Lo transformamos en un array que nos gusta mas trabajar asi 
    
    """
    Para crear el fondo tomamos 100 fotogramas aleatorios de video_array y nos quedamos con la moda
    """
    
    aleatorios= np.random.choice(len(video_array), size= min(100,len(video_array)),replace= False)
    
    fondo= scp.stats.mode(video_array[aleatorios], keepdims= True)[0]#Creamos un fondo quedandonos con la moda de cada uno de los puntos de cada fotograma en el tiempo

    video_array= video_array.astype(np.float32)#Este formato es el que usamos para restarlos entre si
    
    fondo= fondo.astype(np.float32)#

    '''
    En fondo nos quedamos con el cero porque suelta dos arrays, y el unico que
    interesa es el primero
    '''    
    
    """
    Muy bien, aqui ya tenemos el fotograma y el fondo operando, ahora queremos 
    restarlos y despues ir puliendo la imagen para quitar todo lo que no sea 
    objeto
    
    Para ello usaremos un filtro de mediana con el metodo cv2.medianBlur
    """
    
    restado= video_array - fondo#Obtenemos un video sin el fondo
    
    restado= np.clip(restado,0,255)
    
    restado= restado.astype(np.uint8)#Cambiamos el formato a uno que se trague el filtro de la mediana
    
    for i in range(restado.shape[0]):#Hay que pasarle los fotogramas uno a uno porque solo acepta uint8 de un canal

        restado[i]= cv2.medianBlur(restado[i],7)
    
    restado= restado.astype(np.float32)#Volvemos a cambiar el formato para poder binarizar mas o menos
      
    restado= (restado>100).astype(np.uint8)*255 #Binarizamos y volvemos a cambiar el formato para luego poder mostrarlo

    return restado

def centroides(restado): #Le pasamos un video ya restado y procesado
    
    """
    Perfecto, ya tenemos casi todo hecho. Tenemos el frame restado y hemos
    conseguido practicamente aislar el objet. La idea ahora viene a ser identificar todos los 
    candidatos a objetos y quedarnos unicamente con los que sean verdaderos.
    
    Para ello usaremos cv2.connectedComponentWithStats(imagen). Al cual le pasas un fotograma y
    te devuelve.
    
    1. Numero de objetos detectados (el indice 0 es el fondo)
    2. Matriz donde cada pixel tiene el indice del objeto al que pertenece
    3. Estadisticas geometricas [x,y,width,height, area]. Con el area podemos jugar para
    discretizar los objetos que nos valen
    4. Centros de masa. Esto es lo que finalmente nos vamos a guardar
    
    Importante que la imagen que le das sea una de 8bit con un unico canal
    """
    
    centroides_validos=[]
    area_valida= 30

    for fotograma in restado:

        num_labels, labels, stats, centroids= cv2.connectedComponentsWithStats(fotograma)
        
        """
        Aqui tomamos todos los objetos, ahora los vamos a discriminar por area y quedarnos con 
        los centros de masa
        """
        
        stats_bien= stats[1:]#Hemos quitado la primera fila que es el fondo
        areas= stats_bien[:,4]#Tomamos el cuarto objeto que son las areas de todo lo que identifica
        
        for i in range(num_labels-1):#Porque me he quitado el area del fondo
        
            if areas[i]>= area_valida and areas[i]==max(areas): #areas[i]>=area_valida or areas[i]== max(areas):
                
                centroides_validos.append(centroids[i])
                
    centroides_validos= np.array(centroides_validos)
    
    return centroides_validos   