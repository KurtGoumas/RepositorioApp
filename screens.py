import tkinter as tk
from aplicacion.constantes import style
from threading import Thread
from PIL import Image, ImageTk
import imutils
import time
import cv2

from aplicacion.grabacion.Camara_arreglo import Camara
from aplicacion.grabacion.control import *

"""
En la pantalla de Home tendremos que indicar el tiempo 
de grabacion y los intervalos, despues le daremos
al boton de incicio y pasaremos a la pantalla de 
monitorizacion.
"""

class CamThread(Thread):
    def __init__(self, camara, start):
        super().__init__()
        self.cam = camara
        self.comienzo= start
        self.frame_anterior= 0
        self.frame_actual= 0
        self.frame = None
        self.running = True
        self.Contador_Frames= 0
        self.Prom_fps= 0
        self.fps_real=0

    def run(self):
        self.frame_anterior= 0
        while self.running:
            ret, frame = self.cam.cap.read()
            if ret:
                self.Contador_Frames += 1
                self.frame = frame
                self.cam.out.write(frame)
                self.frame_actual= time.time()
                self.Prom_fps+= 1/(self.frame_actual-self.frame_anterior)
                self.fps_real= 1/(self.frame_actual-self.frame_anterior)
                MetadatosIteracionCamara= MetadatosIteracion(self.cam.filename,self.cam,self)

                self.frame_anterior= self.frame_actual            

    def stop(self):
        self.running = False

class Home(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.configure(background= style.BACKGROUND)
        self.controller= controller

        #Todo lo relativo a la camara

        self.indices= listar_indices()
        self.cam1= Camara(self.indices[0])
        #self.cam2= Camara(self.indices[1])

        self.Promedio_fps1= 0
        #self.Promedio_fps2= 0
        self.Frames1= 0
        #self.Frames2= 0

        #Todo lo relativo a los metadatos

        self.MetadatosGLobalesCamara1= None
        self.MetadatosGLobalesCamara2= None

        #Los valores de las horas, minutos y segundos y sus intervalos

        self.t_horas= tk.StringVar(self, value='')
        self.t_minutos= tk.StringVar(self, value='')
        self.t_segundos= tk.StringVar(self, value= '')

        self.intervalo_minutos= tk.StringVar(self, value= '' )
        self.intervalo_segundos= tk.StringVar(self, value= '')

        self.text_entry_width = 10

        self.init_widgets()

    def start(self): #Al pulsar START, guarda los  tiempos e inicia la grabacion
        horas= self.t_horas.get()
        minutos= self.t_minutos.get()
        segundos= self.t_segundos.get()

        intervalo_minutos= self.intervalo_minutos.get()
        intervalo_segundos= self.intervalo_segundos.get()
        if horas!= '' and minutos!= '' and segundos!= '' and intervalo_minutos!= '' and intervalo_segundos!= '':
            horas= int(horas)
            minutos= int(minutos)
            segundos= int(segundos)

            intervalo_minutos= int(intervalo_minutos)
            intervalo_segundos= int(intervalo_segundos)

            tiempo= horas*3600 + minutos*60 + segundos
            intervalo= intervalo_minutos*60 + intervalo_segundos
            if intervalo== 0:
                intervalo= tiempo

            #Activamos la camara y lo dejamos todo listo para grabar

            self.cam1.preparar()
            #self.cam2.preparar()

            self.cam1.activar()
            #self.cam2.activar()

            self.MetadatosGLobalesCamara1= MetadatosGlobalesIniciales(self.cam1.filename, self.cam1)
            #self.MetadatosGLobalesCamara2= MetadatosGlobalesIniciales(self.cam2.filename, self.cam2)

            #self.cam1.cerrar()
            self.start_time = time.time()
            self.bucle(self.start_time, tiempo, intervalo)
            #self.visualizar(self.cam1, self.videolbl1)
        else:
            print('Faltan Parámetros por rellenar')

    def stop(self):
        self.t_horas= tk.StringVar(self, value='')
        self.t_minutos= tk.StringVar(self, value='')
        self.t_segundos= tk.StringVar(self, value= '')

        self.intervalo_minutos= tk.StringVar(self, value= '' )
        self.intervalo_segundos= tk.StringVar(self, value= '')
        self.cam1.cerrar()

    def bucle_intervalo(self, start_cycle, intervalo):
        print('abriendo bucle')
        if time.time()-start_cycle < intervalo:    
            self.visualizar(self.cam1, self.videolbl1)
            self.after(34,self.visualizar, self.cam1,self.videolbl1)
            self.after(1,self.bucle_intervalo, start_cycle,intervalo)
        else:
            print('cerrando bucle')
            pass

    def bucle(self, start_time, tiempo, intervalo):

        if time.time()- start_time<tiempo:
            self.cam1.crear_salida()
            #self.cam2.crear_salida()

            t1 = CamThread(self.cam1,start_time)
            #t2 = CamThread(self.cam2,start_time)

            t1.start()
            #t2.start()

            start_ciclo = time.time()
            self.bucle_intervalo(start_ciclo, intervalo)

            MetadatosFinalesCamara1= MetadatosGlobalesFinales(t1)
            #MetadatosFinalesCamara2= MetadatosGlobalesFinales(t2)

            self.Promedio_fps1+= MetadatosFinalesCamara1[0]
            #self.Promedio_fps2+=MetadatosFinalesCamara2[0]

            self.Frames1+= MetadatosFinalesCamara1[1]
            #self.Frames2+= MetadatosFinalesCamara2[1]

            t1.stop()
            #t2.stop()
            t1.join()
            #t2.join()

            self.cam1.cerrar_salida()
            #self.cam2.cerrar_salida()
            cv2.destroyAllWindows()
        
            self.after(34, self.bucle, start_time, tiempo,intervalo)
        else:
            self.cam1.cerrar()
            #self.cam2.cerrar()

            self.Promedio_fps1= self.Promedio_fps1/self.Frames1
            #self.Promedio_fps2= self.Promedio_fps2/self.Frames2

            Resumen1= Resumen_final(self.MetadatosGLobalesCamara1 ,self.Promedio_fps1,self.Frames1)
            #Resumen2= Resumen_final(self.MetadatosGLobalesCamara2 ,self.Promedio_fps2,self.Frames2)
            print("Programa finalizado")

    def visualizar(self,cam, lblVideo):

        if cam is not None:
            ret, frame = cam.cap.read()
            if ret == True:
                frame = imutils.resize(frame, width= cam.shape[1])
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                im = Image.fromarray(frame)
                img = ImageTk.PhotoImage(image=im)
                lblVideo.configure(image=img)
                lblVideo.image = img
                #lblVideo.after(34, self.visualizar, cam,lblVideo)
        else:
            lblVideo.image = ""
            cam.cap.release()
    
    #def grabar(self):

    def init_widgets(self): #Aqui iran todos los botones y demas

        """
        Voy a crear un Frame para las etiquetas de tiempo y de intervalos de tiempo
        """

        posicion = {'horas':[0,0], 'minutos':[0,2], 'segundos':[0,4], 'intervalo_min':[1, 0], 'intervalo_s':[1,2],'grabar':[0, 6], 'parar': [1,6]}

        etiquetasFrame= tk.Frame(self)
        etiquetasFrame.configure(background= style.COMPONENT)
        etiquetasFrame.pack(
            side= tk.BOTTOM,
            fill= tk.BOTH,
            expand= True,
        )

        #Textos y etiquetas interactuables (entradas de texto)

        #Primero las de tiempo
        t_horas= tk.Entry(etiquetasFrame,
                          **style.STYLE,
                          textvariable= self.t_horas,
                          width = self.text_entry_width

        ).grid(row= posicion['horas'][0], column= posicion['horas'][1]+1)

        t_minutos= tk.Entry(etiquetasFrame,
                          **style.STYLE,
                          textvariable= self.t_minutos,
                          width = self.text_entry_width

        ).grid(row= posicion['minutos'][0], column=posicion['minutos'][1]+1)
        
        t_segundos= tk.Entry(etiquetasFrame,
                          **style.STYLE,
                          textvariable= self.t_segundos,
                          width = self.text_entry_width
                          

        ).grid(row= posicion['segundos'][0], column=posicion['segundos'][1]+1)

        #Ahora los intervalos
        intervalo_minutos= tk.Entry(etiquetasFrame,
                          **style.STYLE,
                          textvariable= self.intervalo_minutos,
                          width = self.text_entry_width

        ).grid(row= posicion['intervalo_min'][0], column=posicion['intervalo_min'][1]+1)


        intervalo_segundos= tk.Entry(etiquetasFrame,
                          **style.STYLE,
                          textvariable= self.intervalo_segundos,
                          width = self.text_entry_width

        ).grid(row= posicion['intervalo_s'][0], column=posicion['intervalo_s'][1]+1)

        #Textos y etiquetas no interactuables

        #Primero los de tiempo

        texto_horas= tk.Label(etiquetasFrame,
                              text='Horas: ',
                              **style.STYLE

        ).grid(row=posicion['horas'][0],column=posicion['horas'][1])

        texto_minutos= tk.Label(etiquetasFrame,
                              text='Minutos: ',
                              **style.STYLE
                              
        ).grid(row=posicion['minutos'][0],column=posicion['minutos'][1])

        texto_segundos= tk.Label(etiquetasFrame,
                              text='Segundos: ',
                              **style.STYLE
                              
        ).grid(row=posicion['segundos'][0],column=posicion['segundos'][1])

        #Ahora los intervalos

        texto_intervalo_minutos= tk.Label(etiquetasFrame,
                              text='Intervalos en minutos: ',
                              **style.STYLE
                              
        ).grid(row=posicion['intervalo_min'][0],column=posicion['intervalo_min'][1])

        texto__intervalo_sgundos= tk.Label(etiquetasFrame,
                              text='Intervalos en segundos: ',
                              **style.STYLE
                              
        ).grid(row=posicion['intervalo_s'][0],column=posicion['intervalo_s'][1])


        #Botones
        boton_inicio= tk.Button(etiquetasFrame, 
                                text= 'START',
                                command= self.start, 
                                activebackground= style.BACKGROUND ,
                                activeforeground= style.TEXT,
                                **style.STYLE
                                ).grid(row=posicion['grabar'][0], column=posicion['grabar'][1])
        boton_finalizado= tk.Button(etiquetasFrame, 
                                text= 'STOP',
                                command= self.stop, 
                                activebackground= style.BACKGROUND ,
                                activeforeground= style.TEXT,
                                **style.STYLE
                                ).grid(row=posicion['parar'][0], column=posicion['parar'][1])
        
        # Hacemos un Frame superior para los videos
        videoFrame= tk.Frame(self)
        videoFrame.configure(background=style.COMPONENT)
        videoFrame.pack(
            side= tk.TOP,
            fill= tk.BOTH,
            expand= True,
        )

        '''
        Para los videos vamos a necesitar una Label que es lo que rellenaremos con las
        sucesivas imagenes
        '''

        self.videolbl1= tk.Label(videoFrame, **style.STYLE)
        self.videolbl1.grid(column= 0, row= 0, columnspan= 2)
        self.videolbl2= tk.Label(videoFrame, **style.STYLE)
        self.videolbl2.grid(column= 1, row= 0, columnspan= 2)

class Monitor(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.configure(background= style.BACKGROUND)
        self.controller= controller
