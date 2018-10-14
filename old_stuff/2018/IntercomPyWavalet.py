#Graba y recibe audio simultaneamente con UDP y PyAudio
#Usando dos hilos

#Libreria PyAudio
import pyaudio
# Libreria socket para poder mandar data con conexion udp
import socket
#Libreria threading para usar hilos
from threading import Thread
#Libreria numpy utilizamos para crear array
import numpy as np
#Libreria pywt para utilizar wavelet transform
import pywt as wt
#Libreria ctypes utilizamos solo c_int32
from ctypes import c_int32
import time


FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
VALORES = 32
ITERACIONESDWT = 9
CHUNK = 1024


#Transformada obtiene un array de datos. Realiza la transformada y separa los datos. Cada bloque 32 bits
def Transformada(frames):
    coeffs = wt.wavedec(frames, 'db1', level=ITERACIONESDWT)
    transformada = []
    for i in coeffs:
        for e in i:
            transformada.append(int(round(e)))

    planos = {}
    for plano in range(0, 32):
        comp = 31-plano

        n = 0
        bloque = 0
        planos[plano] = []

        for entero in transformada:
            if plano == 0:
                temp = ((entero & (2**comp)) >> comp)
            else:
                temp = ((abs(entero) & (2**comp)) >> comp)
            bloque += (temp << (31 - n))
            n = n+1
            if n == 32:
                planos[plano].append(bloque)
                n = 0
                bloque = 0
    return planos

#deTransformada
def deTransformada(diciPlanos):
    destransformacion = []
    for plano in diciPlanos:
        n = 31-plano
        if plano == 0:
            for bloque in diciPlanos[plano]:
                for bit in reversed(range(0, 32)):
                    temp = ((bloque & (2**bit)) >> bit)
                    if temp == 1:
                        temp = c_int32(-1)
                    else:
                        temp = c_int32(temp << n)

                    destransformacion.append(temp.value)
        else:
            cuentaBloque = 0
            for bloque in diciPlanos[plano]:
                for bit in reversed(range(0, 32)):
                    temp = ((bloque & (2**bit)) >> bit)
                    temp = temp << n
                    if destransformacion[cuentaBloque] >= 0:
                        destransformacion[cuentaBloque] += temp
                    else:
                        destransformacion[cuentaBloque] -= temp
                    cuentaBloque += 1
    destransformacion = list(map(sumaUnoNegativos, destransformacion))
    coeffs = []
    stack = 0
    w = wt.Wavelet('db1')
    values = wt.dwt_max_level(len(destransformacion), w) - ITERACIONESDWT
    for x in range(0, ITERACIONESDWT+1):
        trick = ((2 ** (values)) * (2 ** x))
        x = np.array(destransformacion[stack:trick])
        coeffs.append(x)
        stack = trick
    destransformacion = wt.waverec(coeffs, 'db1')
    print(list(map(len, coeffs)))
    destransformacion = destransformacion.tolist()
    destransformacion = list(map(round, destransformacion))
    return destransformacion

#Valor negativo sumo 1
def sumaUnoNegativos(x):
    if x < 0:
        return x+1
    return x

#Guardamos los datos en un array
def arraySecuencial(data):
    frames = []
    for i in range(0, len(data)):
        frames.append(data[i])
    return frames

#Iniciamos dos hilos: un hilo para reproducir la entrada de udp y otro hilo para enviar grabacion udp
#Solicitamos direccion IP del host
def main():
   
	p = pyaudio.PyAudio()
	stream = p.open(format=FORMAT,
		            channels=CHANNELS,
		            rate=RATE,
		            input=True,
		            frames_per_buffer=CHUNK)

	stream1 = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True,
					frames_per_buffer=CHUNK)

    #He puesto el bucle para que se vaya leyendo, aplicando la transformada, detransformada y reproduciendo después
    #Sin hacer lo de "un único chunk", si no se complicaría bastante. No se si esto satisface el issue

	while True:
		data = stream.read(CHUNK)
		frames = arraySecuencial(data)
		diciPlanos = Transformada(frames)
		print("\nResultado: ")
		dest = deTransformada(diciPlanos)
		stream1.write(data)

if __name__ == '__main__':
    main()
