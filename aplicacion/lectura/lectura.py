import numpy as np 
import scipy as scp
import matplotlib.pyplot as plt
import cv2

from numba import njit, prange
from numba.typed import List
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

@njit(fastmath= True, parallel= True)
def cent_correspondencias(cent_primitivo_ant, cent_primitivo_act, peso= 1.):
    cent_anterior = []
    cent_actual = []
    for j in prange(len(cent_primitivo_act)):
        for k in range(len(cent_primitivo_ant)):
            norma= ((cent_primitivo_ant[j][0]-cent_primitivo_act[k][0])**2 + (cent_primitivo_ant[j][1]-cent_primitivo_act[k][1])**2)**0.5
            if norma<= peso:
                cent_anterior.append(cent_primitivo_ant[k])
                cent_actual.append(cent_primitivo_act[j])
    return cent_anterior, cent_actual

def centroides(restado): #Le pasamos un video ya restado y procesado
    
    """
    Perfecto, ya tenemos casi todo hecho. Tenemos el frame restado y hemos
    conseguido practicamente aislar el object. La idea ahora viene a ser identificar todos los 
    candidatos a objetos y quedarnos unicamente con los que sean verdaderos.
    
    Para ello usaremos cv2.connectedComponentWithStats(imagen). Al cual le pasas un fotograma y
    te devuelve.
    
    1. Numero de objetos detectados (el indice 0 es el fondo)
    2. Matriz donde cada pixel tiene el indice del objeto al que pertenece
    3. Estadisticas geometricas [x,y,width,height, area]. Con el area podemos jugar para
    discretizar los objetos que nos valen
    4. Centros de masa. Esto es lo que finalmente nos vamos a guardar
    
    Importante que la imagen que le das sea una de 8bit con un unico canal
    
    La idea es crear una lsita vacia de centroides, esta lista vacia la iremos llenando fotograma
    a fotograma de forma que nos quede centroides:[fotogramas:[objeto:[x,y],[x,y],...],[],...]
    
    Una vez tengamos esto, iremos quitando objetos relacionando los objetos de dos frames 
    consecutivos, los que tengan correspondencia seran preservados, los que no borrados
    
    Finalmente, nos deberia quedar un array similar pero ahora todos los candidatos deberian ser
    objetos reales (luego veremos que los reflejos tienen algo que decir ante esto, pero nos
                    los sacudiremos cuando comparemos las dos camaras)
    """
    
    n= len(restado)
    
    centroides_aproximados= []#Es la lista preliminar de centroides antes de que desechemos los falsos
    area_valida= 50

    for fotograma in restado:

        num_labels, labels, stats, centroids= cv2.connectedComponentsWithStats(fotograma)
        
        """
        Aqui tomamos todos los objetos, ahora los vamos a discriminar por area y quedarnos con 
        los centros de masa
        """
        
        stats_bien= stats[1:]#Hemos quitado la primera fila que es el fondo
        areas= stats_bien[:,4]#Tomamos el cuarto objeto que son las areas de todo lo que identifica
        
        centroides_fotograma= [] #Aqui meteremos todos los centroides posiblemente validos
        for i in range(num_labels-1):#Porque me he quitado el area del fondo
        
            if areas[i]>= area_valida or areas[i]==max(areas):#Para al menos asegurarnos de pillar un centroide, la gamba deberia ser el mayor
                
                centroides_fotograma.append(centroids[i])
                
        centroides_fotograma= np.array(centroides_fotograma)#Lo transformamos en array
        
        
        centroides_aproximados.append(centroides_fotograma)#En cada fotograma habra un array de objetos
    
    """
    Ahora que ya tenemos la lista de centroides aproximados, los volvemos a meter en un bucle 
    para que nos quedemos unicamente con los centroides que tengan correspondencia entre frames
    """
    
    centroides_finales= []
    
    for i in range(1,n):#Para ir cogiendo cada fotograma, empezamos en 1 y hacemos correspondencia entre el actual y el anterior

        
        centroides_fotograma_anterior, centroides_fotograma_actual= cent_correspondencias(centroides_aproximados[i-1], centroides_aproximados[i])
        
        centroides_fotograma_anterior= np.array(centroides_fotograma_anterior)
        centroides_fotograma_actual= np.array(centroides_fotograma_actual)
        
        centroides_finales.append(centroides_fotograma_anterior)
    
    centroides_finales.append(centroides_fotograma_actual)#Para añadir el ultimo
        
    return centroides_finales

@njit(fastmath= True, parallel= True)
def Union_fotograma(cent_x, cent_y, peso= 1.):
    """
    En esta funcion tomamos cada uno de los objetos del mismo fotograma para las dos camaras y los vamos
    comparando por su coordenada z.
    
    cent_x= [objeto:[x,z],...] mientras que cent_y= [objeto:[y,z],...]
    
    Si las z son suficientemente parecidas, crea una correspondencia y la añade a cent_xyz de forma que
    este sera tal que cent_xyz= [objeto:[x,y,z],...]
    """
    
    cent_xyz= []
    
    for j in prange(len(cent_x)):
        
        for k in range(len(cent_y)):
            norma= ((cent_x[j][1] - cent_y[k][1])**2)**0.5 #Es como usar abs() pero numba trabaja mejor con opraciones explicitas
            
            if norma<=peso:
                x= cent_x[j][0]
                y= cent_y[k][0]
                z= (cent_x[j][1] + cent_y[j][1])/2 #Nos quedamos con z como la media
                
                pos_xyz= np.array([x,y,z])
                cent_xyz.append(pos_xyz)
                
        return cent_xyz
    
@njit(fastmath= True, parallel= True)
def cent_correspondencias_3D(cent_primitivo_ant, cent_primitivo_act, peso= 1.):
    cent_anterior = []
    cent_actual = []
    for j in prange(len(cent_primitivo_act)):
        for k in range(len(cent_primitivo_ant)):
            norma= ((cent_primitivo_ant[j][0]-cent_primitivo_act[k][0])**2 + (cent_primitivo_ant[j][1]-cent_primitivo_act[k][1])**2 + (cent_primitivo_ant[j][2]-cent_primitivo_act[k][2])**2)**0.5
            if norma<= peso:
                cent_anterior.append(cent_primitivo_ant[k])
                cent_actual.append(cent_primitivo_act[j])
    return cent_anterior, cent_actual
    
def Union_camaras(cent_finales_x, cent_finales_y):
    
    """
    En esta funcion vamos a intentar por fin obtener un array del tipo 
    
    cent_finales_xyz= [fotograma:[objeto:[x,y,z],...],...]
    
    Asi obtenemos cent_aprox_xyz.
    
    Pero todavia podemos depurarlo y hacer algo a lo que hicimos con correspondencias y quedarnos 
    unicamente con los objetos que prevalecen entre mas de dos fotogramas, necesitaremos la ayuda de un 
    Correspondencias_3D()
    """
    
    cent_aprox_xyz= []
    
    n= len(cent_finales_x) #Damos por hecho que son el mismo numero de fotogramas, habra que cambiarlo luego
    
    for i in range(n):
        
        cent_xyz= Union_fotograma(cent_finales_x[i], cent_finales_y[i])
        cent_xyz= np.array(cent_xyz)
        
        cent_aprox_xyz.append(cent_xyz)
    
    """
    Aqui ya tenemos el tipo de array que queremos, pero nos falta hacer una correspondencia para tener
    unicamente objetos que existan de verdad 
    """
    
    cent_finales_xyz= []
    
    for i in range(1,n):#Para ir cogiendo cada fotograma, empezamos en 1 y hacemos correspondencia entre el actual y el anterior

        
        centroides_fotograma_anterior, centroides_fotograma_actual= cent_correspondencias_3D(cent_aprox_xyz[i-1], cent_aprox_xyz[i])
        
        centroides_fotograma_anterior= np.array(centroides_fotograma_anterior)
        centroides_fotograma_actual= np.array(centroides_fotograma_actual)
        
        cent_finales_xyz.append(centroides_fotograma_anterior)
    
    cent_finales_xyz.append(centroides_fotograma_actual)#Para añadir el ultimo

    return cent_finales_xyz
