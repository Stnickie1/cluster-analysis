from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import numpy as np
import operator
import Utils

class ClusterPointsView(QMainWindow):

    def __init__(self, parent, cluster):
        super().__init__(parent)
        self.cluster = cluster
        self.columnCount = self.parent().globalData.columnCount()
        self.centralWidget = QWidget()
        self.layout = QHBoxLayout(self.centralWidget)
        self.setCentralWidget(self.centralWidget)
        self.tabletabs = QTabWidget()
        self.tabletabs.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.clusterPointsTable = QTableWidget();
        self.clusterPointsTable.resizeColumnsToContents()
        self.tabletabs.addTab(self.clusterPointsTable, "Удаление точек")
        self.unbusyPointsTable = QTableWidget()
        self.tabletabs.addTab(self.unbusyPointsTable, "Добавление точек")
        self.layout.addWidget(self.tabletabs)

        self.figure = Figure()
        self.barWidget = FigureCanvas(self.figure)
        self.axes = self.figure.add_subplot(111)
        self.refreshBarChart()

        self.figure_manh = Figure()
        self.barWidget_manh = FigureCanvas(self.figure_manh)
        self.axes_manh = self.figure_manh.add_subplot(111)
        self.refreshManhBarChart()

        self.bartabs = QTabWidget()
        self.bartabs.addTab(self.barWidget, "Евклидово расстояние")
        self.bartabs.addTab(self.barWidget_manh, "Манхэттэнское расстояние")
        self.bartabs.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)


        self.layout.addWidget(self.bartabs)
        self.refreshUnbusyPointsTable()
        self.refreshClusterPointsTable()
        self.resize(1000, 500)
        self.setWindowTitle("Точки кластера: " + cluster.getName())
        self.show()

    def refreshBarChart(self):
        self.axes.clear()
        xcoords = np.arange(self.cluster.getSize())
        distances = []
        indexes = self.cluster.getIndexList()
        massCenter = self.cluster.evaluateMassCenter()
        for row in self.cluster.getRows():
            distances.append(row.distanceTo(massCenter))
        sorteddata = self.sortBarData(indexes, distances)
        self.axes.bar(xcoords, sorteddata[1], align="center", tick_label=sorteddata[0])
        if self.cluster.getSize() > 10:
            for item in self.axes.get_xticklabels():
                item.set_fontsize(10 - self.cluster.getSize() // 8)
        self.axes.set_title("Расстояния до центра \n масс кластера")
        self.barWidget.draw()

    def refreshManhBarChart(self):
        self.axes_manh.clear()
        xcoords = np.arange(self.cluster.getSize())
        distances = []
        indexes = self.cluster.getIndexList()
        massCenter = self.cluster.evaluateMassCenter()
        for row in self.cluster.getRows():
            distances.append(row.manhattanDistanceTo(massCenter))
        sorteddata = self.sortBarData(indexes, distances)
        self.axes_manh.bar(xcoords, sorteddata[1], align="center", tick_label=sorteddata[0])
        if self.cluster.getSize() > 10:
            for item in self.axes_manh.get_xticklabels():
                item.set_fontsize(10 - self.cluster.getSize() // 8)
        self.axes_manh.set_title("Манхэттенские расстояния до центра \n масс кластера")
        self.barWidget_manh.draw()


    def refreshClusterPointsTable(self): # TODO установить заголовки для таблицы, использовать функцию
        self.clusterPointsTable.setRowCount(0)
        Utils.fillTableWithCluster(self.clusterPointsTable, self.cluster)
        self.clusterPointsTable.setColumnCount(self.columnCount + 1)
        for i, row in enumerate(self.cluster.getRows()):
            removePointButton = QPushButton("Исключить")
            self.clusterPointsTable.setCellWidget(i, self.columnCount, removePointButton)
            index = QPersistentModelIndex(self.clusterPointsTable.model().index(i, 0))
            removePointButton.clicked.connect(
                lambda *args, index=index: self.removePointFromCluster(index.row()))
        indexes = list(map(str, self.cluster.getIndexList()))
        self.clusterPointsTable.setVerticalHeaderLabels(indexes)

    def refreshUnbusyPointsTable(self):
        self.unbusyPointsTable.setColumnCount(self.columnCount + 1)
        self.unbusyPointsTable.setRowCount(0)
        busyIndexes = self.cluster.getIndexSet()
        indexes = []
        for rowNum, row in enumerate(self.parent().globalData.getRows()):
            if row.getIndex() not in busyIndexes:
                self.unbusyPointsTable.setRowCount(self.unbusyPointsTable.rowCount() + 1)
                indexes.append(row.getIndex())
                for columnIndex in range(0, self.columnCount):
                    self.unbusyPointsTable.setItem(self.unbusyPointsTable.rowCount() - 1, columnIndex,
                                                    QTableWidgetItem(str(row[columnIndex])))
                addPointButton = QPushButton("Добавить")
                a = self.unbusyPointsTable.rowCount()
                b = self.columnCount
                self.unbusyPointsTable.setCellWidget(self.unbusyPointsTable.rowCount() - 1, self.columnCount, addPointButton)
                addPointButton.clicked.connect(
                    lambda *args, row=row: self.addPointToCluster(row))
        self.unbusyPointsTable.setVerticalHeaderLabels(list(map(str, indexes)))

    def removePointFromCluster(self, index):
        del self.cluster[index]  # TODO почистить код от вызовов в стиле cluster.getRows() или row.getDataArray(),
        # в перспективе вообще удалить эти функции из классов
        self.refreshBarChart()
        self.refreshManhBarChart()
        self.refreshClusterPointsTable()
        self.refreshUnbusyPointsTable()

    def addPointToCluster(self, row):
        self.cluster.getRows().append(row)  # TODO cluster.addRow(row)
        self.refreshBarChart()
        self.refreshManhBarChart()
        self.refreshClusterPointsTable()
        self.refreshUnbusyPointsTable()

    def sortBarData(self, indexes, distances):
        mappeddata = dict(zip(indexes, distances))
        sorteddata = sorted(mappeddata.items(), key=operator.itemgetter(1))
        sorteddistances = []
        sortedindexes = []
        for element in sorteddata:
            sortedindexes.append(element[0])
            sorteddistances.append(element[1])
        return sortedindexes, sorteddistances

    def closeEvent(self, event):
        self.parent().refreshCanvas()
        self.parent().refreshClusterTable()
        event.accept()

