import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

from threading import Thread
from PIL import Image, ImageTk
import imutils
import time
import cv2
import os

from aplicacion.constantes import style
from aplicacion.grabacion.Camara_arreglo import Camara
from aplicacion.grabacion.control import *
from aplicacion.lectura import lectura, movimiento

"""
En la pantalla de Home podremos previsualizar y grabar.

En la pantalla de procesado tomaremos videos ya grabados y los usaremos para obtener lo
que necesitemos.
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
        self.fps_real= 0

    def run(self):
        self.frame_anterior= time.time()
        while self.running:
            ret, frame = self.cam.cap.read()
            if ret:
                self.Contador_Frames += 1
                self.frame = frame
                self.cam.out.write(frame)
                #self.cam.out.write(frame[200:800, 500:1300])#Aqui lo que escribimos es el frame recortado para que no ocupe tanto
                self.frame_actual= time.time()
                if self.frame_actual-self.frame_anterior== 0:
                    sel.fps_real= 0
                else:
                    self.fps_real= 1/(self.frame_actual-self.frame_anterior)
                self.Prom_fps+= self.fps_real
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

        try: 
            self.indices= listar_indices()
            self.cam1= Camara(self.indices[0])
            self.cam2= Camara(self.indices[1])

        except(IndexError, RuntimeError):#Por si no estan las dos camara que pase a procesado
            self.after(1,self.Cambiar_a_Procesado)
            return

        self.previsualizacion= True #Esto es para la previsualizacion

        self.Promedio_fps1= 0
        self.Promedio_fps2= 0
        self.Frames1= 0
        self.Frames2= 0

        #Todo lo relativo a los metadatos

        self.MetadatosGLobalesCamara1= None
        self.MetadatosGLobalesCamara2= None

        #Los valores de las horas, minutos y segundos y sus intervalos

        self.t_horas= tk.IntVar(self,value= 0)
        self.t_minutos= tk.IntVar(self, value= 1)
        self.t_segundos= tk.IntVar(self, value= 0)

        self.intervalo_minutos= tk.IntVar(self, value= 0 )
        self.intervalo_segundos= tk.IntVar(self, value= 20)

        #Nombre de extra de los videos

        self.nombre_prefijo= tk.StringVar(self, value= '')

        self.text_entry_width = 10

        style.aplicar_tema_ttk()#Configura el estilo oscuro de las barras de progreso (ttk)
        self.init_widgets()

        #Barra de progreso
        self.progreso_id= None

    #Funciones que gestionan el bucle

    def start(self): #Al pulsar START, guarda los  tiempos e inicia la grabacion

        """
        Vamos a hacer una previsualizacion expres antes de todo
        """
        self.previsualizar()

        horas= self.t_horas.get()
        minutos= self.t_minutos.get()
        segundos= self.t_segundos.get()

        intervalo_minutos= self.intervalo_minutos.get()
        intervalo_segundos= self.intervalo_segundos.get()
        if horas!= 0 or minutos!= 0 or segundos!= 0:

            tiempo= horas*3600 + minutos*60 + segundos
            intervalo= intervalo_minutos*60 + intervalo_segundos
            if intervalo== 0:
                intervalo= tiempo

            #Activamos la camara y lo dejamos todo listo para grabar

            self.cam1.preparar()
            self.cam2.preparar()

            self.cam1.activar()
            self.cam2.activar()

            self.MetadatosGLobalesCamara1= MetadatosGlobalesIniciales(self.cam1.filename, self.cam1)
            self.MetadatosGLobalesCamara2= MetadatosGlobalesIniciales(self.cam2.filename, self.cam2)

            self.previsualizacion= False #Para acabar la previsualizacion

            start_time= time.time()
            self.bucle(start_time, tiempo, intervalo)
            self.progreso(self.barra1, tiempo, start_time)
            
        else:
            print('Faltan Parámetros por rellenar')

    def stop(self):#Al pulsar STOP resetea los tiempos y cierra las camaras, rompiendo el bucle

        """
        Primero vamos a cerrar ambas camaras
        """
        self.cam1.cerrar()
        self.cam2.cerrar()

    def bucle(self, start_time, tiempo, intervalo):#Este es el bucle grande donde se crean hilos y salidas

        if time.time()- start_time<tiempo:
            self.cam1.crear_salida(prefijo= self.nombre_prefijo.get())
            self.cam2.crear_salida(prefijo= self.nombre_prefijo.get())

            t1 = CamThread(self.cam1,start_time)
            t2 = CamThread(self.cam2,start_time)

            t1.start()
            t2.start()

            #start_ciclo = time.time()
            
            self.after(1000*intervalo, self.salidas, start_time, tiempo, intervalo, t1, t2)#t2 para dos camaras

        else:
            self.stop()

            self.Promedio_fps1= self.Promedio_fps1/self.Frames1
            self.Promedio_fps2= self.Promedio_fps2/self.Frames2

            Resumen1= Resumen_final(self.MetadatosGLobalesCamara1 ,self.Promedio_fps1,self.Frames1)
            Resumen2= Resumen_final(self.MetadatosGLobalesCamara2 ,self.Promedio_fps2,self.Frames2)
            print("Programa finalizado")
            print("Restituyendo parametros")

            """
            Ahora restituimos todo a como estaba al inicio del programa
            """

            #Restituimos las camaras

            self.indices= listar_indices()
            self.cam1= Camara(self.indices[0])
            self.cam2= Camara(self.indices[1])

            #Restituimos los archivos de metadatos

            self.Promedio_fps1= 0
            self.Promedio_fps2= 0
            self.Frames1= 0
            self.Frames2= 0

            self.MetadatosGLobalesCamara1= None
            self.MetadatosGLobalesCamara2= None

            #Permitimos de nuevo la visualizacion

            self.previsualizacion= True

            #Reiniciamos la barra de progreso

            if self.progreso_id is not None:
                self.after_cancel(self.progreso_id)
                self.progreso_id = None

            self.barra1.config({'value': 0})
            self.barra1.update()

            #self.barra2.config({'value': 0})
            #self.barra2.update()

            print('Parametros restituidos')

    def salidas(self, start_time, tiempo, intervalo, t1, t2):#Aqui hay que añadirle t2 cuando metamos dos camaras
            MetadatosFinalesCamara1= MetadatosGlobalesFinales(t1)
            MetadatosFinalesCamara2= MetadatosGlobalesFinales(t2)

            self.Promedio_fps1+= MetadatosFinalesCamara1[0]
            self.Promedio_fps2+=MetadatosFinalesCamara2[0]

            self.Frames1+= MetadatosFinalesCamara1[1]
            self.Frames2+= MetadatosFinalesCamara2[1]

            t1.stop()
            t2.stop()
            t1.join()
            t2.join()

            self.cam1.cerrar_salida()
            self.cam2.cerrar_salida()
            cv2.destroyAllWindows()

            self.bucle(start_time, tiempo, intervalo)

    def visualizar(self,cam, lblVideo):#Funcion para ver los videos en pantalla

        if cam is not None and self.previsualizacion:
            ret, frame = cam.cap.read()
            if ret == True:
                frame = imutils.resize(frame, width= 640)#Redimensionamos para que la previsualizacion se vea bien
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                im = Image.fromarray(frame)
                img = ImageTk.PhotoImage(image=im)
                lblVideo.configure(image=img)
                lblVideo.image = img
                lblVideo.after(10, self.visualizar, cam,lblVideo)#A lo mejor habria que subir el after a 33
            else:
                lblVideo.image = ""
                cam.cap.release()
    
    def previsualizar(self):#Funcion que comandara el boton de previsualizado

        self.cam1.preparar_previsualizacion()
        self.cam2.preparar_previsualizacion()

        self.cam1.activar()
        self.cam2.activar()

        self.visualizar(self.cam1, self.videolbl1)
        self.visualizar(self.cam2,self.videolbl2)

    def progreso(self, barra1, tiempo, start_time):#Habra que añadir seguna barra cuando haya dos camaras
            
        barra1.config({'value': (time.time()-start_time)/tiempo *100})
        barra1.update()

        self.progreso_id= barra1.after(10, self.progreso, barra1, tiempo, start_time)

    #Funciones de los botones que cambian parametros de la camara
    
    def Exp_up(self):
        self.cam1.exp_up()
        self.cam2.exp_up()

    def Exp_down(self):
        self.cam1.exp_down()
        self.cam2.exp_down()

    def Gain_up(self):
        self.cam1.gain_up()
        self.cam2.gain_up()
    
    def Gain_down(self):
        self.cam1.gain_down()
        self.cam2.gain_down()
    
    def Cambiar_a_Procesado(self):
        self.controller.show_frame(Procesado)

    #Pequeño ayudante puramente visual: crea una fila "etiqueta + entrada" dentro
    #de una sección, sin tocar ninguna variable ni lógica de ejecución.
    def _fila_entrada(self, contenedor, etiqueta, variable, fila):
        tk.Label(contenedor, text=etiqueta, **style.STYLE).grid(
            row=fila, column=0, sticky=tk.W, padx=(0, style.PAD), pady=4
        )
        tk.Entry(contenedor,
                 textvariable=variable,
                 width=self.text_entry_width,
                 **style.STYLE_ENTRY
                 ).grid(row=fila, column=1, sticky=tk.W, pady=4)

    def init_widgets(self): #Aqui iran todos los botones y demas

        """
        Disposición visual de la pantalla de grabación, organizada en secciones:
        - Cabecera con el título de la pantalla y el acceso a Procesado
        - Vista previa de las dos cámaras
        - Panel inferior con: duración, intervalos, ajustes de cámara,
          barras de progreso y acciones principales (previsualizar/iniciar/detener)

        Ninguna variable de control ni función de ejecución cambia respecto al original,
        solo su disposición y estilo.
        """

        PAD = style.PAD

        # ---------------- Cabecera ----------------
        header= tk.Frame(self, bg= style.BACKGROUND)
        header.pack(side= tk.TOP, fill= tk.X, padx= PAD*2, pady= (PAD*2, PAD))

        tk.Label(header, text= 'Grabación', **style.STYLE_TITLE).pack(side= tk.LEFT)

        tk.Button(header,
                  text= 'Ir a Procesado',
                  command= self.Cambiar_a_Procesado,
                  **style.STYLE_BOTON
                  ).pack(side= tk.RIGHT)

        # ---------------- Vista previa de cámaras ----------------
        videoFrame= tk.Frame(self, bg= style.BACKGROUND)
        videoFrame.pack(side= tk.TOP, fill= tk.BOTH, expand= True, padx= PAD*2, pady= (0, PAD))

        videoFrame.grid_columnconfigure(0, weight= 1)
        videoFrame.grid_columnconfigure(1, weight= 1)
        videoFrame.grid_rowconfigure(1, weight= 1)

        tk.Label(videoFrame, text= 'Cámara 1', **style.STYLE_SECTION_TITLE).grid(
            row= 0, column= 0, sticky= tk.W, pady= (0, 4)
        )
        tk.Label(videoFrame, text= 'Cámara 2', **style.STYLE_SECTION_TITLE).grid(
            row= 0, column= 1, sticky= tk.W, pady= (0, 4)
        )

        cam1Wrap= tk.Frame(videoFrame, bg= style.SURFACE, highlightbackground= style.BORDER, highlightthickness= 1)
        cam1Wrap.grid(row= 1, column= 0, sticky= tk.NSEW, padx= (0, PAD//2))
        cam2Wrap= tk.Frame(videoFrame, bg= style.SURFACE, highlightbackground= style.BORDER, highlightthickness= 1)
        cam2Wrap.grid(row= 1, column= 1, sticky= tk.NSEW, padx= (PAD//2, 0))

        #Los Label donde se pintan los fotogramas: mismos nombres que usa previsualizar()/visualizar()
        self.videolbl1= tk.Label(cam1Wrap, bg= style.SURFACE)
        self.videolbl1.pack(fill= tk.BOTH, expand= True, padx= 2, pady= 2)
        self.videolbl2= tk.Label(cam2Wrap, bg= style.SURFACE)
        self.videolbl2.pack(fill= tk.BOTH, expand= True, padx= 2, pady= 2)

        # ---------------- Panel inferior ----------------
        panel= tk.Frame(self, bg= style.BACKGROUND)
        panel.pack(side= tk.BOTTOM, fill= tk.X, padx= PAD*2, pady= (0, PAD*2))
        panel.grid_columnconfigure(0, weight= 1)
        panel.grid_columnconfigure(1, weight= 1)
        panel.grid_columnconfigure(2, weight= 1)

        # -- Duración de la grabación --
        tiempoBox= tk.LabelFrame(panel, text= 'Duración de la grabación', **style.STYLE_LABELFRAME)
        tiempoBox.grid(row= 0, column= 0, sticky= tk.NSEW, padx= (0, PAD))

        self._fila_entrada(tiempoBox, 'Horas', self.t_horas, 0)
        self._fila_entrada(tiempoBox, 'Minutos', self.t_minutos, 1)
        self._fila_entrada(tiempoBox, 'Segundos', self.t_segundos, 2)

        # -- Intervalo entre archivos y nombre --
        intervaloBox= tk.LabelFrame(panel, text= 'Intervalo y nombre del archivo', **style.STYLE_LABELFRAME)
        intervaloBox.grid(row= 0, column= 1, sticky= tk.NSEW, padx= PAD)

        self._fila_entrada(intervaloBox, 'Intervalo (min)', self.intervalo_minutos, 0)
        self._fila_entrada(intervaloBox, 'Intervalo (s)', self.intervalo_segundos, 1)
        self._fila_entrada(intervaloBox, 'Prefijo del vídeo', self.nombre_prefijo, 2)

        # -- Ajustes de cámara --
        ajustesBox= tk.LabelFrame(panel, text= 'Ajustes de cámara', **style.STYLE_LABELFRAME)
        ajustesBox.grid(row= 0, column= 2, sticky= tk.NSEW, padx= (PAD, 0))

        tk.Label(ajustesBox, text= 'Exposición', **style.STYLE).grid(row= 0, column= 0, sticky= tk.W, pady= 4)
        tk.Button(ajustesBox, text= '–', command= self.Exp_down, **style.STYLE_BOTON).grid(row= 0, column= 1, padx= 2)
        tk.Button(ajustesBox, text= '+', command= self.Exp_up, **style.STYLE_BOTON).grid(row= 0, column= 2, padx= 2)

        tk.Label(ajustesBox, text= 'Ganancia', **style.STYLE).grid(row= 1, column= 0, sticky= tk.W, pady= 4)
        tk.Button(ajustesBox, text= '–', command= self.Gain_down, **style.STYLE_BOTON).grid(row= 1, column= 1, padx= 2)
        tk.Button(ajustesBox, text= '+', command= self.Gain_up, **style.STYLE_BOTON).grid(row= 1, column= 2, padx= 2)

        # -- Barras de progreso --
        progresoBox= tk.Frame(panel, bg= style.BACKGROUND)
        progresoBox.grid(row= 1, column= 0, columnspan= 3, sticky= tk.EW, pady= (PAD, 0))
        progresoBox.grid_columnconfigure(0, weight= 1)
        progresoBox.grid_columnconfigure(1, weight= 1)

        tk.Label(progresoBox, text= 'Progreso cámara 1', **style.STYLE_MUTED_ON_BG).grid(
            row= 0, column= 0, sticky= tk.W
        )
        tk.Label(progresoBox, text= 'Progreso cámara 2', **style.STYLE_MUTED_ON_BG).grid(
            row= 0, column= 1, sticky= tk.W, padx= (PAD, 0)
        )

        #Mismas barras de progreso que usa progreso(); solo cambia estilo y disposición
        self.barra1= ttk.Progressbar(progresoBox, style= 'Moderna.Horizontal.TProgressbar')
        self.barra1.grid(row= 1, column= 0, sticky= tk.EW, pady= (2, 0))

        self.barra2= ttk.Progressbar(progresoBox, style= 'Moderna.Horizontal.TProgressbar')
        self.barra2.grid(row= 1, column= 1, sticky= tk.EW, padx= (PAD, 0), pady= (2, 0))

        # -- Acciones principales --
        accionesBox= tk.Frame(panel, bg= style.BACKGROUND)
        accionesBox.grid(row= 2, column= 0, columnspan= 3, sticky= tk.EW, pady= (PAD, 0))

        tk.Button(accionesBox,
                  text= 'PREVISUALIZAR',
                  command= self.previsualizar,
                  **style.STYLE_BOTON
                  ).pack(side= tk.LEFT, padx= (0, PAD))

        tk.Button(accionesBox,
                  text= 'INICIAR GRABACIÓN',
                  command= self.start,
                  **style.STYLE_BOTON_EXITO
                  ).pack(side= tk.LEFT, padx= PAD)

        tk.Button(accionesBox,
                  text= 'DETENER',
                  command= self.stop,
                  **style.STYLE_BOTON_PELIGRO
                  ).pack(side= tk.LEFT, padx= PAD)

class Procesado(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.configure(background= style.BACKGROUND)
        self.controller= controller

        #Todos los valores de la configuracion del dispositivo experimental

        self.xc1= tk.DoubleVar(self, value= '0.5')
        self.yc1= tk.DoubleVar(self, value= '1.86')
        self.zc1= tk.DoubleVar(self, value= '0.43')

        self.xc2= tk.DoubleVar(self, value= '1.86')
        self.yc2= tk.DoubleVar(self, value= '0.5')
        self.zc2= tk.DoubleVar(self, value= '0.43')

        self.Lx= tk.DoubleVar(self, value= '1')
        self.Ly= tk.DoubleVar(self, value= '1')

        self.N_Objetos= tk.IntVar(self, value= '1')

        self.peso_mov= tk.DoubleVar(self, value= '100')
        self.peso_3d= tk.DoubleVar(self, value= 1)

        self.h_start= tk.IntVar(self, value= 350)
        self.h_last= tk.IntVar(self, value= 850)

        self.w_start= tk.IntVar(self, value= 550)
        self.w_last= tk.IntVar(self, value= 1350)

        self.text_entry_width = 10

        #Para poder introducir todos los widgets
        self.init_widgets()


    #Funciones que gestionan el bucle

    def leer_y_procesar_videos(self):

        """
        Esta funcion que es una que nos ayudara para subir videos y que los
        empiece a procesar.
        Primero vamos a pedir que se nos entreguen videos para procesar.
        Una vez los tenemos, en el if estamos creando un hilo, similar a lo que haciamos
        con las camaras, para que esta tarea no nos ocupe el bucle principal

        Una nota importante es que si quieres luego meter una barra de progreso tienes
        que ir con cuidado y usar un self.after() para conectar el hilo con el principal

        Importante, cuando decimos Nombre, es un archivo sin su extencion, cuando decimos archivo 
        estamos diciendo que va con extension
        """

        archivos= filedialog.askopenfilenames(
            title= "Selecciona los vídeos",
            filetypes= [("Archivos de vídeo","*.mp4")]
        )

        if archivos:
            t= Thread(target= self.procesar, args= (archivos,),daemon= True)
            t.start()#el hilo deberia detenerse al acabarse la funcion procesar, ya veremos

    def procesar(self, archivos):

        """
        Esta funcion esta subordinada a la de leer_y_procesar_videos. 
        Basicamente, lo que escribamos aqui va a ser invocado por la funcion mas grande y
        repetido tantas veces como videos carguemos a la aplicacion
        De tal forma que no seran devueltas las listas de centroides.

        Tendremos una lista para cada camara, luego habra que usar otra funcion para llamar
        a Union_camaras para que junte las trayectorias y por ultimo la que nos las pinte
        """

        print('Entrando a procesar los vídeos')
        self.procesado= [] #Es una lista que rellenaremos con arrays de centroides
        #Uno del primer video y otro del segundo.

        Nombres=[]#Lista de los nombres sin extension

        for archivo in archivos:

            Nombre= os.path.splitext(archivo)[0]
            Nombres.append(Nombre)

            restado= lectura.leer(archivo,self.h_start.get(), 
                                            self.h_last.get(), self.w_start.get(),
                                            self.w_last.get())
            centroides_validos= lectura.centroides(restado)
            
            self.procesado.append(centroides_validos)
            del restado #Liberamos la celda de memoria de restado para que no pete 
        self.procesado= np.array(self.procesado, dtype= object)

        """
        Vale, aqui tenemos los centroides de una camara y de la otra con Union_camaras vamos a 
        conseguir un unico array de centroides
        """

        cent_x= self.procesado[0]
        print('x :',cent_x[:20])
        t_x= lectura.Tiempos_csv(Nombres[0])#Necesitamos los tiempos para la interpolacion en Union_camaras
        
        
        cent_y= self.procesado[1]
        print('y :',cent_y[:20])
        t_y= lectura.Tiempos_csv(Nombres[1])

        print('Uniendo cámaras')
        posiciones, tiempos= lectura.Union_camaras(cent_x,cent_y, t_x, t_y, self.N_Objetos.get(),self.peso_mov.get(),self.xc1.get(),self.yc1.get(),self.zc1.get(),self.xc2.get(),self.yc2.get(),self.zc2.get(),self.Lx.get(),self.Ly.get(), self.h_last.get(), self.w_last.get())
        print('Cámaras Unidas')
        """
        Nos falta solo sacar las imagenes usando posiciones y tiempos
        """

        resultados= movimiento.Movimiento(Nombres[0], posiciones, tiempos)#Daria igual que cogiera Nombres[0] o [1], porque lo voy a cortar
        print('Todo genial')

        return True
    
    def leer_y_procesar_csv(self):

        """
        A esta funcion le podremos pasar varios archivos csv que contengan en su interior
        posiciones y tiempos.

        Con ellos simplemente habra que leerlos y pintar las trayectorias con lo que nos den.
        """
        
        archivos= filedialog.askopenfilenames(
        title= "Selecciona los archivos de datos",
        filetypes= [("Archivos de datos","*.csv")]
        )

        if archivos:
            t= Thread(target= self.procesar_csv, args= (archivos,),daemon= True)
            t.start()#el hilo deberia detenerse al acabarse la funcion procesar_csv, ya veremos

        return True
    
    def procesar_csv(self, archivos):

        """
        En esta funcion auxiliar de leer_y_procesar_csv vamos a tomar cada uno de los archivos que 
        se pasen y extraeremos su posicion y tiempo para luego obtener las graficas pertinentes
        """

        for archivo in archivos:
            
            Nombre= os.path.splitext(archivo)[0] #para luego usarlo en la llamada a la creacion de la grafica
            """
            Lo primero que queremos es disponer de las posiciones y el tiempo en su forma de array
            para asi ya trabajar con ellos
            """
            pos, t, v, a= movimiento.Obtener_p_t_v_a(Nombre)

            resultados= movimiento.Movimiento_csv(Nombre, pos, t, v, a)     

    #Pequeño ayudante puramente visual, igual que el de Home: etiqueta + entrada en una fila
    def _fila_entrada(self, contenedor, etiqueta, variable, fila, columna=0):
        tk.Label(contenedor, text=etiqueta, **style.STYLE).grid(
            row=fila, column=columna, sticky=tk.W, padx=(0, 6), pady=4
        )
        tk.Entry(contenedor,
                 textvariable=variable,
                 width=self.text_entry_width,
                 **style.STYLE_ENTRY
                 ).grid(row=fila, column=columna+1, sticky=tk.W, padx=(0, 18), pady=4)

    def init_widgets(self): #Aqui van los botones y demas

        """
        Disposición visual de la pantalla de Procesado, organizada en secciones:
        - Cabecera con el título de la pantalla
        - Carga de datos (vídeos o csv ya procesados)
        - Parámetros de configuración del experimento, agrupados por tema:
          posición de las cámaras, dimensiones del tanque, detección de objetos
          y recorte de la imagen

        Ninguna variable de control ni función de ejecución cambia respecto al original,
        solo su disposición y estilo.
        """

        PAD = style.PAD

        # ---------------- Cabecera ----------------
        header= tk.Frame(self, bg= style.BACKGROUND)
        header.pack(side= tk.TOP, fill= tk.X, padx= PAD*2, pady= (PAD*2, PAD))

        tk.Label(header, text= 'Procesado', **style.STYLE_TITLE).pack(side= tk.LEFT)

        # ---------------- Carga de datos ----------------
        cargaBox= tk.LabelFrame(self, text= 'Cargar datos', **style.STYLE_LABELFRAME)
        cargaBox.pack(side= tk.TOP, fill= tk.X, padx= PAD*2, pady= (0, PAD))

        tk.Button(cargaBox,
                  text= 'Seleccionar Vídeos',
                  command= self.leer_y_procesar_videos,
                  **style.STYLE_BOTON_PRIMARIO
                  ).pack(side= tk.LEFT, padx= (0, PAD))

        tk.Button(cargaBox,
                  text= 'Seleccionar Archivos CSV',
                  command= self.leer_y_procesar_csv,
                  **style.STYLE_BOTON
                  ).pack(side= tk.LEFT)

        # ---------------- Parámetros del experimento ----------------
        paramFrame= tk.Frame(self, bg= style.BACKGROUND)
        paramFrame.pack(side= tk.TOP, fill= tk.BOTH, expand= True, padx= PAD*2, pady= (0, PAD*2))
        paramFrame.grid_columnconfigure(0, weight= 1)
        paramFrame.grid_columnconfigure(1, weight= 1)

        # -- Posición de las cámaras --
        camarasBox= tk.LabelFrame(paramFrame, text= 'Posición de las cámaras', **style.STYLE_LABELFRAME)
        camarasBox.grid(row= 0, column= 0, sticky= tk.NSEW, padx= (0, PAD//2), pady= (0, PAD))

        tk.Label(camarasBox, text= 'Cámara 1', **style.STYLE).grid(row= 0, column= 0, columnspan= 6, sticky= tk.W, pady= (0, 4))
        self._fila_entrada(camarasBox, 'x', self.xc1, 1, 0)
        self._fila_entrada(camarasBox, 'y', self.yc1, 1, 2)
        self._fila_entrada(camarasBox, 'z', self.zc1, 1, 4)

        tk.Label(camarasBox, text= 'Cámara 2', **style.STYLE).grid(row= 2, column= 0, columnspan= 6, sticky= tk.W, pady= (10, 4))
        self._fila_entrada(camarasBox, 'x', self.xc2, 3, 0)
        self._fila_entrada(camarasBox, 'y', self.yc2, 3, 2)
        self._fila_entrada(camarasBox, 'z', self.zc2, 3, 4)

        # -- Dimensiones del tanque --
        tanqueBox= tk.LabelFrame(paramFrame, text= 'Dimensiones del tanque', **style.STYLE_LABELFRAME)
        tanqueBox.grid(row= 0, column= 1, sticky= tk.NSEW, padx= (PAD//2, 0), pady= (0, PAD))

        self._fila_entrada(tanqueBox, 'Lx', self.Lx, 0)
        self._fila_entrada(tanqueBox, 'Ly', self.Ly, 1)

        # -- Detección de objetos --
        deteccionBox= tk.LabelFrame(paramFrame, text= 'Detección de objetos', **style.STYLE_LABELFRAME)
        deteccionBox.grid(row= 1, column= 0, sticky= tk.NSEW, padx= (0, PAD//2), pady= (0, PAD))

        self._fila_entrada(deteccionBox, 'Número de objetos', self.N_Objetos, 0)
        self._fila_entrada(deteccionBox, 'Peso del movimiento (0-100)', self.peso_mov, 1)

        # -- Recorte de la imagen --
        recorteBox= tk.LabelFrame(paramFrame, text= 'Recorte de la imagen', **style.STYLE_LABELFRAME)
        recorteBox.grid(row= 1, column= 1, sticky= tk.NSEW, padx= (PAD//2, 0), pady= (0, PAD))

        self._fila_entrada(recorteBox, 'Ancho inicial (w_s)', self.w_start, 0)
        self._fila_entrada(recorteBox, 'Ancho final (w_l)', self.w_last, 1)
        self._fila_entrada(recorteBox, 'Alto inicial (h_s)', self.h_start, 2)
        self._fila_entrada(recorteBox, 'Alto final (h_l)', self.h_last, 3)

