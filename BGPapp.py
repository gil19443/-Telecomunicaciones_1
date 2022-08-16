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
        self.textEdit_2.setText('174')
        self.textEdit_3.setText('07:00:00')
        self.textEdit_4.setText('12:00:00')
        self.textEdit_5.setText('2022-08-14')
        self.textEdit_6.setText('2022-08-14') #se colocan las condiciones iniciales de los elementos de la interfaz
        self.showMaximized()#Funcion para que la interfaz se abra en pantalla completa
        self.pushButton.clicked.connect(self.graph)#callback function del boton
        self.pushButton_2.clicked.connect(self.changes)#callback function del boton 2
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
        #se establecen las variables que se van a utilizar
        global cambio
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
        resp = requests.get(url)
        #se guardan todos los cambiso registrados en el intervalo ingresado
        for i in range(len(resp.json()['data']['events'])):
            if (len(resp.json()['data']['events'][i]["attrs"])>2):
                paths.append(resp.json()['data']['events'][i]["attrs"]['path'])
        #se revisa que si se hayan guardado cambios
        if (len(paths)!=0):
            for i in range(len(paths)):
                for j in range(len(paths[i])):
                    #se revisaa si hay una coincidencia con el AS ingresado por el usuario
                    if (int(paths[i][j])==int(self.textEdit_2.toPlainText())):
                        print(paths[i])
                        #se almacenan los paths desde el AS de origen hasta el AS de coincidencia
                        for k in range(len(paths[i])-paths[i].index(paths[i][j])):
                            changes.append(paths[i][len(paths[i])-k-1])
            print(changes)
            #se revisa que si hayan habido coincidencias
            if (len(changes)!=0):
                changes1 = np.array(changes)
                #se bucan las ubicaciones del AS de origen en el arreglo general para separarlo por paths individuales
                ubi = np.where(changes1 == paths[0][len(paths[0])-1])
                #se coloca el numero de paths registrados en la interfaz
                self.label_7.setText('Eventos: {}'.format(len(ubi[0])))
                #se guardan en el diccionario las rutas individuales
                for i in range(len(ubi[0])):
                    if (i==(len(ubi[0])-1)):
                        final[i] = changes[ubi[0][i]:]
                    else:
                        final[i] = changes[ubi[0][i]:ubi[0][i+1]]
                #se verifica que el valor del cambio no exceda la cantidad de eventos registrados
                if (cambio < (len(ubi[0])-1)):
                    cambio = cambio +1
                else:
                    cambio = 0
                #se arman los arreglos con los puntos
                for j in range(len(final[cambio])-1):
                    y.append(final[cambio][j+1])
                    x.append(final[cambio][j])
                #para graficar, mismo proceso que el anterior
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
                #en caso que no hubieran coincidencias con los cambios, se buscan en en otra ubicacion
                #para graficar el estado inicial
                #se registran los paths del estado inicial
                for i in range(len(resp.json()['data']['initial_state'])):
                    if (len(resp.json()['data']['initial_state'][i]["path"])!=0):
                        original.append(resp.json()['data']['initial_state'][i]["path"])
                #se revisa que hayan paths registrados
                if (len(original)!=0):
                    for i in range(len(original)):
                        for j in range(len(original[i])):
                            if (int(original[i][j])==int(self.textEdit_2.toPlainText())):
                                for k in range(len(original[i])-original[i].index(original[i][j])):
                                    temp_state.append(original[i][len(original[i])-k-1])
                    #se revisa que hayan coincidencias con el AS ingresado por el usuario
                    if (len(temp_state)==0):
                        temp_state.append("nada que mostrar")
                        temp_state.append(self.textEdit_2.toPlainText())
                    else:
                        #si hubieron coincidencias, mismo proceso que el descrito anteriormente
                        print(temp_state)
                        temp1 = np.array(temp_state)
                        ubi2 = np.where(temp1 == original[0][len(original[0])-1])
                        print(len(ubi2[0]))
                        self.label_7.setText('Eventos: {}'.format(len(ubi2[0])))
                        for i in range(len(ubi2[0])):
                            if (i==(len(ubi2[0])-1)):
                                final_state[i] = temp_state[ubi2[0][i]:]
                            else:
                                final_state[i] = temp_state[ubi2[0][i]:ubi2[0][i+1]]
                        print(final_state)
                        print(cambio)
                        if (cambio < (len(ubi2[0])-1)):
                            cambio = cambio +1
                        else:
                            cambio = 0
                        for j in range(len(final_state[cambio])-1):
                            y.append(final_state[cambio][j+1])
                            x.append(final_state[cambio][j])
                    #para graficar, lo mismo que se realizo en los ciclos anteriores
                    G = nx.Graph()
                    edges = list(zip(x,y))
                    print(edges)
                    G.add_edges_from(edges)
                    print(G)
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
        else:
            #si no hay cambios, tambien se bucann paths en el estado iniciales
            #se realiza lo descrito anterioremente
            for i in range(len(resp.json()['data']['initial_state'])):
                if (len(resp.json()['data']['initial_state'][i]["path"])!=0):
                    original.append(resp.json()['data']['initial_state'][i]["path"])
            if (len(original)!=0):
                for i in range(len(original)):
                    for j in range(len(original[i])):
                        if (int(original[i][j])==int(self.textEdit_2.toPlainText())):
                            print(original[i])
                            for k in range(len(original[i])-original[i].index(original[i][j])):
                                temp_state.append(original[i][len(original[i])-k-1])
                if (len(temp_state)==0):
                    temp_state.append("nada que mostrar")
                    temp_state.append(self.textEdit_2.toPlainText())
                else:
                    temp1 = np.array(temp_state)
                    ubi2 = np.where(temp1 == original[0][len(original[0])-1])
                    self.label_7.setText('Eventos: {}'.format(len(ubi2[0])))
                    for i in range(len(ubi2[0])):
                        if (i==(len(ubi2[0])-1)):
                            final_state[i] = temp_state[ubi2[0][i]:]
                        else:
                            final_state[i] = temp_state[ubi2[0][i]:ubi2[0][i+1]]

                    if (cambio < (len(ubi2[0])-1)):
                        cambio = cambio +1
                    else:
                        cambio = 0
                    for j in range(len(final_state[cambio])-1):
                        y.append(final_state[cambio][j+1])
                        x.append(final_state[cambio][j])

                    G = nx.Graph()
                    edges = list(zip(x,y))
                    print(edges)
                    G.add_edges_from(edges)
                    print(G)
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
