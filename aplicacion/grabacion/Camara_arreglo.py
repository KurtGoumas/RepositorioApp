import cv2
import datetime as dt
import time
import os

class Camara:
    def __init__(self, indice):
        self.indice = indice
        self.winname = f'Imagen cámara [{self.indice}]'
        self.cap = cv2.VideoCapture(self.indice)
        self.out = None
        self.preparada = False
        self.filename= None
        self.activa = False
        self.shape = None
        self.fps= self.cap.get(cv2.CAP_PROP_FPS)
        self.fourcc= None #El codec
        self.exposicion= self.cap.get(cv2.CAP_PROP_EXPOSURE)
        self.ganancia= self.cap.get(cv2.CAP_PROP_GAIN)

    def preparar(self):
        """Captura un primer frame válido y prepara el VideoWriter."""
        if not self.cap.isOpened():
            raise RuntimeError(f"No se pudo abrir cámara {self.indice+1}")

        ret, frame = self.cap.read()
        while not ret:
            time.sleep(0.05)
            ret, frame = self.cap.read()

        self.shape = frame.shape
        self.out = self.crear_salida()
        self.preparada = True
        print(f"Cámara {self.indice+1} preparada")

    def crear_salida(self):
        h, w, _ = self.shape
        if not os.path.exists('./videos'):
            os.makedirs('./videos')
        fecha = dt.datetime.now()
        self.filename = f'videos/{fecha.day}-{fecha.month}-{fecha.year}-{fecha.hour}-{fecha.minute}-{fecha.second}_{self.indice}'
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.fps= self.cap.get(cv2.CAP_PROP_FPS)
        self.out= cv2.VideoWriter(self.filename + '.mp4', self.fourcc, self.fps, (w, h))
        return self.out

    def activar(self):
        self.activa = True

    def grabar_frame(self):
        """Captura y guarda un frame, muestra ventana si se desea."""
        ret, frame = self.cap.read()
        if not ret:
            return False
        self.out.write(frame)
        cv2.imshow(self.winname, frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC para cerrar
            self.activa = False
        return True

    def cerrar(self):
        print("Cerrando cámara")
        if self.out:
            self.out.release()
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
    
    def cerrar_salida(self):#Esto sólo cierra la salida y permite crear una nueva
        print('Cerrando vídeo')
        if self.out:
            self.out.release
        cv2.destroyAllWindows()

    def exp_up(self):
        self.exposicion+= 0.5
        self.cap.set(cv2.CAP_PROP_EXPOSURE, self.exposicion)

    def exp_down(self):
        self.exposicion-= 0.5
        self.cap.set(cv2.CAP_PROP_EXPOSURE, self.exposicion)

    def gain_up(self):
        self.ganancia+=1
        self.cap.set(cv2.CAP_PROP_GAIN,self.ganancia)

    def gain_down(self):
        self.ganancia-=1
        self.cap.set(cv2.CAP_PROP_GAIN,self.ganancia)
    