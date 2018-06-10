from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import Utils
import GraphInspection
from ClusterAdjustments import ClusterDialog
from ClusterPointsAdjustments import ClusterPointsView
from CureImplementation import CureWindow
from KMeansImplementation import KMeansWindow
from XMeansImplementation import XMeansWindow
from AglomerativeImplementation import AgglomerativeWindow
from DataPreview import DataPreviewWindow
from UtilityClasses import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import Constants


class MainWindow(QMainWindow):
    inspectionWindow = None

    clusterPointsAdjustmentsWindow = None

    clusters = []

    def __init__(self):
        super().__init__()
        self.menubar = self.menuBar()
        self.fileMenu = self.menubar.addMenu("Файл")
        self.openFile = QAction('Открыть', self)
        self.openFile.triggered.connect(self.openFilePressed)
        self.fileMenu.addAction(self.openFile)
        self.algorithmsMenu = self.menubar.addMenu("Алгоритмы")

        self.kmeansoption = QAction("Алгоритм KMeans(KMeans++)", self)
        self.kmeansoption.triggered.connect(self.kmeansoptionChosen)

        self.xmeansoption = QAction("Алгоритм xMeans", self)
        self.xmeansoption.triggered.connect(self.xmeansoptionChosen)

        self.agglomerativeoption = QAction("Алгоритм Agglomerative", self)
        self.agglomerativeoption.triggered.connect(self.agglomerativeChosen)

        self.cureoption = QAction("Алгоритм CURE", self)
        self.cureoption.triggered.connect(self.cureoptionChosen)
        self.algorithmsMenu.addAction(self.cureoption)

        self.algorithmsMenu.addAction(self.kmeansoption)

        self.algorithmsMenu.addAction(self.xmeansoption)

        self.algorithmsMenu.addAction(self.agglomerativeoption)

        self.mainTabs = QTabWidget()
        self.mainTabs.setStyleSheet("QTabWidget { border: 0px solid black }; ");
        self.setCentralWidget(self.mainTabs)
        self.figure = Figure()
        self.matrixWidget = FigureCanvas(self.figure)
        self.matrixWidget.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.matrixWidget.setMinimumSize(640, 480)
        self.matrixWidget.resize(640, 480)
        self.matrixScrollArea = QScrollArea()
        self.matrixScrollArea.setWidget(self.matrixWidget)
        self.matrixScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.matrixScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.mainTabs.addTab(self.matrixScrollArea, "Графики")
        self.dataWidget = QWidget()
        self.dataLayout = QVBoxLayout(self.dataWidget)
        self.dataTable = QTableWidget()
        self.dataLayout.addWidget(self.dataTable)
        self.mainTabs.addTab(self.dataWidget, "Данные")
        self.clustersWidget = QWidget()
        self.clustersLayout = QVBoxLayout(self.clustersWidget)
        self.clustersTable = QTableWidget()
        self.clustersTable.setColumnCount(5)
        self.clustersTable.setHorizontalHeaderLabels(
            ["Имя кластера", "Количество", "Маркер", "Скрыт", ""])
        self.clustersLayout.addWidget(self.clustersTable)
        self.mainTabs.addTab(self.clustersWidget, "Кластеры")

        self.setWindowTitle('Cluster Analysis 2.0')
        self.setWindowIcon(QIcon('icon\\app_icon.png'))
        self.setGeometry(100, 100, 640, 480)
        self.showMaximized()

    def openFilePressed(self):
        filename = QFileDialog.getOpenFileName(self, 'Open file', "data")[0]
        if len(filename) > 0:
            newData = DataPreviewWindow.preprocessData(Data(Utils.readExcelData(filename)))
            if newData is not None:
                self.startWorkingWithData(newData)

    def startWorkingWithData(self, data):
        self.globalData = data
        self.cleanupAppData()
        Utils.fillTableWithData(self.dataTable, self.globalData)
        self.initCanvas()

    def canvasClicked(self, event):
        if event.inaxes is not None:
            ax = event.inaxes
            if (len(ax.lines)) != 0:
                self.inspectionWindow = GraphInspection.GraphInspectionWindow(self, ax)

    def addCluster(self, cluster):
        self.clusters.append(cluster)
        self.addClusterToTable(cluster)
        self.refreshCanvas()

    def addClusterToTable(self, cluster):
        self.clustersTable.setRowCount(self.clustersTable.rowCount() + 1)
        currentRowIndex = self.clustersTable.rowCount() - 1
        self.clustersTable.setItem(currentRowIndex, 0, QTableWidgetItem(cluster.getName()))
        self.clustersTable.setItem(currentRowIndex, 1, QTableWidgetItem(str(cluster.getSize())))

        figure = Figure()
        markerShapeCell = FigureCanvas(figure)
        markerShapeCell.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        axes = figure.add_subplot(111)
        axes.axis("off")
        markerSize = 8
        axes.plot([1], [1], linestyle="None", marker=cluster.getShape(), color=cluster.getColor(),
                  markersize=markerSize)
        markerShapeCell.draw()
        self.clustersTable.setCellWidget(currentRowIndex, 2, markerShapeCell)
        if cluster.isHidden():
            self.clustersTable.setItem(currentRowIndex, 3, QTableWidgetItem("Да"))
        else:
            self.clustersTable.setItem(currentRowIndex, 3, QTableWidgetItem("Нет"))

        clusterOptionsButton = QPushButton("Опции")
        clusterOptionsMenu = QMenu()
        self.clustersTable.setCellWidget(currentRowIndex, 4, clusterOptionsButton)
        index = QPersistentModelIndex(self.clustersTable.model().index(currentRowIndex, 4))

        adjustClusterAction = QAction("Параметры кластера", self)
        adjustClusterAction.triggered.connect(
            lambda *args, index=index: self.adjustCluster(index.row()))
        clusterOptionsMenu.addAction(adjustClusterAction)

        hideorshowClusterAction = QAction("Скрыть/показать кластер", self)
        hideorshowClusterAction.triggered.connect(
            lambda *args, index=index: self.hideorshowCluster(index.row()))
        clusterOptionsMenu.addAction(hideorshowClusterAction)

        removeClusterAction = QAction("Удалить кластер", self)
        removeClusterAction.triggered.connect(
            lambda *args, index=index: self.removeCluster(index.row()))
        clusterOptionsMenu.addAction(removeClusterAction)

        adjustClusterPointsAction = QAction("Просмотр точек", self)
        adjustClusterPointsAction.triggered.connect(
            lambda *args, index=index: self.adjustClusterPoints(index.row()))
        clusterOptionsMenu.addAction(adjustClusterPointsAction)

        clusterOptionsButton.setMenu(clusterOptionsMenu)

    def adjustCluster(self, index):
        cluster = ClusterDialog.adjustCluster(self.clusters[index])
        if cluster is not None:
            self.clusters[index] = cluster
            self.refreshClusterTable()  # TODO вместо обновления всей таблицы, обновлять только строку этого кластера refreshRow
            self.refreshCanvas()  # TODO и перерисовывать только его точеи

    def hideorshowCluster(self, index):
        self.clusters[index].setHidden(not self.clusters[index].isHidden())
        self.refreshCanvas()
        self.refreshClusterTable()

    def removeCluster(self, index):
        del self.clusters[index]
        self.clustersTable.removeRow(index)
        self.refreshCanvas()

    def adjustClusterPoints(self, index):
        self.clusterPointsAdjustmentsWindow = ClusterPointsView(self, self.clusters[index])

    def initCanvas(self):
        columns = self.globalData.getSignificantColumns()
        columnCount = self.globalData.significantColumnCount()
        self.matrixWidget.resize(columnCount * 200, columnCount * 200)
        for j in range(0, columnCount):
            for i in range(0, columnCount):
                columnForAbscissas = columns[i]
                columnForOrdinates = columns[j]
                axes = self.figure.add_subplot(columnCount, columnCount, j * columnCount + i + 1)
                axes.scatterMatrixXIndex = columnForAbscissas.getIndex()
                axes.scatterMatrixYIndex = columnForOrdinates.getIndex()
                if columnForAbscissas == columnForOrdinates:
                    axes.hist(columnForAbscissas.getData(), facecolor=Constants.DEFAULT_HISTOGRAM_COLOR)
                    axes.set_title("гистограмма " + columnForOrdinates.getName())
                else:
                    axes.plot(columnForAbscissas.getData(), columnForOrdinates.getData(),
                              marker=Constants.DEFAULT_POINT_SHAPE,
                              linestyle="None",
                              markersize=Constants.DEFAULT_MARKER_SIZE_SMALL,
                              color=Constants.DEFAULT_POINT_COLOR)
                    axes.set_title(columnForOrdinates.getName() + "_" + columnForAbscissas.getName())
                for item in ([axes.title, axes.xaxis.label, axes.yaxis.label] +
                                 axes.get_xticklabels() + axes.get_yticklabels()):
                    item.set_fontsize(8)
                axes.tick_params(axis=u'both', which=u'both', length=0)
        self.matrixWidget.mpl_connect('button_press_event', self.canvasClicked)
        self.figure.tight_layout()
        self.matrixWidget.draw()
        self.matrixScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.matrixScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    def refreshCanvas(self):
        columnCount = self.globalData.significantColumnCount()
        columns = self.globalData.getSignificantColumns()
        for i in range(0, columnCount):
            for j in range(0, columnCount):
                if i != j:
                    axes = self.figure.add_subplot(columnCount, columnCount, j * columnCount + i + 1)
                    while len(axes.lines) > 0:
                        del axes.lines[-1]
                    axes.add_line(Utils.getSupportiveLine(self.globalData.getSignificantColumns(), i, j))
                    for cluster in self.clusters:
                        cluster.draw2DProjection(axes, columns[i].getIndex(), columns[j].getIndex())
                    dummyCluster = self.globalData.getDummyCluster(self.clusters)
                    dummyCluster.draw2DProjection(axes, columns[i].getIndex(), columns[j].getIndex())
        self.matrixWidget.draw()

    def refreshClusterTable(self):
        self.clustersTable.setRowCount(0)
        for cluster in self.clusters:
            self.addClusterToTable(cluster)

    def cleanupAppData(self):
        self.clustersTable.setRowCount(0)
        self.clusters.clear()
        self.figure.clear()

    def cureoptionChosen(self):
        self.curewindow = CureWindow(self)

    def kmeansoptionChosen(self):
        self.kmeanswindow = KMeansWindow(self)

    def xmeansoptionChosen(self):
        self.xmeanswindow = XMeansWindow(self)

    def agglomerativeChosen(self):
        self.agqlomerativewindow = AgglomerativeWindow(self)
