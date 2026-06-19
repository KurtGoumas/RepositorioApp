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
            norma= ((cent_primitivo_ant[k][0]-cent_primitivo_act[j][0])**2 + (cent_primitivo_ant[k][1]-cent_primitivo_act[j][1])**2)**0.5
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
        centroides_bien= centroids[1:]
        areas= stats_bien[:,4]#Tomamos el cuarto objeto que son las areas de todo lo que identifica
        
        centroides_fotograma= [] #Aqui meteremos todos los centroides posiblemente validos
        for i in range(num_labels-1):#Porque me he quitado el area del fondo
        
            if areas[i]>= area_valida or areas[i]==max(areas):#Para al menos asegurarnos de pillar un centroide, la gamba deberia ser el mayor
                
                centroides_fotograma.append(centroides_bien[i])
                
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
def Ordenar_fotograma(cent_x, cent_y, peso= 1.):
    """
    En esta funcion tomamos cada uno de los objetos del mismo fotograma para las dos camaras y los vamos
    comparando por su coordenada z.
    
    cent_x= [objeto:[x,z],...] mientras que cent_y= [objeto:[y,z],...]
    
    Si las z son suficientemente parecidas, crea una correspondencia y la añade a cent_ord_x y cent_ord_y de forma que
    que el orden de los objetos será el mismo de cara a resolver posteriormente el sistema de ecuaciones para cada uno
    """
    
    cent_ord_x= []
    cent_ord_y= []
    
    for j in prange(len(cent_x)):
        
        for k in range(len(cent_y)):
            norma= abs(cent_x[j][1] - cent_y[k][1])#Si no se traga abs() haces ((resta)**2)**0.5
            
            if norma<=peso:
                cent_ord_x.append(cent_x[j])
                cent_ord_y.append(cent_y[k])
        
        """
        Al finalizar todo tenemos otra vez dos arrays de centroides pero sabemos que los indices de cada uno se corresponden
        con los del otro. Ademas nos hemos desecho de los objetos que no tengan correspondencia entre camaras
        """
                
    return cent_ord_x, cent_ord_y

def Resolver_Sistema(cent_x, cent_y,xc1, yc1, zc1, xc2, yc2, zc2, Lx, Ly, w= 800, h= 1300):#w y h son los pixeles que mide la camara de ancho y alto
    
    """
    En esta funcion cogemos un fotograma y, para cada objeto resolvemos el sistema 
    de ecuaciones y obtenemos su posicion 3D en el espacio
    
    Aqui ya si que cent_x y cent_y deben tener el mismo numero 
    de objetos porque han sido ordenados previamente 

    w y h tienen que ser modificados con cada nuevo corte que elijamos, ya veremos como pulir eso
    """
    
    cent_xyz= []
    
    n= len(cent_x)
    
    for i in range(n):
        
        x1= cent_x[i][0]/w
        z1= cent_x[i][1]/h
        
        y2= cent_y[i][0]/w
        z2= cent_y[i][1]/h
        
        """
        Resolvemos un sistema tq M*x= N donde M es una matriz 4x3 y N es una matriz 4x1, nuestra solucion es un array 
        de la forma [x,y,z]

        Hemos divido entre el ancho (w) y el alto (h) para tener valores adimensionales entre 0 y 1 
        siendo que Lx y Ly valen 1 precisamente por eso.
        """
        
        M= np.array([[y2-yc2,xc2-Lx,0],
            [z2-zc2,0,xc2-Lx],
            [yc1-Ly,x1-xc1,0],
            [0,z1-zc1,yc1-Ly]])#Si hay algun problema, a lo mejor es en esta matriz
        
        N= np.array([xc2*y2 - Lx*yc2, xc2*z2 - Lx*zc2, yc1*x1 - Ly*xc1, yc1*z1 - Ly*zc1])
        
        sol= scp.linalg.lstsq(M,N)[0]#La que importa es la cero, el resto son otras cosas
        
        cent_xyz.append(sol)
    
    return cent_xyz

@njit(fastmath= True, parallel= True)
def Ordenar_3D(cent_xyz, N_objetos, peso):#N_objetos es el numero de objetos que espera el usuario

    """
    Esta funcion toma el tipo de objeto que tenemos y lo convierte en un tipo 
    [objeto:[fotograma:[x,y,z], ...], ...]
    """
    
    Nf= len(cent_xyz)
    
    Ordenado= np.zeros((N_objetos,Nf,3))
    Ordenado[:,0:,]= cent_xyz[0]#Rellenamos con posiciones el primer fotograma
    
    for f in range(1, Nf):
        n0= len(cent_xyz[f])#Numero de objetos del fotograma a tratar
        
        for i in range(N_objetos):#Anterior
            
            minNorm= 1000000
            candidato= False #Por si no encontramos ninguno
            
            for j in range(n0):#Actual
                
                norma= ((Ordenado[i][f-1][0]-cent_xyz[f][j][0])**2 + (Ordenado[i][f-1][1]-cent_xyz[f][j][1])**2 + (Ordenado[i][f-1][2]-cent_xyz[f][j][2])**2)**0.5
                
                if norma<= peso and norma<= minNorm:
                    Ordenado[i][f]= cent_xyz[f][j]
                    minNorm= norma
                    candidato= True
                
                if not candidato:
                    Ordenado[i][f]= Ordenado[i][f-1]#Si no encontramos correspondencia porque la gamba se ha escondido, rellenamos con el anterior
                    
    return Ordenado
    
def Union_camaras(cent_finales_x, cent_finales_y, N_objetos= 10, peso=1, xc1= 0.5, yc1= 1.5, zc1= 0.5 , xc2= 1.5, yc2= 0.5, zc2= 0.5, Lx= 1, Ly= 1):
    
    """
    En esta funcion vamos a intentar por fin obtener un array del tipo 
    
    cent_finales_xyz= [fotograma:[objeto:[x,y,z],...],...]
    
    Primero ordenamos los centroides de cada fotograma de cara a resolver el sistema de ecuaciones
    """
    
    cent_ord_x= []
    cent_ord_y= []
    
    n= len(cent_finales_x) #Damos por hecho que son el mismo numero de fotogramas, habra que cambiarlo luego
    
    for i in range(n):
        
        cent_x, cent_y= Ordenar_fotograma(cent_finales_x[i], cent_finales_y[i],peso)
        
        cent_ord_x.append(cent_x)
        cent_ord_y.append(cent_y)
    
    """
    Aqui tenemos dos arrays tal que,
    
        camara 1: [fotogrma_1:[Objeto_1: [x,z],... ],...]
        camara 2: [fotogrma_1:[Objeto_1: [y,z],... ],...]
        
    Aunque el obejto 1 del fotograma 1 es el mismo para ambas camaras, el objeto 1 del fotograma 1 no es el mismo que el 
    objeto 1 del fotograma 2 para una misma camara, pero esto nos da igual. 
        
    Ahora vamos a resolver el sistema para cada objeto en cada fotograma y al fin obtendremos un array del tipo
    
    cent_xyz= [fotograma:[objeto:[x,y,z],...],...]
    """
    
    cent_xyz= []
    
    for i in range(n):
        
        posicion= Resolver_Sistema(cent_ord_x[i], cent_ord_y[i], xc1, yc1, zc1, xc2, yc2, zc2, Lx, Ly)
        cent_xyz.append(posicion)
    
    cent_finales= Ordenar_3D(cent_xyz, N_objetos, peso)

    return cent_finales