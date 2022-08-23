#Universidad del Valle de Guatemala
#Sistemas de telecomunicaciones 1
#Propagación de prefijos de internet
#Autor: Carlos Gil
#Guatemala, 16 de agosto del 2022


from BGPplay import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPainter, QPen, QPixmap, QColor
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import networkx as nx
import numpy as np
import threading
import time
import sys
import math
import networkx as nx
import requests
import numpy as np
import BGPplay #esqueleto de la interfaz utilizada
cambio = 0 #variable global para registrar los cambios en el tiempo
respuesta = {}
cambios = {}
changes = []
original = []
class master (QtWidgets.QMainWindow, Ui_MainWindow,QWidget):
    def __init__ (self):
        super(master,self).__init__()
        self.setupUi(self)
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)#se establece una ventana de matplotlib
        self.toolbar = NavigationToolbar(self.canvas, self)#se establece la barra de navegación a la ventana
        self.gridLayout_3.addWidget(self.canvas)#se colocan los elemento anteriores en la interfaz
        self.gridLayout_3.addWidget(self.toolbar)


        self.show()#se muestran los graficos
        self.textEdit.setText('181.174.107.0/24')
        self.textEdit_2.setText('134823')
        self.textEdit_3.setText('23:42:56')
        self.textEdit_4.setText('23:58:25')
        self.textEdit_5.setText('2022-08-14')
        self.textEdit_6.setText('2022-08-14') #se colocan las condiciones iniciales de los elementos de la interfaz
        self.showMaximized()#Funcion para que la interfaz se abra en pantalla completa
        self.pushButton.clicked.connect(self.graph)#callback function del boton
        self.pushButton_2.clicked.connect(self.changes)#callback function del boton 2
        self.pushButton_3.clicked.connect(self.filtrar)#callback function del boton 3
        self.update()#actualizar valores

    def graph(self):
        self.figure.clf() #se llimpia la figura
        paths = [] #se declaran las variables que se van a utilizar
        x = []
        y = []
        edges = []
        index = 0
        color = []
        url = 'https://stat.ripe.net/data/ris-peerings/data.json?resource={0}&starttime={3}T{1}&endtime={4}T{2}'.format(self.textEdit.toPlainText(),self.textEdit_3.toPlainText(),self.textEdit_4.toPlainText(),self.textEdit_5.toPlainText(),self.textEdit_6.toPlainText())
        print(url) #se arma la url para hacer la solicitud
        resp = requests.get(url)#se guarda la repuesta de la solicitud
        #se busca en el diccionario de la solicitud cada AS path disponible
        for i in range (len(resp.json()['data']['peerings'])):
            #print(resp.json()['data']['peerings'][i]["probe"]["city"])
            for j in range (len(resp.json()['data']['peerings'][i]['peers'])):
                    if(len(resp.json()['data']['peerings'][i]['peers'][j]['routes']) != 0):
                        paths.append(resp.json()['data']['peerings'][i]['peers'][j]['routes'][0]['as_path'])
        #se verifica que si hayan paths registrados
        if (len(paths)!=0):
            #se almacenan los datos en dos arreglos, para luego hacer el grafico
            for i in range(len(paths)):
                #3print(len(paths))
                for j in range(len(paths[i])-1):
                    y.append(paths[i][len(paths[i])-2-j])
                    x.append(paths[i][len(paths[i])-j-1])
            #se crea un grafico
            G = nx.Graph()
            #se añade un arreglo de tuplas con cada elemento de los arreglos armados previamente
            edges = list(zip(x,y))
            print(edges)
            #Se establecen los enlaces entre los elementoss del grafico
            G.add_edges_from(edges)
            print(G)
            #se colorea de diferente color el AS de origen de los anuncios
            for i in range(G.number_of_nodes()):
                if (i==0):
                    color.append("red")
                else:
                    color.append('lightblue')
            #se establece un layout para hacer la gráfica
            pos = nx.spring_layout(G,k=0.045,seed = 123456)
            nx.draw(G, pos , with_labels = True, width=0.4,node_color=color, node_size=1000)
            #se coloca el grafico en el canvas de la interfaz
            self.canvas.draw_idle()
        else:
            #si no hay paths disponibles, se grafica una ventana de alerta
            self.figure.clf()
            G = nx.Graph()
            G.add_edges_from([("no hay rutas para mostrar de",self.textEdit.toPlainText())])
            pos = nx.spring_layout(G,k=0.045,seed = 123456)
            nx.draw(G, pos , with_labels = True, width=0.4,node_color="red", node_size=1000)
            self.canvas.draw_idle()

    def changes(self):
        self.figure.clf()
        global original
        global changes
        global cambio
        paths = []
        x = []
        y = []
        edges = []
        index = 0
        color = []
        final = {}
        temp_state = []
        final_state = {}

        if (cambio < (len(changes)-1)):
            cambio = cambio +1
        else:
            cambio = 0
            #se muestra los eventos dispoibles
        self.label_7.setText('E:{0}/{1}'.format(cambio,len(changes)))
        #se revisa si ASN final coincide con evento para remplazarlo
        for i in range(len(original)):
            if (int(original[i][0])==int(changes[cambio][0])):
                print(original[i])
                original[i]=changes[cambio]

        if (len(original)!=0):
            #se filtran las rutas que poseen el AS ingreasado por le usuario
            for i in range(len(original)):
                for j in range(len(original[i])):
                    if (int(original[i][j])==int(self.textEdit_2.toPlainText())):
                        temp_state.append(original[i])
            if (len(temp_state)==0):
                temp_state.append("nada que mostrar")
                temp_state.append(self.textEdit_2.toPlainText())
            else: #mismo proceso para graficar que el que se describio anteriormente
                for i in range(len(temp_state)):
                    for j in range(len(temp_state[i])-1):
                        y.append(temp_state[i][len(temp_state[i])-2-j])
                        x.append(temp_state[i][len(temp_state[i])-j-1])
                G = nx.Graph()
                edges = list(zip(x,y))
                G.add_edges_from(edges)
                for i in range(G.number_of_nodes()):
                    if (i==0):
                        color.append("red")
                    else:
                        color.append('lightblue')
                pos = nx.spring_layout(G,k=0.045,seed = 123456)
                nx.draw(G, pos , with_labels = True, width=0.4,node_color=color, node_size=1000)
        else:
            self.figure.clf()
            G = nx.Graph()
            G.add_edges_from([("no hay rutas para mostrar de",self.textEdit.toPlainText())])
            pos = nx.spring_layout(G,k=0.045,seed = 123456)
            nx.draw(G, pos , with_labels = True, width=0.4,node_color="red", node_size=1000)
        self.canvas.draw_idle()

    def filtrar(self):
        self.figure.clf()
        #se establecen las variables que se van a utilizar
        global cambio
        global respuesta
        global original
        global changes
        paths = []
        changes=[]
        x = []
        y = []
        edges = []
        index = 0
        color = []
        final = {}
        original = []
        temp_state = []
        final_state = {}
        url = 'https://stat.ripe.net/data/bgplay/data.json?resource={0}&starttime={3}T{1}&endtime={4}T{2}'.format(self.textEdit.toPlainText(),self.textEdit_3.toPlainText(),self.textEdit_4.toPlainText(),self.textEdit_5.toPlainText(),self.textEdit_6.toPlainText())
        print(url)
        respuesta = requests.get(url).json()
        #se guarda el estado inicial de cada ruta
        for i in range(len(respuesta['data']['initial_state'])):
            if (len(respuesta['data']['initial_state'][i]["path"])!=0):
                original.append(respuesta['data']['initial_state'][i]["path"])
        #se guardan los cambios en el intervalo
        for i in range(len(respuesta['data']['events'])):
            if (len(respuesta['data']['events'][i]["attrs"])>2):
                changes.append(respuesta['data']['events'][i]["attrs"]['path'])
                #se grafica el estado inicial de las rutas que incluye el ASN ingresado por el usuario
        if (len(original)!=0):
            for i in range(len(original)):
                for j in range(len(original[i])):
                    if (int(original[i][j])==int(self.textEdit_2.toPlainText())):
                        temp_state.append(original[i])
            if (len(temp_state)==0):
                temp_state.append("nada que mostrar")
                temp_state.append(self.textEdit_2.toPlainText())
            else:
                for i in range(len(temp_state)):
                    for j in range(len(temp_state[i])-1):
                        y.append(temp_state[i][len(temp_state[i])-2-j])
                        x.append(temp_state[i][len(temp_state[i])-j-1])
                G = nx.Graph()
                edges = list(zip(x,y))
                G.add_edges_from(edges)
                for i in range(G.number_of_nodes()):
                    if (i==0):
                        color.append("red")
                    else:
                        color.append('lightblue')
                pos = nx.spring_layout(G,k=0.045,seed = 123456)
                nx.draw(G, pos , with_labels = True, width=0.4,node_color=color, node_size=1000)
        else:
            self.figure.clf()
            G = nx.Graph()
            G.add_edges_from([("no hay rutas para mostrar de",self.textEdit.toPlainText())])
            pos = nx.spring_layout(G,k=0.045,seed = 123456)
            nx.draw(G, pos , with_labels = True, width=0.4,node_color="red", node_size=1000)
        self.canvas.draw_idle()

aplication = QtWidgets.QApplication([])
mastermain=master()
mastermain.show()
aplication.exec_()
