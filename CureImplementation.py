from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from pyclustering.cluster.cure import cure
import Constants
import random
from UtilityClasses import Cluster, Row
from Utils import calculate_ssw, calculate_ssb, calculate_sst

SST = 0

RS_RESULT = list()


class CureWindow(QMainWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.setGeometry(100, 100, 200, 200)
        label1 = QLabel('Numbers of clusters', self)
        label1.move(15, 10)
        self.createClusterButton = QPushButton("Create clusters", self)
        self.createClusterButton.move(90, 90)
        self.createClusterButton.clicked.connect(self.cureAlgorithm)
        self.numofclusterscure = QLineEdit(self)
        self.numofclusterscure.move(15, 40)
        # здесь создаем интерфейс, в котором просим от пользователя ввести какие-то данные типо,
        # сколько кластеров он хочет и все остальное

        self.setWindowTitle("Алгоритм CURE")
        self.show()

    def cureAlgorithm(self):
        # получаем данные из родительского окна
        clusters = CureWindow.get_cure_clusters(self.parent().globalData, int(self.numofclusterscure.text()))
        for cluster in clusters:
            self.parent().addCluster(cluster)
        self.close()

    @staticmethod
    def getRowIndexByData(data, row_data):
        rows = data.getRows()
        for row in rows:
            if row.getDataArray() == row_data:
                return row.getIndex()

    @staticmethod
    def get_rows(data, cluster):
        rows = list()

        for i, data_array in enumerate(cluster):
            index = CureWindow.getRowIndexByData(data, data_array)
            rows.append(Row(index=index, dataArray=data_array))

        return rows

    @staticmethod
    def get_cure_clusters(data, count_clusters=3):
        rows = data.getRows()
        input_data = list()
        result_clusters = list()
        for row in rows:
            input_data.append(row.getDataArray())
        SST = calculate_sst(input_data)
        cure_instance = cure(input_data, count_clusters)
        cure_instance.process()
        clusters = cure_instance.get_clusters()
        colorRange = Constants.DEFAULT_COLOR_SET
        SSB = 0
        SSW = 0
        for i, cluster in enumerate(clusters):
            SSW = SSW + calculate_ssw(cluster)
            result_cluster = Cluster(CureWindow.get_rows(data, cluster))
            colour = random.choice(colorRange)
            result_cluster.setName(colour)
            result_cluster.setColor(colour)
            result_clusters.append(result_cluster)
        SSB = calculate_ssb(SST, SSW)
        RS_RESULT.append(SSB / SST)

        print(RS_RESULT)
        return result_clusters
