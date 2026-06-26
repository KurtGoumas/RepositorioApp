import cv2
import time
import datetime as dt
import csv
import os
import pandas as pd

def listar_indices(max= 2):
    l = []
    for i in range(max):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            l.append(i)
        cap.release()
    return l

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
        formato = csv.writer(file, delimiter = '\t',dialect='excel' ,quoting=csv.QUOTE_NONE, escapechar= '\\')
        lista= [f'{camara.shape}',f'{camara.fourcc}']
        formato.writerow(lista)

    return Nombre

def Resumen_final(Nombre, fps, frames):
    with open(Nombre + '_globales' + '.csv', 'a', newline='') as file:
        formato = csv.writer(file, delimiter = '\t',dialect='excel' ,quoting=csv.QUOTE_NONE, escapechar= '\\')
        lista= [f'{fps}',f'{frames}']
        formato.writerow(lista)

    return Nombre

def MetadatosGlobalesFinales(hilo):
    fps_suma= hilo.Prom_fps
    Frames= hilo.Contador_Frames
    return fps_suma, Frames


def MetadatosIteracion(Nombre,camara,hilo):

    existe= os.path.exists(Nombre + '.csv')
    with open(Nombre + '.csv', 'a', newline='') as file:
        formato = csv.writer(file, delimiter = '\t',dialect='excel' ,quoting=csv.QUOTE_NONE, escapechar= '\\')
        if not existe:
            formato.writerow(['Fotograma', 'Hora-Minuto-Segundo','Tiempo', 'fps','Exposición','Ganancia', 'Bitrate','WB'])
        lista= [f'{hilo.Contador_Frames}', 
                f'{dt.datetime.now().hour}-{dt.datetime.now().minute}-{dt.datetime.now().second}',
                f'{time.time()-hilo.comienzo}', 
                f'{hilo.fps_real}', f'{camara.exposicion}', f'{camara.ganancia}', f'{camara.cap.get(cv2.CAP_PROP_BITRATE)}', 'WB']
        formato.writerow(lista)
    return True



