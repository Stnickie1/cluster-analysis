from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from pyclustering.cluster.center_initializer import kmeans_plusplus_initializer
import Constants
import random
from pyclustering.cluster.kmeans import kmeans

from UtilityClasses import Cluster
from Utils import calculate_ssw, calculate_ssb, calculate_sst


SST = 0

RS_RESULT = list()


class KMeansWindow(QMainWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.setGeometry(100, 100, 200, 200)
        label1 = QLabel('Numbers of centers', self)
        label1.move(15, 10)
        self.createClusterButton = QPushButton("Create clusters", self)
        self.createClusterButton.move(90, 90)
        self.createClusterButton.clicked.connect(self.KMeansAlgorithm)
        self.numofclusterscure = QLineEdit(self)
        self.numofclusterscure.move(15, 40)
        # здесь создаем интерфейс, в котором просим от пользователя ввести какие-то данные типо,
        # сколько кластеров он хочет и все остальное

        self.setWindowTitle("Алгоритм KMeans(KMeans++)")
        self.show()

    def KMeansAlgorithm(self):
        # получаем данные из родительского окна
        clusters = KMeansWindow.get_kmeans_clusters(self.parent().globalData, int(self.numofclusterscure.text()))
        for cluster in clusters:
            self.parent().addCluster(cluster)
        self.close()

    @staticmethod
    def get_rows_kmeans(data, cluster):
        rows = data.getRowsByIndexSet(cluster)
        return rows

    @staticmethod
    def get_kmeans_clusters(data, count_centers):
        rows = data.getRows()
        input_data = list()
        result_clusters = list()
        for row in rows:
            input_data.append(row.getDataArray())
        SST = calculate_sst(input_data)

        # initialize initial centers using K-Means++ method
        initial_centers = kmeans_plusplus_initializer(input_data, count_centers).initialize()
        # create instance of K-Means algorithm with prepared centers
        kmeans_instance = kmeans(input_data, initial_centers)
        # run cluster analysis and obtain results
        kmeans_instance.process()
        clusters = kmeans_instance.get_clusters()
        colorRange = Constants.DEFAULT_COLOR_SET
        SSB = 0
        SSW = 0
        for i, cluster in enumerate(clusters):
            result_cluster = Cluster(KMeansWindow.get_rows_kmeans(data, cluster))
            ro = KMeansWindow.get_rows_kmeans(data, cluster)
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
