# Librerias necesarias para recibir audio por udp
import socket
import pyaudio
#Libreria threading para usar hilos
from threading import Thread

# Variables del audio
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Número de puerto
PORT = 5000

def transmitter(HOST):
	# Conectamos al que nos envia los datos
    transmisor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Crear variable de pyaudio
    p = pyaudio.PyAudio()
    # Creamos otra variable para trabajar con pyaudio
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    print("*_>recording")
    # Se va leyendo el audio miemtras se recibe
    while True:
    	data = stream.read(CHUNK)
    	transmisor.sendto(data, (HOST, PORT)) 

    # Cerramos el audio terminamos con la libreria pyaudio
    # Y cerramos el trabajo con el puerto
    # stream.stop_stream()
    # stream.close()
    # p.terminate()
    # s.close()   

def receiver():
    # Recibimos audio usando udp
    recibir = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Socket escucha por el puerto indicado
    recibir.bind(("0.0.0.0", PORT))

    # Creamos una variable para pyaudio y despues
    # Creamos otra necesaria para el envio de audio
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
		            channels=CHANNELS,
		            rate=RATE,
		            output=True,
		            frames_per_buffer=CHUNK)

    # Iniciamos el envio de audio

    while True:
        data, addr = recibir.recvfrom(CHUNK*2)
        stream.write(data)

# Creamos dos threads para recibir y transmitir simultáneamente
def main():

	Tr = Thread(target=receiver)
	Tr.daemon = True
	Tr.start()

	HOST = input("Introduce una dirección IP\n")
   
	Tt = Thread(target=transmitter, args=(HOST,))
	Tt.daemon = True
	Tt.start()
	input("Presiona enter para terminar con el streaming de audio")
if __name__ == '__main__':
	main()
