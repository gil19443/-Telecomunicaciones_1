#Universidad del Valle de Guatemala
#Sistemas de telecomunicaciones 1
#Propagación de prefijos de internet
#Autor: Carlos Gil 19443
#Autor: Carlos Cuellar 19275
#Guatemala, 11 de octubre del 2022


from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtWidgets
from PyQt5 import QtCore, QtGui, QtWidgets,QtWebEngineWidgets
import os
from PyQt5.QtGui import QPainter, QPen, QPixmap, QColor
import threading
import time
import sys
import math
import requests
import numpy as np
import socket
from webbrowser import * #esqueleto de la interfaz utilizada
class browser (QtWidgets.QMainWindow, Ui_MainWindow,QWidget):
	def __init__ (self):
		super(browser,self).__init__()
		self.setupUi(self)
		self.pushButton.clicked.connect(self.search) #conexion de los botones para buscar o resolver con el dns
		self.pushButton_2.clicked.connect(self.dns)
	def search(self):
		sock1=socket.socket(socket.AF_INET, socket.SOCK_STREAM) #se crea el socket
		#Esta variable tendría que venir de la interfaz
		addr=self.textEdit.toPlainText() #se relaciona el textEdit con la direccion que se trabajara
		#http://gaia.cs.umass.edu/search.html
		 #Se elimina el http:// en caso se ingrese para poder encontrar el dominio y hacer el request
		base="http://"
		if(base==addr[0:7]):
			i=len(addr)
			addr=addr[7:i]
			print(addr)
		else:
			print(addr)

		#Se separa el dominio de interés del directorio al cual se busca accesar donde se encuentra el objeto
		addr_prov=""
		flag=1
		direct=""
		for i in range(len(addr)):
			if (addr[i]=='/'):
				flag=0
			if (flag==1):
				addr_prov=addr_prov+addr[i]
			else:
				direct=direct+addr[i]

		addr=str(addr_prov)
		#Caso en que no se ingrese directorio para solicitar el root del dominio que se busca
		if(direct==""):
			direct="/"
		print(addr)
		print(direct)
		#Request de hhtp que se hace en base al input procesado previamente
		req=f"GET {direct} HTTP/1.1\r\nHost: {addr}\r\nConnection: keep-alive\r\nUpgrade-Insecure-Requests: 1\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36 OPR/90.0.4480.100 (Edition std-1)\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\nAccept-Encoding: gzip, deflate\r\nAccept-Language: en US,en;q=0.9\r\n\r\n".encode('ASCII')
		#Conección al soquet para mandar el request
		sock1.connect((addr,80))
		sock1.send(req)
		resp=b""
		#Ciclo para recibir la información solicitada por medio del socket
		while True:
			chunk=sock1.recv(2048)
			if (len(chunk)==0): #se revisa que aun haya algo para recibir
				print('espere')
				break #ademas, se revisa que ya se haya revisado el final del archivo html para ahorrar tiempo
			if ("</html>" in chunk.decode().lower()):
				print('termine antes')
				break
			elif ("</HTML>" in chunk.decode().upper()):
				print('termine antes')
				break
			print(chunk.decode())


		resp=chunk.decode()
		#Procesamiento del request recibido para extraer el código html en un archivo separado
		sep='<html>'
		webcode=sep+'\n'+resp.split(sep)[1]
		print('Aqui va la pagina:')
		print(webcode)
		sock1.close() #se cierra el socket
		self.textEdit_6.setHtml(webcode) #se muestra el html en la interfaz
	def dns(self):
		print(self.textEdit_2.toPlainText()) #se revisan los valores ingresados
		print(self.textEdit_3.toPlainText())
		print(self.textEdit_4.toPlainText())
		dom=self.textEdit_2.toPlainText() #se relacionan los inputs con las variables a trabajar
		serv=self.textEdit_3.toPlainText()
		req=self.textEdit_4.toPlainText()
		lbls=dom.split('.') #se separa por puntos el dominio ingresado
		largos=[]
		domain=''
		#se crea un diccionario con la codificacion de los tipos de registro
		regis ={'A':'0001','AAAA':'001c','NS':'0002','MX':'000F','CNAME':'0005','TXT':'0010','RP':'0011'}
		#se crea una lista que contenga los largos de cada palabra del dominio
		for i in range(len(lbls)):
			largos.append(str(len(lbls[i])))
		print(largos)
		print(lbls)
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #se abre el socket
		sock.connect((serv, 53))
		#'0001 0100 0001 0000 0000 0000'
		# ID  Flag Quest AnsRRAutoRR AddRR
		#Viene el dominio de pregunta codificado. Inicia con 0x03
		#Viene el tipo de preg 0x0001 es tipo A
		#Clase, dejar IN
		h1=bytes.fromhex('000201000001000000000000').decode()
		#h1: 2 bytes de ID,
		#0002
		#bit de query, 4 bits del tipo de query (0 en este caso)
		#AA flag, en 1 cuando es un authoritative answer, por ser query va en 0
		#TC flag, 1 bit que indica si la respuesta excede los 512 bytes
		#RD flag indica si se quieren preguntar a DNS's de manera recursiva. Ahorita en 1
		#El resto de los 16 bits son mas flags.
		#0100
		#Se tiene que escribir el QDCOUNT, ANCOUNT, NSCOUNT y ARCOUNT todos en 0 menos el QDCOUNT
		#0001 QD
		#0000 x3 (ANCOUNT, NSCOUNT, ARCOUNT)
		#0000 answer RRS
		#0000 Authority RRs
		#0000 Additional RRs (RR - resourse record)
		#Header de 12 bytes

		#Se pone el largo del label y despues los bytes de los caracteres del laberl
		for i in range(len(lbls)):
			domain += format(int(largos[i]),'02x')
			for j in range(len(lbls[i])):
				domain += format(ord(lbls[i][j]),'02x')
		print(bytes.fromhex(domain).decode())
		name_fn=bytes.fromhex('00').decode() #Terminador secuencia de labels
		print(name_fn)
		#clase de Record IN
		class_IN=bytes.fromhex('0001').decode()
		#tipo de query
		type_q=bytes.fromhex(regis[req]).decode()
		#se envia el query codificado en ASCII
		sock.send((h1+bytes.fromhex(domain).decode()+name_fn+type_q+class_IN).encode('ASCII'))
		response = sock.recv(4096) #se almacena la respuesta
		sock.close() #se cierra el socket
		auth=[]
		final = ''
		#se ordena la respuesta para extraer solo la direccion IP
		if (req == 'A'):
			ip1 = str(int(response.hex()[len(response.hex())-8:len(response.hex())-6],16))
			ip2 = str(int(response.hex()[len(response.hex())-6:len(response.hex())-4],16))
			ip3 = str(int(response.hex()[len(response.hex())-4:len(response.hex())-2],16))
			ip4 = str(int(response.hex()[len(response.hex())-2:len(response.hex())-0],16))
			final = ip1+'.'+ip2+'.'+ip3+'.'+ip4
			#self.textEdit_5.setText(ip)
		else:
			#se revisa cada byte de la respuesta para ver si se encuentra dentro de los
			#caracteres permitidos para nombres de dominio, si si se encuentra, se decodifica
			#a su descripcion en ASCII, sino, se deja en hexadecimal
			for i in range(int(len(response.hex())/2)):
				auth.append(response.hex()[2*i]+response.hex()[2*i+1])
			for i in range(len(auth)):
				if (48<=int(auth[i],16)<=57):
					final += bytes.fromhex(auth[i]).decode('ASCII')
				elif (97<=int(auth[i],16)<=122):
					final += bytes.fromhex(auth[i]).decode('ASCII')
				elif (65<=int(auth[i],16)<=90):
					final += bytes.fromhex(auth[i]).decode('ASCII')
				elif (int(auth[i],16)==45):
					final += bytes.fromhex(auth[i]).decode('ASCII')
				elif (int(auth[i],16)==46):
					final += bytes.fromhex(auth[i]).decode('ASCII')
				else:
					final +=auth[i]
		#se coloca el string arreglado en la interfaz
		self.textEdit_5.setText(final)

aplication = QtWidgets.QApplication([])
mastermain=browser()
mastermain.show()
aplication.exec_()
