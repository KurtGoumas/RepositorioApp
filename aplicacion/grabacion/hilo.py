'''
from threading import Thread
#from aplicacion.grabacion.control import *
#from aplicacion.grabacion.Camara_arreglo import Camara
import cv2   
import time


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
'''