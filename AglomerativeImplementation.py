from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from pyclustering.cluster.agglomerative import agglomerative
import Constants
import random

from UtilityClasses import Cluster
from Utils import calculate_ssw, calculate_ssb, calculate_sst


SST = 0

RS_RESULT = list()


class AgglomerativeWindow(QMainWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.setGeometry(100, 100, 300, 300)
        label1 = QLabel('Numbers of centers', self)
        label1.move(15, 10)
        self.createClusterButton = QPushButton("Create clusters", self)
        self.createClusterButton.move(90, 90)
        self.createClusterButton.clicked.connect(self.AgglomerativeAlgorithm)
        self.numofclusterscure = QLineEdit(self)
        self.numofclusterscure.move(15, 40)

        self.centroid = QRadioButton("Centroid", self)
        self.single = QRadioButton("Single", self)
        self.single.setChecked(True)
        self.average = QRadioButton("Average", self)
        self.complete = QRadioButton("Complete", self)
        self.centroid.move(15, 125)
        self.single.move(15, 105)
        self.average.move(15, 85)
        self.complete.move(15, 65)
        # здесь создаем интерфейс, в котором просим от пользователя ввести какие-то данные типо,
        # сколько кластеров он хочет и все остальное

        self.setWindowTitle("Алгоритм Agglomerative)")
        self.show()

    def on_radio_button_toggled(self):
        radiobutton = self.sender()

        if radiobutton.isChecked():
            print("Selected country is %s" % (radiobutton.country))

    def AgglomerativeAlgorithm(self):
        # получаем данные из родительского окна
        if self.single.isChecked():
            line_type = 0
        elif self.complete.isChecked():
            line_type = 1
        elif self.average.isChecked():
            line_type = 2
        elif self.centroid.isChecked():
            line_type = 3
        clusters = AgglomerativeWindow.get_agglomerative_clusters(self.parent().globalData,
                                                                  int(self.numofclusterscure.text()), line_type)
        for cluster in clusters:
            self.parent().addCluster(cluster)
        self.close()

    @staticmethod
    def get_rows_agglomerative(data, cluster):
        rows = data.getRowsByIndexSet(cluster)
        return rows

    @staticmethod
    def get_agglomerative_clusters(data, count_clusters, line_type):
        rows = data.getRows()
        input_data = list()
        result_clusters = list()
        for row in rows:
            input_data.append(row.getDataArray())
        # create object that uses python code only
        SST = calculate_sst(input_data)

        agglomerative_instance = agglomerative(input_data, count_clusters, link=line_type)
        # cluster analysis
        agglomerative_instance.process()
        # obtain results of clustering
        clusters = agglomerative_instance.get_clusters()

        colorRange = Constants.DEFAULT_COLOR_SET
        SSB = 0
        SSW = 0
        for i, cluster in enumerate(clusters):
            result_cluster = Cluster(AgglomerativeWindow.get_rows_agglomerative(data, cluster))
            ro = AgglomerativeWindow.get_rows_agglomerative(data, cluster)
            f = [x._dataArray for x in ro]
            SSW = SSW + calculate_ssw(f)
            colour = random.choice(colorRange)
            result_cluster.setName(colour)
            result_cluster.setColor(colour)
            result_clusters.append(result_cluster)
        SSB = calculate_ssb(SST, SSW)
        RS_RESULT.append(SSB / SST)

        print(RS_RESULT)
        return result_clusters
