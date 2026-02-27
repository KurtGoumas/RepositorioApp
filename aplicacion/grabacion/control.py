import cv2
import time
import datetime as dt
import csv

def listar_indices(max= 2):
    l = [i for i in range(max) if cv2.VideoCapture(i).isOpened() and cv2.VideoCapture(i).release() is None]

    return l

def tiempo_grabacion():
    horas= int(input('Horas: '))
    minutos= int(input('Minutos: '))
    segundos= int(input('Segundos: '))

    intervalos_minutos= int(input('Intervalos de grabación en minutos: '))
    intervalos_segundos= int(input('Intervalos de grabación en segundos: '))
    
    tiempo= horas*3600 + minutos*60 + segundos
    intervalo= intervalos_minutos*60 + intervalos_segundos
    if intervalo== 0:
        intervalo= tiempo
    return tiempo,intervalo

def MetadatosGlobalesIniciales(Nombre, camara):
    with open(Nombre + '_globales' + '.csv', 'w', newline='') as file:
        formato = csv.writer(file, delimiter = ' ',dialect='excel', quotechar='|' ,quoting=csv.QUOTE_ALL)
        lista= [f'{camara.shape}',f'{camara.fourcc}']
        formato.writerow(lista)

    return Nombre

def Resumen_final(Nombre, fps, frames):
    with open(Nombre + '_globales' + '.csv', 'a', newline='') as file:
        formato = csv.writer(file, delimiter = ' ',dialect='excel', quotechar='|' ,quoting=csv.QUOTE_ALL)
        lista= [f'{fps}',f'{frames}']
        formato.writerow(lista)

    return Nombre

def MetadatosGlobalesFinales(hilo):
    fps_suma= hilo.Prom_fps
    Frames= hilo.Contador_Frames
    return fps_suma, Frames


def MetadatosIteracion(Nombre,camara,hilo):
    with open(Nombre + '.csv', 'a', newline='') as file:
        formato = csv.writer(file, delimiter = ' ',dialect='excel', quotechar='|' ,quoting=csv.QUOTE_ALL)
        lista= [f'{hilo.Contador_Frames}', 
                f'{dt.datetime.now().hour}-{dt.datetime.now().minute}-{dt.datetime.now().second}',
                f'{time.time()-hilo.comienzo}', 
                f'{hilo.fps_real}', f'{camara.exposicion}', f'{camara.ganancia}', f'{camara.cap.get(cv2.CAP_PROP_BITRATE)}', 'WB']
        formato.writerow(lista)
    return True
